# Doomscroll Sync Service

The Sync Service is responsible for fetching articles from external content sources (Hacker News, Dev.to, Reddit, Lobsters) and normalizing them into a unified format for storage in the database.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYNC SERVICE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│  │  run_sync.py │───▶│ SourceAggregator │───▶│ ArticleRepository │   │
│  │  (Entry)     │    │  (Orchestrator)  │    │   (Persistence)   │   │
│  └──────────────┘    └────────┬─────────┘    └──────────────────┘   │
│                               │                                      │
│                    ┌──────────┴──────────┐                          │
│                    │   SourceRegistry    │                          │
│                    │  (Client Factory)   │                          │
│                    └──────────┬──────────┘                          │
│                               │                                      │
│         ┌─────────────────────┼─────────────────────┐               │
│         │                     │                     │               │
│         ▼                     ▼                     ▼               │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐         │
│  │ HackerNews  │      │   DevTo     │      │   Reddit    │  ...    │
│  │   Client    │      │   Client    │      │   Client    │         │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘         │
│         │                    │                    │                 │
│         └────────────────────┼────────────────────┘                 │
│                              │                                      │
│                              ▼                                      │
│                    ┌──────────────────┐                             │
│                    │  BaseSourceClient │                             │
│                    │ (Abstract Adapter) │                             │
│                    └──────────────────┘                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
sync_service/
├── app/
│   ├── sources/                 # Source adapters (Adapter Pattern)
│   │   ├── base_client.py       # Abstract base class
│   │   ├── hackernews_client.py # Hacker News adapter
│   │   ├── devto_client.py      # Dev.to adapter
│   │   ├── reddit_client.py     # Reddit adapter
│   │   ├── lobsters_client.py   # Lobsters adapter
│   │   ├── registry.py          # Source registry (Factory Pattern)
│   │   └── aggregator.py        # Multi-source orchestrator
│   └── repositories/            # Data access layer
│       ├── base_repository.py
│       ├── article_repository.py
│       ├── source_repository.py
│       └── sync_job_repository.py
├── run_sync.py                  # CLI entry point
└── README.md
```

## Design Patterns

### 1. Adapter Pattern

Each external API has its own data format. The **Adapter Pattern** normalizes all sources into a unified `ArticleCreate` schema.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  External API   │      │  Source Client  │      │  ArticleCreate  │
│  (Raw Format)   │─────▶│   (Adapter)     │─────▶│  (Normalized)   │
└─────────────────┘      └─────────────────┘      └─────────────────┘

Hacker News API:           HackerNewsClient:         ArticleCreate:
{                          transform_item()          {
  "id": 12345,             ─────────────────▶          "id": "hackernews-12345",
  "by": "pg",                                          "title": "...",
  "title": "...",                                      "url": "...",
  "url": "...",                                        "author": "pg",
  "time": 1234567890                                   "source": "hackernews",
}                                                      "published_at": "...",
                                                       "fetched_at": "..."
                                                     }
```

### 2. Template Method Pattern

`BaseSourceClient` defines the algorithm skeleton with `fetch_articles()`, while subclasses implement specific steps:

```python
class BaseSourceClient(ABC):
    # Template method - defines the algorithm
    async def fetch_articles(self, limit: int = 30) -> List[ArticleCreate]:
        raw_items = await self.fetch_raw(limit)    # Step 1: Fetch
        articles = self.transform(raw_items)        # Step 2: Transform
        return articles

    # Abstract methods - implemented by subclasses
    @abstractmethod
    async def fetch_raw(self, limit: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        pass
```

### 3. Registry Pattern (Factory)

`SourceRegistry` maps source slugs to client classes for dynamic instantiation:

```python
# Registration (happens on module import)
SourceRegistry.register("hackernews", HackerNewsClient)
SourceRegistry.register("devto", DevToClient)
SourceRegistry.register("reddit", RedditClient)
SourceRegistry.register("lobsters", LobstersClient)

# Usage
client = SourceRegistry.get_client("hackernews")  # Returns HackerNewsClient instance
```

