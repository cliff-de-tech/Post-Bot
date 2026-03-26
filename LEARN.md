# Learning Guide — Post Bot

> A deep-dive into how Post Bot is architected, what each layer does, and how to extend it.

---

## Table of Contents

- [What the App Does](#what-the-app-does)
- [High-Level Architecture](#high-level-architecture)
- [Technology Stack](#technology-stack)
- [Backend Deep-Dive](#backend-deep-dive)
  - [Entry Point](#entry-point)
  - [Routes](#routes)
  - [Middleware](#middleware)
  - [Repository Pattern](#repository-pattern)
  - [Database & Migrations](#database--migrations)
- [Services Layer](#services-layer)
  - [AI Service](#ai-service)
  - [GitHub Activity](#github-activity)
  - [LinkedIn Service](#linkedin-service)
  - [Persona Service](#persona-service)
  - [Celery & Task Queue](#celery--task-queue)
  - [Encryption & Security](#encryption--security)
- [Frontend Deep-Dive](#frontend-deep-dive)
  - [Pages & Routing](#pages--routing)
  - [Components](#components)
  - [Hooks & State](#hooks--state)
  - [API Client](#api-client)
- [Authentication](#authentication)
- [Data Flow: Scan → Generate → Post](#data-flow-scan--generate--post)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [How to Extend the App](#how-to-extend-the-app)
  - [Adding a New AI Provider](#adding-a-new-ai-provider)
  - [Adding a New Social Platform](#adding-a-new-social-platform)
  - [Adding a New API Route](#adding-a-new-api-route)
  - [Adding a New Frontend Page](#adding-a-new-frontend-page)
- [Key Concepts Glossary](#key-concepts-glossary)

---

## What the App Does

Post Bot watches your GitHub activity (commits, pull requests, pushes, new repositories) and converts it into professional LinkedIn posts using AI. The core loop is:

1. **Scan** — Fetch recent GitHub events via the GitHub REST API.
2. **Generate** — Pass those events to an AI model with a user-defined persona prompt.
3. **Review** — Show the draft post in the dashboard for the user to edit.
4. **Publish** — Post to LinkedIn via OAuth 2.0.

A standalone CLI mode (`bot.py`) lets the same loop run as a scheduled job without the web UI.

---

## High-Level Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Browser (Next.js)                   │
│  pages/ → components/ → hooks/ → lib/api.ts            │
└────────────────────┬───────────────────────────────────┘
                     │ HTTP (JSON)
┌────────────────────▼───────────────────────────────────┐
│             FastAPI Backend  (backend/)                 │
│  app.py → routes/ → middleware/ → repositories/        │
└──────┬─────────────┬────────────────────────────────────┘
       │             │
       │         ┌───▼───────────┐
       │         │  PostgreSQL   │
       │         │  (SQLAlchemy) │
       │         └───────────────┘
       │
┌──────▼───────────────────────────────────────────────┐
│              Services Layer  (services/)              │
│  ai_service · github_activity · linkedin_service     │
│  persona_service · celery_app · encryption · ...     │
└───────────┬───────────────────┬──────────────────────┘
            │                   │
    ┌───────▼──────┐    ┌───────▼──────┐
    │  External AI │    │  Redis        │
    │  APIs        │    │  (Celery)     │
    │  Groq/OpenAI │    └──────────────┘
    │  Anthropic   │
    │  Mistral     │
    └──────────────┘
```

---

## Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 14 (Pages Router) | SSR, file-based routing, React ecosystem |
| Styling | Tailwind CSS 3 | Utility-first, dark/light mode via CSS variables |
| Auth (UI) | Clerk | Managed JWTs, social login, multi-tenant |
| Backend | FastAPI (Python 3.11+) | Async, auto OpenAPI docs, type-safe via Pydantic |
| ORM | SQLAlchemy (async) | Type-safe queries, migration support |
| Migrations | Alembic | Versioned schema changes |
| Background jobs | Celery + Redis | Scheduled / delayed post publishing |
| AI providers | Groq, OpenAI, Anthropic, Mistral | Pluggable multi-provider design |
| LinkedIn API | OAuth 2.0 + REST | Official API, no scraping |
| Payments | Paystack | Free/Pro/Enterprise subscription tiers |
| Image search | Unsplash API | Optional visual enrichment for posts |

---

## Backend Deep-Dive

### Entry Point

`backend/app.py` is intentionally kept slim (~200 lines). It:

- Creates the FastAPI application instance.
- Registers all routers from `backend/routes/`.
- Attaches middleware (CORS, Clerk JWT, request-ID tracing).
- Runs environment validation and database table initialisation on startup.

### Routes

Each file in `backend/routes/` owns one domain:

| File | Endpoints |
|------|-----------|
| `auth.py` | LinkedIn OAuth callback, token exchange |
| `posts.py` | Create, list, update, delete posts |
| `settings.py` | User credentials and preferences |
| `github.py` | GitHub activity scanning |
| `linkedin.py` | Publish to LinkedIn, connection status |
| `payments.py` | Paystack webhook, subscription status |
| `feedback.py` | User feedback submission |
| `webhooks.py` | Inbound webhook handlers |

All routes import `require_auth` from `backend/middleware/clerk_auth.py` and pass the verified user ID down to repositories to enforce per-user data isolation.

### Middleware

- **`clerk_auth.py`** — Verifies Clerk JWT on every protected request. Exposes `require_auth` (dependency) and `get_current_user` (helper).
- **Request-ID middleware** — Injects an `X-Request-ID` header on every request/response pair for distributed tracing.

### Repository Pattern

`backend/repositories/` contains one repository class per database table. All repositories extend `BaseRepository`, which automatically scopes every query to the authenticated `user_id`. This enforces multi-tenant isolation at the data layer — a user can never read or modify another user's records.

```
BaseRepository
├── PostRepository       → user_posts table
└── SettingsRepository   → user_settings table
```

Use the dependency helpers `get_post_repository()` / `get_settings_repository()` in route handlers via FastAPI's `Depends()`.

### Database & Migrations

- Schema definitions live in `backend/database/schema.py` using SQLAlchemy's declarative style with full type annotations.
- `backend/migrations/` contains Alembic revision files. Run `alembic upgrade head` to apply all pending migrations.
- The app calls `init_tables()` on startup as a safety net to create missing tables in environments where Alembic has not been run.

---

## Services Layer

The `services/` directory contains business logic that is shared between the FastAPI backend and the standalone CLI bot.

### AI Service

`services/ai_service.py` is the central post-generation engine. Key concepts:

- **Multi-provider**: Supports Groq, OpenAI, Anthropic, and Mistral. The active provider is selected via a user setting or environment variable.
- **Lazy singletons**: Each AI SDK client is initialised once on first use and cached to avoid redundant setup.
- **Persona injection**: The user's persona string (from `services/persona_service.py`) is prepended to every prompt to tailor the post's tone and style.

### GitHub Activity

`services/github_activity.py` fetches public events from the GitHub Events API. It uses a `TTLCache` to avoid redundant API calls within a short window. The response is normalised into a standard activity object consumed by the AI service.

### LinkedIn Service

`services/linkedin_service.py` handles:

- **OAuth token exchange** — swaps the authorisation code for access + refresh tokens.
- **Token refresh** — transparently refreshes expired access tokens.
- **Publishing** — calls LinkedIn's `/ugcPosts` endpoint with the generated post content and optional image.

Tokens are stored encrypted in the database (see [Encryption & Security](#encryption--security)).

### Persona Service

`services/persona_service.py` maintains a per-user writing persona. After each successful LinkedIn publish, it calls `persona_analyzer.py` to update the stored writing patterns based on the post that was just published. The persona is a plain-text prompt fragment injected into every AI request.

### Celery & Task Queue

`services/celery_app.py` sets up a Celery application backed by Redis. Scheduled posts are stored in the database and dispatched to a Celery worker via `services/tasks.py`. This decouples the HTTP request/response cycle from the actual LinkedIn publish call.

### Encryption & Security

`services/encryption.py` wraps Fernet symmetric encryption to protect sensitive credentials (LinkedIn tokens, API keys) at rest in the database. The encryption key is derived from an environment variable.

> **Production note**: The application checks both `ENVIRONMENT` and `ENV` variables to detect a production context. Production mode enables stricter validation and disables development-only bypass routes (`DEV_MODE=true` required to re-enable them).

---

## Frontend Deep-Dive

### Pages & Routing

`web/src/pages/` uses Next.js file-based routing. Notable pages:

| Page | Path | Purpose |
|------|------|---------|
| `index.tsx` | `/` | Landing page |
| `dashboard.tsx` | `/dashboard` | Main app — scan, generate, publish |
| `settings.tsx` | `/settings` | Credentials, persona, preferences |
| `sign-in.tsx` / `sign-up.tsx` | `/sign-in`, `/sign-up` | Clerk-powered auth pages |
| `history.tsx` | `/history` | Post history with scheduling management |

### Components

Components are organised by feature area under `web/src/components/`:

- **`dashboard/`** — 11 dashboard widgets (activity feed, post queue, stats cards, bot mode panel, etc.)
- **`modals/`** — 5 modal dialogs (post editor, publish confirmation, etc.)
- **`settings/`** — Persona quiz and individual settings panels
- **`ui/`** — 20+ reusable primitives including `AIStatusMessage`, `Icon`, buttons, inputs, and toasts

### Hooks & State

- **`useDashboardData`** — fetches all dashboard data via React Query (TanStack Query). Handles cache invalidation after publish actions.
- **`useAIStatus`** — manages the lifecycle of the `AIStatusMessage` chat bubble: `show()`, `update()`, `complete()`, `error()`, `dismiss()`.
- **`useFocusTrap`** — traps keyboard focus inside modals for accessibility.
- **`web/src/store/`** — lightweight global state (Zustand or React context) for theme and user preferences.

### API Client

`web/src/lib/api.ts` is a centralised Axios (or Fetch) client that:

- Attaches the Clerk JWT to every outbound request via an interceptor.
- Provides typed helpers for each backend endpoint.
- Handles 401 responses by redirecting to sign-in.

---

## Authentication

The app uses **Clerk** for identity management:

1. The browser signs in via Clerk's hosted UI.
2. Clerk issues a short-lived JWT.
3. Every API request from the frontend includes the JWT in the `Authorization: Bearer <token>` header.
4. The FastAPI `require_auth` dependency verifies the JWT against Clerk's public JWKS endpoint.
5. The verified `user_id` (Clerk subject claim) is used as the tenant key throughout the backend.

LinkedIn credentials are stored separately in the database, encrypted at rest, and associated with the Clerk `user_id`.

---

## Data Flow: Scan → Generate → Post

```
User clicks "Scan"
        │
        ▼
GET /github/activity  →  github_activity.py  →  GitHub API
        │
        ▼  (list of activity objects)
POST /posts/generate  →  ai_service.py  →  AI provider API
        │                persona_service.py (injects persona)
        ▼  (draft post text saved to DB)
User reviews & edits in dashboard
        │
        ▼
POST /linkedin/publish  →  linkedin_service.py  →  LinkedIn API
        │
        ▼  (post marked published; persona patterns updated)
Dashboard stats refresh via React Query
```

For **scheduled posts**, the final step queues a Celery task instead of publishing immediately. The task picks up at the scheduled time and calls `linkedin_service.py` directly.

---

## Environment Variables

A full list is in `.env.example`. Key variables:

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | Yes (prod) | PostgreSQL connection string |
| `ENCRYPTION_KEY` | Yes | Fernet key for credential encryption |
| `CLERK_SECRET_KEY` | Yes | Backend JWT verification |
| `ENVIRONMENT` | Yes (prod) | Set to `production` to enable prod mode |
| `REDIS_URL` | Yes (scheduling) | Celery broker URL |
| `DEV_MODE` | No | Set `true` to enable dev-only bypass routes |
| `GROQ_API_KEY` | Optional | Default AI provider key |
| `OPENAI_API_KEY` | Optional | OpenAI provider key |
| `ANTHROPIC_API_KEY` | Optional | Anthropic provider key |
| `MISTRAL_API_KEY` | Optional | Mistral provider key |

> The app validates all required variables at startup via `validate_environment()` and fails fast if any are missing.

---

## Testing

### Backend (pytest)

```bash
cd backend
pytest tests/ -v
```

Tests live in `backend/tests/` (84+ tests). They use an in-memory SQLite database for speed and mock external API calls.

### Frontend (Jest)

```bash
cd web
npm test
```

Tests live in `web/__tests__/` and use Jest + React Testing Library.

### CI

GitHub Actions runs both suites plus a frontend build and Python lint on every push and pull request. See `.github/workflows/` for the workflow definitions.

---

## How to Extend the App

### Adding a New AI Provider

1. Add a new branch in `services/ai_service.py` for the provider's SDK client (follow the lazy-singleton pattern already used for Groq/OpenAI/Anthropic/Mistral).
2. Add the provider name to the selection logic (the `if/elif` block that picks the active client).
3. Add the new API key to `.env.example` and the environment validation list.
4. Update the settings UI in `web/src/components/settings/` to expose the new key field.

### Adding a New Social Platform

1. Create `services/<platform>_service.py` modelled on `linkedin_service.py` — implement `exchange_token`, `refresh_token`, and `publish` functions.
2. Add a route file `backend/routes/<platform>.py` with OAuth callback, connection-status, and publish endpoints.
3. Register the new router in `backend/app.py`.
4. Add the corresponding UI controls in the settings and dashboard pages.
5. Extend the database schema (add a column or table for the new platform's tokens) and create an Alembic migration.

### Adding a New API Route

1. Create `backend/routes/<name>.py`.
2. Define an `APIRouter` instance and add your endpoints.
3. Import and register the router in `backend/app.py`:
   ```python
   from routes.<name> import router as <name>_router
   app.include_router(<name>_router, prefix="/<name>", tags=["<name>"])
   ```
4. Add `require_auth` as a dependency to any endpoint that accesses user data.
5. Write tests in `backend/tests/`.

### Adding a New Frontend Page

1. Create `web/src/pages/<name>.tsx`.
2. The page is automatically available at `/<name>` via Next.js file-based routing.
3. Wrap the page in the shared layout component if one is used.
4. Add a link in the navigation component.
5. Write tests in `web/__tests__/`.

---

## Key Concepts Glossary

| Term | Meaning |
|------|---------|
| **Persona** | A plain-text prompt fragment describing the user's writing voice and style, injected into every AI request |
| **Activity** | A normalised GitHub event (push, PR, new repo, etc.) used as the input for post generation |
| **Draft** | A post that has been AI-generated and saved to the database but not yet published |
| **Scheduled post** | A draft with a future publish time; delivered by a Celery worker |
| **Repository (pattern)** | A data-access class that scopes all queries to the current `user_id` |
| **Repurpose Engine** | A feature that takes any URL and extracts key insights to generate a LinkedIn post |
| **TTLCache** | Time-to-live in-memory cache used in `github_activity.py` to throttle GitHub API calls |
| **`require_auth`** | FastAPI dependency that verifies the Clerk JWT and returns the authenticated `user_id` |
| **`DEV_MODE`** | Environment flag that re-enables development-only bypass routes in production |

---

*For setup instructions, see [`Guides/SETUP_GUIDE.md`](Guides/SETUP_GUIDE.md). For contribution guidelines, see [`CONTRIBUTING.md`](CONTRIBUTING.md).*
