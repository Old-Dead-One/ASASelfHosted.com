# Release Readiness — Initial Release (Closed-Group Testing)

Single list for taking the site to **closed-group testing** before public launch.  
**Must do** = required to be safe and usable. **Should do** = strongly recommended. **Optional** = nice to have.

**Principle:** User trust is non-negotiable. Users must have a clear way to delete their account and all of their data. We do not abuse user trust.

**References:** [FinalCheck.md](FinalCheck.md), [TODO.md](TODO.md), [REMAINING_VS_DESIGN.md](REMAINING_VS_DESIGN.md).

---

## Must do (required for initial release)

These must be done before any closed group uses the site. Without them the site is broken, unsafe, or misrepresents what it does.

### Environment and deployment

- [ ] **Environment variables** — All required vars set for the target environment (Supabase URL, keys, JWT issuer/JWKS, CORS origins). No secrets in repo. See backend `.env.example` and [INSTALL.md](../INSTALL.md).
- [ ] **Database** — All migrations applied in the target Supabase project. Any security advisories (e.g. migrations 018, 020) addressed.
- [ ] **Builds** — Backend and frontend build and start without errors. Tests pass (`backend/tests`, frontend tests).
- [ ] **CORS** — Backend allows the frontend origin(s) testers will use (e.g. staging URL or production URL).

### Auth and core flows

- [ ] **Auth** — Supabase Auth configured (email/password, redirect URLs). Sign up, login, and password reset work.
- [ ] **Email verification** — If you use “confirm email”: SMTP configured in Supabase for the deploy environment, or “Enable email confirmations” disabled and testers verified manually. See [SUPABASE_SETUP.md](../SUPABASE_SETUP.md).

### Trust and policy (legal / honesty)

- [ ] **Trust pages live** — `/verification` and `/consent` are live and linked from footer (and optionally About).
- [ ] **Trust page claims** — Content matches actual behavior. No “future” or unshipped promises. Audit against [TRUST_PAGES.md](TRUST_PAGES.md) (including Audit section).
- [ ] **Contact path** — Contact page works (mailto and/or support email). “Contact us” links (Privacy, Data Rights, footer) resolve correctly. Handling documented in [OPERATIONS.md](OPERATIONS.md) §7.
- [ ] **Account deletion** — Self-service “Delete my account” on Data Rights page: permanent, irreversible; user must confirm before deletion. Backend `DELETE /api/v1/me` with timeout so the request does not hang. See [OPERATIONS.md](OPERATIONS.md) §8.
- [ ] **Data rights** — Privacy Policy and Data Rights page describe account deletion (self-service, permanent) and link to Data Rights page. Process and retention in [OPERATIONS.md](OPERATIONS.md) §8.

### Already done (Sprint 9 — verify if desired)

- **Per-user server limit** — Enforced in API; dashboard shows “X of Y servers” and disables Add Server at limit.
- **Key generation** — Dashboard “Agent verification setup”: generate/rotate keys; private key shown once with copy and warning.
- **Dashboard hub** — Favorites section; “Privacy & Consent (In-Game)” placeholder with link to Consent page.
- **Ranking** — [RANKING.md](RANKING.md) is canonical; backend/frontend conform (no false “Rank #N” when null).

### Smoke test

- [ ] **Smoke test** — Health check, login, directory list, create/edit/delete server (as owner), favorites, filters. Password/join info hidden when logged out. No critical errors in console or logs.

---

## Should do (strongly recommended before or during closed group)

Improve stability, security, and quality of feedback without blocking “go live” for testers.

### Security and abuse

- [ ] **Rate limiting** — Rate limits on auth (login/signup) and/or directory/heartbeat endpoints so abuse is limited. Confirm production/staging config.
- [ ] **Cluster limit (optional)** — If you want to cap clusters per user like servers, add `MAX_CLUSTERS_PER_USER` and enforce; otherwise document “no limit yet.”

### Testing and docs

- [ ] **Pre-launch testing pass** — Run through: create/edit/delete server, favorites, directory filters, Spotlight carousel, password visibility, trust pages. Log any bugs in [TODO.md](TODO.md).
- [ ] **Trust claims audit** — Verification and Consent pages vs [TRUST_PAGES.md](TRUST_PAGES.md) and code; fix any contradictions.
- [ ] **Docs up to date** — README, INSTALL, SUPABASE_SETUP, `.env.example` reflect how to run and deploy. Trust pages spec in TRUST_PAGES.md is current.

### Operational readiness

- [ ] **Backups** — Supabase backups enabled and retention understood (see [OPERATIONS.md](OPERATIONS.md) §8).
- [ ] **Post-deploy check** — After first deploy: smoke test again on live URL; spot-check Supabase and app logs for errors.

---

## Optional (nice to have for initial release)

Can be deferred until after closed-group feedback or until public launch.

- **Monitoring** — Sentry (or equivalent) for errors and performance.
- **Account settings page** — Profile, email/password change (deletion path is in Must do above).
- **Dashboard row view** — Already implemented; no action unless you want to change it.
- **Directory row view sortable** — Click column headers to sort (name, status, players, etc.).
- **Ruleset multi-select** — Multiple ruleset values in directory filter.
- **Server images** — Banner upload and card background per [SERVER_IMAGES.md](SERVER_IMAGES.md) (Phase 1.5 acceptable).
- **Maps: auto-add custom map** — When user enters a map name not in `maps`, insert it (backend policy TBD).
- **Owner diagnostics** — “Last N heartbeats/errors” per server (mentioned in design; not required for closed group).
- **Local agent binary** — .exe and local UI for heartbeat (backend ready; testers can use API or wait for plugin).

---

## Phase 1.5+ (explicitly out of scope for initial release)

Do not block closed-group testing on these. Plan for after feedback or public launch.

- Cluster pages and cluster-scoped UX
- Server image uploads and moderation
- Top 100 / Hot / Stability / Activity carousels (beyond Spotlight)
- Additional badges (Hot, Long-Runner, cluster badges)
- Password sync from agent, auto-favorite onJoin
- Player directory expansion
- Subscription/payments UI
- ASA Server API plugin (post-MVP per [DECISIONS.md](DECISIONS.md))
- Discord bot, platform status page (/status)

---

## Quick checklist (print-friendly)

**Must:** Env → DB → Builds → CORS → Auth → Email verification → Trust pages live & accurate → Contact path → **Account deletion (clear path or self-service)** → Data rights wording → Smoke test.  
**Should:** Rate limiting → Pre-launch test pass → Trust audit → Docs updated → Backups → Post-deploy check.  
**Optional:** Monitoring, account settings link, sortable row view, multi-select ruleset, server images, etc.

---

*Last updated: 2026-02-03*