### 4. Repository Pattern

Database operations are encapsulated in repository classes:

```python
article_repo = ArticleRepository()
await article_repo.upsert_many(db, articles)  # Bulk insert/update
```

## Data Normalization Flow

### Step 1: Fetch Raw Data

Each client fetches data in the source's native format:

```python
# Hacker News returns:
{"id": 12345, "by": "pg", "title": "...", "url": "...", "time": 1234567890}

# Dev.to returns:
{"id": 67890, "user": {"username": "ben"}, "title": "...", "url": "...", "published_at": "2024-01-01T12:00:00Z"}

# Reddit returns:
{"id": "abc123", "author": "spez", "title": "...", "url": "...", "created_utc": 1234567890}

# Lobsters returns:
{"short_id": "xyz789", "submitter_user": "jcs", "title": "...", "url": "...", "created_at": "2024-01-01T12:00:00Z"}
```

### Step 2: Transform to Normalized Schema

The `transform_item()` method converts each raw item to `ArticleCreate`:

```python
@dataclass
class ArticleCreate:
    id: str           # "{source}-{external_id}" e.g., "hackernews-12345"
    title: str
    url: str
    author: str | None
    source: str       # "hackernews", "devto", "reddit", "lobsters"
    published_at: datetime | None
    fetched_at: datetime
```

### Step 3: Upsert to Database

Articles are bulk upserted (insert or update on conflict):

```python
await article_repo.upsert_many(db, [article.model_dump() for article in articles])
```

## Source Adapters

### BaseSourceClient (Abstract)

```python
class BaseSourceClient(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return source identifier: 'hackernews', 'devto', etc."""

    @abstractmethod
    async def fetch_raw(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch raw data from external API."""

    @abstractmethod
    def transform_item(self, raw_item: Dict) -> Optional[ArticleCreate]:
        """Transform single raw item to ArticleCreate."""

    def generate_id(self, external_id: str) -> str:
        """Generate prefixed ID: '{source}-{external_id}'"""
        return f"{self.source_name}-{external_id}"
```

### HackerNewsClient

- **API**: Firebase REST API (`hacker-news.firebaseio.com`)
- **Strategy**: Fetch top story IDs, then fetch each story's details concurrently
- **Filtering**: Skips non-story types and stories without external URLs

```python
async def fetch_raw(self, limit: int) -> List[Dict]:
    # 1. Get top story IDs
    story_ids = await self.client.get("/topstories.json")

    # 2. Fetch each story concurrently
    tasks = [self._fetch_story_raw(id) for id in story_ids[:limit]]
    return await asyncio.gather(*tasks)
```

### DevToClient

- **API**: REST API (`dev.to/api`)
- **Strategy**: Single paginated endpoint
- **Date Parsing**: ISO 8601 format with Z suffix

```python
async def fetch_raw(self, limit: int) -> List[Dict]:
    return await self.client.get("/articles", params={"per_page": limit})
```

### RedditClient

- **API**: JSON endpoints (`reddit.com/r/{sub}/hot.json`)
- **Strategy**: Fetch from multiple subreddits (`programming`, `webdev`)
- **Filtering**: Skips stickied posts and self-posts
- **Headers**: Requires specific User-Agent format

```python
SUBREDDITS = ["programming", "webdev"]

async def fetch_raw(self, limit: int) -> List[Dict]:
    per_subreddit = limit // len(self.SUBREDDITS)
    for subreddit in self.SUBREDDITS:
        items = await self._fetch_subreddit_raw(subreddit, per_subreddit)
```

### LobstersClient

- **API**: JSON endpoint (`lobste.rs/hottest.json`)
- **Strategy**: Single endpoint, simple pagination
- **URL Fallback**: Uses `comments_url` if no external `url`

## Running the Sync

### Command Line

