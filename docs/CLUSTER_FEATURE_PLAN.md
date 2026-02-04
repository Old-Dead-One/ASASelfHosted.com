# Cluster Feature — Implementation Plan

What’s done, what’s missing, and how to implement the rest so the cluster feature is complete end-to-end.

**References:** Design 5_Appendix D.4.2 (cluster pages), DECISIONS.md (cluster display-only MVP), REMAINING_VS_DESIGN.md, backend `app/api/v1/clusters.py`, `app/db/supabase_directory_clusters_repo.py`, frontend ServerForm/Dashboard.

---

## 0. Completed (current)

- **Backend:** DELETE `/api/v1/clusters/{cluster_id}`; GET `/directory/clusters/slug/{slug}`; `server_count` populated in directory cluster responses; per-user cluster limit (default 1) with profile overrides; admin `PATCH /admin/profiles/{user_id}/limits` for servers/clusters overrides.
- **Frontend:** Dashboard “Your Clusters” section with create/edit/delete cluster, key generation; “X of Y servers · X of Y clusters” and “Need more? Request a higher limit” note with contact link; public `/clusters` (list) and `/clusters/:slug` (detail) pages; Clusters link in header; directory clusters API client.

---

## 1. Current state

### Backend (done)

- **Schema:** `clusters` table (id, name, slug, visibility, owner_user_id, key_version, public_key_ed25519, etc.). `servers.cluster_id` FK with ON DELETE SET NULL. `profiles.servers_limit_override`, `profiles.clusters_limit_override` for admin overrides.
- **Owner API** (`/api/v1/clusters/`): POST create, GET list (owner’s clusters), GET `/{cluster_id}`, PUT `/{cluster_id}`, POST `/{cluster_id}/generate-keys`, DELETE `/{cluster_id}`. Create enforces cluster limit (default 1; admin can override per user).
- **Directory API:** GET `/directory/clusters` (list public clusters, cursor pagination, server_count), GET `/directory/clusters/{cluster_id}`, GET `/directory/clusters/slug/{slug}`. Directory list servers supports `cluster`, `cluster_id`, `cluster_visibility`, `is_cluster` filters.
- **Directory clusters repo:** `list_clusters`, `get_cluster(id)`, `get_cluster_by_slug(slug)`. Returns `DirectoryCluster` with `server_count` from servers table (admin client count).

### Frontend (done)

- **Dashboard:** “Your Clusters” section: create cluster (name, slug, visibility), edit/delete per cluster, generate/rotate keys. “Agent verification setup” below. Limits: “X of Y servers · X of Y clusters” and “Need more? Request a higher limit” with link to Contact.
- **ServerForm:** Cluster dropdown (owner’s clusters only); can set `cluster_id` when creating/editing a server.
- **Server card/row and ServerPage:** Show `cluster_name` (and cluster block on ServerPage). ServerFilters: “Cluster” = Has cluster / No cluster (`is_cluster`).
- **Public cluster pages:** Route `/clusters` (ClustersPage) and `/clusters/:slug` (ClusterPage); directory clusters API client; “Clusters” in header.

---

## 2. What needs to be done

### A. Dashboard: cluster CRUD UI

**Goal:** Owners can create, edit, and delete clusters from the dashboard (no DB/API-only workflow).

| # | Task | Notes |
|---|------|--------|
| A1 | **Create cluster** | Form or inline: name, optional slug, visibility (public/unlisted). Call existing POST `/api/v1/clusters/`. Show in “Cluster keys” list and in ServerForm dropdown. |
| A2 | **Edit cluster** | Per-cluster “Edit” (name, slug, visibility). Call PUT `/api/v1/clusters/{id}`. |
| A3 | **Delete cluster** | Backend: add DELETE `/api/v1/clusters/{cluster_id}` (owner-only). DB: servers stay but `cluster_id` → null (existing FK). Frontend: “Delete cluster” with confirmation; unlink servers’ cluster. |
| A4 | **Placement** | Either a dedicated “Clusters” section above “Agent verification setup” (list + Create cluster + Edit/Delete per row) or keep one section “Clusters & keys” with Create + list (keys + Edit/Delete). |

### B. Backend: delete cluster + get by slug

| # | Task | Notes |
|---|------|--------|
| B1 | **DELETE /api/v1/clusters/{cluster_id}** | Require auth + ownership. Delete cluster row; RLS/DB handle servers (ON DELETE SET NULL). Return 204 or 200. |
| B2 | **Get public cluster by slug** | Directory: add `get_cluster_by_slug(slug)` in directory clusters repo; add GET `/directory/clusters/slug/{slug}`. Returns same shape as get by ID (public only). Enables pretty URLs: `/clusters/my-cluster`. |

