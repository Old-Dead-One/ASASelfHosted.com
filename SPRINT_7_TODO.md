# Sprint 7 – TODO (testing & follow-ups)

Tracking items to address from testing and planned work. Add items as you find them.

---

## SpotlightCarousel – qualify servers

**Current behavior:** Spotlight fetches directory with `ruleset=boosted`, `mode=verified`, `limit=10`, `rank_by=quality`, `order=desc`. No dedicated “spotlight” flag or backend logic.

**TODO:**

- [ ] Define and document spotlight criteria (e.g. verified + boosted, top by quality; or newbie-friendly, new servers, hot, etc.).
- [ ] Implement: either keep current directory query and document it, or add backend/curation (e.g. `is_spotlight`, admin pick, or named spotlight categories).
- [ ] Update `SpotlightCarousel.tsx` comment to match implemented behavior.
- [ ] **Layout:** Show 8 total servers on the SpotlightCarousel, 4 server cards wide, to fit within max width (adjust limit to 8 and grid/layout so 4 cards show cleanly).

---

## Ruleset filter – multiple values

**Current behavior:** Ruleset filter is single-select (vanilla, vanilla_qol, boosted, modded).

**TODO:**

- [ ] Make Ruleset filter support multiple selected values.
- [ ] Constrain selections by existing rules: at most one of vanilla / vanilla_qol / modded; boosted can combine with any. Enforce in UI and align with backend `rulesets` (multi-value) if used.

---

## Map filter and CreateServer map field

**TODO:**

- [ ] Add a simple **maps** table in Supabase (e.g. id, name, slug, or similar) as the canonical list of map names.
- [ ] **Filter by map** in the directory: use the maps table to drive a map filter (dropdown or multi-select) and pass `map_name` (or map id) to the directory API.
- [ ] **CreateServer / Edit server:** Connect the same maps table to the map field as a pull-down or autocomplete (suggest from table, optionally allow free text that becomes a new map).
- [ ] **Add user maps:** When a user enters a map name that does not exist in the table, allow adding it with rules (e.g. who can add, validation, normalization, approval, or auto-add on first use). Define and implement the rules.

---

## Row view – sortable table

**TODO:**

- [ ] Make row view a sortable table: click column headers to sort by that column (asc/desc).
- [ ] Decide sortable columns at implementation time (e.g. name, status, players, quality, updated, etc.).

---

## Image support (server card background)

**TODO:**

- [ ] Add image support for servers: upload/store a server image (recommended size **1200 × 630** for social/Discord reuse) and use it as the card background with gradient overlay on directory cards and SpotlightCarousel.
- [ ] Backend: storage (e.g. Supabase Storage), URL or key on servers; upload in Create/Edit server flow.
- [ ] Frontend: display as background with gradient in `ServerCard` (and any dashboard card that shows the same).

---

## Server form: Discord join + website URL

**TODO:**

- [ ] Add a **Discord join** field when creating/editing/cloning a server (e.g. Discord invite URL or link). Optional; store on server record and show on server card/detail where appropriate.
- [ ] Add a **URL field** for server owners’ web pages (e.g. community site, info page). Optional; store on server record and show on server card/detail where appropriate.
- [ ] Backend: add columns (e.g. `discord_url`, `website_url`) to servers table; include in create/update and directory/server read responses.
- [ ] Frontend: add both fields to ServerForm (create/edit/clone); surface on ServerCard and server detail page as links.

---

## Dashboard row view

**TODO:**

- [ ] Add a row/table view for the dashboard (owner’s server list), in addition to the current card view, so owners can switch between card and row like on the home directory.

---

## Cluster logic

**TODO:**

- [ ] Implement cluster logic: cluster pages, cluster-scoped server list, cluster metadata (name, slug, visibility), and any owner flows for managing clusters.
- [ ] Decide: cluster as first-class entity with its own routes/UI, or only as a grouping field on servers; document in DECISIONS or here.

---

## Testing / bugs (add as you find)

- [ ] _Add items from testing here._

---

## Notes

- Sprint 6 is complete; this doc is for Sprint 7 and post–Sprint 6 follow-ups.
- Cluster schema and `cluster_id` on servers already exist; this is about UI and product logic.
