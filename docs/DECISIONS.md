# Official Decisions - ASASelfHosted.com

**These decisions override any mismatches between design documents unless explicitly revised later.**

**Last Updated:** 2026-02-03

---

## 1. Agent vs ASA Server API Plugin — MVP Scope

**Decision:** MVP ships the **Local Host Agent** only. The **ASA Server API plugin is post-MVP**; we will build it after the site gains traction.

- **Local Host Agent (MVP):** Verification and heartbeat reporter that runs outside the ASA ecosystem. Delivers reliable server status without depending on in-game mods or plugin maintenance.
- **ASA Server API Plugin (post-MVP):** Deeper automation, in-game consent flows, richer telemetry, and optional features (e.g. auto wipe/mod reporting, password sync, onJoin signals). Built once the platform has traction and the plugin investment is justified.

**Rationale:** Reliable verification first with the agent; add the plugin when demand and resources support it.

**Note:** Feature List and Dev Plan sometimes use "Plugin" in MVP context—for MVP scope, that means the Local Host Agent (heartbeat + verification), not the ASA Server API plugin.

---

## 2. Database Model Alignment

**Decision:** Sprint 0 schema includes only what Web MVP needs + minimal Verified plumbing.

**Sprint 0 includes:**
- Core directory tables (servers, clusters minimal, favorites, etc.)
- Single "heartbeats" table (generic) keyed by server_id with source field
- `directory_view` (public read model for directory)

**Sprint 2 includes:**
- Full agent tables (agents, agent_instances, agent_heartbeats)

**Rationale:** Keep schema stable, avoid rewrite later. Directory view needed for consistent public listing queries.

**Note:** Dev Plan mentions agent tables in MVP - these are Sprint 2, not Sprint 0.

---

## 3. Subscription Model Timing

**Decision:** Subscription plumbing is in MVP, but minimal and "off by default."

**MVP scope:**
- Stripe webhook endpoint scaffolding
- DB tables for subscription state and license/key quota concept
- Minimal UI (placeholder/stub is fine)

**Not in MVP:**
- Full pricing UX, upgrades, invoices, etc.

**Rationale:** Feature List explicitly calls out "Subscription plumbing (even if minimal UI)" in MVP scope lock.

---

## 4. Cluster Model Timing

**Decision:** Cluster data model is MVP. Cluster pages are Phase 1.5.

**MVP scope (data-only):**
- `clusters` table
- Server-to-cluster association
- Cluster key metadata (no plaintext private keys)
- Display-only: show cluster name on server page, view-only association

**Not in MVP:**
- Cluster pages, dashboards, analytics, "Full map coverage" views

**Rationale:** Feature List shows cluster pages in Phase 1.5, but data model needed for MVP features.

---

## 5. Design Direction

**Decision:** Set up lightweight token structure now (Tailwind config + CSS variables), but don't over-engineer full design system.

**"Tactical Sci-Fi accents" means:**
- Base: Clean, classic SaaS registry (white/near-black, strong spacing, readable type)
- Accents: Subtle "ops console" vibe without neon gamer UI
- Use: Muted slate/graphite surfaces, thin separators/cards/panels, small mono/technical touches, lucide-style icons sparingly
- Avoid: Glowing gradients, heavy scanlines, "HUD overload"

**Rationale:** Classic registry foundation with personality, but not over-designed.

---

## 6. Payment Service Research

**Decision:** Wait. Don't research alternatives now.

**Use Stripe as default** until real traction and fee sensitivity is proven. Revisit alternatives post-launch.

**Rationale:** Subscriptions need proper recurring billing and webhooks. Many alternatives are messy for this.

---

## 7. Verification Model — Status Precedence

**Decision:** Implement only schema hooks in Sprint 0. Full RYG logic in Sprint 2.

**Sprint 0:**
- Schema: `servers.status` (manual) + fields for `status_source`, `last_seen_at`, `effective_status`
- Or: `server_status` table that view reads from (minimal)

**Sprint 2:**
- Full precedence logic: agent beats manual if fresh, stale = degrade confidence, compute R/Y/G

