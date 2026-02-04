# What’s Left vs Design Docs

Consolidated list of remaining work when comparing the current codebase to the original design docs and to implied/added features. Sprint 9 (contact, limits, key UI, favorites on dashboard, privacy placeholder, ranking doc, data rights) is complete; items below are still open.

**References:** `docs/design/` (1_DESCRIPTION, 2_FEATURE_LIST, 3_TECH_STACK, 4_Dev_Plan, 5_Appendix), `docs/TODO.md`.

---

## 1. From original numbered design docs (not done)

### 1.1 Feature list (2_FEATURE_LIST)

| Item | Status | Note |
|------|--------|------|
| **Subscription management** | Not done | Subscription plumbing stubbed (tables/endpoints); no checkout or management UI. Design: “Subscription management” under Subscription Logic. |
| **Pricing page** | Not done | Optional in dev plan; not built. Could stub or add simple “Pricing” (e.g. /pricing). |
| **Banner carousels beyond Newbie** | Not done | Design: Top 100, Stability, Activity, Hot, Newbie Servers, etc. We have one carousel (Spotlight). Rest = Phase 1.5. |
| **Player directory** | Not done | Player profiles, favorited clusters, activity indicators, optional public visibility, auto-favorite onJoin. Phase 1.5+. |
| **Cluster badges** | Partial | Verified Cluster, Full Map Coverage, Stable Cluster, Growing, etc. Some cluster data exists; badge logic/UI not fully built. |
| **Player badges** | Not done | Verified Player, Active, Cluster Loyalist, Founder, etc. Phase 2 / consent-bound. |
| **Discord bot** | Not done | Free bot (status embed, manual/wipe announcements); Verified+ bot (auto sync, activity). Post-MVP in design. |
| **Plugin automation (beyond heartbeat)** | Not done | Auto wipe reporting, auto mod hash, auto password sync, auto-favorite onJoin. Phase 1.5+ or plugin-side. |

### 1.2 Dev plan (4_Dev_Plan)

| Item | Status | Note |
|------|--------|------|
| **Local host agent client** | Not done | Node/TS or Python agent: local UI, instance table, R/Y/G lights, “Test now”, logs; process/port checks; heartbeat every 300s; Windows .exe packaging, “Run at startup”. Backend heartbeat ready; agent binary deferred. |
| **Owner diagnostics panel** | Not done | “Last 20 heartbeats/errors” per server. Mentioned Sprint 3; not implemented. |
| **Agent install / troubleshooting docs** | Partial | Dashboard has minimal “how to” copy; no dedicated install doc or troubleshooting page. |
| **Platform status page (/status)** | Not done | Optional post-MVP in dev plan for uptime/service status. |
| **Stabilization: rate limits on heartbeat** | Partial | Rate limiting scaffold exists; confirm production config. |
| **Packaging agent into .exe** | Not done | Tied to local agent client. |

### 1.3 Tech stack / appendix (3_TECH_STACK, 5_Appendix)

| Item | Status | Note |
|------|--------|------|
| **Supabase Storage (logos/banners)** | Not done | Post-MVP in design; server images spec in SERVER_IMAGES.md. |
| **Stripe (or alternative) payments** | Not done | Stack mentions Stripe; research small-fee alternatives. Subscription checkout not built. |
| **Cluster pages** | Not done | 5_Appendix D.4.2: member server aggregation, map coverage, cluster-level verification, aggregate uptime. Phase 1.5. |
| **Player profile pages (consent-bound)** | Not done | 5_Appendix D.4.3: opt-in profiles, favorites, badges, activity. Phase 1.5+. |

---

## 2. Implied or added features (partially started or in backlog)

### 2.1 From TODO.md (still open after Sprint 9)

| Item | Status | Note |
|------|--------|------|
| **Ruleset filter – multiple values** | Open | Single-select today; multi-select (vanilla/vanilla_qol/modded/boosted rules) and backend alignment. |
| **Directory row view – sortable table** | Open | Click column headers to sort (e.g. name, status, players, quality, updated). |
| **Server images (banner)** | Open | Spec: docs/SERVER_IMAGES.md. Backend: image_path, storage, report; frontend: upload/crop, card background; admin: approve/reject. |
| **Dashboard row view** | Open | Owner server list as table/row view in addition to card carousel; switch like directory. |
| **Maps table – auto-add custom map** | Open | When user enters custom map name not in `maps`, insert (backend or endpoint); policy: who can add, validation. |
| **Cluster pages / cluster-scoped UX** | Open | Cluster as first-class routes/UI; cluster metadata (name, slug, visibility); owner flows. Schema exists; UI/product logic. |
| **Account settings page** | Open | Profile, email change, password change, account deletion entry point (deletion is “by request” and documented; no self-serve settings UI). |
| **Cluster limit per user** | Open | Optional; MAX_CLUSTERS_PER_USER enforce + optional UI (like server limit). |
| **Agent instance management** | Open | Backend: create/list instances, link to servers (if we adopt instance model). Key generation UI done; instance CRUD not. |
| **Pre-launch testing & trust audit** | Open | Run checklist: create/edit/delete server, favorites, filters, Spotlight, password gating; trust pages vs TRUST_PAGES.md. |

### 2.2 Phase 1.5 (post-launch, from design + TODO)

| Item | Note |
|------|------|
| Cluster pages | Read-only or owner management. |
| Top 100 / Hot / Stability / Activity carousels | Beyond Spotlight. |
| Additional badges | Hot, Long-Runner, cluster badges. |
| Password sync | Auto from agent/plugin. |
| Auto-favorite onJoin | Plugin-assisted. |
| Player directory expansion | Profiles, favorited clusters, activity. |

### 2.3 Done in Sprint 9 (no longer “left”)

- Contact (mailto + OPERATIONS.md §7).
- Per-user server limit (14, enforced, UI).
- Key generation & rotation UI on dashboard.
- Favorites section on dashboard.
- Privacy & Consent (In-Game) placeholder.
- RANKING.md canonical + backend/frontend alignment.
- Data rights / account deletion documented (by request).

---

## 3. Summary by priority (suggested)

**Pre-launch (if desired)**  
- Account settings page (at least link to deletion/contact).  
- Pre-launch testing + trust audit pass.  
- Deploy checklist (env, DB, email, CORS, rate limit, monitoring) per FinalCheck.

**Short-term backlog**  
- Server images (SERVER_IMAGES.md).  
- Ruleset multi-select.  
- Directory sortable row view.  
- Dashboard row view.  
- Maps: auto-add custom map.  
- Owner diagnostics (last N heartbeats/errors).

**Phase 1.5**  
- Cluster pages.  
- Extra carousels (Top 100, Hot, etc.).  
- Additional badges.  
- Password sync, auto-favorite onJoin.  
- Player directory expansion.

**Deferred / separate**  
- Local agent binary (.exe, local UI, checks) — MVP deliverable; build before plugin.  
- Discord bot.  
- Subscription/payments UI.  
- ASA Server API plugin — **post-MVP per DECISIONS.md**; build after site gains traction.  
- Platform status page (/status).

---

**Last updated:** 2026-02-03
