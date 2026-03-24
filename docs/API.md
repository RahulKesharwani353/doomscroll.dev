# API Reference

Base URL: `http://localhost:8000/api`

Interactive API docs: `http://localhost:8000/docs`

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/articles` | Get paginated articles |
| GET | `/articles/search` | Search articles |
| GET | `/articles/{id}` | Get single article |
| GET | `/sources` | List all sources |
| GET | `/sources/{id}` | Get single source |
| POST | `/sources` | Create source |
| PUT | `/sources/{id}` | Update source |
| DELETE | `/sources/{id}` | Delete source |
| PATCH | `/sources/{id}/toggle` | Enable/disable source |
| GET | `/sync/status` | Get sync status |
| GET | `/sync/jobs` | Get sync job history |
| POST | `/sync/trigger` | Trigger manual sync |

---

## Health

### GET /health

Check API and database health.

**Response:**
```json
{
  "data": {
    "status": "ok",
    "database": "connected",
    "version": "1.0.0"
  }
}
```

---

## Articles

### GET /articles

Get paginated list of articles.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (min: 1) |
| `limit` | int | 20 | Items per page (1-100) |
| `source` | string | null | Filter by source slug |

**Example:**
```bash
curl "http://localhost:8000/api/articles?page=1&limit=20&source=hackernews"
```

**Response:**
```json
{
  "data": [
    {
      "id": "hn-38291045",
      "title": "Understanding PostgreSQL Query Performance",
      "url": "https://example.com/postgres-performance",
      "author": "techwriter",
      "source": "hackernews",
      "published_at": "2025-01-20T14:30:00Z",
      "fetched_at": "2025-01-21T09:15:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "has_more": true
}
```

### GET /articles/search

Search articles by title.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | required | Search query (2-100 chars) |
| `page` | int | 1 | Page number |
| `limit` | int | 20 | Items per page (1-100) |
| `source` | string | null | Filter by source slug |

**Example:**
```bash
curl "http://localhost:8000/api/articles/search?q=postgres&limit=10"
```

### GET /articles/{id}

Get single article by ID.

**Example:**
```bash
curl "http://localhost:8000/api/articles/hn-38291045"
```

**Response:**
```json
{
  "data": {
    "id": "hn-38291045",
    "title": "Understanding PostgreSQL Query Performance",
    "url": "https://example.com/postgres-performance",
    "author": "techwriter",
    "source": "hackernews",
    "published_at": "2025-01-20T14:30:00Z",
    "fetched_at": "2025-01-21T09:15:00Z"
  }
}
```

---

## Sources

### GET /sources

List all content sources.

**Example:**
```bash
curl "http://localhost:8000/api/sources"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "slug": "hackernews",
      "name": "Hacker News",
      "url": "https://news.ycombinator.com",
      "is_enabled": true,
      "ui_config": {
        "color": "#ff6600",
        "short_label": "HN"
      }
    },
    {
      "id": 2,
      "slug": "devto",
      "name": "Dev.to",
      "url": "https://dev.to",
      "is_enabled": true,
      "ui_config": {
        "color": "#3b82f6",
        "short_label": "DEV"
      }
    }
  ]
}
```

### GET /sources/{id}

Get single source by ID.

### POST /sources

Create a new source.

**Request Body:**
```json
{
  "slug": "medium",
  "name": "Medium",
  "url": "https://medium.com",
  "is_enabled": true,
  "ui_config": {
    "color": "#00ab6c",
    "short_label": "M"
  }
}
```

### PUT /sources/{id}

Update an existing source.

### DELETE /sources/{id}

Delete a source.

### PATCH /sources/{id}/toggle

Enable or disable a source.

**Request Body:**
```json
{
  "is_enabled": false
}
```

---

## Sync

### GET /sync/status

Get current sync status.

**Example:**
```bash
curl "http://localhost:8000/api/sync/status"
```

**Response:**
```json
{
  "data": {
    "is_running": false,
    "last_sync": {
      "id": 42,
      "source_slug": null,
      "status": "completed",
      "articles_fetched": 120,
      "started_at": "2025-01-21T09:00:00Z",
      "completed_at": "2025-01-21T09:00:15Z"
    },
    "enabled_sources": 4,
    "total_sources": 4
  }
}
```

### GET /sync/jobs

Get paginated sync job history.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `limit` | int | 10 | Items per page (1-100) |
| `source_slug` | string | null | Filter by source |

### GET /sync/jobs/{id}

Get single sync job by ID.

### POST /sync/trigger

Manually trigger a sync.

**Request Body:**
```json
{
  "source_slug": "hackernews"
}
```

Or sync all sources:
```json
{}
```

**Response:**
```json
{
  "data": {
    "job_id": 43,
    "message": "Sync triggered for all enabled sources"
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async operation started) |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 409 | Conflict (e.g., sync already running) |
| 500 | Internal Server Error |

---

## Article Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID: `{source}-{original_id}` |
| `title` | string | Article title |
| `url` | string | Link to original article |
| `author` | string | Author name (nullable) |
| `source` | string | Source slug |
| `published_at` | datetime | Publication time (UTC) |
| `fetched_at` | datetime | When fetched (UTC) |

## Source Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Source ID |
| `slug` | string | Unique identifier |
| `name` | string | Display name |
| `url` | string | Source website URL |
| `is_enabled` | boolean | Whether source is active |
| `ui_config` | object | UI styling config |
| `ui_config.color` | string | Hex color code |
| `ui_config.short_label` | string | Short label (1-3 chars) |
