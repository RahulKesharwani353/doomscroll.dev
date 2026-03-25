# Architecture

## Overview

Doomscroll uses a separated architecture with three main components:

1. **Backend API** - Serves articles to frontend, handles CRUD operations
2. **Sync Service** - Background job service that fetches from external sources
3. **Frontend** - React SPA that displays the unified feed

<!-- Add your architecture diagram here -->
<!-- ![Architecture Diagram](assets/architecture.png) -->

## System Components
<img width="1402" height="670" alt="Image" src="https://github.com/user-attachments/assets/85dd8a80-1f83-40ad-9d0b-85208c62fe35" />

## Data Flow

### 1. Background Sync (Cron Job)

```
External Cron (every 15 min)
    │
    ▼
run_sync.py
    │
    ├──► Fetch from Hacker News API ──► Normalize ──┐
    ├──► Fetch from Dev.to API ───────► Normalize ──┤
    ├──► Fetch from Reddit API ───────► Normalize ──┼──► Upsert to DB
    └──► Fetch from Lobsters API ─────► Normalize ──┘
```

### 2. User Request

```
Frontend
    │
    ▼
GET /api/articles?source=hackernews
    │
    ▼
Backend API
    │
    ├──► Check Cache ──► Cache Hit ──► Return cached data
    │
    └──► Cache Miss ──► Query PostgreSQL ──► Cache result ──► Return
```

## Background Jobs (External Cron)

The sync process runs via `run_sync.py` script, designed to be triggered by an **external cron scheduler**.

### Script Usage

```bash
# Sync all enabled sources
python sync_service/run_sync.py

# Sync specific source only
python sync_service/run_sync.py --source hackernews
```

### Cron Configuration

**Linux/Mac (crontab):**
```bash
# Edit crontab
crontab -e

# Add entry (every 15 minutes)
*/15 * * * * cd /path/to/project && /path/to/venv/bin/python sync_service/run_sync.py >> /var/log/doomscroll-sync.log 2>&1
```

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task → "Doomscroll Sync"
3. Trigger: Daily, repeat every 15 minutes
4. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `sync_service\run_sync.py`
   - Start in: `C:\path\to\project`

### Job Execution Flow

1. **Cron Trigger** - External scheduler runs script every 15 minutes
2. **Create Job Record** - Logs sync job to database
3. **Get Enabled Sources** - Query database for active sources
4. **Concurrent Fetch** - Fetch from all sources in parallel using `asyncio.gather`
5. **Normalize Data** - Transform each API response to unified schema
6. **Upsert to Database** - Insert or update articles
7. **Log Results** - Record sync job status and metrics

### Error Handling

| Scenario | Handling |
|----------|----------|
| Single source fails | Log error, continue with other sources |
| All sources fail | Keep serving cached/existing content |
| Database error | Log error, exit with code 1 |
| Script interrupted | Graceful shutdown, log message |

### Verifying Jobs

```bash
# Run sync manually
python sync_service/run_sync.py

# Check sync status via API
curl http://localhost:8000/api/sync/status

# View sync job history
curl http://localhost:8000/api/sync/jobs
```

## Cache Layer

The backend implements an abstract cache layer that's swappable between backends.

### Architecture

```
┌─────────────────────────────────────────────────┐
│                 CacheService                     │
│        (High-level caching operations)          │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│               CacheBackend (ABC)                 │
│    get() | set() | delete() | clear()           │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│ InMemoryCache │         │  RedisCache   │
│  (Default)    │         │  (Optional)   │
└───────────────┘         └───────────────┘
```

### Cache Keys

| Key Pattern | TTL | Description |
|-------------|-----|-------------|
| `articles:{page}:{limit}:{source}` | 2 min | Article list cache |
| `search:{query}:{page}:{limit}:{source}` | 2 min | Search results cache |
| `sources` | 10 min | Sources list cache |

### Configuration

```env
# backend/.env
CACHE_BACKEND=memory    # memory | redis
CACHE_TTL_SHORT=120     # 2 minutes (articles)
CACHE_TTL_LONG=600      # 10 minutes (sources)
REDIS_URL=redis://localhost:6379/0
```

### Switching to Redis

1. Start Redis: `docker compose up redis -d`
2. Update `.env`: `CACHE_BACKEND=redis`
3. Restart backend

## Database Schema

