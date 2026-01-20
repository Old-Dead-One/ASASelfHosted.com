# Design Tokens Reference

Quick reference for design tokens used throughout the application.

## Color Tokens

### Semantic Colors
| Token | Usage | Light Mode | Dark Mode |
|-------|-------|------------|-----------|
| `background` | Page background | White | Dark slate |
| `foreground` | Primary text | Near black | Near white |
| `card` | Card surfaces | White | Dark slate |
| `muted` | Secondary backgrounds | Light gray | Dark gray |
| `border` | Borders, dividers | Light gray | Dark gray |
| `input` | Form inputs | Light gray | Dark gray |

### Primary & Accent
| Token | Usage | Color |
|-------|-------|-------|
| `primary` | Primary actions, links | Cyan (188° 85% 45%) |
| `accent` | Hover states, highlights | Lighter cyan |
| `ring` | Focus rings | Cyan |

### Status Colors
| Token | Usage |
|-------|-------|
| `destructive` | Errors, delete actions |
| `success` | Success states, confirmations |
| `warning` | Warnings, cautions |

### Tactical Accents
| Token | Usage |
|-------|-------|
| `gridline` | Subtle separators, grid lines |
| `panel` | Registry panel surfaces |

## Usage Examples

### Server Card
```tsx
<div className="bg-card border border-border rounded-lg p-4">
  <h3 className="text-foreground font-semibold">Server Name</h3>
  <p className="text-muted-foreground">Description</p>
  <div className="border-t border-gridline mt-4 pt-4">
    <button className="bg-primary text-primary-foreground hover:bg-accent">
      Join Server
    </button>
  </div>
</div>
```

### Status Badge
```tsx
<span className="bg-success text-success-foreground px-2 py-1 rounded text-sm">
  Online
</span>
```

### Panel Surface
```tsx
<div className="bg-panel border border-gridline rounded p-6">
  {/* Registry panel content */}
</div>
```

## Design Philosophy

**Classic Registry Foundation:**
- Clean, readable typography
- Strong spacing and contrast
- Professional, credible appearance

**Tactical Sci-Fi Accents:**
- Subtle "ops console" vibe
- Cyan accent for technical/operational elements
- Muted slate/graphite base
- Thin separators, cards, panels
- Small mono/technical touches

**Avoid:**
- Neon colors
- Heavy gradients
- Scanlines
- "HUD overload"
- Glowing effects everywhere
