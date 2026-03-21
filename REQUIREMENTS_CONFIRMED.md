# Confirmed Requirements - Content Aggregator Service

## Manager Clarifications (Received)

| Question | Answer |
|----------|--------|
| **Article Display** | Card preview with redirect to original source |
| **Content Type** | General trending from programming-related sources |
| **Reddit Subreddits** | `r/programming` and `r/webdev` |
| **Authentication** | Public feed (no auth for core submission) |
| **Deployment** | Must be deployed and accessible over internet |

---

## Final Scope for Core Submission

### What We're Building

```
+-------------------------------------------------------------------+
|                    CONTENT AGGREGATOR                             |
+-------------------------------------------------------------------+
|                                                                   |
|  PUBLIC FEED (No Login Required)                                  |
|                                                                   |
|  +-----------------------------------------------------------+   |
|  |  [All] [Hacker News] [Dev.to] [Reddit] [Lobsters]         |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
|  +-------------------------+  +-------------------------+        |
|  | Article Title           |  | Article Title           |        |
|  | HN | @author            |  | Dev.to | @author        |        |
|  | 2 hours ago        [->] |  | 4 hours ago        [->] |        |
|  +-------------------------+  +-------------------------+        |
|                                                                   |
|  [1] [2] [3] ... [Next ->]                                       |
|                                                                   |
+-------------------------------------------------------------------+
```

### Content Sources

| Source | What to Fetch | Endpoint |
|--------|---------------|----------|
| Hacker News | Top stories | `/topstories` |
| Dev.to | Latest articles | `/articles` |
| Reddit | Hot posts | `r/programming` + `r/webdev` |
| Lobste.rs | Hottest stories | `/hottest.json` |

### Article Card Content

```
+-------------------------------------------+
| Understanding PostgreSQL Performance      |  <- Title (clickable)
|-------------------------------------------|
| Hacker News  |  @techwriter              |  <- Source + Author
| 2 hours ago                         [->] |  <- Time + External link
+-------------------------------------------+
```

**No full article content needed** - just metadata and redirect link.

---

## Deployment Options

Since deployment is required, here are recommended platforms:

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Render** | Yes | Backend + PostgreSQL + Frontend |
| **Railway** | $5 credit | Full stack deployment |
| **Vercel + Supabase** | Yes | Frontend (Vercel) + DB (Supabase) |
| **Fly.io** | Yes | Backend containers |

**Recommended:** Render (all-in-one, free PostgreSQL included)

---

## Updated Phase Plan

### Core Phases (Required)
- Phase 1: Project Setup & Database
- Phase 2: Backend API & 4 Sources
- Phase 3: Background Jobs
- Phase 4: Frontend UI (Cards + Filter + Pagination)
- Phase 5: Integration & Documentation
- **Phase 5.5: Deployment**

### Bonus Phases (If Time Permits)
- Phase 6: Authentication
- Phase 7: Bookmarks & Preferences
- Phase 8: Search & Caching

---

## Key Takeaway

> "Handling ambiguity in requirements and specifications is one of the points of assessment."

This means:
1. Make reasonable assumptions when unclear
2. Document your decisions
3. Don't over-engineer - keep it simple
4. Show good judgment in trade-offs

---

## Ready to Build

All requirements are now clear. Core submission needs:

- [x] 4 sources (HN, Dev.to, Reddit, Lobsters)
- [x] Card preview with redirect (no full content)
- [x] Public feed (no auth)
- [x] Source filtering + pagination
- [x] Background refresh
- [x] Deployed to internet
