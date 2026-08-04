# Handoff: dissdb Redesign (Direction A · Archive)

## Overview

This is a redesign of the **History Dissertation Database** (`dissdb.dev.rrchnm.org`) — a Django project that catalogues doctoral history dissertations, their authors, advisors, and committee members. The redesign covers the six core screens:

1. **Home / landing**
2. **Dissertations** — primary table with filters
3. **Scholars** — table of dissertation authors
4. **Committee Members** — table of advisors and readers
5. **Single dissertation** — record detail page
6. **Scholar profile** — person detail page

The chosen direction (out of three explored) is **"Archive"** — scholarly, library-coded, with a "bone + indigo" palette. Mono-accented typography (EB Garamond display + JetBrains Mono labels + Source Sans 3 body) gives it a current-university-press feel without leaning on cream / old-library tropes.

## About the Design Files

The HTML/JSX files in this bundle are **design references**, not production code to ship. They are React + inline-Babel prototypes hosted in a single page so the look, structure, and behavior can be reviewed visually.

**Your job** is to recreate these designs in the existing **Django** codebase using its templates (likely Django Template Language), static CSS, and any vanilla JS already in use. **Do not** introduce React, a JS framework, or a bundler for this redesign — the originals work as static server-rendered HTML with progressively enhanced JS, and that's the simplest target. Use the existing template inheritance, view structure, and any partials already in the project.

If you find Django patterns that conflict with how the prototype is structured (e.g. table rendering loops, pagination), prefer the codebase's existing patterns over a literal port.

## Fidelity

**High-fidelity.** Exact colors, typography, spacing, and layout values are specified. Recreate the UI pixel-perfectly. Where the prototype shows fake data, swap in real model queries from the Django app.

---

## Quick preview

Open `preview.html` in a browser. It renders each of the six screens at full size with a top picker to switch between them — no canvas/zoom chrome.

(`archive.html` is the original review canvas that lets a stakeholder pan/zoom across all six artboards. Useful for context but not needed to implement.)

### Screen reference images

The `screenshots/` folder contains one image per screen — top-of-page captures showing each screen's hero/header at the design width of 1280px. They're a quick visual reference; for the full page, open `preview.html` and scroll.

| # | Screen | File |
|---|--------|------|
| 1 | Home / landing | `screenshots/01-home.png` |
| 2 | Dissertations · table | `screenshots/02-dissertations-table.png` |
| 3 | Scholars · table | `screenshots/03-scholars-table.png` |
| 4 | Committee Members · table | `screenshots/04-committee-table.png` |
| 5 | Single dissertation | `screenshots/05-single-dissertation.png` |
| 6 | Scholar profile | `screenshots/06-scholar-profile.png` |

---

## Design Tokens

All colors are defined as CSS custom properties on `:root` in `archive.html` / `preview.html`. Reuse them in the Django templates:

```css
:root {
  --paper:  #f4f1ec;  /* main page bg                          */
  --paper2: #e9e5dd;  /* deeper panel bg (footer, filter bar)  */
  --paper3: #fbfaf6;  /* lightest tint (cards, chips, inputs)  */
  --ink:    #141822;  /* primary text                          */
  --ink2:   #313644;  /* secondary text                        */
  --mute:   #6f7585;  /* tertiary / caption                    */
  --line:   #c8cad2;  /* hairline                              */
  --line2:  #e0e2e8;  /* softer hairline                       */
  --accent: #1f3a6b;  /* deep indigo — links, kickers, focus   */
  --avatar: #d8dbe2;  /* avatar / seal placeholder             */
}
```

### Typography

Three families, loaded from Google Fonts:

| Role | Family | Weights used | Used for |
|------|--------|--------------|----------|
| **Display / serif** | EB Garamond | 400, 500, 500-italic | h1–h2, titles, body callouts, italic accents |
| **Mono / label** | JetBrains Mono | 400, 500, 700 | Kickers, eyebrows, metadata, record IDs |
| **Body / sans** | Source Sans 3 | 400, 500, 600 | Body copy, table cells, UI controls |

