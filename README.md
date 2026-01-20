# ASASelfHosted.com

Production-grade web platform for a vendor-neutral public registry of self-hosted Ark: Survival Ascended (ASA) servers and clusters.

## Core Mission

- Reliable discovery of non-Nitrado ASA servers
- Trust via cryptographic verification, not reputation or payment
- Free public directory forever
- Optional automation via local server agent/plugin, never remote control

## Architecture Principles

- **API-first**: All functionality exposed via REST API
- **Consent-first**: No data collection without explicit consent
- **Least privilege**: Row Level Security (RLS) enforces permissions
- **Supabase as source of truth**: Auth, database, and permissions
- **Frontend is thin client**: Zero business logic in React components
- **Backend enforces rules**: Not UI

## Tech Stack

### Frontend
- React + TypeScript
- Vite (build + dev)
- Tailwind CSS
- Radix UI (headless accessibility primitives)
- shadcn/ui (locally owned components)
- TanStack Query (data fetching, caching)
- React Hook Form
- Zod (schema + validation)

### Backend
- Python
- FastAPI
- Pydantic

### Data & Auth
- Supabase Postgres
- Supabase Auth (email-based only)
- Row Level Security (RLS) — mandatory on all tables

### Payments
- Stripe (subscriptions, license keys, webhooks)

### Monitoring
- Sentry (frontend + backend)

## Project Structure

```
asaselfhosted.com/
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── lib/      # Utilities, API client, query client
│   │   └── App.tsx   # Main application component
│   └── package.json
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Configuration, errors, Supabase client
│   │   ├── schemas/  # Pydantic schemas
│   │   └── models/   # Domain models (reference only)
│   └── requirements.txt
└── README.md
```

## Getting Started

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (see `.env.example`):
```bash
VITE_API_BASE_URL=http://localhost:5173
```

4. Start development server:
```bash
npm run dev
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (see `.env.example`):
```bash
ENVIRONMENT=development
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
# ... see .env.example for all variables
```

5. Start development server:
```bash
uvicorn app.main:app --reload --port 5173
```

## Development Principles

1. **No business logic in React components** — All logic in API or shared utilities
2. **No silent data collection** — Explicit consent required for all data
3. **Consistent error handling** — All errors follow standard format
4. **Type safety** — TypeScript strict mode, Pydantic validation
5. **Documentation** — Comments explain decisions affecting trust, consent, or security

## API Contract

All API responses follow a consistent format:

**Success:**
```json
{
  "data": { ... }
}
```

**Error:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }  // Optional
  }
}
```

## Documentation

- `DEV_NOTES.md` - Development notes, decisions, and context (referenced during development)
- `PROJECT_STRUCTURE.md` - Complete file and folder structure
- `VERIFICATION.md` - Setup and verification checklist
- `INSTALL.md` - Installation instructions

## License

[To be determined]
