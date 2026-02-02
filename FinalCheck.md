# Final Check — Ready to Deploy

Use this checklist before deploying to production.

---

## Pre-deploy checklist

- [ ] **Environment variables** — All required vars set in production (Supabase URL, service_role, anon key, JWT issuer/JWKS, CORS origins, etc.). No secrets in repo.
- [ ] **Database** — All migrations applied in production Supabase. Security advisories addressed (e.g. 018, 020) if applicable.
- [ ] **Auth** — Supabase Auth configured (email/password, redirect URLs). HaveIBeenPwned optional (Pro plan).
- [ ] **Builds** — Backend and frontend build and start without errors. Tests pass.
- [ ] **CORS** — Backend allows production frontend origin(s) only.
- [ ] **Rate limiting / abuse** — Consider rate limits on auth and directory endpoints if not already in place.
- [ ] **Monitoring** — Sentry or equivalent configured (optional but recommended).
- [ ] **Docs** — README, INSTALL, SUPABASE_SETUP, and env examples are up to date.

---

## TODO before or soon after deploy

### Per-user limits (servers and clusters)

- [ ] **Server limit per user** — Add a limit on how many servers one user can create (e.g. max N servers per owner). Enforce in backend on create; optionally surface in UI.
- [ ] **Cluster limit per user** — Add a limit on how many clusters one user can create (e.g. max N clusters per owner). Enforce in backend on create; optionally surface in UI.

Define limits (e.g. 10 servers, 5 clusters) and document in DECISIONS or config. Consider making limits configurable via env.

---

## Post-deploy

- [ ] Smoke test: health, login, directory list, create/edit server (if auth works).
- [ ] Verify Supabase logs and app logs for errors.
- [ ] Confirm backups and retention for Supabase (if enabled).
