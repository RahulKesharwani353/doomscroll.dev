# PowerShell script to stop Doomscroll Local Deployment

param(
    [switch]$Clean
)

Write-Host "Stopping Doomscroll Local Deployment..." -ForegroundColor Yellow

if ($Clean) {
    Write-Host "Stopping and removing volumes (clean shutdown)..." -ForegroundColor Red
    docker compose down -v
    Write-Host "All containers and volumes removed." -ForegroundColor Green
} else {
    docker compose down
    Write-Host "Containers stopped. Data volumes preserved." -ForegroundColor Green
    Write-Host "Use -Clean flag to remove volumes: .\stop.ps1 -Clean" -ForegroundColor Gray
}
