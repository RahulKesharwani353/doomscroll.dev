# Content Aggregator - Phased Development Plan

## Overview

This document outlines the incremental development approach, starting with core requirements and progressively adding features.

---

## Phase Summary

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1** | Project Setup & Database | COMPLETED |
| **Phase 2** | Backend API & Sources | IN PROGRESS |
| **Phase 3** | Background Jobs | NOT STARTED |
| **Phase 4** | Frontend - Basic UI | NOT STARTED |
| **Phase 5** | Integration & Testing | NOT STARTED |
| **Phase 6** | Authentication (Bonus) | NOT STARTED |
| **Phase 7** | Bookmarks & Preferences (Bonus) | NOT STARTED |
| **Phase 8** | Search & Caching (Bonus) | NOT STARTED |

---

## Code Patterns Adopted (from Governance Project)

Following patterns from your existing Governance project for consistency:

### 1. Controller-Service-Repository Pattern
```
Controller (HTTP) → Service (Business Logic) → Repository (Database)
```

### 2. Dependency Injection
```python
def get_article_service(
    article_repository: ArticleRepository = Depends(get_article_repository)
) -> ArticleService:
    return ArticleService(article_repository=article_repository)
```

### 3. Standardized Response DTOs
- `ApiResponseDTO` - Single item responses
- `ListResponseDTO` - Non-paginated lists
- `PaginatedResponseDTO` - Paginated lists with metadata

### 4. Error Handling Pattern
```python
try:
    result = await service.do_something()
    return ApiResponseDTO(data=result)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except HTTPException:
    raise
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 5. Logging
```python
from app.core.logging_config import get_logger
logger = get_logger(__name__)
```

---

## PHASE 1: Project Setup & Database

### Goal
Set up project structure, configure PostgreSQL, and create database models.

### Tasks

#### 1.1 Backend Project Setup
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── config.py
├── requirements.txt
├── .env.example
└── .gitignore
```

**Files to create:**
- [ ] `requirements.txt` - Python dependencies
- [ ] `app/main.py` - FastAPI app initialization
- [ ] `app/config.py` - Environment configuration with Pydantic
- [ ] `.env.example` - Environment template
- [ ] `.gitignore` - Git ignore rules

**Dependencies:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
python-dotenv==1.0.0
alembic==1.13.1
```

#### 1.2 Database Setup
- [ ] Install PostgreSQL locally
- [ ] Create database `content_aggregator`
- [ ] Configure connection string

#### 1.3 Database Models
```
app/
├── core/
│   ├── __init__.py
│   └── database.py
├── models/
│   ├── __init__.py
│   └── article.py
```

**Article Model:**
```python
class Article(Base):
    __tablename__ = "articles"

    id = Column(String(100), primary_key=True)  # e.g., "hn-12345"
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False)
    author = Column(String(200), nullable=True)
    source = Column(String(50), nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), index=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### 1.4 Database Migrations
- [ ] Initialize Alembic
- [ ] Create initial migration
- [ ] Run migration to create tables

### Deliverable
✅ Backend project running with database connected

### Verification
```bash
# Start server
uvicorn app.main:app --reload

# Check health endpoint
curl http://localhost:8000/health
# Expected: {"status": "ok", "database": "connected"}
```

---

## PHASE 2: Backend API & Content Sources

### Goal
Build API endpoints and integrate all 4 content sources.

### Tasks

#### 2.1 Pydantic Schemas
```
app/schemas/
├── __init__.py
├── article.py
└── common.py
```

**Files to create:**
- [ ] `ArticleResponse` - API response schema
- [ ] `ArticleCreate` - Internal creation schema
- [ ] `PaginationParams` - Query parameters
- [ ] `PaginatedResponse` - Paginated list response

#### 2.2 Source Integrations
```
app/services/sources/
├── __init__.py
├── base.py
├── hackernews.py
├── devto.py
├── reddit.py
└── lobsters.py
```

**Order of implementation:**

| # | Source | API Complexity | Notes |
|---|--------|----------------|-------|
| 1 | Hacker News | Simple | Fetch top stories, then individual items |
| 2 | Dev.to | Simple | Direct article list endpoint |
| 3 | Lobsters | Simple | JSON feed endpoint |
| 4 | Reddit | Medium | Use .json suffix on subreddit |

**Base Source Interface:**
```python
class BaseSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        pass
```

#### 2.3 Article Service
```
app/services/
├── __init__.py
└── article_service.py
```

**Functions:**
- [ ] `get_articles(source, page, limit)` - Paginated fetch
- [ ] `get_article_by_id(id)` - Single article
- [ ] `upsert_articles(articles)` - Bulk insert/update
- [ ] `get_sources()` - List available sources

