# App-Wide Style Guide (Tek / ServerForm Look)

This guide documents shared UI patterns derived from `ServerForm` so the same look is used across all pages and forms. All classes live in `src/index.css` unless noted.

---

## Cards & Surfaces

| Class | Use | Notes |
|-------|-----|-------|
| `card-elevated` | Form containers, auth cards, modal-style content, dialogs | `rounded-xl border border-input bg-background-elevated shadow-lg shadow-black/40`. Add padding (e.g. `p-4`, `p-6`, `p-8`) as needed. |
| `card-tek` | Single cards in carousels or lists (e.g. `ServerCard`, `DashboardServerCard`) | `rounded-xl border border-input bg-background-elevated shadow-md shadow-black/30`. Slightly lighter shadow than `card-elevated`. |
| `tek-border` + `bg-tek-wall` + `tek-seam` | Grouped form sections (Tek panels) | Use the section structure from `ServerForm`: `<section class="relative overflow-hidden rounded-lg tek-border">` with inner `bg-tek-wall`, `tek-seam`, and content div. |

---

## Form Inputs & Labels

| Class | Use | Notes |
|-------|-----|-------|
| `input-tek` | `<input>`, `<select>` (single-line) | Full-width, h-9, border/ring/focus matches ServerForm. Add `min-h-[44px]` for touch-friendly auth flows. Add `disabled:opacity-50` for disabled state. |
| `input-tek-auto` | `<textarea>` | Same as `input-tek` but no fixed height. Use with `!h-auto min-h-[4.5rem] resize-none` (and `flex-1` where needed). |
| `label-tek` | `<label>` or `<span>` above inputs | `block text-sm font-medium text-foreground mb-0.5`. Use with `htmlFor` on labels. |
| `form-error` | Validation / API error message | Red alert box: `p-2 bg-destructive/20 border border-destructive rounded-md text-destructive text-sm`. |

---

## Buttons

Use the shared `Button` component from `@/components/ui/Button`:

- **Primary** (`variant="primary"`): Tek-powered main actions (Save, Sign In, Apply Filters).
- **Secondary** (`variant="secondary"`): Cancel, Reset, outline actions.
- **Ghost** (`variant="ghost"`): Low-emphasis actions.
- **Danger** (`variant="danger"`): Destructive actions.

Sizes: `sm` (h-8), `md` (h-10), `lg` (h-11). Pass `className` to extend (e.g. `w-full min-h-[44px]` for full-width or touch targets).

---

## Form Layout Conventions

- **Form spacing**: `space-y-3` or `space-y-4` on the `<form>`.
- **Grid fields**: `grid grid-cols-1 md:grid-cols-2 gap-3` for two-column layouts.
- **Action row**: `border-t border-input/60 pt-4 mt-2 flex gap-3` for submit/cancel above the fold.

---

## Theme Tokens (CSS Variables)

Defined in `index.css` under `:root` and `.dark`; use via Tailwind semantic names:

- `background`, `foreground`, `background-elevated`
- `muted`, `muted-foreground`
- `primary`, `primary-foreground`, `ring`
- `destructive`, `destructive-foreground`
- `input`, `border`

Prefer these over hardcoded colors so dark/light and future themes stay consistent.
