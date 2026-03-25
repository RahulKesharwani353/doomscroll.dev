# Doomscroll Frontend

A modern React frontend for the Doomscroll content aggregator - a tech news aggregation platform that pulls articles from Hacker News, Dev.to, Reddit, and Lobsters.

## Tech Stack

- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Router** for navigation

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app runs at `http://localhost:5173` by default.

### Build

```bash
npm run build
```

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── assets/
│   └── icons/           # SVG icon components
├── components/          # Reusable UI components
│   ├── ArticleCard.tsx
│   ├── ArticleList.tsx
│   ├── AuthModal.tsx
│   ├── ErrorBoundary.tsx
│   ├── Header.tsx
│   ├── SourceFilter.tsx
│   └── index.ts
├── contexts/            # React Context providers
│   ├── types/           # Context types and context objects
│   │   ├── auth.ts
│   │   ├── bookmark.ts
│   │   ├── source.ts
│   │   └── index.ts
│   ├── AuthContext.tsx
│   ├── BookmarkContext.tsx
│   └── SourceContext.tsx
├── hooks/               # Custom React hooks
│   ├── useArticles.ts
│   ├── useAuth.ts
│   ├── useBookmarks.ts
│   ├── useSourceContext.ts
│   ├── useSources.ts
│   └── index.ts
├── pages/               # Page components
│   ├── ArticlesPage.tsx
│   ├── BookmarksPage.tsx
│   ├── NotFoundPage.tsx
│   └── index.ts
├── services/            # API layer
│   ├── api/
│   │   ├── repositories/    # Data access layer
│   │   │   ├── articleRepository.ts
│   │   │   ├── authRepository.ts
│   │   │   ├── bookmarkRepository.ts
│   │   │   ├── sourceRepository.ts
│   │   │   └── index.ts
│   │   ├── client.ts        # Base API client with interceptors
│   │   └── index.ts
│   ├── auth/
│   │   ├── tokenManager.ts  # JWT token management
│   │   └── index.ts
│   └── index.ts
├── types/               # TypeScript type definitions
│   └── index.ts
├── utils/               # Utility functions
│   └── helpers.ts
├── App.tsx
├── index.css            # Global styles & theme
└── main.tsx
```

## Architecture

### Context Pattern

Contexts are split for React Fast Refresh compatibility:
- **Provider components** (`*Context.tsx`) - Only export React components
- **Types and context objects** (`contexts/types/`) - Separate file for types
- **Hooks** (`hooks/`) - Consume contexts via `useContext`

### Repository Pattern

API calls are abstracted through repositories:

```typescript
// Example usage
import { articleRepository } from '../services/api';

const articles = await articleRepository.getAll({ page: 1, limit: 20 });
const results = await articleRepository.search({ query: 'react' });
```

### Token Management

JWT tokens are managed centrally via `tokenManager`:
- Automatic token refresh before expiry
- Secure storage in localStorage
- Auth header injection via API client interceptors

### API Client

The `apiClient` provides:
- Request/response interceptors
- Automatic auth header injection
- Retry logic with exponential backoff
- Error handling

## Theme System

All colors use CSS variables defined in `index.css`. Use theme utility classes instead of hardcoded colors:

```css
/* Text colors */
.text-primary    /* Main text */
.text-secondary  /* Secondary text */
.text-muted      /* Muted/disabled text */
.text-accent     /* Accent/highlight */

/* Backgrounds */
.bg-primary      /* Main background */
.bg-card         /* Card background */
.bg-card-hover   /* Card hover state */

/* Borders */
.border-default  /* Default border */
.border-hover    /* Hover border */

/* Source-specific (HN, DevTo, Reddit, Lobsters) */
.source-hn-gradient
.source-hn-badge
.source-hn-text
```

## Features

### Authentication
- Email/password registration and login
- JWT-based authentication with refresh tokens
- Token blacklisting on logout
- Protected routes for bookmarks

### Articles
- Paginated article list with "Load More"
- Search with debouncing
- Filter by source
- Staggered load animations

### Bookmarks
- Add/remove bookmarks (authenticated users)
- Optimistic UI updates
- Dedicated bookmarks page

### Error Handling
- Global ErrorBoundary component
- API error handling with retry logic
- User-friendly error states

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
