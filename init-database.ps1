# Tech Sarathi - Database Initialization Script (PowerShell)
# Run this after AlloyDB is provisioned

Write-Host "🗄️  Tech Sarathi - Database Initialization" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "❌ backend\.env file not found" -ForegroundColor Red
    Write-Host "Please create it with your AlloyDB connection details"
    exit 1
}

# Load environment variables
Get-Content backend\.env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        Set-Item -Path "env:$name" -Value $value
    }
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Host: $env:ALLOYDB_HOST"
Write-Host "   Database: $env:ALLOYDB_DATABASE"
Write-Host "   User: $env:ALLOYDB_USER"
Write-Host ""

# Check if psql is installed
try {
    $null = Get-Command psql -ErrorAction Stop
    Write-Host "✅ psql found" -ForegroundColor Green
} catch {
    Write-Host "❌ psql is not installed" -ForegroundColor Red
    Write-Host "Please install PostgreSQL client:"
    Write-Host "  https://www.postgresql.org/download/windows/"
    exit 1
}

Write-Host ""

# Test connection
Write-Host "🔌 Testing connection..." -ForegroundColor Cyan
$env:PGPASSWORD = $env:ALLOYDB_PASSWORD
$testResult = psql -h $env:ALLOYDB_HOST -U $env:ALLOYDB_USER -d postgres -c "SELECT 1" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cannot connect to database" -ForegroundColor Red
    Write-Host "Please check your connection details in backend\.env"
    exit 1
}

Write-Host "✅ Connection successful" -ForegroundColor Green
Write-Host ""

# Create database if it doesn't exist
Write-Host "📦 Creating database '$env:ALLOYDB_DATABASE'..." -ForegroundColor Cyan
psql -h $env:ALLOYDB_HOST -U $env:ALLOYDB_USER -d postgres -c "CREATE DATABASE $env:ALLOYDB_DATABASE;" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Database already exists" -ForegroundColor Yellow
}

Write-Host "✅ Database ready" -ForegroundColor Green
Write-Host ""

# Run schema
Write-Host "📝 Running schema..." -ForegroundColor Cyan
psql -h $env:ALLOYDB_HOST -U $env:ALLOYDB_USER -d $env:ALLOYDB_DATABASE -f backend\db\schema.sql

Write-Host "✅ Schema created" -ForegroundColor Green
Write-Host ""

# Load seed data
$loadSeed = Read-Host "Load seed data? (y/n)"
if ($loadSeed -eq "y") {
    Write-Host "🌱 Loading seed data..." -ForegroundColor Cyan
    psql -h $env:ALLOYDB_HOST -U $env:ALLOYDB_USER -d $env:ALLOYDB_DATABASE -f backend\db\seed.sql
    Write-Host "✅ Seed data loaded" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Database initialization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now start the application:" -ForegroundColor Cyan
Write-Host "  cd backend && python -m uvicorn api.main:app --reload"
Write-Host ""
