# Project Structure

Complete file and folder structure for ASASelfHosted.com development.

**Last Updated:** After Sprint 2 completion

## Root Level Files

```
asaselfhosted.com/
├── backend/              # FastAPI backend
├── frontend/            # React frontend
├── 1_DESCRIPTION.txt     # Project description
├── 2_FEATURE_LIST.txt    # Feature list (definitive MVP scope)
├── 3_TECH_STACK.txt      # Technology stack
├── 4_Dev_Plan.txt        # Development plan
├── DECISIONS.md          # Official decisions (override design docs)
├── DEV_NOTES.md          # Development notes and context
├── GIT_SETUP.md          # Git setup and workflow
├── INSTALL.md            # Installation instructions
├── PROJECT_STRUCTURE.md  # This file
├── README.md             # Project overview
├── SPRINT_1_COMPLETION_CHECKLIST.md  # Sprint 1 completion tracking
├── SPRINT_ONE_PLAYBOOK.txt           # Sprint 1 playbook
├── SPRINT_TWO_PLAYBOOK.md            # Sprint 2 playbook
└── VERIFICATION.md       # Setup verification checklist
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
│   │       ├── heartbeat.py    # Heartbeat ingestion
│   │       ├── consent.py      # Consent management
│   │       ├── subscriptions.py # Subscription management
│   │       └── webhooks.py     # Stripe webhooks
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Settings (env vars, get_settings pattern)
│   │   ├── deps.py            # FastAPI dependencies (auth, user identity)
│   │   ├── errors.py          # Error handling (centralized API errors)
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
│   │   ├── heartbeat.py     # Heartbeat schemas
│   │   ├── consent.py       # Consent schemas
│   │   └── subscriptions.py # Subscription schemas
│   ├── models/              # Domain models (reference only)
│   │   ├── __init__.py
│   │   └── domain.py       # Domain type definitions
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── crypto.py      # Cryptographic utilities
│   │   └── stripe.py       # Stripe utilities
│   ├── db/                 # Database layer (Sprint 1+)
│   │   ├── __init__.py
│   │   ├── directory_repo.py      # Directory repository interface
│   │   ├── mock_directory_repo.py # Mock implementation (Sprint 1)
│   │   ├── supabase_directory_repo.py # Supabase implementation (Sprint 2+)
│   │   ├── providers.py           # Repository provider (DI)
│   │   ├── queries.py            # Database query helpers
│   │   └── migrations/            # Migration references
│   └── main.py            # FastAPI app entry point
├── tests/                 # Test suite (Sprint 1+)
│   ├── __init__.py
│   └── test_auth_contract.py  # Auth contract smoke tests
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
│   │   ├── utils.ts       # General utilities
│   │   └── tokens.md      # Token documentation
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

## Sprint 1 & 2 Additions

### New Backend Components (Sprint 1+)
- **Directory API** (`api/v1/directory.py`): Public read-only directory endpoints
- **Repository Layer** (`db/directory_repo.py`, `mock_directory_repo.py`, `supabase_directory_repo.py`): Abstract data access
- **Request ID Middleware** (`middleware/request_id.py`): Request correlation
- **Directory Schemas** (`schemas/directory.py`): Complete directory contract with filters, ranking, facets
- **Auth Dependencies** (`core/deps.py`): `get_optional_user()`, `require_user()`
- **JWKS Security** (`core/security.py`): Real JWT verification with JWKS

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

**Ready for Sprint 3:**
- Supabase SQL implementation
- Real filtering and ranking
- Indexes and performance optimization
