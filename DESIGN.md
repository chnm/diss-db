# Design Specification

This document describes the visual design system for the History Dissertation Database, implemented as the "Archive" direction — scholarly, library-coded, with a bone + indigo palette.

## Color Palette

All colors are defined as CSS custom properties in `theme/static_src/src/styles.css` and mapped to Tailwind utilities in `tailwind.config.js`.

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `--paper` | `#f4f1ec` | `bg-paper`, `text-paper` | Main page background |
| `--paper2` | `#e9e5dd` | `bg-paper2` | Deeper panel bg (footer, filter bar, callout cards) |
| `--paper3` | `#fbfaf6` | `bg-paper3` | Lightest tint (cards, chips, form inputs) |
| `--ink` | `#141822` | `text-ink`, `border-ink` | Primary text, heavy rules |
| `--ink2` | `#313644` | `text-ink2` | Secondary text |
| `--mute` | `#6f7585` | `text-mute` | Tertiary / caption text |
| `--line` | `#c8cad2` | `border-line` | Hairline borders |
| `--line2` | `#e0e2e8` | `border-line2` | Softer hairlines (between table rows) |
| `--accent` | `#1f3a6b` | `text-accent`, `border-accent` | Deep indigo — links, kickers, focus states |
| `--avatar` | `#d8dbe2` | `bg-avatar` | Avatar / seal placeholder background |

## Typography

Three font families loaded from Google Fonts:

| Role | Family | Tailwind class | Weights | Usage |
|------|--------|---------------|---------|-------|
| Display / serif | EB Garamond | `font-serif` | 400, 500, 600, italic | Headings, titles, body callouts |
| Body / sans | Source Sans 3 | `font-sans` | 300–700 | Body copy, table cells, UI controls |
| Mono / label | JetBrains Mono | `font-mono` | 400, 500, 700 | Kickers, metadata, record IDs, years |

### Type Scale

Custom font sizes defined in `tailwind.config.js`:

| Token | Size | Line-height | Letter-spacing | Usage |
|-------|-----:|-------------|----------------|-------|
| `text-display-xl` | 60px | 1.05 | -1.2px | Home page hero `<h1>` |
| `text-display-lg` | 48px | 1.1 | -0.6px | Table page headers |
| `text-display-md` | 38px | 1.1 | -0.5px | Dissertation title on scholar profile |
| `text-display-sm` | 30px | 1.2 | -0.4px | Section headings, stat numbers |
| `text-heading` | 28px | 1.2 | -0.3px | Sub-section headings |
| `text-title-lg` | 22px | 1.25 | -0.2px | Card titles, list-row titles |
| `text-title` | 19px | 1.3 | — | Dissertation row titles |
| `text-body-lg` | 19px | 1.65 | — | Abstract text |
| `text-body` | 15px | 1.55 | — | General body copy |
| `text-meta` | 13px | 1.4 | — | Metadata, years, counts |
| `text-meta-sm` | 11px | 1.4 | — | Kicker labels, chips |

## Component Classes

Defined in `theme/static_src/src/styles.css` via `@layer components`:

### Layout

| Class | Description |
|-------|-------------|
| `.page-section` | 64px horizontal padding (responsive: 24px tablet, 16px mobile) |
| `.section-header` | Page header section with padding + bottom border |
| `.filter-bar` | Paper2 background filter strip with border |
| `.breadcrumb` | Mono breadcrumb navigation |

### Cards & Panels

| Class | Description |
|-------|-------------|
| `.card` | 28px padding, paper3 background, line border |
| `.card-sm` | 24px padding variant |
| `.card-callout` | Paper2 background with line border (field notes, contribute CTAs) |

### Rules & Dividers

| Class | Description |
|-------|-------------|
| `.rule-heavy` | 2px `border-ink` bottom + padding-bottom 12px + margin-bottom 24px |
| `.rule-soft` | 1px `border-line2` bottom |

### Buttons

| Class | Description |
|-------|-------------|
| `.btn-primary` | Ink background, paper text, kicker font |
| `.btn-secondary` | Transparent, ink border, ink text |
| `.btn-subtle` | Transparent, line border, ink2 text |

### Forms

| Class | Description |
|-------|-------------|
| `.form-input` | Full-width input with line border, paper3 bg |
| `.form-label` | Kicker-styled label (mono caps, mute color) |

### Data Display

| Class | Description |
|-------|-------------|
| `.kicker` | Mono uppercase label (11px, 500 weight, 0.14em tracking) |
| `.chip` | Inline tag/chip (mono, line border, paper3 bg) |
| `.meta-table` | Key-value metadata table with kicker labels |
| `.stat-number` | Big serif number display (display-sm size) |
| `.avatar` | Circle with initials (avatar bg, line border, italic serif) |
| `.lineage-indent` | Indented block with accent left border (lineage chains) |

### Tables

| Class | Description |
|-------|-------------|
| `.archive-table` | Full-width data table with 2px header rule, alternating row tint |
| `.table-pagination` | Pagination bar with mono page buttons |
| `.page-btn` / `.page-btn.active` | Individual pagination buttons |

## Borders & Rules

- **Hairline:** `border-line2` (soft, between table rows, list items)
- **Hairline strong:** `border-line` (panel borders, around chips, cards)
- **Section rule:** `border-b-2 border-ink` (under section headings)
- **Accent rule:** `border-l-2 border-accent` (lineage indent blocks)
- **Border radius:** `0` everywhere except avatar circles. Sharp corners throughout.

## Shadows

None. The design is intentionally flat.

## Spacing

The 64px page padding is the primary horizontal rhythm (`page-section` class). Custom spacing values in Tailwind config:

| Token | Value |
|-------|-------|
| `page` | 64px |
| `page-tablet` | 24px |
| `page-mobile` | 16px |

## Responsive Breakpoints

- `1024px` — collapse two-column layouts to single column, reduce page padding to 24px
- `640px` — stack everything, reduce page padding to 16px

Responsive padding is handled automatically by the `.page-section`, `.section-header`, `.filter-bar`, `.table-pagination`, and `.breadcrumb` classes via media queries in `styles.css`.

## Interactions

- **Links:** `color: inherit` by default, transition to `var(--accent)` on hover
- **Table links:** Always `var(--accent)` color
- **Nav links:** Inactive = `text-ink2`, active = `text-accent` with `border-accent` underline
- **Tab buttons:** Same pattern as nav (accent color + 2px bottom border when active)
- **Lineage tree hover:** Path-to-root highlighting with accent color, non-path elements fade to 15% opacity

## File Structure

| File | Purpose |
|------|---------|
| `theme/static_src/src/styles.css` | Design tokens, base styles, component classes, table styles |
| `theme/static_src/tailwind.config.js` | Color/font/spacing extensions to Tailwind |
| `templates/base.html` | Header, footer, nav, shared structure |
| `templates/index.html` | Home / landing page |
| `templates/about.html` | About page |
| `templates/contributing.html` | Contributing guide |
| `templates/dissertations/scholar_detail.html` | Scholar profile (includes dissertation tab) |
| `templates/dissertations/*_filter.html` | Data table pages (dissertations, scholars, committee) |
| `templates/dissertations/*_edit.html` | Edit forms |
| `templates/dissertations/*_create.html` | Create forms |
| `templates/django_tables2/tailwind.html` | django-tables2 table template |
| `templates/network_viz.html` | Committee network visualization |