Google Fonts import (already in the prototype):
```html
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=JetBrains+Mono:wght@400;500;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Type scale (from the prototype)

| Token | Family | Size | Weight | Letter-spacing | Used for |
|-------|--------|-----:|-------:|---------------:|----------|
| `display-xl` | EB Garamond | 60–80px | 500/700 | -1.2 to -2 | Page hero (`<h1>` on Home, Scholar, Diss detail) |
| `display-lg` | EB Garamond | 48px | 500 | -0.6 | Table headers (`<h1>` on Dissertations/Scholars/Committee) |
| `display-md` | EB Garamond | 28–32px | 500 | -0.3 to -0.5 | Section headings ("Recently catalogued", footer brand) |
| `title` | EB Garamond | 18–22px | 500 | -0.2 | Card titles, list-row titles |
| `title-italic` | EB Garamond italic | 14–18px | 400 italic | 0 | Author lines ("by …"), small attributions |
| `body` | Source Sans 3 | 14–18px | 400 | 0 | Body copy, table cells |
| `kicker` | JetBrains Mono | 11px | 500 | 0.14em UPPERCASE | "AN OPEN SCHOLARLY INDEX", section labels, table heads |
| `meta` | JetBrains Mono | 11–13px | 400 | 0 | Record IDs, years, counts, metadata |

### Spacing

The prototype uses a loose 4px grid; the values that recur most are: `4 6 8 10 12 14 16 18 20 24 28 32 36 40 48 56 64 72 80`. Common patterns:

- **Page horizontal padding:** `64px` left/right on all screens
- **Section vertical padding:** `40–56px` between major sections
- **Card padding:** `22–28px`
- **Table cell padding:** `14–24px` (denser on mid-density tables, looser on data tables)
- **Type rhythm:** `8–14px` between label and value; `4–6px` between row and metadata

### Borders & rules

- **Hairline:** `1px solid var(--line2)` (soft, between table rows)
- **Hairline strong:** `1px solid var(--line)` (panel borders, around chips)
- **Section rule:** `2px solid var(--ink)` (under section headings, "Recently catalogued" etc.)
- **Accent rule:** `2px solid var(--accent)` (under accented sidebar headings)
- **Border radius:** `0` everywhere except avatar circles. The design uses sharp corners as part of its scholarly register; do not add radius.

### Shadows

The design is intentionally **flat**. No drop shadows on cards, no elevation. The only "shadow" is the `box-shadow` on the design canvas itself, which is preview chrome — do not port.

---

## Screen 1 · Home / Landing

### Purpose
Orient a researcher arriving at the site. Show what's new, the scale of the catalogue, and the most active advisors. Provide entry points to the table views.

### Layout
Top-to-bottom flow at `1280px` design width. All sections share `64px` horizontal padding.

```
[Header: brand + counts ─ nav row + search ────────]
[Hero (1.4fr) │ Featured this month (1fr)         ]   ← 72px top padding, gap: 80px
[Recently catalogued (2fr) │ Sidebar (1fr)        ]   ← gap: 64px
   sidebar = By the numbers + Heavy advisors + Field note
