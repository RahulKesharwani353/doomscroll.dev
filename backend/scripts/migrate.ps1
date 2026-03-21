# Alembic migration helper script for Doomscroll (PowerShell)
#
# Usage:
#     .\scripts\migrate.ps1 generate "migration description"
#     .\scripts\migrate.ps1 upgrade
#     .\scripts\migrate.ps1 downgrade
#     .\scripts\migrate.ps1 current
#     .\scripts\migrate.ps1 history
#     .\scripts\migrate.ps1 check

param(
    [Parameter(Position=0)]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Argument
)

$BackendDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $BackendDir

try {
    switch ($Command.ToLower()) {
        "generate" {
            if (-not $Argument) {
                Write-Host "Error: Migration description required" -ForegroundColor Red
                Write-Host "Usage: .\scripts\migrate.ps1 generate 'migration description'"
                exit 1
            }
            Write-Host "Generating migration: $Argument" -ForegroundColor Cyan
            alembic revision --autogenerate -m $Argument
        }
        "upgrade" {
            $revision = if ($Argument) { $Argument } else { "head" }
            Write-Host "Upgrading to: $revision" -ForegroundColor Cyan
            alembic upgrade $revision
        }
        "downgrade" {
            $revision = if ($Argument) { $Argument } else { "-1" }
            Write-Host "Downgrading: $revision" -ForegroundColor Cyan
            alembic downgrade $revision
        }
        "current" {
            Write-Host "Current revision:" -ForegroundColor Cyan
            alembic current
        }
        "history" {
            Write-Host "Migration history:" -ForegroundColor Cyan
            alembic history --verbose
        }
        "check" {
            Write-Host "Checking for pending migrations..." -ForegroundColor Cyan
            alembic check
        }
        default {
            Write-Host @"
Alembic Migration Helper for Doomscroll

Usage:
    .\scripts\migrate.ps1 generate "migration description"  - Auto-generate migration
    .\scripts\migrate.ps1 upgrade [revision]               - Upgrade to revision (default: head)
    .\scripts\migrate.ps1 downgrade [revision]             - Downgrade (default: -1)
    .\scripts\migrate.ps1 current                          - Show current revision
    .\scripts\migrate.ps1 history                          - Show migration history
    .\scripts\migrate.ps1 check                            - Check if migrations needed (CI)
"@
        }
    }
} finally {
    Pop-Location
}