#### 2.4 API Endpoints
```
app/api/routes/
├── __init__.py
├── articles.py
├── sources.py
└── health.py
```

**Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/sources` | List sources |
| GET | `/api/articles` | Paginated feed |
| GET | `/api/articles/{id}` | Single article |
| POST | `/api/refresh` | Manual refresh trigger |

### Deliverable
✅ All endpoints working, sources fetching data

### Verification
```bash
# List sources
curl http://localhost:8000/api/sources

# Get articles
curl "http://localhost:8000/api/articles?page=1&limit=10"

# Filter by source
curl "http://localhost:8000/api/articles?source=hackernews"

# Manual refresh
curl -X POST http://localhost:8000/api/refresh
```

---

## PHASE 3: Background Jobs

### Goal
Implement automated content refresh using APScheduler.

### Tasks

#### 3.1 Scheduler Setup
```
app/jobs/
├── __init__.py
├── scheduler.py
└── refresh_job.py
```

**Files to create:**
- [ ] `scheduler.py` - APScheduler configuration
- [ ] `refresh_job.py` - Refresh logic

#### 3.2 Refresh Job Implementation
```python
async def refresh_all_sources():
    """Fetch from all sources and save to database."""
    sources = [
        HackerNewsSource(),
        DevToSource(),
        RedditSource(),
        LobstersSource(),
    ]

    # Fetch concurrently
    results = await asyncio.gather(
        *[source.safe_fetch() for source in sources],
        return_exceptions=True
    )

    # Save to database
    all_articles = []
    for articles in results:
        if isinstance(articles, list):
            all_articles.extend(articles)

    await article_service.upsert_articles(all_articles)
```

#### 3.3 Scheduler Integration
- [ ] Start scheduler on app startup
- [ ] Shutdown scheduler on app shutdown
- [ ] Configure interval via environment variable

#### 3.4 Error Handling
- [ ] Log failures per source
- [ ] Continue serving cached content on failure
- [ ] Retry logic for transient errors

### Deliverable
✅ Background job runs every 15 minutes automatically

### Verification
```bash
# Check logs for refresh activity
# Should see: "Refreshed X articles from Y sources"

# Or check database for fetched_at timestamps
```

---

## PHASE 4: Frontend - Basic UI

### Goal
Build React frontend with feed display, filtering, and pagination.

### Tasks

#### 4.1 Project Setup
```bash
npx create-react-app frontend
cd frontend
npm install axios
```

```
frontend/src/
├── index.js
├── App.js
├── App.css
├── components/
├── hooks/
├── services/
└── utils/
```

#### 4.2 API Service
```
src/services/
└── api.js
```

**Functions:**
- [ ] `getArticles(page, limit, source)`
- [ ] `getSources()`

#### 4.3 Core Components

**Header Component:**
```
src/components/Header/
├── Header.jsx
└── Header.css
```
- [ ] Logo and title
- [ ] Simple navigation

**Source Filter Component:**
```
src/components/SourceFilter/
├── SourceFilter.jsx
└── SourceFilter.css
```
- [ ] Filter tabs/chips for each source
- [ ] "All" option
- [ ] Active state styling

**Article Card Component:**
```
src/components/ArticleCard/
├── ArticleCard.jsx
└── ArticleCard.css
```
- [ ] Title (clickable link)
- [ ] Source badge with color
- [ ] Author name
- [ ] Relative time (e.g., "2 hours ago")

**Article Feed Component:**
```
src/components/ArticleFeed/
├── ArticleFeed.jsx
└── ArticleFeed.css
```
- [ ] Maps ArticleCard components
- [ ] Loading skeleton
- [ ] Empty state
- [ ] Error state with retry

**Pagination Component:**
```
src/components/Pagination/
├── Pagination.jsx
└── Pagination.css
```
- [ ] Page numbers
- [ ] Previous/Next buttons
- [ ] Current page indicator

#### 4.4 Custom Hooks
```
src/hooks/
├── useArticles.js
└── useSources.js
```

#### 4.5 Styling
- [ ] Responsive design (mobile-first)
- [ ] Source color coding
- [ ] Clean, minimal aesthetic

### Deliverable
✅ Working frontend displaying articles with filtering and pagination

### Verification
- Open http://localhost:3000
- See article feed loading
- Filter by source works
- Pagination works
- Clicking article opens in new tab

---

## PHASE 5: Integration & Testing

### Goal
Connect frontend to backend, test end-to-end, write documentation.

### Tasks

#### 5.1 CORS Configuration
- [ ] Configure FastAPI CORS middleware
- [ ] Allow frontend origin

#### 5.2 Environment Configuration
- [ ] Frontend `.env` for API URL
- [ ] Backend `.env.example` complete

#### 5.3 End-to-End Testing
- [ ] Start backend
- [ ] Start frontend
- [ ] Verify all features work together

#### 5.4 Documentation
- [ ] Update README.md with setup instructions
- [ ] API documentation (auto-generated by FastAPI)
- [ ] Design decisions document

#### 5.5 Error Handling
- [ ] Frontend error boundaries
- [ ] User-friendly error messages
- [ ] Network retry logic

### Deliverable
✅ Fully integrated application with documentation

### Verification
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm start

# Test all features in browser
```