[Browse by decade │ Browse by field │ Contribute  ]   ← 3-col, gap: 48px
[Footer                                            ]
```

### Components

#### 1.1 Header (`ANav` in `archive.jsx`)
- Padding `28px 64px 24px`, bottom border `1px solid var(--line)`.
- Top row: brand block (left) + count block (right).
  - Brand: eyebrow `"EST. 2024 · VOL. I"` in mono, then `"The History Dissertation Database"` in EB Garamond 32px / weight 500 / letter-spacing -0.4.
  - Counts: 3 lines in JetBrains Mono 12px, `var(--mute)`. Right-aligned. Real values from the DB (`Dissertation.count`, `Scholar.count`, `Advisor.count`).
- Nav row: 5 links (`Dissertations`, `Scholars`, `Committee Members`, `About`, `Contribute`) in mono caps, then a search input on the right.
  - Active link: `var(--accent)` color + `2px solid var(--accent)` bottom border.
  - Inactive: `var(--ink2)` color, transparent bottom border.
  - Search: `1px solid var(--line)`, padding `6px 12px`, `var(--paper3)` background, 13px input, search SVG icon left.

#### 1.2 Hero
Two-column grid `1.4fr 1fr`, gap `80px`, top-aligned.

**Left column:**
- Kicker: `"AN OPEN SCHOLARLY INDEX"` — JetBrains Mono 11px / 500 / 0.14em / `var(--accent)`.
- `<h1>`: EB Garamond 60px / 500 / line-height 1.05 / letter-spacing -1.2. Three lines:
  > A catalogue of *history*
  > and the scholars who
  > shaped its writing.
  - The word "history" is wrapped in `<em>` and colored `var(--accent)`.
- Sub-paragraph: 18px Source Sans 3, `var(--ink2)`, max-width `540px`.
- Button row (gap 12px, margin-top 32px):
  - Primary: `var(--ink)` background, `var(--paper)` text, mono caps, `12px 22px` padding.
  - Secondary: transparent background, `1px solid var(--ink)`, `var(--ink)` text, same padding.

**Right column — "Featured this month" card:**
- `1px solid var(--line)`, `var(--paper3)` background, `28px` padding.
- Kicker (`var(--accent)`) + record ID line (mono 11px) + title (EB Garamond 26px / 500) + 3-line "by / at / under" attribution + soft hairline + abstract opening (italic EB Garamond 14px) + "Read full entry →" link.

#### 1.3 Recently catalogued + sidebar (mid section)
Two-column grid `2fr 1fr`, gap `64px`.

**Recently catalogued (left, 2fr):**
- Section header: `<h2>` EB Garamond 30px / 500 / -0.4, with "See all 142 →" mono link on the right. Bottom border `2px solid var(--ink)`, padding-bottom 12px.
- Row grid: `64px | 1fr | 170px`, gap `24px`, padding `22px 0`, bottom border `1px solid var(--line2)`.
  - Col 1: year, JetBrains Mono 13px / 600 / `var(--accent)`.
  - Col 2: title (EB Garamond 22px / 500 / -0.2) + author line (Source Sans 3 14px, author in `var(--accent)`, institution in `var(--ink2)` after a `var(--mute)` middot).
  - Col 3 (right-aligned): kicker "ADVISED BY" + advisor name in EB Garamond italic 14px.
- Show the 6 most recently catalogued dissertations.

**Sidebar (right, 1fr) — three stacked blocks:**

1. **By the numbers** — section header (mono kicker + `2px solid var(--ink)` underline). Then a 2-column grid of 6 stat cells. Each cell: `14px 0` padding, bottom border `1px solid var(--line2)`, big number in EB Garamond 30px / 500 / `var(--ink)`, label in mono caps 11px / `var(--mute)`. Stats: `12,418 dissertations`, `4,932 scholars`, `1,206 advisors`, `218 institutions`, `1965 first record`, `2024 most recent`.
2. **Heavy advisors · last decade** — same section-header treatment. Then a list of 5 ranked advisor links: `01` (mono 11px mute), name (EB Garamond 18px / 500), advised count (mono 12px / `var(--accent)`). Bottom border `1px solid var(--line2)` between rows.
3. **Field note** — block: `var(--paper2)` background, `1px solid var(--line)`, `22px` padding. Kicker "FIELD NOTE" in `var(--accent)`. EB Garamond 19px / 500 callout text ending with an `var(--accent)`-colored highlight ("Submit a correction."). Mono caps link to contributor guide below.

#### 1.4 Browse rails (3-col)
Three columns, gap `48px`, `0 64px 24px` padding:

1. **Browse by decade** — kicker + 5 rows: decade name (EB Garamond 22px) + count (mono 12px / mute), bottom hairline.
2. **Browse by field** — kicker + 8 rows: field name + em-dash (smaller density, EB Garamond 17px).
3. **Contribute** — `var(--paper2)` block, `1px solid var(--line)`, `24px` padding. Same shape as the field-note card but bigger headline (EB Garamond 22px).

#### 1.5 Footer (`AFooter`)
- `40px 64px 56px` padding, top border `1px solid var(--line)`, top margin `64px`, background `var(--paper2)`.
- 4-col grid `2fr 1fr 1fr 1fr`, gap `48px`.
- Brand block (col 1) + three link columns: Explore / About / Hosted at.

---

## Screen 2 · Dissertations table

### Purpose
The catalogue's primary index. Researchers filter, sort, and click through to records.

### Layout
```
[Header — same as Home, with "Dissertations" active]
[Table header section: kicker + h1 + count]
[Filter bar: filter chips + sort dropdown]
[Table: 5 columns, alternating row tint]
[Pagination]
[Footer]
```

### Components

#### 2.1 Table header section (`ATableHeader`)
- `56px 64px 28px` padding, bottom border `1px solid var(--line)`.
- Kicker `"CATALOGUE · PRIMARY INDEX"` (`var(--accent)`).
- `<h1>`: EB Garamond 48px / 500 / -0.6 — "Dissertations".
- Right-aligned mono count: `showing 1–18 of 12,418`.

#### 2.2 Filter bar (`AFilterBar`)
- `20px 64px` padding, bottom border `1px solid var(--line)`, background `var(--paper2)`. Flex row, gap `12px`, wrap.
- Each chip: mono 12px, padding `6px 12px`, `1px solid var(--line)`, transparent bg → `var(--ink)` bg + `var(--paper)` text when active. Caret `▾` at right, 50% opacity.
- Sort control on the right: same chip style, no caret, "Year ↓" text.
- Filters used: `Year`, `Field`, `Institution`, `Advisor`, `Region`.

#### 2.3 Table
- Full-width, `border-collapse: collapse`, font-size 14px.
- **Header row:** `2px solid var(--ink)` bottom border. Cells: mono caps 11px / 500 / `var(--mute)`, `14px 24px` padding, left-aligned. Columns: `Year | Title & Author | Institution | Advisor | Field`.
- **Body row:** `1px solid var(--line2)` bottom border. Alternating row tint: every other row gets `rgba(255,255,255,0.4)` background.
  - **Year cell:** JetBrains Mono 13px / `var(--ink2)`, width 80px, top-aligned, padding `18px 24px`.
  - **Title cell:** EB Garamond 18px / 500 / line-height 1.3 for the title (link, `var(--ink)`, no underline). Below: `by` (Garamond italic) + author (`var(--accent)` link) + middot + record ID (mono 11px / `var(--mute)`).
  - **Institution cell:** Source Sans 14px, `var(--ink2)`, max-width 180px.
  - **Advisor cell:** link, `var(--ink)`, `1px dotted var(--mute)` underline.
  - **Field cell:** chip — mono 11px, `1px solid var(--line)`, `2px 8px` padding, `var(--paper3)` background.

#### 2.4 Pagination (`APagination`)
- `32px 64px` padding, centered flex row, gap 8px.
- Buttons `8px 14px` padding, min-width 36px, mono 13px. Active: `var(--ink)` bg / `var(--paper)` text; inactive: transparent bg, `1px solid var(--line)`. Ellipsis `…` and chevrons `‹` / `›` use the same style.

---

## Screen 3 · Scholars table

Identical chrome to Dissertations. Differences:

- Kicker `"PEOPLE · AUTHORS OF DISSERTATIONS"`, h1 `"Scholars"`.
- Filter chips: `Status`, `Institution`, `Field`, `Cohort`.
- Columns: `Scholar | Institution | Position | Fields | Advised | Committee`.
- **Scholar cell:** flex row with 36×36 circle avatar (`var(--avatar)` bg, `1px solid var(--line)`, initials in EB Garamond italic 14px / `var(--accent)`), then name (EB Garamond 18px / 500 link).
- **Position cell:** EB Garamond italic 13px / `var(--ink2)`.
- **Fields cell:** wrap-flex of chips (same as table 2).
- **Advised / Committee cells:** JetBrains Mono 13px. Show em-dash for zero.

---

## Screen 4 · Committee Members table

Same chrome again. Differences:

- Kicker `"PEOPLE · ADVISORS AND READERS"`, h1 `"Committee Members"`.
- Filters: `Institution`, `Field`, `Active years`.
- Columns: `Member | Institution | Fields | Advised | Served on | Active span | (action)`.
- **Member cell:** big EB Garamond 19px / 500 link, no avatar.
- **Advised cell:** mono 14px / 600 / `var(--accent)` — visually emphasized because this is the headline number.
- **Served on / span cells:** mono 12–13px / `var(--ink)` or `var(--ink2)`.
- **Action cell (last col):** right-aligned, mono caps 10px / `var(--accent)` link "Lineage →".

---

## Screen 5 · Single dissertation

### Purpose
Show one record in full: title, author, advisor, committee, abstract, metadata, related work.

### Layout
```
[Header]
[Breadcrumb: Dissertations / D-XXXX-XXXX]
[Hero block (1.5fr) │ Metadata sidebar (1fr) — bottom border]
[Abstract (1.5fr) │ Lineage panel (1fr)]
[Related dissertations — 3 cards, full width]
[Footer]
```

### Components

#### 5.1 Breadcrumb
`20px 64px 0` padding. Mono 12px, `var(--mute)`. `Dissertations / D-2019-0341`.

#### 5.2 Hero (two-col `1.5fr 1fr`, gap 64px, padding `40px 64px 56px`, bottom border `1px solid var(--line)`)

**Left:** kicker `"DISSERTATION · 2019"` + `<h1>` EB Garamond 44px / 500 / line-height 1.1 / -0.5 + attribution line (18px Garamond) with "by [author]" link and "at [institution]".

**Right:** metadata table — `1px solid var(--line)` left border, `32px` left padding. `<table>` with two columns:
- Label col: mono caps 11px / 500 / `var(--mute)`, width 110px, top-aligned, `paddingTop: 6px`.
- Value col: `var(--ink)`, `paddingTop: 6px`. Line-height 1.8.
- Rows: `Record ID`, `Granted`, `Institution`, `Advisor`, `Committee` (comma-joined links), `Field`, `Keywords` (mono small chips, comma-separated inline).
- Below table: button row — primary "Cite this" + secondary "Suggest edit", same button style as Home hero.

#### 5.3 Abstract block (two-col, padding `48px 64px`)

**Left (1.5fr) — Abstract:**
- Kicker `"ABSTRACT"`.
- Body: EB Garamond 19px / line-height 1.65 / `var(--ink)`. First paragraph has a drop-cap: the first letter is a `float: left` Garamond span at 64px / line-height 0.85 / `var(--accent)` / 500, with `marginRight: 10` and `marginTop: 6`.

**Right (1fr) — Lineage at a glance:**
- Kicker "LINEAGE AT A GLANCE".
- Panel: `1px solid var(--line)`, `var(--paper3)` background, `20px` padding.
  - "Advised by" (mono 11px mute) → advisor name (Garamond 20px / 500).
  - Indented `borderLeft: 2px solid var(--accent)` block: alternating "Who was advised by" labels (mono 11px) and names (Garamond 16px). Last name shown as Garamond italic 16px / mute.
- "Open full genealogy →" link below in mono caps `var(--accent)`.

#### 5.4 Related dissertations
- Section kicker `"RELATED DISSERTATIONS"`, then `grid-template-columns: repeat(3, 1fr)`, gap 28px.
- Each card: `2px solid var(--ink)` top border, `16px` top padding. Meta line (mono 11px mute) + title (Garamond 20px / 500 / 1.25) + "by [author]" italic.

---

## Screen 6 · Scholar profile

### Purpose
Profile of a committee member (advisor) — shows their dissertations advised, committees served, and lineage.

### Layout
```
[Header]
[Breadcrumb: Scholars / Name]
[Profile head: avatar │ name + meta │ stat strip — bottom border]
[Tab bar: Advised | Committees | Lineage | About]
[Main column (2fr): dissertations list │ Sidebar (1fr): lineage + co-readers]
[Footer]
```

### Components

#### 6.1 Profile head (3-col grid `120px 1fr auto`, gap 32px, padding `40px 64px`)

- **Avatar:** 120×120 circle, `var(--avatar)` bg, `1px solid var(--line)`, initials in EB Garamond italic 40px / `var(--accent)`.
- **Name block:** kicker `"COMMITTEE MEMBER · ACTIVE 1992–2024"` (`var(--accent)`), `<h1>` EB Garamond 52px / 500 / -0.7, then institution + fields (Garamond 17px / `var(--ink2)`).
- **Stat strip:** 3 right-aligned stats — `Advised | Served on | Lineage depth`. Each stat: EB Garamond 36px / 500 number above mono caps 11px label.

#### 6.2 Tab bar
- `20px 64px` padding, bottom border `1px solid var(--line)`, gap 28px.
- Tab labels in mono caps 11px / 500 / 0.14em. Active: `var(--accent)` color + `2px solid var(--accent)` bottom border. Inactive: `var(--ink2)` color, transparent border.
- Tabs: `Dissertations advised`, `Committees served`, `Lineage`, `About`.

#### 6.3 Main + sidebar (2-col, padding `36px 64px`, gap 48px)

**Main (2fr) — Dissertations advised:**
- Kicker "14 DISSERTATIONS ADVISED — RECENT".
- 6 rows, each `18px 0` padding, bottom border `1px solid var(--line2)`. Row layout: `[year 50px] [title + author block (flex 1)] [field chip — shrink 0]`.
  - Year: mono 13px / `var(--mute)`, width 50px, paddingTop 4px.
  - Title: Garamond 19px / 500 / 1.3. Below: 13px sans, author + middot + institution.
  - Field chip: same style as table chips.
- "See all 14 →" link in mono caps below.

**Sidebar (1fr) — Lineage card + Co-readers:**

- **Lineage card:** `1px solid var(--line)`, `var(--paper3)` background, `24px` padding. Kicker "LINEAGE" (`var(--accent)`). Inside: same pattern as Diss page — "advised by" labels and names indented with `2px solid var(--accent)` left border, alternating Garamond / mono.
- **Frequent co-readers:** kicker "FREQUENT CO-READERS", then 4 rows of Garamond 16px name + mono small count, separated by `1px solid var(--line2)`.

---

## Interactions & Behavior

The prototype is intentionally non-interactive (placeholder links go to `#`). To implement:

