# Sprint 7 Feature Dev Plan — Server Listing Images (Supabase Storage)

## Objective

Allow server owners to upload **one banner image per server** and display it as the **background image on server cards** (no row-table images). Images must be safe, moderated, and enforceable to protect the platform.

---

## Scope Decisions Locked In

* Storage: **Supabase Storage**
* One image per server listing
* Card view only (no images in row/table layout)
* Default banner target size: **1200 × 630** (Open Graph standard)
* Implement **cropping UI** if needed (library TBD)
* Strict content rules + enforcement:

  * Upload confirmation + rules
  * Violations → **remove all servers/clusters, blacklist user** (no notice)
* Community moderation:

  * "Report image" on server cards
  * Reported images replaced with a default **"Image under review"**

---

## User Stories

### US-1: Server owner uploads a banner image

**As a server owner**, I want to upload a banner image so my server card looks credible and recognizable.

**Acceptance Criteria**

* Upload supports JPG/PNG/WebP only
* Upload enforces file size limit (recommend: 2–5MB)
* Image is cropped/resized to 1200×630 (or stored as transformed output)
* Saved image appears on server card immediately (or after refresh)
* Owner can replace or remove the banner

---

### US-2: Players see banner images on card listings

**As a player**, I want server cards to show banners so listings feel modern and trustworthy.

**Acceptance Criteria**

* Card uses banner as background with overlay for readability
* If no banner → default Tek-style gradient background
* Row/table listing shows no images
* Lazy-load images for performance

---

### US-3: Content policy enforcement + reporting

**As an admin/community**, I want the ability to report inappropriate images and stop abuse quickly.

**Acceptance Criteria**

* Card includes "Report Image" action
* Report flags image as "under review"
* Under review → card shows placeholder image ("Image under review")
* Admin can:

  * approve (restore)
  * reject (remove image)
  * escalate enforcement (ban/blacklist + remove servers/clusters)

---

## Data Model & Storage

### Storage Bucket

* Bucket: `server-images`
* Path convention:

  * `server-images/{owner_user_id}/{server_id}/banner.webp` (or `.jpg`)
* One current image per server (overwrite replaces)

### Database Fields (Servers table)

Add fields to the server listing record:

* `image_path` (nullable text) — storage path or public URL
* `image_status` enum: `none | active | under_review | removed`
* `image_updated_at` timestamp
* `image_report_count` int default 0 (optional but useful)
* `image_last_reported_at` timestamp (optional)

Optional audit table (recommended for enforcement):

* `image_reports`:

  * `id`
  * `server_id`
  * `reported_by_user_id` (nullable if anon reporting allowed)
  * `reason` (enum or text)
  * `created_at`

Blacklist mechanism (if not already present):

* `blacklist_users`:

  * `user_id`
  * `reason`
  * `created_at`
  * `created_by`

---

## Security & Permissions

### Upload permissions

* Only authenticated owners can upload/replace their server's image.
* Upload is done via backend endpoint that returns a **signed upload URL** or uses service-role upload on behalf of the user (pick whichever fits current auth model best).
* Store API key/service role strictly on backend.

### Access permissions (viewing)

* Images should be **public-read** OR served via signed URLs with caching.
* For simplicity and performance, public bucket with strict write controls is acceptable since content moderation is in place.

---

## Upload Rules / Validation

### Client-side validation (UX)

* Allowed formats: jpg/png/webp
* Max size: recommend **<= 3MB** (adjustable)
* Minimum dimensions: recommend **>= 1200×630**
* If larger: crop/resize to 1200×630

### Server-side validation (security)

* Enforce MIME type and file size
* Reject invalid files regardless of client checks
* Normalize output format (prefer WebP) if feasible

---

## Cropping & Resizing Approach (TBD but planned)

### Option A: Frontend crop → upload final (preferred UX)

* Use a cropper component to force 1200×630 aspect ratio
* Export compressed image (WebP) and upload

Pros: predictable output, lower storage/bandwidth
Cons: more frontend work, library selection

### Option B: Upload original → backend transforms

* Upload raw image, backend resizes to 1200×630 and stores final

Pros: consistent pipeline
Cons: requires image processing infra (runtime cost)

**Recommendation for Sprint 7:** Frontend cropper + upload final output.

---

## UI/UX Requirements

### Server Edit Form

Add section: **Server Banner**

* Preview of current banner (if active)
* Buttons:

  * Upload / Replace
  * Remove
* Warning confirmation modal before upload:

  * "Only appropriate images. Violations will result in removal of all servers/clusters, blacklist, without notice."

### Server Card Display

* If `image_status=active` and `image_path` exists:

  * render background image
  * apply overlay gradient and Tek border styling
* If `image_status=under_review`:

  * show placeholder "Image under review"
* If none/removed:

  * default background

### Report Image Action

* On server card menu:

  * "Report image"
* If already under review:

  * hide/disable report button

---

## Moderation Workflow

### When reported

1. Create `image_reports` row
2. Increment `image_report_count`
3. Set `image_status=under_review`
4. Replace image rendered in UI with placeholder

### Admin tools (Sprint 7 minimal admin panel or DB-only)

* Approve:

  * set `image_status=active`
* Remove:

  * set `image_status=removed`, clear `image_path` (or keep for audit), optionally delete storage object
* Escalate:

  * Add user to `blacklist_users`
  * Remove/disable all user servers and clusters

---

## Performance Requirements

* Lazy-load banner images in card view
* Serve only 1200×630 images (no originals)
* Consider caching headers / CDN behavior via Supabase Storage defaults

---

## Tasks Breakdown (Sprint 7)

### Backend

1. DB migration: new fields + (optional) `image_reports` + `blacklist_users`
2. Storage integration:

   * endpoint to request upload (signed URL or backend upload)
   * endpoint to remove image
   * endpoint to report image
3. Image status handling in server read endpoints
4. Enforcement hook: if user blacklisted, block creation/update and hide listings

### Frontend

1. Add "Server Banner" section to server form
2. Cropper integration (library selection) enforcing 1200×630
3. Upload/replace/remove flow
4. Card view background rendering + overlay
5. Report image action on card
6. Placeholder rendering for under review

### Admin/Operations

1. Minimal admin actions (could be direct DB for Sprint 7)
2. Document enforcement policy and "Image rules" text

---

## Risks / Notes

* Moderation policy is aggressive (by design). Ensure:

  * The warning modal is explicit
  * Actions are auditable (reports + admin decision trail)
* Cropping library choice matters for UX; pick a well-maintained one.
* Keep "under review" state server-driven, not client-only.

---

## Definition of Done

* Server owners can upload/replace/remove a banner.
* Server cards show banner backgrounds with overlay; row view remains text-only.
* Reporting sets image to "under review" with placeholder swap.
* Enforcement and blacklist mechanism exists and is applied.
* No "easy mode" external URLs.

---

If you want, this can be converted into Sprint 7 tickets (epics → stories → tasks) using the same sprint formatting used elsewhere in the project.
