# Phase 0-2 Verification Checklist

## ✅ Completed Setup

### Backend
- ✅ FastAPI app structure with `create_app()` function
- ✅ Settings configured with `ENV` (not `ENVIRONMENT`)
- ✅ CORS configured via environment variables
- ✅ Sentry initialization (if DSN provided)
- ✅ Error handlers configured
- ✅ Health endpoints: `/health` and `/api/v1/health`
- ✅ API v1 router mounted
- ✅ All domain routers scaffolded

### Frontend
- ✅ Vite + React + TypeScript configured
- ✅ TanStack Query provider at root
- ✅ Tailwind CSS configured
- ✅ API client with error handling
- ✅ Sentry initialization (if DSN provided)
- ✅ Health check test in App component

### Configuration Files
- ✅ `backend/requirements.txt` - All primary dependencies listed
- ✅ `frontend/package.json` - All primary dependencies listed
- ✅ TypeScript strict mode enabled
- ✅ ESLint configured

## 📝 Environment Files Needed

### `backend/.env.example` (create manually)
```env
# Environment
ENV=local

# API
API_V1_PREFIX=/api/v1

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:5173

# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Sentry (optional)
SENTRY_DSN=
```

### `frontend/.env.example` (create manually)
```env
# API Base URL
VITE_API_BASE_URL=http://localhost:5173

# Sentry (optional)
VITE_SENTRY_DSN=
```

## 🧪 Verification Steps

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # mac/linux
# .venv\Scripts\activate    # windows
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Create Backend .env
```bash
cd backend
cp .env.example .env
# Edit .env if needed (defaults should work for local dev)
```

### 3. Start Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 5173
```

**Expected:** Server starts on `http://localhost:5173`

**Test:**
- `http://localhost:5173/health` → `{"status": "ok"}`
- `http://localhost:5173/api/v1/health` → `{"status": "ok", "api": "v1"}`
- `http://localhost:5173/docs` → Swagger UI (if ENV != production)

### 4. Frontend Setup
```bash
cd frontend
npm install
```

### 5. Create Frontend .env
```bash
cd frontend
cp .env.example .env
# Edit .env if needed (defaults should work)
```

### 6. Start Frontend
```bash
cd frontend
npm run dev
```

**Expected:** App loads on `http://localhost:5173` with no console errors

**Test:**
- App displays "ASASelfHosted.com" heading
- Health status shows "✅ ok" (indicating successful API call to `/health`)

## ✅ Acceptance Criteria

- [ ] Backend runs: `uvicorn app.main:app --reload --port 5173`
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `GET /api/v1/health` returns `{"status": "ok", "api": "v1"}`
- [ ] Frontend runs: `npm run dev`
- [ ] App loads with no console errors
- [ ] Frontend successfully calls `GET /health` and displays status

## 🔧 If Something Fails

### Backend Issues
- Check Python version (3.11+ recommended)
- Verify virtual environment is activated
- Check that all dependencies installed: `pip list`
- Verify `.env` file exists (can be empty for local dev)

### Frontend Issues
- Check Node version (18+ recommended)
- Verify all dependencies installed: `npm list`
- Check browser console for errors
- Verify `.env` file exists with `VITE_API_BASE_URL`

### CORS Issues
- Verify `CORS_ORIGINS` in backend `.env` includes `http://localhost:5173`
- Check browser network tab for CORS errors

## 📦 Dependencies Installed

### Backend
- fastapi
- uvicorn[standard]
- pydantic
- pydantic-settings
- python-dotenv
- httpx
- supabase
- sentry-sdk[fastapi]

### Frontend
- react, react-dom
- @tanstack/react-query
- react-hook-form
- zod
- @hookform/resolvers
- @radix-ui/react-slot
- clsx, tailwind-merge
- tailwindcss, postcss, autoprefixer
- @sentry/react

## 🎯 Next Steps (After Verification)

Once both servers run successfully:

1. **API Contract Draft** - Define server/cluster/heartbeat schemas
2. **Supabase Schema** - Design tables + RLS policies
3. **Auth Wiring** - Supabase Auth integration
4. **Server Directory MVP** - Basic listing pages
5. **Verification System** - Cryptographic verification
6. **Consent UX** - Dual-consent model implementation