```
┌──────────────────────────────────────────────────────────────────┐
│                          articles                                 │
├──────────────────────────────────────────────────────────────────┤
│ id            VARCHAR(100)  PK    # "hn-12345"                   │
│ title         VARCHAR(500)        # Article title                │
│ url           VARCHAR(2000)       # Original URL                 │
│ author        VARCHAR(200)        # Author name (nullable)       │
│ source        VARCHAR(50)         # Source slug                  │
│ published_at  TIMESTAMP           # Publication time (UTC)       │
│ fetched_at    TIMESTAMP           # When fetched                 │
│ created_at    TIMESTAMP           # Record created               │
│ updated_at    TIMESTAMP           # Record updated               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                          sources                                  │
├──────────────────────────────────────────────────────────────────┤
│ id            SERIAL        PK                                    │
│ slug          VARCHAR(50)   UNIQUE  # "hackernews"               │
│ name          VARCHAR(100)          # "Hacker News"              │
│ url           VARCHAR(500)          # Website URL                │
│ is_enabled    BOOLEAN               # Active flag                │
│ ui_config     JSON                  # {color, short_label}       │
│ created_at    TIMESTAMP                                          │
│ updated_at    TIMESTAMP                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         sync_jobs                                 │
├──────────────────────────────────────────────────────────────────┤
│ id              SERIAL      PK                                    │
│ source_id       INTEGER     FK → sources (nullable)              │
│ source_slug     VARCHAR(50)                                       │
│ status          VARCHAR(20)   # pending|running|completed|failed │
│ articles_fetched INTEGER                                          │
│ error_message   TEXT                                              │
│ started_at      TIMESTAMP                                         │
│ completed_at    TIMESTAMP                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                           users                                   │
├──────────────────────────────────────────────────────────────────┤
│ id              UUID        PK                                    │
│ email           VARCHAR(255) UNIQUE                               │
│ hashed_password VARCHAR(255)                                      │
│ is_active       BOOLEAN      DEFAULT true                         │
│ created_at      TIMESTAMP                                         │
│ updated_at      TIMESTAMP                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         bookmarks                                 │
├──────────────────────────────────────────────────────────────────┤
│ id              UUID        PK                                    │
│ user_id         UUID        FK → users                            │
│ article_id      VARCHAR(100) FK → articles                        │
│ created_at      TIMESTAMP                                         │
│ UNIQUE(user_id, article_id)                                       │
└──────────────────────────────────────────────────────────────────┘
```

## Source Adapters (Strategy Pattern)

Each external source implements a common interface:

```python
class BaseSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        pass

    async def safe_fetch(self, limit: int = 30) -> List[ArticleCreate]:
        """Wrapper with error handling."""
        try:
            return await self.fetch_articles(limit)
        except Exception as e:
            logger.error(f"Failed to fetch from {self.source_name}: {e}")
            return []
```

### Benefits

- **Isolation** - API quirks contained within each adapter
- **Extensibility** - Adding new source = new class
- **Testability** - Easy to mock individual sources
- **Resilience** - One source failing doesn't affect others

## Authentication

JWT-based authentication with access and refresh tokens.

### Token Flow

```
┌─────────────┐     POST /auth/login      ┌─────────────┐
│   Client    │ ────────────────────────► │   Backend   │
│             │ ◄──────────────────────── │             │
└─────────────┘   {access_token,          └─────────────┘
                   refresh_token}
       │
       │  Store tokens in localStorage
       ▼
┌─────────────┐     GET /api/bookmarks    ┌─────────────┐
│   Client    │ ────────────────────────► │   Backend   │
│             │   Authorization: Bearer   │             │
│             │ ◄──────────────────────── │             │
└─────────────┘      {bookmarks}          └─────────────┘
       │
       │  Access token expires (30 min)
       ▼
┌─────────────┐    POST /auth/refresh     ┌─────────────┐
│   Client    │ ────────────────────────► │   Backend   │
│             │   {refresh_token}         │             │
│             │ ◄──────────────────────── │             │
└─────────────┘   {new access_token}      └─────────────┘
```

### Security

- Passwords hashed with bcrypt
- Access tokens: 30 minute expiry
- Refresh tokens: 7 day expiry
- Tokens stored in localStorage (client-side)
- Token blacklisting on logout (prevents token reuse)
- Rate limiting on auth endpoints (5 req/min)
- Rate limiting on API endpoints (100 req/min)
- Input validation with allowlist patterns
- SQL injection prevention via parameterized queries

## Frontend Components

```
┌─────────────────────────────────────────────────────────────┐
│                         App                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Providers                            │ │
│  │  AuthProvider → BookmarkProvider → SourceProvider      │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│           ┌───────────────┼───────────────┐                 │
│           ▼               ▼               ▼                 │
│     ArticlesPage    BookmarksPage    AuthModal             │
│           │               │                                  │
│           ▼               ▼                                  │
│      ArticleList    ArticleCard (with bookmark button)      │
└─────────────────────────────────────────────────────────────┘
```

### State Management

| Context | Purpose |
|---------|---------|
| `AuthContext` | User auth state, login/logout, modal control |
| `BookmarkContext` | Bookmarked article IDs, toggle bookmark |
| `SourceContext` | Available sources, source styling |
