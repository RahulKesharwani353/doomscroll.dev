# Doomscroll Backend

FastAPI backend providing REST APIs for the Doomscroll content aggregator. Handles article serving, user authentication, bookmarks, and caching.

## Tech Stack

- **FastAPI** - Async Python web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Pydantic** - Data validation and settings
- **JWT** - Token-based authentication
- **SlowAPI** - Rate limiting

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker (for local database)

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Environment Variables

Create a `.env` file:

```env
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5433/doomscroll
JWT_SECRET_KEY=your-secret-key-min-10-chars
MIGRATION_API_KEY=your-migration-key

# Optional
DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CACHE_BACKEND=memory
RATE_LIMIT_ENABLED=true
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── controllers/         # Route handlers
│   │       ├── article_controller.py
│   │       ├── auth_controller.py
│   │       ├── bookmark_controller.py
│   │       ├── health_controller.py
│   │       ├── source_controller.py
│   │       ├── sync_controller.py
│   │       └── migration_controller.py
│   ├── cache/                   # Caching layer
│   │   ├── backends.py          # Memory/Redis backends
│   │   └── cache_service.py     # Cache operations
│   ├── dependencies/            # FastAPI dependencies
│   │   └── auth.py              # Auth dependencies
│   ├── middleware/              # Middleware
│   │   ├── rate_limit.py        # Rate limiting
│   │   └── exception_handler.py # Global error handling
│   ├── repositories/            # Data access layer
│   │   ├── base_repository.py   # Generic CRUD
│   │   ├── article_repository.py
│   │   ├── bookmark_repository.py
│   │   ├── user_repository.py
│   │   └── unit_of_work.py
│   ├── services/                # Business logic
│   │   ├── article_service.py
│   │   ├── auth_service.py
│   │   ├── bookmark_service.py
│   │   └── token_blacklist.py
│   ├── utils/                   # Utilities
│   │   ├── auth.py              # JWT helpers
│   │   └── validation.py        # Input sanitization
│   ├── config.py                # Settings
│   ├── exceptions.py            # Custom exceptions
│   └── main.py                  # App entry point
├── alembic/                     # Database migrations
├── requirements.txt
└── README.md
```

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Controllers                             │
│            (HTTP handling, request/response)                 │
├─────────────────────────────────────────────────────────────┤
│                       Services                               │
│                   (Business logic)                           │
├─────────────────────────────────────────────────────────────┤
│                     Repositories                             │
│                    (Data access)                             │
├─────────────────────────────────────────────────────────────┤
│                   SQLAlchemy + DB                            │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

```
Request
   │
   ▼
┌──────────────┐
│  Middleware  │ ──▶ Rate Limiting, CORS
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Dependencies │ ──▶ Auth, DB Session
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Controller  │ ──▶ Validate input, call service
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Service    │ ──▶ Business logic, caching
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Repository  │ ──▶ Database operations
└──────────────┘
```

## API Endpoints

### Articles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles` | List articles (paginated) |
| GET | `/api/articles/{id}` | Get single article |
| GET | `/api/articles/search` | Search articles |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout, blacklist tokens |
| GET | `/api/auth/me` | Get current user |

### Bookmarks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookmarks` | List user's bookmarks |
| POST | `/api/bookmarks` | Add bookmark |
| DELETE | `/api/bookmarks/{article_id}` | Remove bookmark |
| GET | `/api/bookmarks/check/{article_id}` | Check if bookmarked |
| GET | `/api/bookmarks/ids` | Get all bookmarked IDs |

### Sources & Sync

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sources` | List all sources |
| GET | `/api/sync/status` | Get sync status |

## Authentication

### JWT Token Flow

```
┌─────────┐      POST /auth/login       ┌─────────┐
│  Client │ ───────────────────────────▶│ Backend │
└─────────┘                             └────┬────┘
                                             │
     ┌───────────────────────────────────────┘
     │  { access_token, refresh_token }
     ▼
┌─────────┐    GET /api/articles         ┌─────────┐
│  Client │ ────────────────────────────▶│ Backend │
│         │  Authorization: Bearer xxx   └────┬────┘
└─────────┘                                   │
                                              │ Validate token
     ┌────────────────────────────────────────┘
     │  { articles: [...] }
     ▼
```

### Token Types

| Token | Expiry | Purpose |
|-------|--------|---------|
| Access Token | 30 min | API authentication |
| Refresh Token | 7 days | Get new access tokens |

### Token Blacklisting

On logout, tokens are added to an in-memory blacklist with automatic cleanup:

```python
# Logout blacklists both tokens
blacklist.add(access_token)
blacklist.add_refresh_token(refresh_token)

# Subsequent requests are rejected
if blacklist.is_blacklisted(token):
    raise HTTPException(401, "Token revoked")
