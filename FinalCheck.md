# Final Check — Ready to Deploy

Use this checklist before deploying to production.

---

## Pre-deploy checklist

- [ ] **Environment variables** — All required vars set in production (Supabase URL, service_role, anon key, JWT issuer/JWKS, CORS origins, etc.). No secrets in repo.
- [ ] **Database** — All migrations applied in production Supabase. Security advisories addressed (e.g. 018, 020) if applicable.
- [ ] **Auth** — Supabase Auth configured (email/password, redirect URLs). HaveIBeenPwned optional (Pro plan).
- [ ] **Email verification** — If using email confirmation: configure SMTP in Supabase (SendGrid, Mailgun, SES, etc.) for production; for dev, either disable “Enable email confirmations” in Supabase Auth settings or manually verify users in Dashboard. See INSTALL/SUPABASE_SETUP if needed.
- [ ] **Builds** — Backend and frontend build and start without errors. Tests pass.
- [ ] **CORS** — Backend allows production frontend origin(s) only.
- [ ] **Rate limiting / abuse** — Consider rate limits on auth and directory endpoints if not already in place.
- [ ] **Monitoring** — Sentry or equivalent configured (optional but recommended).
- [ ] **Docs** — README, INSTALL, SUPABASE_SETUP, and env examples are up to date. Trust pages content and acceptance criteria: **docs/TRUST_PAGES.md**.

---

## Trust pages (Sprint 7)

Before deploy, confirm:

- [ ] Trust pages (/verification, /consent) are live
- [ ] Trust pages linked from footer (and optionally About)
- [ ] Trust page claims audited against code
- [ ] No “future” language present

Full spec: **docs/TRUST_PAGES.md**.

---

## Open development work (before or after deploy)

Development tasks (per-user limits, server card image, contact/email wiring) are tracked in **SPRINT_8_TODO.md**. Before launch, confirm whether any of these are required for your release; if so, implement per that backlog and then run the pre-deploy checklist above.

---

## Post-deploy

- [ ] Smoke test: health, login, directory list, create/edit server (if auth works).
- [ ] Verify Supabase logs and app logs for errors.
- [ ] Confirm backups and retention for Supabase (if enabled).

---

## Closing Note

These pages are not about convincing users to trust you.

They are about making it **technically impossible** to lie to them.

If these pages feel overly explicit, that is intentional.


