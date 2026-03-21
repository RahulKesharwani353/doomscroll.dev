# Doomscroll - Local Deployment

This folder contains Docker Compose configuration for local development.

## Prerequisites

- Docker Desktop installed and running
- PowerShell (Windows) or Bash (Linux/Mac)

## Services

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5433 | Database server |
| Redis | 6379 | Cache server (optional) |

## Quick Start

### Windows (PowerShell)

```powershell
cd deployment-local
.\start.ps1
```

### Linux/Mac (Bash)

```bash
cd deployment-local
docker compose up -d
```

## Database Connection

| Property | Value |
|----------|-------|
| Host | localhost |
| Port | 5433 |
| Database | doomscroll |
| User | doomscroll_user |
| Password | doomscroll_password |

### Connection String

```
postgresql+asyncpg://doomscroll_user:doomscroll_password@localhost:5433/doomscroll
```

## Commands

### Start Services
```powershell
.\start.ps1
```

### Stop Services (preserve data)
```powershell
.\stop.ps1
```

### Stop Services (remove data)
```powershell
.\stop.ps1 -Clean
```

### View Logs
```bash
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f redis
```

### Connect to PostgreSQL
```bash
docker compose exec postgres psql -U doomscroll_user -d doomscroll
```

### Connect to Redis
```bash
docker compose exec redis redis-cli
```

## Backend Configuration

Update your backend `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://doomscroll_user:doomscroll_password@localhost:5433/doomscroll
```

## Troubleshooting

### Port already in use
Change the port in `.env`:
```env
POSTGRES_PORT=5434
```

### Database not initializing
Check logs:
```bash
docker compose logs postgres
```

### Reset database
```powershell
.\stop.ps1 -Clean
.\start.ps1
```
