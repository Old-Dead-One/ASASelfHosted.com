# Project Structure

Complete file and folder structure for ASASelfHosted.com development.

## Root Level Files

```
asaselfhosted.com/
├── backend/              # FastAPI backend
├── frontend/            # React frontend
├── DEV_NOTES.md          # Development notes and context
├── INSTALL.md            # Installation instructions
├── PROJECT_STRUCTURE.md  # This file
├── README.md             # Project overview
├── VERIFICATION.md       # Setup verification checklist
├── DESCRIPTION.txt       # Project description (if exists)
└── FEATURE_LIST.txt      # Feature list (if exists)
```

## Backend Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # Main v1 router (includes all domain routers)
│   │       ├── servers.py       # Server CRUD endpoints
│   │       ├── clusters.py     # Cluster endpoints
│   │       ├── verification.py # Verification endpoints
│   │       ├── heartbeat.py    # Heartbeat ingestion
│   │       ├── consent.py      # Consent management
│   │       ├── subscriptions.py # Subscription management
│   │       └── webhooks.py     # Stripe webhooks
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Settings (env vars)
│   │   ├── errors.py          # Error handling
│   │   └── supabase.py        # Supabase client
│   ├── middleware/            # Request middleware
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication middleware
│   │   └── consent.py       # Consent checking middleware
│   ├── schemas/              # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── base.py          # Base schemas
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
│   ├── db/                 # Database utilities
│   │   ├── __init__.py
│   │   ├── queries.py     # Database query helpers
│   │   └── migrations/     # Migration references
│   └── main.py            # FastAPI app entry point
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
│   │   ├── ui/            # shadcn/ui components (to be installed)
│   │   ├── servers/       # Server-related components
│   │   │   ├── ServerCard.tsx
│   │   │   └── ServerList.tsx
│   │   ├── verification/ # Verification components
│   │   │   └── VerificationBadge.tsx
│   │   ├── badges/        # Badge components
│   │   │   └── Badge.tsx
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
│   │   ├── useServers.ts
│   │   └── useClusters.ts
│   ├── lib/               # Utilities and configuration
│   │   ├── api.ts        # API client
│   │   ├── query-client.ts # TanStack Query client
│   │   └── utils.ts      # General utilities
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── routes/            # Routing (when router is added)
│   │   └── __init__.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   ├── index.css         # Global styles
│   └── vite-env.d.ts     # Vite environment types
├── components.json        # shadcn/ui configuration
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── .eslintrc.cjs
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
- **Error handling**: Centralized error handlers with consistent format
- **Schemas**: Pydantic schemas for all request/response validation

### Frontend
- **Thin client**: No business logic in components
- **Data fetching**: TanStack Query for all API calls
- **Type safety**: TypeScript strict mode, shared types
- **Component organization**: Feature-based folder structure
- **UI components**: shadcn/ui for accessible primitives

## Development Workflow

1. **Database**: Create migrations in Supabase Dashboard
2. **Backend**: Update schemas, implement endpoints, add tests
3. **Frontend**: Create components, add hooks, implement UI
4. **Integration**: Connect frontend to backend APIs

## Next Steps

1. Set up Supabase project and configure environment variables
2. Create database schema with RLS policies
3. Implement authentication flow
4. Build out server listing functionality
5. Add verification system
6. Implement consent management
