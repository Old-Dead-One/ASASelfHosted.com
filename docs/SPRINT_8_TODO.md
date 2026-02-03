# Sprint 8 – TODO (open items from all sprints)

Sprint 7 core is complete (trust pages, SpotlightCarousel, maps, Discord/website URLs). This doc holds **remaining open items** from Sprint 7 and earlier, plus pre-launch and Phase 1.5 work. No code here—task list only.

---

## From Sprint 7 (deferred to Sprint 8)

### SpotlightCarousel – completed in Sprint 7

- [x] Selection locked: mode=verified, ruleset=boosted, rank_by=quality, order=desc, limit=8.
- [x] Layout: horizontal carousel with wrap-around; limit 8.
- [x] Comment in SpotlightCarousel.tsx matches behavior.

*No open Sprint 7 Spotlight items.*

### Ruleset filter – multiple values

**Current:** Ruleset filter is single-select (vanilla, vanilla_qol, boosted, modded).

- [ ] Support multiple selected values in Ruleset filter.
- [ ] Constrain: at most one of vanilla / vanilla_qol / modded; boosted can combine with any. Align with backend `rulesets` (multi-value) if used.

---

### Ranking logic – clarify and implement

**Current:** Directory supports `rank_by` (updated, new, favorites, players, quality, uptime) and `order` (asc/desc); backend sorts by the mapped column + id. Quality score is computed by the quality engine (uptime + activity + confidence). `rank_position` and `rank_delta_24h` are in the schema but backend returns null (placeholders).

- [ ] **Clarify and document** — **docs/RANKING.md** is the single source of truth: what each rank_by option means, how quality_score is computed, that rankings are not sold, and how NULLs/cursor pagination work. Share with backend and frontend.
- [ ] **Backend** — Ensure directory list and single-server responses apply sort consistently (rank_by → column, order, tie-break by id); NULLs last for numeric sort columns. Optionally implement rank_position (e.g. 1-based for first page only) and/or rank_delta_24h (e.g. historical snapshot job); if not, keep null and document.
- [ ] **Frontend** — Ensure Sort by / Order labels and behavior match docs/RANKING.md; pass rank_by and order to API; display quality_score and (when present) rank_position/rank_delta_24h; handle nulls (hide or "—") so users are not misled. No claims of global "rank" if backend does not compute it.

---

### Row view – sortable table

- [ ] Make directory row view a sortable table: click column headers to sort (asc/desc).
- [ ] Decide sortable columns (e.g. name, status, players, quality, updated).

---

### Image support (server card background)

**Spec:** docs/SERVER_IMAGES.md (Supabase Storage, one banner per server, 1200×630, cropping, report + moderation).

- [ ] **Backend:** Migration (image_path, image_status, image_updated_at; optional image_reports, blacklist_users). Storage: signed URL or backend upload; remove image; report image endpoint. Server read endpoints return image status. Enforcement: blacklist blocks create/update and hides listings.
- [ ] **Frontend:** Server form "Server Banner" section (preview, upload/replace/remove, rules confirmation). Cropper (1200×630). Card/dashboard card: background image + overlay when image_status=active; placeholder when under_review; default tek when none/removed. "Report image" on card; hide when under review.
- [ ] **Admin/Operations:** Approve/reject/escalate (DB or minimal admin). Document enforcement and "Image rules" text.
- [ ] Recommended size 1200×630 for social/Discord; JPG/PNG/WebP, max ~3MB.

---

### Full user dashboard

**Current:** Dashboard is owner-focused (My Servers only). It should serve as the full logged-in user hub.

- [ ] **Favorites section** — Add a section on the dashboard that lists the user's favorited servers (read from existing favorites API). Allows quick access and unfavorite from dashboard; consider card/row consistency with directory.
- [ ] **Privacy permissions placeholder** — Add a placeholder section for "Privacy & consent" that will later generate or display in-game console commands for granting privacy/consent permissions (so players can copy and run commands in-game to opt in). Can be "Coming soon" or minimal UI with link to Consent page until backend/plugin support exists.
- [ ] **Agent key generation** — Add UI in the dashboard for generating the **private and public keys** used by the agent to send heartbeats to asaselfhosted.com. Backend: generate key pair (e.g. Ed25519), store public key, return private key **once** for the user to configure the agent; support revocation/rotation. Frontend: trigger generation, one-time private-key display (copy), install/configure instructions, and optional revocation. (See "From GAP_ANALYSIS (agent track)" below for backend/agent-client details.)

---

### Dashboard row view

- [ ] Add row/table view for dashboard (owner’s server list) in addition to card view; allow switch like home directory.

