# Installation Guide

## Quick Start (Without Sentry)

Both frontend and backend are configured to work **without Sentry** installed. Sentry is optional and can be added later when you're ready to set up monitoring.

### Backend Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # mac/linux
# .venv\Scripts\activate    # windows

pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv httpx supabase
```

**Note:** `sentry-sdk` is commented out in `requirements.txt`. Uncomment it when you're ready to add monitoring.

### Frontend Installation

```bash
cd frontend
npm install
```

**Note:** `@sentry/react` is not in `package.json` by default. Add it when you're ready:
```bash
npm install @sentry/react
```

## With Sentry (Optional)

If you want to enable Sentry monitoring:

### Backend
1. Uncomment the `sentry-sdk[fastapi]` line in `backend/requirements.txt`
2. Install: `pip install sentry-sdk[fastapi]`
3. Add `SENTRY_DSN=your_dsn_here` to `backend/.env`

### Frontend
1. Install: `npm install @sentry/react`
2. Add `VITE_SENTRY_DSN=your_dsn_here` to `frontend/.env`

The app will automatically initialize Sentry if the DSN is provided and the package is installed.

## Verification

After installation, verify everything works:

**Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 5173
```
Test: `http://localhost:5173/health` → `{"status": "ok"}`

**Frontend:**
```bash
cd frontend
npm run dev
```
Test: App loads and shows API health status
