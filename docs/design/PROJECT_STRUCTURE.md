# Project Structure

File and folder structure for ASASelfHosted.com development. For a full index of working docs, see **docs/WORKING_DOCS.md**.

**Last Updated:** 2026-02-03

## Root Level Files

```
asaselfhosted.com/
├── backend/                 # FastAPI backend
├── frontend/                 # React frontend
├── docs/                     # Working docs and reference (see WORKING_DOCS.md)
│   └── design/               # Canonical design docs (1_DESCRIPTION.txt … 5_Appendix.txt)
├── DEV_NOTES.md              # Dev context, ports, workflow; links to docs
├── INSTALL.md                # Installation instructions
├── README.md                 # Project overview
├── SUPABASE_SETUP.md         # Supabase setup guide
```

## Docs (docs/)

```
docs/
├── WORKING_DOCS.md            # Index of all working docs (start here)
├── DECISIONS.md               # Official decisions (override design docs)
├── FinalCheck.md              # Pre-launch checklist
├── TODO.md                    # Single backlog (all open items)
├── REMAINING_VS_DESIGN.md     # What's left vs design docs; priority summary
├── OPERATIONS.md              # Ingest, violation policy, responsibility map, jobs, failure modes, alerting
├── SPRINT_8.md                # Sprint 8 playbook + status
├── SPRINT_9.md                # Sprint 9 playbook + status
├── design/                    # Canonical product scope
│   ├── 1_DESCRIPTION.txt      # Project vision
│   ├── 2_FEATURE_LIST.txt    # Feature list (MVP scope)
│   ├── 3_TECH_STACK.txt      # Tech stack
│   ├── 4_Dev_Plan.txt         # Development plan
│   ├── 5_Appendix.txt         # Appendix (competitive ref, page architecture)
│   ├── PROJECT_STRUCTURE.md   # This file
│   └── README.md              # Design docs index
├── RANKING.md                 # Ranking/sort contract (rank_by, quality_score)
├── REFERENCE_SCHEMA_SPRINT0_TO_5.md
├── SERVER_IMAGES.md           # Server images feature spec
├── TRUST_PAGES.md             # Trust pages (/verification, /consent) + audit table
└── STEAM_OAUTH_TODO.md        # Steam OAuth implementation notes
```

