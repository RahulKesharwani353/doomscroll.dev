# Setup Guide

Complete instructions for setting up Doomscroll locally.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop (for PostgreSQL)
- Git

## 1. Clone Repository

```bash
git clone https://github.com/RahulKesharwani353/doomscroll.dev.git
cd content-aggregator
```

## 2. Database Setup

Start PostgreSQL using Docker:

```bash
cd deployment-local
docker compose up -d
```

Verify it's running:
```bash
docker compose ps
```

| Service | Port | Credentials |
|---------|------|-------------|
| PostgreSQL | 5433 | `doomscroll_user` / `doomscroll_password` |

## 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Linux/Mac)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

API docs at: http://localhost:8000/docs

## 4. Sync Service Setup

The sync service is a script (`run_sync.py`) designed to be triggered by an external cron scheduler.

```bash
cd sync_service

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Linux/Mac)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run initial sync manually
python run_sync.py
```

For automated syncing, configure your OS cron scheduler (see [Architecture docs](ARCHITECTURE.md#cron-configuration)).

## 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start dev server
npm run dev
```

Frontend will be available at: http://localhost:5173

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | Secret key for JWT tokens (min 10 chars) | Required |
| `MIGRATION_API_KEY` | API key for migration endpoints | Required |
| `API_HOST` | Server host | `0.0.0.0` |
| `API_PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `true` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:5173` |
| `CACHE_BACKEND` | Cache type (`memory` or `redis`) | `memory` |
| `CACHE_TTL_SHORT` | Short cache TTL (seconds) | `120` |
| `CACHE_TTL_LONG` | Long cache TTL (seconds) | `600` |
| `CACHE_REDIS_URL` | Redis connection (if using redis) | Optional |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token expiry | `7` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` |
| `RATE_LIMIT_AUTH_REQUESTS` | Auth endpoint rate limit per minute | `5` |
| `RATE_LIMIT_API_REQUESTS` | API endpoint rate limit per minute | `100` |

### Sync Service (`sync_service/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `DEBUG` | Debug mode | `false` |
| `REDDIT_USER_AGENT` | Reddit API user agent | Required |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Verify Setup

### 1. Check Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy", "database": "connected"}
```

### 2. Run Initial Sync
```bash
cd sync_service
.venv\Scripts\activate  # Windows
python run_sync.py
```

### 3. Verify Articles
```bash
curl http://localhost:8000/api/articles
```

### 4. Open Frontend
Visit http://localhost:5173 - you should see articles loading.

## Troubleshooting

### Database Connection Failed
- Ensure Docker is running: `docker compose ps`
- Check port 5433 is not in use
- Verify credentials in `.env` match `docker-compose.yml`

### No Articles Showing
- Run sync manually: `cd sync_service && python run_sync.py`
- Check sync script output for errors

### CORS Errors
- Ensure `CORS_ORIGINS` in backend `.env` includes frontend URL
- Restart backend after changing `.env`

### Port Already in Use
- Change port in respective `.env` file
- Or kill process using the port
