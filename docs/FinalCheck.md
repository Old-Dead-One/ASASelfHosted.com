# Final Check — Ready to Deploy

Use this checklist before deploying to production.

**For a single Must/Should/Optional list for closed-group testing**, see **[docs/RELEASE_READINESS.md](RELEASE_READINESS.md)**.

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
- [ ] **Monitoring mode UI** — Verify "manual monitoring" vs "local agent (heartbeat)" is wired correctly: if status is not being updated by heartbeats, treat it as manually monitored and reflect this on the Server page "Monitoring" card.
- [ ] **Breadcrumb navigation** — Add a breadcrumb (path-based navigation) at the top of every page, above the page title.
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

## Sprint 9 completion (pre-launch log)

As of Sprint 9 the following are implemented and aligned with policy:

- **Contact:** Contact page uses mailto/support email; handling flow in **docs/OPERATIONS.md** §7.
- **Per-user limits:** MAX_SERVERS_PER_USER enforced in backend; dashboard shows "X of Y servers" and disables Add Server at limit; 403 `server_limit_reached` on create when at limit.
- **Data rights:** Account deletion is documented as "by request" (manual process) in **docs/OPERATIONS.md** §8; Data Rights and Privacy Policy state "by request" and link to Contact.
- **Key generation:** Dashboard "Agent verification setup" lists clusters and offers Generate/Rotate key; private key shown once with copy and warning.
- **Dashboard hub:** Favorites section (list + unfavorite); "Privacy & Consent (In-Game)" placeholder with link to Consent page; advanced controls marked "Coming soon."
- **Ranking:** **docs/RANKING.md** is canonical; backend and frontend conform (sort labels, NULLs last, no false "Rank #N" when null).
- **Trust audit:** Consent, Verification, Privacy, Data Rights pages audited; no claims that imply automatic collection, retroactive data, or server-side enablement without consent.

**Known gaps / Phase 1.5 (out of scope for Sprint 9):** Server image uploads, cluster-scoped UX, local agent binary, multi-select ruleset filters, full account settings UI, auto map creation on server add. See **docs/TODO.md**.

**Exceptions:** FinalCheck items that require production (env, DB, email verification, CORS, rate limiting, monitoring) must be verified at deploy time; mark each done or document exceptions when you run the checklist.

---

## Open development work (before or after deploy)

Remaining development tasks (e.g. server card image, optional features) are tracked in **docs/TODO.md**. Per-user limits and contact handling are implemented as of Sprint 9. Before launch, confirm any remaining items required for your release; then run the pre-deploy checklist above.

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