```bash
# Sync all enabled sources
python sync_service/run_sync.py

# Sync specific source only
python sync_service/run_sync.py --source hackernews
python sync_service/run_sync.py --source devto
python sync_service/run_sync.py --source reddit
python sync_service/run_sync.py --source lobsters
```

### Scheduled Execution

**Cron (Linux/Mac)**:
```bash
# Every 15 minutes
*/15 * * * * cd /path/to/project && python sync_service/run_sync.py
```

**Task Scheduler (Windows)**:
```
Program: python
Arguments: sync_service/run_sync.py
Start in: C:\path\to\project
```

### Programmatic Usage

```python
from sync_service.app.sources.aggregator import SourceAggregator
from shared.core.database import AsyncSessionLocal

async with AsyncSessionLocal() as db:
    aggregator = SourceAggregator()
    await aggregator.init_from_db(db)  # Load enabled sources

    result = await aggregator.fetch_and_save(db)

    print(f"Stats: {result.stats}")    # {"hackernews": 30, "devto": 25, ...}
    print(f"Errors: {result.errors}")  # Any fetch failures

    await aggregator.close()
```

## Sync Job Tracking

Each sync run creates a `SyncJob` record in the database:

| Field | Description |
|-------|-------------|
| `id` | Job ID |
| `source_id` | Source ID (null if all sources) |
| `source_slug` | Source slug (null if all sources) |
| `status` | `pending`, `running`, `completed`, `failed` |
| `articles_fetched` | Total articles fetched |
| `articles_created` | New articles created |
| `articles_updated` | Existing articles updated |
| `articles_failed` | Failed article count |
| `error_message` | Error details (if any) |
| `started_at` | Job start time |
| `completed_at` | Job completion time |

## Adding a New Source

### 1. Create Client Class

```python
# sync_service/app/sources/newsource_client.py

from sync_service.app.sources.base_client import BaseSourceClient

class NewSourceClient(BaseSourceClient):
    BASE_URL = "https://api.newsource.com"

    @property
    def source_name(self) -> str:
        return "newsource"

    async def fetch_raw(self, limit: int = 30) -> List[Dict[str, Any]]:
        response = await self.client.get(f"{self.BASE_URL}/articles")
        return response.json()[:limit]

    def transform_item(self, raw_item: Dict[str, Any]) -> Optional[ArticleCreate]:
        return ArticleCreate(
            id=self.generate_id(str(raw_item["id"])),
            title=raw_item["title"],
            url=raw_item["link"],
            author=raw_item.get("author_name"),
            source=self.source_name,
            published_at=parse_date(raw_item["date"]),
            fetched_at=self.get_current_time(),
        )
```

### 2. Register the Client

```python
# sync_service/app/sources/registry.py

from sync_service.app.sources.newsource_client import NewSourceClient

def register_all_sources() -> None:
    # ... existing registrations ...
    SourceRegistry.register("newsource", NewSourceClient)
```

### 3. Add Source to Database

```sql
INSERT INTO sources (name, slug, url, is_enabled, fetch_limit)
VALUES ('New Source', 'newsource', 'https://newsource.com', true, 30);
```

## Error Handling

- **Network Errors**: Caught and logged, sync continues with other sources
- **Transform Errors**: Individual item failures don't stop the batch
- **Database Errors**: Transaction rollback, job marked as failed
- **Validation Errors**: Items failing Pydantic validation are skipped

```python
# Per-item error handling in transform()
for item in raw_items:
    try:
        article = self.transform_item(item)
        if article:
            articles.append(article)
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
    except Exception as e:
        logger.error(f"Transform error: {e}")
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDDIT_USER_AGENT` | Reddit API User-Agent | `windows:doomscroll:1.0` |

## Dependencies

- `httpx` - Async HTTP client
- `pydantic` - Data validation and schemas
- `sqlalchemy` - Database ORM (async)
- `asyncpg` - PostgreSQL async driver
