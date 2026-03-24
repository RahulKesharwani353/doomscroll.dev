# Doomscroll

A content aggregator that fetches articles from multiple sources (Hacker News, Dev.to, Reddit, Lobsters), normalizes data into a unified schema, and presents it through a clean interface with automated background refresh.

<img width="1896" height="851" alt="Image" src="https://github.com/user-attachments/assets/c7d2b820-f9bd-451a-8011-711a986f6fa4" />

## Features

- **Multi-Source Aggregation** - Fetches from 4 sources: Hacker News, Dev.to, Reddit, Lobsters
- **Data Normalization** - Unified schema with UTC timestamps
- **Unified Feed** - Single feed sorted by publication date
- **Source Filtering** - Filter by individual sources
- **Search** - Full-text search across article titles
- **Pagination** - Load more with infinite scroll
- **Background Refresh** - Automated sync every 15 minutes
- **Caching Layer** - In-memory cache (swappable for Redis)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Frontend | React + TypeScript + Vite |
| Database | PostgreSQL |
| Background Jobs | External Cron + Script |
| Styling | Tailwind CSS |

<img width="1402" height="670" alt="Image" src="https://github.com/user-attachments/assets/85dd8a80-1f83-40ad-9d0b-85208c62fe35" />

## Quick Start

```bash
# 1. Start database
cd deployment-local && docker compose up -d

# 2. Start backend
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Start sync service
cd sync_service
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# 4. Start frontend
cd frontend
npm install && npm run dev
```

See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

## Documentation

| Document | Description |
|----------|-------------|
| [Setup Guide](docs/SETUP.md) | Detailed installation & configuration |
| [API Reference](docs/API.md) | Endpoints & examples |
| [Architecture](docs/ARCHITECTURE.md) | System design & data flow |
| [Design Decisions](docs/DESIGN_DECISIONS.md) | Tech choices & trade-offs |

## Project Structure

```
doomscroll/
├── backend/           # FastAPI backend API
├── sync_service/      # Background sync service
├── frontend/          # React frontend
├── shared/            # Shared models & schemas
├── deployment-local/  # Docker setup
└── docs/              # Documentation
```
