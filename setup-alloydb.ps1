# Tech Sarathi - AlloyDB Setup Script (PowerShell)
# This script provisions AlloyDB on Google Cloud Platform
# Project: nirman-project-493414 | Region: asia-south1

Write-Host "🚀 Tech Sarathi - AlloyDB Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "nirman-project-493414"
$REGION = "asia-south1"
$CLUSTER_NAME = "sarathi-cluster"
$INSTANCE_NAME = "sarathi-primary"
$NETWORK = "default"
$IP_RANGE_NAME = "sarathi-private-ip-alloc"

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
    Write-Host "✅ gcloud CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ gcloud CLI is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

Write-Host ""

# Prompt for project ID
$inputProject = Read-Host "Enter your GCP Project ID (default: nirman-project-493414)"
if ($inputProject) { $PROJECT_ID = $inputProject }

# Prompt for region
$inputRegion = Read-Host "Enter region (default: asia-south1)"
if ($inputRegion) { $REGION = $inputRegion }

# Prompt for password
$PASSWORD = ""
while ([string]::IsNullOrEmpty($PASSWORD)) {
    $securePassword = Read-Host "Enter database password" -AsSecureString
    $PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    )
    if ([string]::IsNullOrEmpty($PASSWORD)) {
        Write-Host "❌ Password cannot be empty" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Project ID: $PROJECT_ID"
Write-Host "   Region: $REGION"
Write-Host "   Cluster: $CLUSTER_NAME"
Write-Host "   Instance: $INSTANCE_NAME"
Write-Host "   Network: $NETWORK"
Write-Host ""

$confirm = Read-Host "Continue with setup? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Setup cancelled"
    exit 0
}

Write-Host ""
Write-Host "🔧 Setting up Google Cloud project..." -ForegroundColor Cyan

# Set project
gcloud config set project $PROJECT_ID

# ============================================================
# Step 1: Enable required APIs
# ============================================================
Write-Host "📦 Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable alloydb.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable aiplatform.googleapis.com

Write-Host "✅ APIs enabled" -ForegroundColor Green
Write-Host ""

# ============================================================
# Step 2: Setup VPC peering (required for AlloyDB private networking)
# ============================================================
Write-Host "🔗 Setting up VPC private service connection..." -ForegroundColor Cyan

# Allocate IP range for private services
Write-Host "   Allocating private IP range..." -ForegroundColor Gray
gcloud compute addresses create $IP_RANGE_NAME `
    --global `
    --purpose=VPC_PEERING `
    --prefix-length=16 `
    --network=$NETWORK `
    --project=$PROJECT_ID 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "   IP range already exists or created" -ForegroundColor Yellow
}

# Create private connection
Write-Host "   Creating private VPC connection..." -ForegroundColor Gray
gcloud services vpc-peerings connect `
    --service=servicenetworking.googleapis.com `
    --ranges=$IP_RANGE_NAME `
    --network=$NETWORK `
    --project=$PROJECT_ID

Write-Host "✅ VPC peering configured" -ForegroundColor Green
Write-Host ""

# ============================================================
# Step 3: Create AlloyDB cluster
# ============================================================
Write-Host "🗄️  Creating AlloyDB cluster (this takes ~10-15 minutes)..." -ForegroundColor Cyan
gcloud alloydb clusters create $CLUSTER_NAME `
    --region=$REGION `
    --network=$NETWORK `
    --password=$PASSWORD `
    --project=$PROJECT_ID `
    --allocated-ip-range-name=$IP_RANGE_NAME

Write-Host "✅ Cluster created" -ForegroundColor Green
Write-Host ""

# ============================================================
# Step 4: Create primary instance
# ============================================================
Write-Host "💾 Creating primary instance..." -ForegroundColor Cyan
gcloud alloydb instances create $INSTANCE_NAME `
    --cluster=$CLUSTER_NAME `
    --region=$REGION `
    --instance-type=PRIMARY `
    --cpu-count=2 `
    --project=$PROJECT_ID

Write-Host "✅ Instance created" -ForegroundColor Green
Write-Host ""

# ============================================================
# Step 5: Get connection details
# ============================================================
Write-Host "📝 Getting connection details..." -ForegroundColor Cyan
$INSTANCE_IP = gcloud alloydb instances describe $INSTANCE_NAME `
    --cluster=$CLUSTER_NAME `
    --region=$REGION `
    --format="value(ipAddress)"

$INSTANCE_URI = "projects/$PROJECT_ID/locations/$REGION/clusters/$CLUSTER_NAME/instances/$INSTANCE_NAME"

Write-Host ""
Write-Host "✅ AlloyDB Setup Complete!" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  Host (private IP): $INSTANCE_IP"
Write-Host "  Port: 5432"
Write-Host "  Database: postgres"
Write-Host "  User: postgres"
Write-Host "  Password: [your password]"
Write-Host ""
Write-Host "AlloyDB Connector URI:" -ForegroundColor Yellow
Write-Host "  $INSTANCE_URI"
Write-Host ""
Write-Host "📝 Update your backend/.env file with:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# For AlloyDB Connector (recommended for Cloud Run):"
Write-Host "ALLOYDB_USE_CONNECTOR=true"
Write-Host "ALLOYDB_INSTANCE_URI=$INSTANCE_URI"
Write-Host "ALLOYDB_DATABASE=sarathi"
Write-Host "ALLOYDB_USER=postgres"
Write-Host "ALLOYDB_PASSWORD=$PASSWORD"
Write-Host "ALLOYDB_IAM_AUTH=false"
Write-Host "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
Write-Host "GOOGLE_CLOUD_REGION=$REGION"
Write-Host ""
Write-Host "# For direct connection (via Cloud SQL Auth Proxy or VPC):"
Write-Host "ALLOYDB_USE_CONNECTOR=false"
Write-Host "ALLOYDB_HOST=$INSTANCE_IP"
Write-Host "ALLOYDB_DATABASE=sarathi"
Write-Host "ALLOYDB_USER=postgres"
Write-Host "ALLOYDB_PASSWORD=$PASSWORD"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create the 'sarathi' database:"
Write-Host "   psql -h $INSTANCE_IP -U postgres -c 'CREATE DATABASE sarathi;'"
Write-Host ""
Write-Host "2. Run the schema:"
Write-Host "   psql -h $INSTANCE_IP -U postgres -d sarathi -f backend/db/schema.sql"
Write-Host ""
Write-Host "3. Load seed data:"
Write-Host "   psql -h $INSTANCE_IP -U postgres -d sarathi -f backend/db/seed.sql"
Write-Host ""
Write-Host "4. Generate skill embeddings:"
Write-Host "   curl -X POST http://localhost:8000/api/v1/team/refresh-all-embeddings"
Write-Host ""