**Rationale:** Keep MVP moving without reworking data shape later.

---

## 8. MVP Scope — Definitive Source

**Decision:** Feature List "90% MVP Scope Lock (30 days, solo dev)" is the **definitive MVP scope**.

**Dev Plan is secondary:** Useful for sequencing and implementation notes, but does not override scope lock.

**MVP must include (from scope lock):**
- Website: Public directory, search, manual + verified status, favorites, player accounts, server pages + join instructions, one carousel (Newbie), basic badges, subscription plumbing (minimal), classy ad space
- Plugin/Agent: Secure key system, server verification, auto status, map identity, cluster grouping, heartbeat endpoint
- Discord: Optional / can slip

---

## Reference Documents

- `docs/design/1_DESCRIPTION.txt` - Project description
- `docs/design/2_FEATURE_LIST.txt` - **Definitive MVP scope** (90% MVP Scope Lock)
- `docs/design/3_TECH_STACK.txt` - Technology stack
- `docs/design/4_Dev_Plan.txt` - Development plan (secondary, useful for sequencing)

---

## 9. Agent Authentication Method (Sprint 4)

**Decision:** Use **Ed25519 signature verification** with cluster-based public keys, not HMAC with agent tokens.

**Sprint 4 Implementation:**
- Cluster stores `public_key_ed25519` (base64-encoded Ed25519 public key)
- Agent signs heartbeat envelope with cluster's private key
- Backend verifies signature using cluster's public key
- Replay protection via `UNIQUE(server_id, heartbeat_id)`

**Rationale:**
- Aligns with cluster key model in `2_FEATURE_LIST.txt` (lines 95-97): "Private Key: one-to-many (cluster owner), Public Key: one-to-one (server instance)"
- More secure than HMAC (asymmetric crypto vs symmetric)
- Supports key rotation via `key_version`
- Better for cluster identity and multi-server clusters

**Note:** `docs/design/4_Dev_Plan.txt` mentions HMAC with agent token (line 106), but Ed25519 cluster-based approach is the correct long-term solution and aligns with the cluster key model.

---

## 10. Directory Read Consistency Model (Sprint 5)

**Decision:** Directory reads use transaction-scoped reads from `directory_view` with cursor pagination for determinism.

**Consistency Guarantees:**
- **Repeatable within request**: All items in a single response use the same `now_utc` timestamp (request handling time)
- **No partial updates mid-read**: Single query from `directory_view` ensures atomic snapshot
- **Cursor pagination determinism**: Cursor encodes `{sort_by, order, last_value, last_id}` for stable pagination

**Cursor Pagination Determinism Limitations:**
- **Stable sort keys required**: Cursor pagination is deterministic **only if sort keys remain stable** between requests
- **No duplicates within traversal**: Assuming stable ordering and correct cursor seek predicates, no item appears twice in a single traversal
- **Concurrent updates may shift items**: Under concurrent writes, items may shift between pages (expected behavior)
- **Duplicates possible if sort keys change**: If a server's sort key (e.g., `updated_at`) changes between page requests, it may appear on multiple pages
- **Cursors remain valid**: Cursors reduce (but don't eliminate) pagination issues under churn

**Implementation:**
- All directory reads go through repositories (no direct Supabase calls in routes)
- `directory_view` COALESCEs nullable sort columns to 0 for deterministic sorting
- Tie-break ordering: `ORDER BY sort_key, id` (id as deterministic tie-breaker)
- `seconds_since_seen` computed server-side using consistent `now_utc` across all items in response

**Rationale:**
- Transaction-scoped reads provide consistency without read replicas (future optimization)
- Cursor pagination is more deterministic than offset-based pagination under concurrent writes
- COALESCE to 0 ensures NULL values don't break cursor pagination (NULLs treated as 0 for sorting)
- Explicit tie-break ordering (id) ensures deterministic ordering even when sort keys are equal

**Future Optimizations:**
- Read replicas for better read scalability (not in Sprint 5)
- Materialized view refresh strategy (if needed for stronger consistency guarantees)

---

*When in doubt, refer to these decisions. They override any conflicting information in the design documents.*
