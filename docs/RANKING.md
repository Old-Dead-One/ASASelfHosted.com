# Ranking and Sort Logic (Directory)

Single source of truth for how directory servers are ranked/sorted. **Backend and frontend must conform to this doc.**

---

## Overview

- **Ranking** here means **sort order** of directory results. Users choose a **rank_by** metric and **order** (asc/desc). Results are ordered by that metric with a tie-break on `id`.
- **Rankings are not sold.** Verification and placement do not affect sort order; order is determined only by the chosen metric and data.
- **rank_position** (e.g. "Rank #5") and **rank_delta_24h** (trending) are **not yet computed**; the backend returns `null` for both. Do not display "Rank #N" or "trending" unless the backend returns these fields. They can be implemented later (e.g. position for first page only, delta from historical snapshots).
- **NULLs last**: For numeric sort columns (players, quality, uptime), NULL values sort last regardless of asc/desc so servers with no data don't dominate.
- **Pagination**: Cursor-based; next page uses the last item's sort value + id for consistent order across pages. No global rank index is required for MVP.

---

## rank_by Options

| rank_by     | Meaning | Backend column / source | Notes |
|------------|---------|--------------------------|-------|
| `updated`  | Last updated (server or listing) | `updated_at` | Default. Most recently updated first (desc). |
| `new`      | Newest listings | `created_at` | When the server was added to the directory. |
| `favorites`| Favorite count | `favorite_count` | Servers with more favorites sort higher (desc). |
| `players`  | Current player count | `players_current` | More players = higher (desc). NULL sorts last. |
| `quality`  | Quality score (0–100) | `quality_score` | Higher score = higher rank (desc). NULL sorts last. |
| `uptime`   | Uptime percentage (0–100) | `uptime_percent` | Higher uptime = higher (desc). NULL sorts last. |

- **order**: `asc` or `desc`. Applied to the chosen column; tie-break on `id` (asc) for stable pagination.
- **Cursor pagination**: Next page uses the last item’s sort value + id so order is consistent across pages. No global "rank #1–100" is required for MVP.

---

## Quality Score (quality_score)

- **Source**: Computed by the backend **quality engine** from uptime, player activity, and confidence (RYG). Stored on the directory view / server-derived data; updated when heartbeats are processed.
- **Range**: 0.0–100.0, or `null` when there is insufficient data (e.g. no uptime).
- **Formula (v1)**: Weighted combination of:
  - Uptime percent (e.g. 60% weight)
  - Normalized player activity (e.g. 30% weight)
  - Confidence multiplier: green &gt; yellow &gt; red (e.g. 10% base)
- **Invariants**: Monotonic—quality goes down when uptime drops, confidence degrades, or activity drops. Deterministic (same inputs → same output).
- **Code**: `backend/app/engines/quality_engine.py`; used by heartbeat worker when processing agent heartbeats.

---

## Backend Contract

- **Query params**: `rank_by` (default `updated`), `order` (default `desc`). Map `rank_by` to a single sort column; order by that column then `id`.
- **Response**: Each server includes `rank_by` and `order` in the response so the client knows how the list was sorted. `rank_position` and `rank_delta_24h` may be `null`; if present, they are informational (e.g. "Rank #3", "+2 in 24h").
- **Filters**: Filters (status, ruleset, map, etc.) are applied **before** sorting. Sort is applied to the filtered set.
- **NULLs**: For numeric sort columns (players, quality, uptime), NULL values sort last regardless of asc/desc so that servers with no data don’t dominate.

---

## Frontend Contract

- **Filters UI**: Expose **Sort by** (rank_by) and **Order** (asc/desc) and send them to the directory API. Labels should match the meanings above (e.g. "Quality Score", "Favorites", "Last updated").
- **Display**: Show quality_score and (if present) rank_position / rank_delta_24h on server card and server detail page. If rank_position/rank_delta_24h are null, hide or show "—" so users are not misled.
- **Spotlight**: Spotlight carousel uses a fixed sort (e.g. `rank_by=quality`, `order=desc`) for its slice; that is separate from the user’s directory sort choice.

---

## Implementation Checklist (Sprint 8)

- [ ] **Document**: This doc (docs/RANKING.md) is the source of truth; link from DECISIONS or README if desired.
- [ ] **Backend**: Confirm directory repo maps rank_by → column and orders by sort column + id; NULLs last for numeric columns. Optionally implement rank_position (e.g. 1-based index for first page only) and/or rank_delta_24h (historical snapshot job) per product decision.
- [ ] **Frontend**: Confirm ServerFilters and useServers pass rank_by and order; labels match this doc; ServerPage and cards handle null rank_position/rank_delta_24h; no claims that "rank" is global if we don’t compute it.
- [ ] **Trust**: About and FAQ already state that rankings are data-driven and not purchasable; no code changes required for that message if behavior already matches.
