# Frontend Setup Guide

## Initial Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API base URL
```

3. Start development server:
```bash
npm run dev
```

## shadcn/ui Components

When you need to add shadcn/ui components, use the CLI:

```bash
npx shadcn-ui@latest add [component-name]
```

Example:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
```

Components will be installed to `src/components/ui/` and are locally owned (not dependencies).

## Project Structure

```
src/
├── lib/           # Utilities, API client, query client
├── components/    # React components (including shadcn/ui)
└── App.tsx        # Main application
```

## Development Principles

- **No business logic in components** - All API calls go through `src/lib/api.ts`
- **Type safety** - TypeScript strict mode enabled
- **Consistent errors** - All API errors use `APIErrorResponse` class
- **Data fetching** - Use TanStack Query for all data fetching

## Design Tokens

The project uses CSS variables for design tokens, supporting light and dark modes.

### Using Tokens

**Semantic Colors:**
- `bg-background` / `text-foreground` - Base page colors
- `bg-card` / `text-card-foreground` - Card surfaces
- `bg-muted` / `text-muted-foreground` - Muted/secondary content
- `border-border` / `border-input` - Borders and inputs
- `bg-primary` / `text-primary-foreground` - Primary actions (cyan accent)
- `bg-accent` / `text-accent-foreground` - Accent/hover states
- `ring-ring` - Focus rings

**Status Colors:**
- `bg-destructive` / `text-destructive-foreground` - Errors
- `bg-success` / `text-success-foreground` - Success states
- `bg-warning` / `text-warning-foreground` - Warnings

**Tactical Accents:**
- `bg-panel` - Registry panel surfaces
- `border-gridline` - Subtle separators

**Example:**
```tsx
<div className="bg-card border border-border rounded-lg p-4">
  <h2 className="text-foreground">Server Card</h2>
  <p className="text-muted-foreground">Description</p>
  <button className="bg-primary text-primary-foreground hover:bg-accent">
    Join Server
  </button>
</div>
```

### Color Palette

- **Base:** Slate/graphite neutrals (classic registry foundation)
- **Accent:** Cyan (tactical sci-fi, ops console vibe)
- **Avoid:** Neon colors, heavy gradients, scanlines

Tokens are defined in `src/index.css` and mapped in `tailwind.config.js`.