```

## Caching

### Cache Backends

```python
# Configuration
CACHE_BACKEND=memory  # or 'redis'
CACHE_REDIS_URL=redis://localhost:6379
CACHE_TTL_SHORT=120   # 2 minutes
CACHE_TTL_LONG=600    # 10 minutes
```

### Cache Keys

| Key Pattern | TTL | Description |
|-------------|-----|-------------|
| `articles:list:p{page}:l{limit}:{source}` | Short | Article listing |
| `articles:search:{query}:p{page}:...` | Short | Search results |
| `sources:list` | Long | Source list |

### Thundering Herd Prevention

Per-key locking prevents multiple requests from computing the same cache value:

```python
async def get_or_set(self, key, factory, ttl):
    cached = await self.get(key)
    if cached:
        return cached  # Cache hit

    async with self._key_locks[key]:  # Lock per key
        cached = await self.get(key)
        if cached:
            return cached  # Another request filled it

        value = await factory()  # Compute value
        await self.set(key, value, ttl)
        return value
```

## Rate Limiting

### Configuration

```python
RATE_LIMIT_ENABLED=true
RATE_LIMIT_AUTH_REQUESTS=5     # per minute
RATE_LIMIT_API_REQUESTS=100    # per minute
```

### Application

```python
# Auth endpoints (stricter)
@router.post("/login")
@auth_rate_limit()  # 5/min
async def login(...):

# General API (standard)
@router.get("/articles")
@api_rate_limit()   # 100/min
async def list_articles(...):
```

## Exception Handling

### Custom Exceptions

```python
class AppException(Exception):
    """Base with message, status_code, error_code, details"""

class ValidationError(AppException):      # 400
class NotFoundError(AppException):        # 404
class AuthenticationError(AppException):  # 401
class AuthorizationError(AppException):   # 403
class ConflictError(AppException):        # 409
class RateLimitError(AppException):       # 429
class ExternalServiceError(AppException): # 502
class DatabaseError(AppException):        # 500
```

### Global Error Handler

All exceptions are caught and formatted consistently:

```json
{
  "success": false,
  "error_code": "NOT_FOUND",
  "message": "Article with ID 'xyz' not found",
  "details": {
    "resource": "Article",
    "identifier": "xyz"
  }
}
```

## Repository Pattern

### Base Repository

Generic CRUD operations for all models:

```python
class BaseRepository(Generic[ModelType]):
    async def get(self, db, id) -> Optional[ModelType]
    async def get_all(self, db, skip, limit) -> List[ModelType]
    async def create(self, db, obj) -> ModelType
    async def update(self, db, db_obj) -> ModelType
    async def delete(self, db, id) -> bool
    async def count(self, db) -> int
```

### Specialized Repositories

```python
# ArticleRepository
await article_repo.get_paginated(db, page, limit, source)
await article_repo.search(db, query, page, limit)

# BookmarkRepository
await bookmark_repo.get_user_bookmarks(db, user_id)
await bookmark_repo.add_bookmark(db, user_id, article_id)
await bookmark_repo.get_bookmarked_article_ids(db, user_id)

# UserRepository
await user_repo.get_by_email(db, email)
await user_repo.email_exists(db, email)
```

## Dependency Injection

FastAPI's `Depends()` for clean dependency management:

```python
# Database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Current user (required)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    user_repository: UserRepository = Depends(get_user_repository)
) -> User:

# Current user (optional)
async def get_optional_current_user(...) -> Optional[User]:

# Usage in controllers
@router.get("/bookmarks")
async def list_bookmarks(
    user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
```

## Database

### Connection Pool

```python
# config.py
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 1800  # 30 minutes
```

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add bookmarks table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Configuration

### All Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Doomscroll | Application name |
| `APP_VERSION` | 1.0.0 | Version |
| `DEBUG` | false | Debug mode |
| `DATABASE_URL` | - | PostgreSQL connection string (required) |
| `JWT_SECRET_KEY` | - | JWT signing key (required, min 10 chars) |
| `MIGRATION_API_KEY` | - | Migration endpoint key (required) |
| `CORS_ORIGINS` | localhost:3000,5173 | Allowed origins |
| `CACHE_BACKEND` | memory | Cache type (memory/redis) |
| `CACHE_TTL_SHORT` | 120 | Short cache TTL (seconds) |
| `CACHE_TTL_LONG` | 600 | Long cache TTL (seconds) |
| `CACHE_REDIS_URL` | redis://localhost:6379 | Redis URL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Access token expiry |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token expiry |
| `RATE_LIMIT_ENABLED` | true | Enable rate limiting |
| `RATE_LIMIT_AUTH_REQUESTS` | 5 | Auth rate limit/min |
| `RATE_LIMIT_API_REQUESTS` | 100 | API rate limit/min |

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## API Documentation

FastAPI auto-generates OpenAPI docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
