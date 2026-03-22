# Content Aggregator Service - Implementation Plan

## Overview

A full-stack application that aggregates technical content from multiple external APIs, normalizes the data into a unified schema, stores it in a database, and presents it through a clean React interface with background refresh capabilities.

**Architecture:** Separated into Backend API and Sync Service for independent scaling and fault isolation.

---

## Tech Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Backend API** | FastAPI (Python) | Async support, automatic OpenAPI docs, type hints, high performance |
| **Sync Service** | FastAPI (Python) | Separate service for source management and background sync |
| **Frontend** | React.js | Component-based, large ecosystem, easy state management |
| **Database** | PostgreSQL | Strong indexing, UPSERT support, full-text search, ACID compliance |
| **Background Jobs** | APScheduler | Lightweight, easy integration with FastAPI, cron-like scheduling |
| **HTTP Client** | httpx | Async HTTP requests, modern Python HTTP client |

---

## External APIs (4 Sources)

| Source | API Documentation | Auth Required | Notes |
|--------|-------------------|---------------|-------|
| **Hacker News** | [Official API](https://github.com/HackerNews/API) | No | Simple REST, returns IDs then fetch individual items |
| **Dev.to** | [Forem API](https://developers.forem.com/api) | No (optional API key) | Direct article listing, well-structured responses |
| **Reddit** | [Reddit API](https://www.reddit.com/dev/api) | No (public endpoints) | Use `.json` suffix on subreddit URLs |
| **Lobste.rs** | [About Page](https://lobste.rs/about) | No | Simple JSON feed, tech-focused community |

> **Note:** X.com (Twitter) API requires paid access ($100+/month) and OAuth. Not included due to cost constraints.

---

## Project Structure

```
content-aggregator/
│
├── shared/                       # Shared code between services
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py          # DB connection, Base, AsyncSessionLocal
│   ├── models/
│   │   ├── __init__.py
│   │   └── article.py           # Article model
│   └── schemas/
│       ├── __init__.py
│       ├── article.py           # ArticleCreate, ArticleResponse
│       └── common.py            # PaginationParams, etc.
│
├── backend/                      # Backend API (user-facing)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   │
│   │   ├── api/
│   │   │   └── controllers/
│   │   │       ├── __init__.py
│   │   │       ├── article_controller.py
│   │   │       ├── source_controller.py
│   │   │       └── health_controller.py
│   │   │
│   │   ├── repositories/
│   │   │   └── article_repository.py
│   │   │
│   │   └── services/
│   │       └── article_service.py
│   │
│   ├── alembic/                 # Database migrations
│   ├── scripts/                 # Utility scripts
│   └── requirements.txt
│
├── sync_service/                 # Sync Service (background jobs & source management)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   └── controllers/
│   │   │       ├── source_controller.py    # CRUD sources
│   │   │       ├── job_controller.py       # Sync history
│   │   │       └── scheduler_controller.py # Pause/resume
│   │   │
│   │   ├── core/
│   │   │   └── scheduler.py     # APScheduler setup
│   │   │
│   │   ├── sources/             # Source adapters (plugin-based)
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # BaseSource with fetch_raw/transform
│   │   │   ├── registry.py      # Source registry
│   │   │   ├── hackernews.py
│   │   │   ├── devto.py
│   │   │   ├── reddit.py
│   │   │   └── lobsters.py
│   │   │
│   │   ├── models/
│   │   │   ├── source.py        # Source config model
│   │   │   └── sync_job.py      # Job history model
│   │   │
│   │   ├── schemas/
│   │   │   ├── source.py
│   │   │   └── sync_job.py
│   │   │
│   │   └── services/
│   │       └── sync_service.py  # Orchestrates sync
│   │
│   └── requirements.txt
│
├── frontend/                     # React application
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
│
├── deployment-local/             # Docker setup
│   └── docker-compose.yml
│
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Feature Implementation Details

### 1. Content Aggregation Layer

#### What It Does
Connects to external APIs and fetches raw article data from each source.

#### Design Pattern: Strategy Pattern
Each source implements a common interface, making it easy to add new sources without modifying existing code.

```python
from abc import ABC, abstractmethod
from typing import List
from app.schemas.article import ArticleCreate

class BaseSource(ABC):
    """Abstract base class for all content sources."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this source."""
        pass

    @abstractmethod
    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        """Fetch and normalize articles from this source."""
        pass

    async def safe_fetch(self, limit: int = 30) -> List[ArticleCreate]:
        """Wrapper that handles errors gracefully."""
        try:
            return await self.fetch_articles(limit)
        except Exception as e:
            logger.error(f"Failed to fetch from {self.source_name}: {e}")
            return []
```

#### Why This Design
- **Isolation**: API-specific quirks (rate limits, pagination, auth) are contained within each adapter
- **Extensibility**: Adding a new source = creating a new class
- **Testability**: Easy to mock individual sources for testing
- **Resilience**: One source failing doesn't affect others

---

### 2. Data Normalization Layer

#### What It Does
Transforms different API responses into a unified schema, ensuring consistent data regardless of source.

#### Normalized Article Schema

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    """Unified article schema across all sources."""

    id: str                      # Unique ID: "{source}-{original_id}"
    title: str                   # Article title
    url: str                     # Link to original article
    author: Optional[str]        # Author name (may be null)
    source: str                  # Source identifier
    published_at: datetime       # Publication time (UTC)
    fetched_at: datetime         # When we fetched it (UTC)

# Example normalized article:
{
    "id": "hn-38291045",
    "title": "Understanding PostgreSQL Query Performance",
    "url": "https://example.com/postgres-performance",
    "author": "techwriter",
    "source": "hackernews",
    "published_at": "2025-01-20T14:30:00Z",
    "fetched_at": "2025-01-21T09:15:00Z"
}
```

#### Normalization Rules

| Field | Handling |
|-------|----------|
| `id` | Generated as `{source}-{original_id}` to ensure uniqueness |
| `title` | Required, trimmed of whitespace |
| `url` | Required, validated as proper URL |
| `author` | Optional, defaults to "unknown" if missing |
| `source` | Enum value: hackernews, devto, reddit, lobsters |
| `published_at` | Converted to UTC, parsed from various formats |
| `fetched_at` | Set to current UTC time when fetched |

#### Why This Design
- **Consistency**: Frontend receives identical structure regardless of source
- **Robustness**: Handles missing/optional fields gracefully
- **Timezone Safety**: All times in UTC prevents display issues
- **Traceability**: `fetched_at` helps debug stale data issues

---

### 3. Database Layer (PostgreSQL)

#### What It Does
Persists normalized articles for fast retrieval, enabling pagination and filtering without re-fetching from external APIs.

#### Database Schema

```sql
-- Articles table
CREATE TABLE articles (
    id VARCHAR(100) PRIMARY KEY,           -- e.g., "hn-12345"
    title VARCHAR(500) NOT NULL,
    url VARCHAR(2000) NOT NULL,
    author VARCHAR(200),
    source VARCHAR(50) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_source_published ON articles(source, published_at DESC);

-- Full-text search index (for bonus search feature)
CREATE INDEX idx_articles_title_search ON articles USING gin(to_tsvector('english', title));
```

#### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, func
from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(String(100), primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False)
    author = Column(String(200), nullable=True)
    source = Column(String(50), nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), index=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### Why PostgreSQL
- **Indexing**: Efficient queries for timestamp-based sorting and source filtering
- **UPSERT**: `ON CONFLICT DO UPDATE` handles duplicate articles gracefully
- **Full-Text Search**: Built-in support for search feature without additional infrastructure
- **ACID Compliance**: Data integrity during concurrent refresh jobs
- **Mature Ecosystem**: Excellent Python support via SQLAlchemy and asyncpg

---

### 4. Background Refresh System

#### What It Does
Periodically fetches fresh content from all sources without blocking user requests.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKGROUND REFRESH FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                                              │
│   │  APScheduler │                                              │
│   │  (every 15m) │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │  Hacker News │     │    Dev.to    │     │    Reddit    │   │
│   │    Fetcher   │     │   Fetcher    │     │   Fetcher    │   │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘   │
│          │                    │                    │            │
│          └────────────────────┼────────────────────┘            │
│                               ▼                                  │
│                    ┌──────────────────┐                         │
│                    │    Normalizer    │                         │
│                    └────────┬─────────┘                         │
│                             │                                    │
│                             ▼                                    │
│                    ┌──────────────────┐                         │
│                    │    PostgreSQL    │                         │
│                    │  (UPSERT batch)  │                         │
│                    └──────────────────┘                         │
│                                                                  │
│   ════════════════════════════════════════════════════════════  │
│   USER REQUESTS (independent, served from DB cache)             │
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │   GET /api/  │────►│   Database   │────►│   Response   │   │
│   │   articles   │     │    Query     │     │    (fast)    │   │
│   └──────────────┘     └──────────────┘     └──────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Implementation

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

async def refresh_all_sources():
    """Fetch fresh content from all sources."""
    sources = [
        HackerNewsSource(),
        DevToSource(),
        RedditSource(),
        LobstersSource(),
    ]

    # Fetch from all sources concurrently
    results = await asyncio.gather(
        *[source.safe_fetch() for source in sources],
        return_exceptions=True
    )

    # Flatten and save to database
    all_articles = []
    for articles in results:
        if isinstance(articles, list):
            all_articles.extend(articles)

    await article_service.upsert_articles(all_articles)
    logger.info(f"Refreshed {len(all_articles)} articles")

# Schedule job to run every 15 minutes
scheduler.add_job(
    refresh_all_sources,
    trigger=IntervalTrigger(minutes=15),
    id="refresh_content",
    replace_existing=True
)
```

#### Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Single source fails | Log error, continue with other sources |
| All sources fail | Keep serving existing cached content |
| Database error | Retry with exponential backoff |
| Rate limited | Respect retry-after header, skip this cycle |

#### Why This Design
- **Non-Blocking**: User requests are served from database, never wait for external APIs
- **Resilient**: Failures are isolated and logged, service continues
- **Efficient**: Concurrent fetching reduces total refresh time
- **Configurable**: Interval can be adjusted via environment variables

---

### 5. REST API Endpoints

#### What It Does
Exposes data to the frontend through a consistent, well-documented API.

#### Endpoint Specifications

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `GET /api/articles` | GET | Paginated article feed | `page`, `limit`, `source` |
| `GET /api/articles/{id}` | GET | Single article by ID | - |
| `GET /api/sources` | GET | List available sources | - |
| `GET /api/health` | GET | Health check | - |
| `POST /api/refresh` | POST | Trigger manual refresh | - |

#### Response Structures

```python
# GET /api/articles?page=1&limit=20&source=hackernews

{
    "success": true,
    "data": {
        "articles": [
            {
                "id": "hn-38291045",
                "title": "Understanding PostgreSQL Query Performance",
                "url": "https://example.com/postgres-performance",
                "author": "techwriter",
                "source": "hackernews",
                "published_at": "2025-01-20T14:30:00Z",
                "fetched_at": "2025-01-21T09:15:00Z"
            }
            // ... more articles
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 150,
            "total_pages": 8,
            "has_next": true,
            "has_prev": false
        }
    }
}

# GET /api/sources

{
    "success": true,
    "data": {
        "sources": [
            {"id": "hackernews", "name": "Hacker News", "url": "https://news.ycombinator.com"},
            {"id": "devto", "name": "Dev.to", "url": "https://dev.to"},
            {"id": "reddit", "name": "Reddit", "url": "https://reddit.com"},
            {"id": "lobsters", "name": "Lobste.rs", "url": "https://lobste.rs"}
        ]
    }
}

# Error Response

{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid source parameter",
        "details": {"source": "must be one of: hackernews, devto, reddit, lobsters"}
    }
}
```

#### Why RESTful Design
- **Predictable**: Standard HTTP methods and status codes
- **Cacheable**: GET requests can be cached at multiple levels
- **Documented**: FastAPI auto-generates OpenAPI/Swagger docs
- **Consistent**: Same response structure across all endpoints

---

### 6. Frontend (React)

#### What It Does
Displays the unified feed with source filtering, pagination, and responsive design.

#### Component Hierarchy

```
App
├── Header
│   └── Logo, Title
│
├── SourceFilter
│   └── Filter chips/buttons for each source
│
├── ArticleFeed
│   ├── Loading (skeleton)
│   ├── Error (retry button)
│   └── ArticleCard (mapped list)
│       ├── Title (link)
│       ├── Source badge
│       ├── Author
│       └── Published date
│
└── Pagination
    └── Page numbers, prev/next buttons
```

#### State Management

```javascript
// useArticles.js - Custom hook for article data
const useArticles = (source, page) => {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({});

    useEffect(() => {
        fetchArticles(source, page)
            .then(response => {
                setArticles(response.data.articles);
                setPagination(response.data.pagination);
            })
            .catch(setError)
            .finally(() => setLoading(false));
    }, [source, page]);

    return { articles, loading, error, pagination };
};
```

#### Responsive Design Breakpoints

| Breakpoint | Layout |
|------------|--------|
| Mobile (<768px) | Single column, stacked filters |
| Tablet (768-1024px) | Two columns, horizontal filters |
| Desktop (>1024px) | Three columns, sidebar filters |

#### Why React
- **Component-Based**: Reusable UI pieces
- **Hooks**: Clean state management without external libraries
- **Ecosystem**: Easy integration with UI libraries if needed
- **Developer Experience**: Hot reloading, excellent debugging tools

---

## Bonus Features (For Future Implementation)

### Redis Caching

#### What It Does
Reduces database load by caching frequently accessed data.

#### Implementation Approach
```python
# Cache the feed response for 60 seconds
@cache(ttl=60, key="articles:{source}:{page}")
async def get_articles(source: str, page: int):
    return await article_service.get_paginated(source, page)
```

#### When to Invalidate
- After background refresh completes
- When new articles are manually added

---

### User Preferences

#### What It Does
Remembers user's preferred sources across sessions.

#### Implementation Approach
- **Simple**: Store in localStorage (no backend changes)
- **Persistent**: Add users table and preferences table

```sql
CREATE TABLE user_preferences (
    user_id UUID REFERENCES users(id),
    preferred_sources TEXT[],  -- Array of source IDs
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### Bookmarking

#### What It Does
Lets users save articles for later reading.

#### Implementation Approach
```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    article_id VARCHAR(100) REFERENCES articles(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);
```

#### New Endpoints
- `POST /api/bookmarks` - Add bookmark
- `GET /api/bookmarks` - List user's bookmarks
- `DELETE /api/bookmarks/{id}` - Remove bookmark

---

### Search

#### What It Does
Find articles by searching titles.

#### Implementation Approach
```python
# Using PostgreSQL full-text search
@router.get("/api/articles/search")
async def search_articles(q: str):
    query = """
        SELECT * FROM articles
        WHERE to_tsvector('english', title) @@ plainto_tsquery('english', :query)
        ORDER BY published_at DESC
        LIMIT 50
    """
    return await db.fetch_all(query, {"query": q})
```

---

### Unit Tests

#### What It Does
Verifies correctness of normalization logic and API endpoints.

#### Test Coverage Goals
- **Normalization**: Each source adapter with various edge cases
- **API Endpoints**: Request/response validation
- **Database**: CRUD operations, upsert behavior

```python
# Example test
def test_hackernews_normalization():
    raw = {"id": 123, "title": "Test", "by": "user", "time": 1705766400}
    normalized = HackerNewsSource().normalize(raw)

    assert normalized.id == "hn-123"
    assert normalized.source == "hackernews"
    assert normalized.author == "user"
```

---

## Environment Variables

```bash
# .env.example

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/content_aggregator

# Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Background Jobs
REFRESH_INTERVAL_MINUTES=15

# External APIs (optional)
DEVTO_API_KEY=           # Optional, increases rate limit
REDDIT_USER_AGENT=ContentAggregator/1.0

# Redis (for caching bonus feature)
REDIS_URL=redis://localhost:6379/0
```

---

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Development Workflow

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git

### Setup Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd content-aggregator

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials

# 3. Database setup
alembic upgrade head

# 4. Run backend
uvicorn app.main:app --reload

# 5. Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env
npm start
```

### Verifying Background Jobs

```bash
# Check logs for refresh activity
tail -f backend/logs/app.log | grep "refresh"

# Or trigger manual refresh
curl -X POST http://localhost:8000/api/refresh
```

---

## Trade-offs & Decisions

| Decision | Trade-off | Reasoning |
|----------|-----------|-----------|
| APScheduler over Celery | Less scalable, but simpler | Single-server deployment, no Redis dependency initially |
| PostgreSQL over MongoDB | Less flexible schema, but better for relational queries | Filtering and pagination are core features |
| No X.com integration | Missing popular platform | API costs ($100+/month) not justified for demo |
| Sync to DB vs. real-time proxy | Higher latency for new content | Reliability and speed for users outweighs freshness |

---

## Future Improvements

With more time, the following improvements could be made:

1. **WebSocket Support** - Real-time updates when new articles arrive
2. **Rate Limiting** - Protect API from abuse
3. **Elasticsearch** - More powerful search capabilities
4. **Kubernetes Deployment** - Horizontal scaling for production
5. **Analytics Dashboard** - Track popular sources and articles
6. **Email Digest** - Daily/weekly summary emails
7. **Mobile App** - React Native version

---

## Timeline Estimate

| Phase | Tasks | Notes |
|-------|-------|-------|
| Phase 1 | Backend scaffolding, DB setup, first source | Foundation |
| Phase 2 | Remaining sources, normalization | Core feature |
| Phase 3 | Background jobs, error handling | Reliability |
| Phase 4 | Frontend implementation | User interface |
| Phase 5 | Testing, documentation, polish | Quality |

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [React Documentation](https://react.dev/)
- [Hacker News API](https://github.com/HackerNews/API)
- [Dev.to API](https://developers.forem.com/api)
- [Reddit API](https://www.reddit.com/dev/api)