### C. Backend: server_count for clusters

| # | Task | Notes |
|---|------|--------|
| C1 | **server_count on DirectoryCluster** | In `list_clusters` and `get_cluster` (and `get_cluster_by_slug`), set `server_count` from a count of servers where `cluster_id = cluster.id`. Optional: same for directory list response if we already have a join/count available. |

### D. Public cluster list page

| # | Task | Notes |
|---|------|--------|
| D1 | **Route** | e.g. `/clusters` (list of public clusters). |
| D2 | **API client** | `listDirectoryClusters(limit, cursor, sort_by, order)` → GET `/directory/clusters`. Types for `DirectoryCluster`, `DirectoryClustersResponse`. |
| D3 | **ClustersPage** | Paginated list (cards or table): cluster name, slug, server count, link to cluster detail. Reuse cursor pattern from directory servers. |
| D4 | **Nav** | Link “Clusters” in header and/or footer (and/or from Home/directory area). |

### E. Public cluster detail page

| # | Task | Notes |
|---|------|--------|
| E1 | **Route** | `/clusters/:slug` (slug-based; 404 if not found or unlisted). |
| E2 | **API client** | `getDirectoryClusterBySlug(slug)` → GET `/directory/clusters/slug/{slug}`. Plus existing directory servers list with `cluster_id` filter. |
| E3 | **ClusterPage** | Show cluster name, slug, visibility, server count. List member servers: use directory servers API with `cluster_id=<cluster.id>` (or filter by slug if backend supports). Reuse ServerCard or ServerRow; optional “View all” to directory with cluster filter. |
| E4 | **Breadcrumbs / SEO** | Title/heading “Cluster: {name}”; link back to Clusters list and/or Directory. |

### F. Optional: cluster limit per user

| # | Task | Notes |
|---|------|--------|
| F1 | **MAX_CLUSTERS_PER_USER** | Config + env; enforce in POST `/api/v1/clusters/` (return 403 when at limit). |
| F2 | **Dashboard** | Show “X of Y clusters” and disable “Create cluster” at limit (like server limit). |

---

## 3. Suggested implementation order

1. **Backend: DELETE cluster + get by slug + server_count**  
   So dashboard and public pages have the APIs they need.

2. **Dashboard: cluster CRUD UI**  
   Create / Edit / Delete clusters; keep key generation where it is.

3. **Frontend: directory clusters API client + types**  
   `listDirectoryClusters`, `getDirectoryClusterBySlug` (and `getDirectoryCluster(id)` if you want it).

4. **Public cluster list page**  
   Route, ClustersPage, nav link.

5. **Public cluster detail page**  
   Route by slug, ClusterPage, member servers list.

6. **Optional:** Cluster limit per user (config + enforce + dashboard).

---

## 4. File checklist (where to touch)

| Area | Files |
|------|--------|
| Backend cluster API | `backend/app/api/v1/clusters.py` (add DELETE) |
| Backend directory clusters repo | `backend/app/db/supabase_directory_clusters_repo.py` (add `get_cluster_by_slug`, add server_count in list/get) |
| Backend directory router | `backend/app/api/v1/directory.py` (add GET `/directory/clusters/slug/{slug}`) |
| Backend directory repo interface | `backend/app/db/directory_clusters_repo.py` (add `get_cluster_by_slug` to interface) |
| Mock directory clusters | `backend/app/db/mock_directory_clusters_repo.py` (implement get_cluster_by_slug, server_count if used in tests) |
| Frontend API | `frontend/src/lib/api.ts` (directory clusters: list, get by id, get by slug) |
| Frontend types | `frontend/src/types/index.ts` (DirectoryCluster if not already) |
| Dashboard | `frontend/src/pages/DashboardPage.tsx` (Clusters section: create form, edit/delete per cluster) |
| Routes | `frontend/src/routes/index.tsx` (`/clusters`, `/clusters/:slug`) |
| New pages | `frontend/src/pages/ClustersPage.tsx`, `frontend/src/pages/ClusterPage.tsx` |
| Nav | `frontend/src/components/layout/Header.tsx` and/or `Footer.tsx` (link to Clusters) |
| Optional limit | `backend/app/core/config.py`, `backend/app/api/v1/clusters.py`, dashboard limits display |

---

## 5. Design notes (from 5_Appendix D.4.2)

- Cluster pages = **member server aggregation**, map coverage, cluster-level verification, aggregate uptime (Phase 1.5+).
- For “finish cluster feature” we can ship: **list public clusters**, **cluster detail by slug with member servers**, and **owner create/edit/delete clusters + keys**. Map coverage and aggregate uptime can be Phase 1.5 enhancements once the pages exist.

---

*Last updated: 2026-02-03*