### Navigation
- **Header nav links** route to `dissertations`, `scholars`, `committee`, `about`, `contribute` URLs.
- **Search input** (header) — submit to a `q=` query string; results page can reuse the table chrome.
- **Table row links** (title, author, advisor) all go to the matching detail page (`/dissertations/<id>`, `/scholars/<slug>`).
- **Pagination** is server-side; the active page just has `aria-current="page"`.

### Filter chips
Pressing a chip should open a filter popover (not designed yet — fall back to a `<select>` or native popover if you need a quick implementation). The active state on a chip is purely visual; the chip text reflects the current filter value, e.g. `Year: 2015–2024`.

### Sort
The `Year ↓` chip on the right of the filter bar toggles direction. Document the URL convention if you adopt one (`?sort=year&dir=desc`).

### States to design
- **Loading:** if you do any client-side filtering, show a subtle skeleton or just a stable layout. The Bone palette has a clear `var(--paper3)` tint that works for skeleton blocks.
- **Empty:** "No dissertations match this filter" — Garamond 22px italic centered, with a "Clear filters" link in `var(--accent)`.
- **Error:** Same shape, but with `var(--accent)` border-left on a `var(--paper2)` block.

### Hover states (already implied by `<a>`s)
- Links default to inherited text color with no underline.
- Add a hover treatment: shift to `var(--accent)` color OR a 1px solid underline at `text-underline-offset: 3px`. Pick one and apply consistently.
- The advisor-link "dotted underline" is intentional — it distinguishes person-links inside a row from the row's primary title link.

