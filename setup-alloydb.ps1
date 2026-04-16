# Tech Sarathi - AlloyDB Setup Script (PowerShell)
# This script provisions AlloyDB on Google Cloud Platform

Write-Host "🚀 Tech Sarathi - AlloyDB Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "tech-sarathi"
$REGION = "asia-south1"
$CLUSTER_NAME = "sarathi-cluster"
$INSTANCE_NAME = "sarathi-primary"
$NETWORK = "default"

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
$inputProject = Read-Host "Enter your GCP Project ID (default: tech-sarathi)"
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

# Enable required APIs
Write-Host "📦 Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable alloydb.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable aiplatform.googleapis.com

Write-Host "✅ APIs enabled" -ForegroundColor Green
Write-Host ""

# Create AlloyDB cluster
Write-Host "🗄️  Creating AlloyDB cluster (this takes ~10-15 minutes)..." -ForegroundColor Cyan
gcloud alloydb clusters create $CLUSTER_NAME `
    --region=$REGION `
    --network=$NETWORK `
    --password=$PASSWORD `
    --project=$PROJECT_ID

Write-Host "✅ Cluster created" -ForegroundColor Green
Write-Host ""

# Create primary instance
Write-Host "💾 Creating primary instance..." -ForegroundColor Cyan
gcloud alloydb instances create $INSTANCE_NAME `
    --cluster=$CLUSTER_NAME `
    --region=$REGION `
    --instance-type=PRIMARY `
    --cpu-count=2 `
    --project=$PROJECT_ID

Write-Host "✅ Instance created" -ForegroundColor Green
Write-Host ""

# Get connection details
Write-Host "📝 Getting connection details..." -ForegroundColor Cyan
$INSTANCE_IP = gcloud alloydb instances describe $INSTANCE_NAME `
    --cluster=$CLUSTER_NAME `
    --region=$REGION `
    --format="value(ipAddress)"

Write-Host ""
Write-Host "✅ AlloyDB Setup Complete!" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  Host: $INSTANCE_IP"
Write-Host "  Port: 5432"
Write-Host "  Database: postgres"
Write-Host "  User: postgres"
Write-Host "  Password: [your password]"
Write-Host ""
Write-Host "📝 Update your backend/.env file with:" -ForegroundColor Yellow
Write-Host ""
Write-Host "ALLOYDB_HOST=$INSTANCE_IP"
Write-Host "ALLOYDB_DATABASE=sarathi"
Write-Host "ALLOYDB_USER=postgres"
Write-Host "ALLOYDB_PASSWORD=$PASSWORD"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create the 'sarathi' database"
Write-Host "2. Run the schema: psql -h $INSTANCE_IP -U postgres -d sarathi -f backend/db/schema.sql"
Write-Host "3. Load seed data: psql -h $INSTANCE_IP -U postgres -d sarathi -f backend/db/seed.sql"
Write-Host ""
