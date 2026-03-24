# Design Decisions

This document explains the technology choices, trade-offs considered, and assumptions made during development.

## Technology Choices

### Backend: FastAPI (Python)

**Why FastAPI:**
- Native async support for concurrent API calls to external sources
- Automatic OpenAPI documentation generation
- Type hints with Pydantic for validation
- High performance (comparable to Node.js)
- Excellent developer experience

**Alternatives Considered:**
- **Express.js** - Would work well, but Python async is cleaner for this use case
- **Django** - Too heavy for this project, sync by default

### Frontend: React + Vite + TypeScript

**Why This Stack:**
- React for component-based UI with hooks
- Vite for fast dev server and builds
- TypeScript for type safety
- Tailwind CSS for rapid styling

**Alternatives Considered:**
- **Next.js** - SSR not needed for this SPA, adds complexity
- **Vue.js** - Would work equally well, React chosen for familiarity

### Database: PostgreSQL

**Why PostgreSQL:**
- Strong indexing for timestamp sorting and source filtering
- UPSERT support (`ON CONFLICT DO UPDATE`) for handling duplicate articles
- Full-text search built-in (used for search feature)
- ACID compliance for data integrity
- JSON column support for flexible `ui_config`

**Alternatives Considered:**
- **MongoDB** - Less suited for relational queries (filtering, pagination)
- **SQLite** - Not production-ready for concurrent writes

### Background Jobs: External Cron + Script

**Why External Cron:**
- Simple `run_sync.py` script triggered by OS scheduler
- No in-process scheduler overhead
- Works with Linux cron, Windows Task Scheduler, or any external scheduler
- Easy to monitor via standard OS tools
- Script can be run manually for testing

**Alternatives Considered:**
- **APScheduler** - In-process, but adds complexity and memory overhead
- **Celery** - Requires Redis/RabbitMQ, overkill for this project

## Architecture Decisions

### Separated Backend + Sync Service

**Decision:** Split into two services instead of one monolith.

**Reasons:**
- **Independent Scaling** - Sync service can scale separately from API
- **Fault Isolation** - Sync failures don't affect user requests
- **Clear Separation** - API serves users, sync service handles external APIs
- **Development** - Can work on each independently

**Trade-off:** Added operational complexity (two services to run).

### Cache Layer Abstraction

**Decision:** Abstract cache interface with swappable backends.

```python
class CacheBackend(ABC):
    async def get(self, key: str) -> Optional[Any]
    async def set(self, key: str, value: Any, ttl: int) -> None
    async def delete(self, key: str) -> bool
```

**Benefits:**
- Start with in-memory cache (no Redis dependency)
- Swap to Redis in production without code changes
- Easy to test with mock backends

**TTL Strategy:**
- Short TTL (2 min) for articles - fresh content matters
- Long TTL (10 min) for sources - rarely change

### Strategy Pattern for Source Adapters

**Decision:** Each source implements a common interface.

**Benefits:**
- Adding new source = create one new class
- API quirks isolated within each adapter
- Easy to test individual sources
- One failing source doesn't break others

### Controller-Service-Repository Pattern

**Decision:** Three-layer architecture.

```
Controller (HTTP) → Service (Logic) → Repository (Database)
```

**Benefits:**
- Clear separation of concerns
- Business logic testable without HTTP
- Database queries isolated and reusable
- Dependency injection for flexibility

## Trade-offs Made

| Decision | Trade-off | Reasoning |
|----------|-----------|-----------|
| External cron over APScheduler | Requires OS setup, but simpler code | No in-process overhead, standard tooling |
| In-memory cache default | Lost on restart, but zero setup | Easy to swap to Redis when needed |
| Separated services | More complexity to run | Better isolation and scalability |
| PostgreSQL over MongoDB | Schema migrations required | Better for relational queries |
| No X.com/Twitter | Missing popular platform | API costs ($100+/month) not justified |

## Assumptions Made

1. **Single Server Deployment** - Designed for single server, though can scale horizontally

2. **Public APIs Only** - No OAuth flows implemented, using public endpoints only

3. **English Content** - Full-text search configured for English language

4. **Reasonable Data Volume** - Optimized for thousands of articles, not millions

5. **15-Minute Freshness** - Background refresh every 15 minutes is acceptable

6. **UTC Timestamps** - All times stored and displayed in UTC

## Future Improvements

With more time, these improvements would strengthen the project:

### High Priority

1. **Unit Tests** - Test coverage for normalization and API endpoints
2. **Rate Limiting** - Protect API from abuse
3. **Redis Cache** - Production-ready caching
4. **Error Monitoring** - Sentry or similar for error tracking

### Medium Priority

5. **WebSocket Updates** - Real-time feed updates
6. **User Authentication** - JWT-based auth for preferences/bookmarks
7. **Bookmarking** - Save articles for later
8. **User Preferences** - Remember source preferences

### Nice to Have

9. **Elasticsearch** - More powerful search
10. **Analytics** - Track popular sources/articles
11. **Mobile App** - React Native version
12. **Email Digest** - Daily/weekly summaries