---

### Maps table – add new map when not present

**Current:** ServerForm allows a custom map name ("Other"); it is stored only on `servers.map_name`. The `maps` table is read-only (seeded by migration); no logic inserts new rows.

- [ ] When a user enters a custom map name (create/edit server) that is not in the `maps` table, add it to the DB so it appears in the reference list and filter options. Options: backend "insert map if not exists" in server create/update (e.g. service role), or a dedicated endpoint; define who can add (e.g. any authenticated owner vs. admin-only) and any validation/normalization.

---

### Cluster logic

- [ ] Cluster pages and cluster-scoped server list; cluster metadata (name, slug, visibility).
- [ ] Owner flows for managing clusters (if in scope).
- [ ] Decide: cluster as first-class entity with routes/UI vs. grouping field only; document in DECISIONS or here.
- *Note:* Cluster schema and `cluster_id` on servers exist; this is UI and product logic.

---

## From GAP_ANALYSIS (pages)

### Account Settings

- [ ] Account settings page: user profile, email change, password change, account deletion (link from header/footer where appropriate).

---

## From FinalCheck / pre-launch

### Contact and email support

- [ ] Wire Contact page (`/contact`): form and/or email so “contact us” works everywhere (Legal §13, Data Rights, footer).
- [ ] Add email support where needed (e.g. contact form submission, reply-to).

### Per-user limits

- [ ] Server limit per user (e.g. max N servers per owner). Enforce in backend on create; optionally surface in UI.
- [ ] Cluster limit per user (e.g. max N clusters). Enforce in backend; optionally surface in UI.
- [ ] Define limits (e.g. 10 servers, 5 clusters); document in DECISIONS or config. Consider env-configurable.

### Server card background (tek + ServerImage)

- [ ] When ServerImage is available, use it as card background (or hero area) instead of tek default; keep rest of card styling (see FinalCheck.md).

---

## From GAP_ANALYSIS (agent track)

### Agent key/instance management (medium priority)

- [ ] Backend: generate **private and public keys** (e.g. Ed25519) for the agent; store public key; return private key **one-time only** (used by agent to sign heartbeats to asaselfhosted.com). E.g. `POST /api/v1/clusters/{id}/generate-keys` or per-server depending on model.
- [ ] Backend: agent instance management (create/list instances, link to servers) if applicable.
- [ ] Frontend: key generation in **dashboard** (see “Full user dashboard” above)—trigger generation, one-time private key display (copy), revocation/rotation UI, agent install and configure instructions.
- *Note:* Agent signs heartbeats with the private key; backend verifies with stored public key. Clarify token vs. key model and cluster vs. server scope if needed.

### Local host agent client (high priority, can ship without)

- [ ] Node.js/TypeScript (or Python) agent service.
- [ ] Local web UI: instance table, R/Y/G lights, “Test now”, logs.
- [ ] Checks: process, port; heartbeat push (e.g. every 300s).
- [ ] Windows .exe packaging; “Run at startup” helper.
- *Note:* Backend heartbeat endpoint ready; platform is soft-launch ready without agent.

---

## Phase 1.5 (post-launch, not Sprint 8 required)

- [ ] Cluster pages (read-only or owner management).
- [ ] Top 100 / Hot / Stability / Activity carousels.
- [ ] Additional badges (Hot, Long-Runner, cluster badges).
- [ ] Password sync (auto from agent).
- [ ] Auto-favorite onJoin (plugin-assisted).
- [ ] Player directory expansion.

---

## Testing and docs

- [ ] Run pre-launch testing: create/edit/delete server, favorites, directory filters, SpotlightCarousel, password hidden when logged out; trust pages readable, claims match behavior.
- [ ] Trust claims audit: Verification and Consent pages vs. docs/TRUST_PAGES.md; no contradictions with code.
- [ ] Add any testing bugs found to this section.

---

## Reference

- **Trust pages spec:** docs/TRUST_PAGES.md (content and acceptance criteria for /verification, /consent).
- **Pre-deploy checklist:** FinalCheck.md.
- **MVP vs. design docs:** GAP_ANALYSIS.md (MVP Complete Analysis section).
- **Completed (launch-ready):** Trust pages, SpotlightCarousel (limit 8, wrap-around), maps + filter + ServerForm, Discord/website URLs.
- **Trust claims audit:** docs/Trust_Claims_Audit.md.
- **Server images spec:** docs/SERVER_IMAGES.md.
- **Doc index:** docs/WORKING_DOCS.md. **Steam OAuth:** docs/STEAM_OAUTH_TODO.md when implementing.

---

**Last Updated:** 2026-02-02
