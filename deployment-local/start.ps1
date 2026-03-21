# PowerShell script to start Doomscroll Local Deployment
# Run this script from the deployment-local directory

Write-Host "Starting Doomscroll Local Deployment..." -ForegroundColor Green

# Check if Docker is running
$dockerStatus = docker version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
$composeVersion = docker compose version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: docker compose is not available. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

Write-Host "Docker is running. Starting services..." -ForegroundColor Yellow

# Start PostgreSQL
Write-Host "Starting PostgreSQL database..." -ForegroundColor Blue
docker compose up -d postgres

# Wait for database to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Blue
$timeout = 60
$elapsed = 0
do {
    Start-Sleep -Seconds 2
    $elapsed += 2
    $dbReady = docker compose exec -T postgres pg_isready -U doomscroll_user -d doomscroll 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PostgreSQL is ready!" -ForegroundColor Green
        break
    }
    Write-Host "Waiting... ($elapsed seconds)" -ForegroundColor Gray
    if ($elapsed -ge $timeout) {
        Write-Host "Timeout waiting for PostgreSQL to be ready." -ForegroundColor Red
        exit 1
    }
} while ($true)

# Start Redis (optional)
Write-Host "Starting Redis..." -ForegroundColor Blue
docker compose up -d redis

Write-Host ""
Write-Host "Doomscroll Local Deployment started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Services available at:" -ForegroundColor Yellow
Write-Host "  PostgreSQL: localhost:5433" -ForegroundColor Cyan
Write-Host "  Redis:      localhost:6379" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database connection details:" -ForegroundColor Yellow
Write-Host "  Host:     localhost" -ForegroundColor Cyan
Write-Host "  Port:     5433" -ForegroundColor Cyan
Write-Host "  Database: doomscroll" -ForegroundColor Cyan
Write-Host "  User:     doomscroll_user" -ForegroundColor Cyan
Write-Host "  Password: doomscroll_password" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connection string for backend:" -ForegroundColor Yellow
Write-Host "  postgresql+asyncpg://doomscroll_user:doomscroll_password@localhost:5433/doomscroll" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  View logs:  docker compose logs -f" -ForegroundColor Gray
Write-Host "  Stop:       docker compose down" -ForegroundColor Gray
Write-Host "  Stop+Clean: docker compose down -v" -ForegroundColor Gray
