# SPEC.md

> For technical implementation details, architecture, and developer documentation, see [AGENTS.md](./AGENTS.md).

---

## Table of Contents

- [Overview](#overview)
- [Users & Roles](#users--roles)
- [Business Rules](#business-rules)
- [Features](#features)
- [User Flows](#user-flows)
  - [Flow 1: Browsing and Filtering Dissertations](#flow-1-browsing-and-filtering-dissertations)
  - [Flow 2: Exploring a Scholar's Genealogy](#flow-2-exploring-a-scholars-genealogy)
- [Out of Scope](#out-of-scope)
- [Open Questions](#open-questions)

---

## Overview

The History Dissertation Database is a public research tool that aggregates dissertation records from the American Historical Association and other sources, and models the scholarly genealogies that connect historians across institutions and generations.

**Problem it solves:** The historical profession has no central, queryable record of which scholars trained which students. Institutional memory is fragmented across department websites, ProQuest, and the AHA's own data exports. Researchers wanting to trace intellectual lineages or discover academic networks have no good tool.

**Core value proposition:** By modeling dissertation committee relationships — specifically the chair (advisor) role — the database makes it possible to traverse entire advisor–advisee trees and see how scholarly influence propagates through the field over time.

**Primary goals:**
1. Provide a browsable, filterable public interface to dissertation records
2. Expose individual scholar profiles showing their advisor, their own dissertation, and their advisees
3. Visualize scholarly genealogy trees
4. Maintain high data quality through provenance tracking, audit history, and a duplicate-detection workflow
5. Offer a REST API for downstream research use

**Target audience:** Digital historians, academic researchers studying the historical profession, RRCHNM staff managing the data.

---

## Users & Roles

### Public Visitor (unauthenticated)
- Accesses all browsable views: dissertation list, committee member list, scholar profiles, genealogy visualizations
- Can filter and search records
- Can export genealogy trees as PNG images
- Cannot edit any data

### Staff / Admin (authenticated Django admin user)
- Full read/write access through Django Admin
- Can create, edit, and delete Scholar, School, Dissertation, CommitteeMember, Source, ScholarWebsite, and DissertationLink records
- Can review and adjudicate DuplicateCandidate records
- Can run data management commands (`import_aha_data`, `find_duplicates`)
- Sees full change history on every record via django-simple-history

| Action | Public | Admin |
|--------|--------|-------|
| Browse dissertations | Yes | Yes |
| Browse committee members | Yes | Yes |
| View scholar profiles | Yes | Yes |
| View genealogy visualizations | Yes | Yes |
| Export tree as PNG | Yes | Yes |
| Access REST API | Yes | Yes |
| Create / edit / delete records | No | Yes |
| Review duplicate candidates | No | Yes |
| View record history | No | Yes |
| Run management commands | No | Yes (CLI) |

---

## Business Rules

### Scholar Records
- A Scholar must have a non-empty `name_first` and `name_last`.
- `name_middle` and `name_suffix` are optional.
- `orcid` must match the format `0000-0000-0000-0000` if provided.
- `aha_name` is read-only; it preserves exactly the name string received from the AHA dataset and must not be edited manually.
- `aha_scholar_id` must be unique across all Scholar records if provided.

### Dissertation Records
- A Dissertation must have a `title`, a `year`, an `author` (Scholar), and a `school` (School).
- `year` must be between 1700 and the current calendar year (inclusive).
- `aha_dissertation_id` must be unique if provided.
- A Scholar may author at most one Dissertation in the current data model (the `author` FK on Dissertation is not unique-constrained, but the application assumes one dissertation per author for genealogy traversal).

### Committee Membership
- A CommitteeMember record links a Scholar to a Dissertation in a `chair` or `reader` role.
- The `chair` role is the authoritative encoding of the advisor relationship. Genealogy traversal uses only `role="chair"` records.
- There is no enforced limit on the number of committee members per dissertation or the number of dissertations a scholar may chair.

### Data Provenance
- Every record must carry a `source` FK pointing to a `Source` record.
- The default source (id=1) represents the AHA.
- Source records track the organization, department, or person responsible for contributing a piece of data.

### Duplicate Detection
- The `find_duplicates` command compares all Scholar pairs whose last names share ≥ 60% similarity (pre-filter), then scores the full name using a weighted algorithm (last name counts double).
- Pairs scoring ≥ 90% similarity (configurable) are stored as `DuplicateCandidate` records with `reviewed=False`.
- Running the command multiple times is safe; `get_or_create` prevents duplicate candidate entries.
- A candidate is marked `is_duplicate=True` or `is_duplicate=False` by an admin reviewer. Merging duplicate Scholar records into one is not yet automated (see Out of Scope).

### Record Deletion
- Deletion of Scholar and School records is protected (`on_delete=PROTECT`) if related Dissertation or CommitteeMember records exist. Records must be reassigned or deleted first.
- DissertationLink and ScholarWebsite records cascade-delete when their parent Dissertation or Scholar is deleted.

---

## Features

### Feature: Dissertation List & Filtering

**Description:** A filterable, sortable, paginated table of all dissertations in the database.

**Functionality:**
- Filter by dissertation title (case-insensitive substring match)
- Filter by author last name (case-insensitive substring match)
- Filter by author first name (case-insensitive substring match)
- Filter by year range (min and max year)
- Filter by school (exact match, dropdown)
- Results displayed in a django-tables2 table with sortable columns
- Pagination with configurable page size

**URL:** `/dissertations/`

---

### Feature: Committee Member List & Filtering

**Description:** A filterable, paginated table of all committee membership records.

**Functionality:**
- Filter by scholar last name (exact match)
- Filter by scholar first name (exact match)
- Filter by dissertation title (case-insensitive substring match)
- Displays scholar name, role (chair/reader), and associated dissertation

**URL:** `/committeemembers/`

---

### Feature: Scholar Profile Page

**Description:** A detail page for an individual scholar showing their full academic context.

**Functionality:**
- Displays scholar's full name, ORCID (linked to orcid.org), and current affiliation
- Shows the scholar's own dissertation (title, year, school) if one exists
- Shows the scholar's advisor (dissertation committee chair) if one is recorded
- Shows a list of the scholar's advisees (dissertations where this scholar served as chair)
- Shows associated website links (personal, department, social media)
- Shows a ProQuest or other access link to the dissertation if available
- Links to the genealogy visualization for this scholar

**URL:** `/scholar/<id>`

**Edge cases:**
- Scholar exists only as a committee member (no dissertation of their own): dissertation and advisor fields show "information not available"
- Scholar has no committee chair recorded: advisor shows "information not available"
- Scholar has no websites or dissertation links: those sections are hidden

---

### Feature: Scholarly Genealogy Visualization

**Description:** An interactive tree visualization showing the advisor–advisee chain centered on a scholar.

**Functionality:**
- `get_viz_data` (shallow): shows the scholar's advisor → scholar → direct advisees
- `get_viz_data_complex` (full): traverses up to the root ancestor (scholar with no recorded advisor), then renders the full descendant tree from that root
- Client-side rendering from slash-delimited path strings returned by the API
- User can click nodes to navigate to scholar profiles
- User can download the rendered visualization as a PNG

**URLs:** `/api/get_viz_data/<pk>`, `/api/get_viz_data_complex/<pk>`

---

### Feature: REST API

**Description:** A read-only JSON API for accessing scholar data programmatically.

**Functionality:**
- `GET /scholars/api/` — paginated list of all scholars; each record includes `aha_scholar_id` and `name_full`
- `GET /scholars/api/<id>/` — single scholar detail with the same fields

---

### Feature: Django Admin Data Management

**Description:** The primary interface for RRCHNM staff to manage all records and data quality.

**Functionality:**
- Full CRUD for Scholar, School, Dissertation, CommitteeMember, Source, ScholarWebsite, DissertationLink
- Scholar admin shows authored dissertation count and committee membership count in list view; inline tables for related records
- Dissertation admin shows committee size; committee members editable inline
- DuplicateCandidate admin provides side-by-side name comparison, ORCID conflict warnings, dissertation activity for both candidates, and inline `reviewed`/`is_duplicate` editing from the list view
- Change history viewable on every record (django-simple-history)

---

### Feature: AHA Data Import

**Description:** A management command to ingest dissertation data from AHA CSV exports.

**Functionality:**
- `python manage.py import_aha_data /path/to/aha-data/` reads CSV files from the AHA dataset directory
- Creates or updates Scholar, School, Dissertation, and CommitteeMember records
- Preserves original AHA IDs in read-only fields for traceability

---

## User Flows

### Flow 1: Browsing and Filtering Dissertations

**Goal:** Find dissertations matching a research interest.

**Starting point:** User navigates to `/dissertations/`.

**Steps:**
1. User sees a paginated table of all dissertations, sortable by title, author, year, school.
2. User enters a keyword in the "Dissertation Title" field and/or selects a school from the dropdown.
3. User optionally enters a year range.
4. Table updates to show matching results.
5. User clicks a column header to sort results.
6. User clicks the author name link to navigate to a scholar profile.

**Success outcome:** User finds the dissertation(s) they were looking for and can navigate to the scholar or school for more context.

**Error paths:**
- No results matching filters: table shows empty state.

---

### Flow 2: Exploring a Scholar's Genealogy

**Goal:** Understand who trained a given historian and who that historian in turn trained.

**Starting point:** User arrives at a scholar profile page (via dissertation list, direct URL, or search).

**Steps:**
1. User sees the scholar's name, dissertation, and advisor name (with a link to the advisor's profile).
2. User sees the list of the scholar's advisees with links to their profiles.
3. User clicks "View Genealogy Tree" (or the visualization link) to load the full tree.
4. The tree visualization renders, showing the scholar's full intellectual lineage from root ancestor to all descendants.
5. User clicks a node to navigate to that scholar's profile.
6. User clicks "Download as PNG" to save the visualization.

**Success outcome:** User can trace the scholarly lineage of a historian across multiple generations in a single view.

**Error paths:**
- Scholar has no recorded advisor and no advisees: visualization shows a single node.
- Genealogy data returns slowly for a large tree: loading state is shown.

---

## Out of Scope

### Not yet implemented (potential future work)
- Dissertation detail pages (the route and view are commented out in the current codebase)
- Automated merging of confirmed duplicate Scholar records via the admin interface
- Full-text search across dissertation abstracts
- User-facing search (beyond the filter forms)
- Mobile-optimized views
- Public user accounts or contributed data submission
- Export of filtered results as CSV or JSON
- Pagination/filtering on the genealogy tree when trees are very large
- Institution-level analytics or aggregate views

### Explicitly excluded
- Payment or subscription features
- User-to-user messaging
- Real-time collaboration on records

---

## Open Questions

### Data Model Questions
- **Q:** Should a Scholar be allowed to author more than one Dissertation?
  - **Context:** The current genealogy traversal assumes one dissertation per scholar (`Dissertation.objects.get(author=...)`). Multiple would break this.
  - **Status:** Unresolved; the unique constraint is not enforced at the DB level.

### Duplicate Resolution
- **Q:** What is the correct workflow for merging two confirmed-duplicate Scholar records?
  - **Context:** Confirming a duplicate in the admin does not yet trigger any merge logic. Related records (Dissertation, CommitteeMember) remain attached to the original Scholar records.
  - **Options:** Admin action that reassigns all FKs and deletes the redundant record; or a separate merge management command.
  - **Status:** Identified as a potential enhancement in `DEVNOTES.md`; not yet designed.

### API Scope
- **Q:** Should the API expose Dissertation and CommitteeMember data, not just Scholar?
  - **Context:** The current API is intentionally minimal. Downstream research use cases may need richer data.
  - **Status:** Open; no immediate plan.

---

*Last Updated: 2026-03-03*
*This document is maintained for AI agent context and onboarding.*