## Backend Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main v1 router (includes all domain routers)
│   │       ├── directory.py    # Directory read endpoints (Sprint 1+)
│   │       ├── servers.py      # Server CRUD endpoints
│   │       ├── clusters.py     # Cluster endpoints
│   │       ├── verification.py # Verification endpoints
│   │       ├── heartbeat.py    # Agent heartbeat ingestion (Sprint 4: Ed25519 auth)
│   │       ├── consent.py      # Consent management
│   │       ├── subscriptions.py # Subscription management
│   │       └── webhooks.py     # Stripe webhooks
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Settings (env vars, get_settings pattern)
│   │   ├── crypto.py          # Ed25519 signature verification (Sprint 4)
│   │   ├── deps.py            # FastAPI dependencies (auth, user identity)
│   │   ├── errors.py          # Error handling (centralized API errors)
│   │   ├── heartbeat.py       # Heartbeat utilities (grace window, etc.) (Sprint 4)
│   │   ├── security.py        # JWT verification, JWKS, user identity
│   │   └── supabase.py        # Supabase client
│   ├── middleware/            # Request middleware
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication middleware
│   │   ├── consent.py        # Consent checking middleware
│   │   ├── rate_limit.py     # Rate limiting middleware
│   │   └── request_id.py     # Request ID middleware (Sprint 1+)
│   ├── schemas/              # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py          # Base schemas
│   │   ├── directory.py     # Directory schemas (Sprint 1+)
│   │   ├── servers.py       # Server schemas
│   │   ├── clusters.py      # Cluster schemas
│   │   ├── verification.py  # Verification schemas
│   │   ├── heartbeat.py     # Heartbeat request/response schemas (Sprint 4: Ed25519)
│   │   ├── consent.py       # Consent schemas
│   │   └── subscriptions.py # Subscription schemas
│   ├── models/              # Domain models (reference only)
│   │   ├── __init__.py
│   │   └── domain.py       # Domain type definitions
│   ├── engines/            # Derived state computation engines (Sprint 4)
│   │   ├── __init__.py
│   │   ├── status_engine.py      # Effective status computation
│   │   ├── confidence_engine.py   # RYG confidence computation
│   │   ├── uptime_engine.py      # Uptime percentage computation
│   │   └── quality_engine.py     # Quality score computation
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── crypto.py      # Legacy crypto utilities (deprecated, use core/crypto.py)
│   │   └── stripe.py       # Stripe utilities
│   ├── workers/            # Background workers (Sprint 4)
│   │   ├── __init__.py
│   │   └── heartbeat_worker.py  # Durable worker for heartbeat processing
│   ├── db/                 # Database layer (Sprint 1+)
│   │   ├── __init__.py
│   │   ├── directory_repo.py      # Directory repository interface
│   │   ├── heartbeat_repo.py      # Heartbeat repository interface (Sprint 4)
│   │   ├── heartbeat_jobs_repo.py # Heartbeat jobs queue interface (Sprint 4)
│   │   ├── servers_derived_repo.py # Servers derived state repository (Sprint 4)
│   │   ├── mock_directory_repo.py # Mock implementation (Sprint 1)
│   │   ├── supabase_directory_repo.py # Supabase implementation (Sprint 3+)
│   │   ├── supabase_heartbeat_repo.py # Heartbeat persistence (Sprint 4)
│   │   ├── supabase_heartbeat_jobs_repo.py # Durable queue (Sprint 4)
│   │   ├── supabase_servers_derived_repo.py # Derived state updates (Sprint 4)
│   │   ├── providers.py           # Repository provider (DI)
│   │   ├── queries.py            # Database query helpers
│   │   └── migrations/            # SQL migration files
│   │       ├── 001_sprint_0_schema.sql
│   │       ├── 003_sprint_3_directory_view.sql
│   │       ├── 004_sample_servers.sql
│   │       ├── 005_validate_platforms_type.sql
│   │       └── 006_sprint_4_agent_auth.sql
│   └── main.py            # FastAPI app entry point
├── tests/                 # Test suite (Sprint 1+)
│   ├── __init__.py
│   ├── test_auth_contract.py  # Auth contract smoke tests
│   ├── test_crypto.py         # Ed25519 crypto tests (Sprint 4)
│   ├── test_heartbeat_endpoint.py  # Heartbeat endpoint tests (Sprint 4)
│   ├── test_status_engine.py  # Status engine tests (Sprint 4)
│   ├── test_confidence_engine.py  # Confidence engine tests (Sprint 4)
│   ├── test_uptime_engine.py   # Uptime engine tests (Sprint 4)
│   └── test_quality_engine.py  # Quality engine tests (Sprint 4)
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Frontend Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── __init__.ts
│   │   ├── ui/            # shadcn/ui components
│   │   │   ├── __init__.ts
│   │   │   ├── Badge.tsx      # Badge component (consolidated)
│   │   │   └── StatusBadge.tsx # Server status badge
│   │   ├── servers/       # Server-related components
│   │   │   ├── ServerCard.tsx
│   │   │   └── ServerList.tsx
│   │   └── layout/        # Layout components
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Layout.tsx
│   ├── pages/             # Page components
│   │   ├── __init__.ts
│   │   ├── HomePage.tsx
│   │   ├── ServerPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── __init__.ts
│   │   ├── useServers.ts   # Server data fetching
│   │   └── useClusters.ts # Cluster data fetching
│   ├── lib/               # Utilities and configuration
│   │   ├── api.ts         # API client (standardized error handling)
│   │   ├── dev-auth.ts    # Dev auth utilities (Sprint 1+)
│   │   ├── query-client.ts # TanStack Query client
│   │   └── utils.ts       # General utilities
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts      # Directory server types (matches backend)
│   ├── routes/            # Routing (when router is added)
│   │   └── __init__.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   ├── index.css         # Global styles
│   └── vite-env.d.ts     # Vite environment types
├── components.json        # shadcn/ui configuration
├── package.json
├── package-lock.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── .env.example
├── .gitignore
├── index.html
├── SETUP.md
└── README.md
```

## Key Architectural Decisions

### Backend
- **API-first**: All functionality exposed via REST endpoints
- **Consent-first**: Consent middleware checks before data operations
- **RLS enforcement**: Database queries respect Supabase RLS policies
- **Error handling**: Centralized error handlers with consistent format (HTTP 501 for NotImplemented)
- **Schemas**: Pydantic schemas for all request/response validation
- **Repository pattern**: Abstract interface for data access (mock vs Supabase)
- **Settings pattern**: `get_settings()` with `@lru_cache` (no import-time side effects)
- **Auth contract**: JWKS-based JWT verification with local bypass for dev

### Frontend
- **Thin client**: No business logic in components
- **Data fetching**: TanStack Query for all API calls
- **Type safety**: TypeScript strict mode, shared types matching backend exactly
- **Component organization**: Feature-based folder structure
- **UI components**: shadcn/ui for accessible primitives
- **Dev auth**: Local bypass utilities for development

## Sprint Additions

### Sprint 1 & 2 Additions
- **Directory API** (`api/v1/directory.py`): Public read-only directory endpoints
- **Repository Layer** (`db/directory_repo.py`, `mock_directory_repo.py`, `supabase_directory_repo.py`): Abstract data access
- **Request ID Middleware** (`middleware/request_id.py`): Request correlation
- **Directory Schemas** (`schemas/directory.py`): Complete directory contract with filters, ranking, facets
- **Auth Dependencies** (`core/deps.py`): `get_optional_user()`, `require_user()`
- **JWKS Security** (`core/security.py`): Real JWT verification with JWKS

### Sprint 3 Additions
- **Supabase Directory Repository** (`db/supabase_directory_repo.py`): Full implementation with filtering, ranking, facets
- **Directory View** (`migrations/003_sprint_3_directory_view.sql`): Denormalized read model
- **Indexing Strategy**: Performance indexes for filtering and ranking

### Sprint 4 Additions (Agent Pipeline)
- **Crypto Module** (`core/crypto.py`): Ed25519 signature verification, canonical envelope serialization
- **Heartbeat Utilities** (`core/heartbeat.py`): Grace window resolution
- **Heartbeat Endpoint** (`api/v1/heartbeat.py`): Secure agent heartbeat ingestion with signature verification
- **Heartbeat Repositories**:
  - `db/heartbeat_repo.py` + `supabase_heartbeat_repo.py`: Append-only heartbeat persistence
  - `db/heartbeat_jobs_repo.py` + `supabase_heartbeat_jobs_repo.py`: Durable queue for async processing
  - `db/servers_derived_repo.py` + `supabase_servers_derived_repo.py`: Derived state updates
- **Engines** (`engines/`): Python-based computation engines
  - `status_engine.py`: Effective status (online/offline/unknown)
  - `confidence_engine.py`: RYG confidence (green/yellow/red)
  - `uptime_engine.py`: 24h rolling window uptime percentage
  - `quality_engine.py`: Quality score (0-100)
- **Worker** (`workers/heartbeat_worker.py`): Durable background worker for heartbeat processing
- **Database Migration** (`migrations/006_sprint_4_agent_auth.sql`): Agent auth fields, heartbeat_jobs table, indexes
- **Error Types** (`core/errors.py`): SignatureVerificationError, KeyVersionMismatchError, HeartbeatReplayError
- **Test Suite**: Comprehensive tests for crypto, engines, and endpoint

### New Frontend Components (Sprint 1+)
- **Directory Types** (`types/index.ts`): Complete TypeScript types matching backend
- **Dev Auth** (`lib/dev-auth.ts`): Local development auth bypass
- **API Client** (`lib/api.ts`): Standardized error handling, JWT attachment
- **Server Components** (`components/servers/`): ServerCard, ServerList
- **UI Components** (`components/ui/`): Badge, StatusBadge

### Removed Components
- `components/badges/Badge.tsx` - Consolidated into `components/ui/Badge.tsx`
- `components/verification/VerificationBadge.tsx` - Removed (functionality in Badge component)

## Development Workflow

1. **Database**: Create migrations in Supabase Dashboard
2. **Backend**: Update schemas, implement endpoints, add tests
3. **Frontend**: Create components, add hooks, implement UI
4. **Integration**: Connect frontend to backend APIs

## Current Status

**Sprint 1 Complete:**
- Authentication backbone (JWKS, local bypass)
- Directory read contract locked
- Frontend-backend handshake
- Production guardrails
- Smoke tests

**Sprint 2 Complete:**
- Full filter & ranking vocabulary accepted
- Facets endpoint
- Supabase read model introduced (stubbed)
- Type safety improvements
- Contract alignment frontend/backend

**Sprint 3 Complete:**
- Supabase SQL implementation (`directory_view`)
- Real filtering and ranking
- Indexes and performance optimization
- `SupabaseDirectoryRepository` fully implemented
- Sample data and validation scripts

**Sprint 4 Complete:**
- Agent heartbeat pipeline with Ed25519 signature verification
- Durable worker for async heartbeat processing
- Derived state engines (status, confidence, uptime, quality)
- Replay protection via `UNIQUE(server_id, heartbeat_id)`
- Row-level job claiming for multi-worker safety
- Production hardening (crypto whitelist, timestamp normalization, etc.)
- FastAPI lifespan handler (replaces deprecated on_event)
- CI workflow with test environment setup
- Comprehensive test suite (26 tests passing)

**Sprint 4 Cleanup Complete:**
- Security: Removed .env from git tracking, updated .gitignore
- Durable queue: Fixed stuck claims (clear claimed_at on success/failure)
- Stale claim reclaim: Added TTL-based reclaim for crashed workers
- Rate limiting: Removed auto-enable in production
- Worker startup: Prevented worker startup during tests
- Heartbeat endpoint: Refactored to use repositories only (fully testable)
- Tests: Replaced stub tests with real hermetic tests
- CI: Updated for test environment gating

**Sprint 5–7 Complete:**
- Directory ranking, quality score, facets; maps table; Discord/website URLs
- Trust pages (Verification, Consent, Legal, Data Rights, Contact, Terms, About, FAQ)
- SpotlightCarousel (selection locked, wrap-around); TekCardSurface; server CRUD + favorites
- Status vs design and what's left: docs/REMAINING_VS_DESIGN.md; docs/TODO.md is the active backlog

**Current focus:** See docs/TODO.md and docs/WORKING_DOCS.md.
