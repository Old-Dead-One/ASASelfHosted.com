# ASASelfHosted.com Backend

Production-grade FastAPI backend for the ASASelfHosted.com platform.

## Architecture Principles

- **API-first**: All functionality exposed via REST API
- **Consent-first**: No data collection without explicit consent
- **Least privilege**: RLS policies enforce permissions, not application code
- **Supabase as source of truth**: Auth, database, and permissions

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with required variables:
```bash
ENVIRONMENT=development
DEBUG=true

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Sentry (optional)
SENTRY_DSN=your_sentry_dsn

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

4. Run the development server:
```bash
uvicorn app.main:app --reload --port 5173
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   │   └── v1/        # API v1 routes
│   ├── core/          # Core configuration and utilities
│   │   ├── config.py  # Settings and environment variables
│   │   ├── errors.py  # Error handling and exception classes
│   │   └── supabase.py # Supabase client
│   ├── schemas/       # Pydantic schemas for validation
│   ├── models/        # Domain models (reference only)
│   └── main.py        # FastAPI application entry point
├── requirements.txt
└── README.md
```

## API Contract Style

All API responses follow a consistent format:

**Success responses:**
```json
{
  "data": { ... }
}
```

**Error responses:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }  // Optional, for validation errors
  }
}
```

## Error Handling

All errors are handled centrally in `app/core/errors.py`:
- `APIError`: Base exception for all API errors
- `ValidationError`: Request validation failed
- `NotFoundError`: Resource not found
- `UnauthorizedError`: Authentication required
- `ForbiddenError`: Permission denied
- `ConsentError`: Consent required or revoked

## Environment Variables

All configuration is loaded from environment variables via Pydantic Settings.
Required variables will raise `ValidationError` at startup if missing.

See `app/core/config.py` for all available settings.