---

## 🎉 CORE REQUIREMENTS COMPLETE

At this point, all core requirements from the assignment are met:
- ✅ Content Aggregation (4 sources)
- ✅ Data Normalization
- ✅ Unified Feed with pagination
- ✅ Background Refresh
- ✅ Source Filtering
- ✅ Documentation

---

## PHASE 6: Authentication (Bonus)

### Goal
Add user registration and login.

### Tasks

#### 6.1 User Model
```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
```

#### 6.2 Auth Dependencies
```txt
# Add to requirements.txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

#### 6.3 Auth Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user info |
| POST | `/api/auth/logout` | Invalidate token |

#### 6.4 Frontend Auth
- [ ] Login page
- [ ] Register page
- [ ] Auth context/state
- [ ] Protected routes
- [ ] Token storage (localStorage)

### Deliverable
✅ Users can register, login, and logout

---

## PHASE 7: Bookmarks & Preferences (Bonus)

### Goal
Allow users to save articles and set preferences.

### Tasks

#### 7.1 Bookmark Model
```python
class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    article_id = Column(String(100), ForeignKey("articles.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint('user_id', 'article_id'),)
```

#### 7.2 Preference Model
```python
class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(UUID, ForeignKey("users.id"), primary_key=True)
    preferred_sources = Column(ARRAY(String))  # e.g., ["hackernews", "devto"]
    updated_at = Column(DateTime, onupdate=func.now())
```

#### 7.3 Bookmark Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookmarks` | Add bookmark |
| GET | `/api/bookmarks` | List user bookmarks |
| DELETE | `/api/bookmarks/{id}` | Remove bookmark |

#### 7.4 Preference Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/preferences` | Get user preferences |
| PUT | `/api/preferences` | Update preferences |

#### 7.5 Frontend Updates
- [ ] Bookmark icon on article cards
- [ ] Bookmarks page
- [ ] Preferences/settings page
- [ ] Apply saved preferences on login

### Deliverable
✅ Users can bookmark articles and save source preferences

---

## PHASE 8: Search & Caching (Bonus)

### Goal
Add search functionality and Redis caching.

### Tasks

#### 8.1 Search Implementation
```python
@router.get("/api/articles/search")
async def search_articles(q: str, limit: int = 20):
    query = """
        SELECT * FROM articles
        WHERE to_tsvector('english', title) @@ plainto_tsquery('english', :q)
        ORDER BY published_at DESC
        LIMIT :limit
    """
    return await db.fetch_all(query, {"q": q, "limit": limit})
```

#### 8.2 Redis Setup
```txt
# Add to requirements.txt
redis==5.0.1
```

#### 8.3 Caching Strategy
```python
# Cache feed for 60 seconds
@cache(ttl=60)
async def get_articles(source: str, page: int):
    ...

# Invalidate on refresh
async def refresh_all_sources():
    ...
    await cache.delete_pattern("articles:*")
```

#### 8.4 Frontend Search
- [ ] Search input in header
- [ ] Debounced search requests
- [ ] Search results display
- [ ] Clear search button

### Deliverable
✅ Users can search articles, responses are cached

---

## Quick Reference: What to Build When

### Must Have (Core)
| Feature | Phase |
|---------|-------|
| Database & Models | Phase 1 |
| 4 Source Integrations | Phase 2 |
| REST API Endpoints | Phase 2 |
| Background Refresh | Phase 3 |
| React Feed UI | Phase 4 |
| Source Filtering | Phase 4 |
| Pagination | Phase 4 |
| Documentation | Phase 5 |

### Nice to Have (Bonus)
| Feature | Phase |
|---------|-------|
| User Authentication | Phase 6 |
| Bookmarking | Phase 7 |
| User Preferences | Phase 7 |
| Search | Phase 8 |
| Redis Caching | Phase 8 |

---

## Next Step

Ready to start? Begin with **Phase 1: Project Setup & Database**.

```bash
mkdir -p backend/app
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install fastapi uvicorn sqlalchemy asyncpg pydantic pydantic-settings
```