### Responsive
Designs are at `1280px`. For narrower viewports:
- Below ~1024px: collapse the 2-col home hero into a single column, stack the metadata sidebar below the abstract on the dissertation page, hide the column with lower priority (e.g. "Institution" or "Field") in tables and reveal it in an expanded row.
- Below ~640px: stack everything; the table becomes a card list (each row's cells stack vertically inside one card).
- Keep `64px` page padding for desktop, drop to `24px` for tablet, `16px` for mobile.

---

## State Management

Most state is server-rendered. Client-side state needed:
- **Filter popover open/closed.**
- **Sort direction.**
- **Mobile nav menu open/closed** (you'll need to add a hamburger trigger when you do the mobile pass).

A small `data-*` API on the existing template + a few `addEventListener` calls is plenty; no need to introduce a framework.

---

## Assets

The prototype uses:
- **Avatars / seals:** placeholder circles with initials. In production, render real images if you have them; fall back to the initials-on-`var(--avatar)` pattern.
- **Search icon:** inline SVG (`<circle>` + `<path>`) — copy directly.
- **No other icons or images.** The design relies on type and rules; do not add stock iconography.

---

## Files included in this handoff

| File | Purpose |
|------|---------|
| `README.md` | This file. |
| `preview.html` | Renders the six screens at full size with a top picker. Open in any browser. |
| `screenshots/` | One PNG per screen (top-of-page captures) for quick reference. |
| `archive.html` | Original review canvas (pan/zoom across all six artboards). |
| `archive.jsx` | The React components for all six screens. Source of truth for colors, type, layout. |
| `data.jsx` | Sample data (fabricated; do not ship). Shows the shape of dissertations / scholars / committee records. |
| `design-canvas.jsx` | Preview infrastructure for `archive.html` — not part of the design. |

When implementing, the file to read most carefully is **`archive.jsx`**. Every layout choice, color, and font size is in there as inline-style values. Translate component-by-component to Django templates, lifting values directly.
