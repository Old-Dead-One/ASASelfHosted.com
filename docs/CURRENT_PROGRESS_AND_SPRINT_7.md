# Current Progress & Sprint 7 Suggestions

**Date:** Post–Sprint 6, pre–Sprint 7  
**Purpose:** Quick pass of project docs and codebase to assess progress and suggest Sprint 7 focus.

---

## 1. Current Progress Summary

### Design docs alignment

| Doc | Status | Notes |
|-----|--------|-------|
| **1_DESCRIPTION** | ✅ On track | Registry, discovery, trust, Supabase, agent-ready; implemented. |
| **2_FEATURE_LIST** | ⚠️ ~80% | Core directory, badges, carousels (one live: Spotlight), auth, dashboard; player directory, Top 100/Hot carousels, subscription logic deferred. |
| **3_TECH_STACK** | ✅ Matched | React/TS/Vite, Tailwind, Supabase, FastAPI, RLS; Stripe/Sentry optional. |
| **4_Dev_Plan** | ⚠️ Post–Sprint 6 | Web MVP largely done; agent client not started; trust pages now in launch checklist. |
| **5_Appendix** | ✅ Aligned | Single account, dashboard-centric, server/cluster/player pages, trust pages by launch; edits applied. |

### What’s implemented (codebase)

**Frontend**

- **Auth:** Login, sign up, forgot/reset password, session, protected routes.
- **Home:** Directory list (paged, filters), SpotlightCarousel (boosted + verified, top by quality), per-page 24/30/36, card/row view.
- **Server page:** Full detail, join instructions, **join password visible only when authenticated**, favorites button, mod resolution.
- **Dashboard:** Owner server list, create/edit/delete server, ServerForm (name, map, description, status, ruleset, game mode, platforms, etc.), agent setup placeholder.
- **Filters:** q, status, verified, game_mode, ruleset, platform, rank_by, order; clear all.
- **Favorites:** FavoriteButton wired to backend; add/remove favorite API used.

**Backend**

- **Directory:** `GET /api/v1/directory/servers` (filtering, pagination, ranking), `GET /api/v1/directory/servers/{id}`; uses service_role; directory_view SECURITY INVOKER (020).
- **Servers CRUD:** `GET/POST/PUT/DELETE /api/v1/servers` implemented (RLS client, Supabase); create/update/delete working.
- **Favorites:** `POST/DELETE /api/v1/servers/{id}/favorites` implemented.
- **Heartbeat:** `POST /api/v1/heartbeat` (Ed25519, replay protection).
- **Mods:** `GET /api/v1/mods` (catalog), resolve endpoint for frontend.
- **Clusters:** `GET /api/v1/directory/clusters`; owner cluster CRUD stubbed or partial.

**Data & infra**

- Supabase: migrations through 020 (directory/heartbeats views, mods_catalog, security_invoker, search_path).
- Join password: on `servers` (014); shown on ServerPage only when `isAuthenticated`.

### GAP_ANALYSIS.md vs reality

- **Server CRUD backend:** Implemented (servers.py + repo); GAP_ANALYSIS still lists it as “Critical Missing” — update GAP when convenient.
- **Favorites API:** Implemented (favorites.py); GAP_ANALYSIS still says “missing” — update GAP.
- **Password gating:** Join password is “account-gated” (visible only to logged-in users), not “favorite-gated”; design choice is documented.

---

## 2. Sprint 7 Suggestions

### Prioritization (suggested order)

1. **Trust & launch readiness (from 4_Dev_Plan + 5_Appendix)**  
   - Add **Verification Explained** and **Consent & Privacy by Design** pages (required by launch).  
   - Link from footer or About.  
   - Keeps promise to design docs and supports go-live.

2. **SpotlightCarousel clarity and layout**  
   - Define and document spotlight criteria (e.g. boosted + verified, top by quality).  
   - Implement layout: 8 servers, 4 cards wide, fit max width (already in SPRINT_7_TODO).  
   - Quick win; improves home page without new backend.

3. **Maps: filter + CreateServer**  
   - Add `maps` table in Supabase; map filter on directory; map field in ServerForm as dropdown/autocomplete (with rules for user-added maps).  
   - High value for discovery and data quality.

4. **Discord + website URL on server**  
   - Add `discord_url`, `website_url` to servers; ServerForm + ServerCard/detail.  
   - Small, clear scope; improves usefulness of listings.

5. **Row view: sortable table (directory)**  
   - Sortable columns on directory row view (name, status, players, quality, updated, etc.).  
   - Complements existing filters and improves usability at scale.

6. **Server images (Sprint 7 plan)**  
   - Follow `docs/SPRINT_7_SERVER_IMAGES.md`: Supabase Storage, one banner per server, 1200×630, card background, report/under-review, enforcement.  
   - Larger chunk; can be split into sub-sprints or phased (upload + display first, moderation next).

7. **Dashboard row view**  
   - Add row/table view for “My Servers” (toggle like home).  
   - Improves owner experience when they have many servers.

8. **Ruleset filter: multiple values**  
   - Multi-select ruleset with rules (at most one of vanilla/vanilla_qol/modded; boosted can combine).  
   - Align with backend `rulesets` if/when used.

9. **Cluster logic**  
   - Cluster pages, cluster-scoped server list, cluster metadata, owner flows.  
   - Larger; can start with read-only cluster page and expand.

10. **Per-user limits (FinalCheck)**  
    - Server limit and cluster limit per user; enforce on create; document in DECISIONS/config.  
    - Good to have before or soon after launch.

### Suggested Sprint 7 “core” (if time-boxed)

- **Must:** (1) Trust pages — Verification Explained + Consent & Privacy; (2) SpotlightCarousel layout (8 servers, 4 wide) + criteria documented.  
- **Should:** (3) Maps table + filter + CreateServer map field; (4) Discord + website URL fields.  
- **Nice:** (5) Sortable row view; (6) Start server images (upload + display only, or full plan phased).

### Docs to update when convenient

- **GAP_ANALYSIS.md:** Mark Server CRUD backend and Favorites API as complete; adjust password gating description to “account-gated”.
- **SPRINT_6_CHECKLIST.md:** Replace “NewbieCarousel” with “SpotlightCarousel” where relevant; note per-page 24/30/36 if you want the checklist to match current UI.

---

## 3. Risks / Notes

- **Agent client:** Still 0%; backend heartbeat and verification are in place. No change to Sprint 7 suggestion; agent remains a separate track.
- **Subscription / Stripe:** Stubbed; acceptable for Sprint 7 if launch is “free tier only” or manual handling.
- **Cluster CRUD:** Backend may be stubbed; cluster *pages* (read-only) and directory cluster list can precede full cluster CRUD.

No architectural changes recommended; current direction matches design docs and is ready for Sprint 7 as above.
