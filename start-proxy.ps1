# Tech Sarathi - AlloyDB Auth Proxy Helper

$PROJECT_ID = "nirman-project-493414"
$REGION = "asia-south1"
$CLUSTER = "sarathi-cluster"
$INSTANCE = "sarathi-primary"
$INSTANCE_URI = "projects/$PROJECT_ID/locations/$REGION/clusters/$CLUSTER/instances/$INSTANCE"

Write-Host "🚀 Setting up AlloyDB Auth Proxy..." -ForegroundColor Cyan

# 1. Download binary if not exists
if (-not (Test-Path "alloydb-auth-proxy.exe")) {
    Write-Host "📥 Downloading AlloyDB Auth Proxy..." -ForegroundColor Gray
    Invoke-WebRequest -Uri "https://storage.googleapis.com/alloydb-auth-proxy/v1.7.0/alloydb-auth-proxy.windows.amd64.exe" -OutFile "alloydb-auth-proxy.exe"
}

# 2. Check if already running
$existing = Get-Process "alloydb-auth-proxy" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "⚠️  AlloyDB Auth Proxy is already running. Stopping it first..." -ForegroundColor Yellow
    Stop-Process -Name "alloydb-auth-proxy" -Force
}

# 3. Start proxy in background
Write-Host "🔌 Starting proxy for $INSTANCE_URI..." -ForegroundColor Green
Start-Process -FilePath ".\alloydb-auth-proxy.exe" -ArgumentList "$INSTANCE_URI", "--port=5432" -WindowStyle Hidden

Write-Host "✅ Proxy started on localhost:5432" -ForegroundColor Green
