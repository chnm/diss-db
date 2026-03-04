# CHANGELOG.md

> For feature specifications, business rules, and domain models, see [SPEC.md](./SPEC.md). For technical implementation details, architecture, and developer documentation, see [AGENTS.md](./AGENTS.md).

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

## [0.2.0] — 2026-03-04

### Added

- **Scholars list page**: New `/scholars/` page with a filterable, sortable table of all scholars. Filter by last name, first name, and current affiliation. Authenticated users see an "+ Add Scholar" button.
- **Scholar create form**: Dedicated `/scholars/create/` form for adding new scholars directly from the Scholars page.
- **Committee member management on dissertation edit**: The dissertation edit form now includes a Committee Members section. Each row has a name autocomplete (backed by the scholar search API) and a role selector (chair/reader). Rows can be added, removed, and saved inline. A "+ New Scholar" modal allows creating a scholar on the fly without leaving the page.
- **Dissertation create from scholar profile**: Authenticated users see an "Add Dissertation" button on a scholar's profile page when no dissertation record exists yet. Submitting the form pre-fills the author and redirects back to the profile.
- **Scholar search API**: `GET /scholars/api/?q=` now accepts a query string. Terms are split on spaces and matched with `icontains` across first, middle, and last name fields, so queries like "John Smith" return the expected results. Results are capped at 50 and returned without pagination wrapping.
- **Scholar create API**: `POST /scholars/api/create/` (login required) creates a scholar from name fields and returns `{id, name_full}`, used by the dissertation edit modal.
- **Readers on scholar profile**: The scholar detail page now shows a Readers section (committee members with `role=reader`) alongside the existing Advisor and Advisees sections.
- **Footer auth controls**: Footer now shows the current username, an Admin link, and a Log out button (POST form) for authenticated users, or a Log in link pointing back to the current page for anonymous users. The RRCHNM wordmark is now a clickable link.

### Fixed

- **Dissertation table horizontal scroll**: Switched `DissTable` to `table-fixed` with percentage column widths so long dissertation titles wrap rather than pushing the table wider than the viewport.
- **Committee member formset prefix collision**: `DissertationLinkFormSet` and `CommitteeMemberFormSet` now use explicit prefixes (`links` / `cm`). Previously the JS `+ Add member` button incremented the wrong `TOTAL_FORMS` counter, causing the Links formset to demand an extra required row on every save.
- **Dissertation edit JS not executing**: The `<script>` block in `dissertation_edit.html` was placed after `{% endblock main %}` and was being silently discarded by Django's template inheritance. Moved inside the block so autocomplete, the add-member button, and the new-scholar modal all work correctly.
- **Scholar detail page crash for new scholars**: The scholar detail view was calling `self.get_object()` a second time inside `get_context_data`, running the slug-matching loop again over the full scholar table. The loop has no `order_by`, so on a second call it could return a different record, leaving `self.object` stale and `scholar_detail.id` as `None`. Refactored to use `self.object` directly throughout. Added a `{% if scholar_detail.id %}` guard around the visualization fetch URLs to prevent `NoReverseMatch` for scholars without a saved pk.

## [0.1.0] — 2025-03-03

### Added

- **Source model for data provenance** (PR #18): Introduced a `Source` model to track the origin of every record (organization, department, person, or other). All core models (`School`, `Scholar`, `Dissertation`, `CommitteeMember`, `ScholarWebsite`, `DissertationLink`) now carry a `source` FK, defaulting to the AHA source record. Enables auditing of where each piece of data came from.
- **Audit trail via django-simple-history** (PR #18): Added `HistoricalRecords()` to all models so that every create, update, and delete is logged with the responsible user and timestamp. Admin interfaces updated to use `SimpleHistoryAdmin`.
- **`ScholarWebsite` and `DissertationLink` models** (PR #28): Added structured storage for scholar web presence (personal site, department profile, social media) and dissertation access links (ProQuest, institutional repository, PDF). Both are managed inline in the Django admin.
- **Duplicate scholar detection system** (PR #12): Implemented a `find_duplicates` management command that uses `difflib.SequenceMatcher` with weighted last-name scoring to identify near-duplicate `Scholar` records. Results are written to a new `DuplicateCandidate` model for human review.
- **`DuplicateCandidate` admin interface** (PR #12): Rich admin view for reviewing candidate pairs side-by-side, including name diff highlighting, ORCID conflict warnings, and inline dissertation/committee activity for each candidate.
- **Scholarly genealogy tree visualization** (PR #11): Added function-based views (`get_viz_data`, `get_viz_data_complex`) that return slash-delimited path strings representing advisor–advisee chains, consumed by a client-side tree visualization. Users can export the rendered SVG as a PNG.
- **`get_absolute_url` on `Scholar` and `Dissertation`** (PR #12): Enables reverse URL lookups from model instances, used throughout the admin and templates.
- **CI/CD pipeline** (PR #9): GitHub Actions workflow builds and publishes a Docker image to `ghcr.io` on push to `main` or `preview`, then deploys to `dissdb.dev.rrchnm.org`.
- **Pre-commit hook configuration** (PR #9): Added `.pre-commit-config.yaml` enforcing Ruff (lint + format), isort, djhtml, and standard file hygiene checks.
- **Cookiecutter-based project structure** (PR #9): Migrated from the original ad-hoc layout to a structured Django project with `config/` for settings and `dissdb/` as the sole application module.
- **Dynamic pagination** (PR #10): Dissertation and committee member list views now support configurable page sizes via URL parameters.

### Fixed

- **Advisor query logic** (PR #10, PR #12): Corrected broken queryset logic that looked up advisors by `aha_scholar_id`; replaced with `id`-based lookups throughout `views.py` to match the normalized data model.
- **Genealogy path highlighting** (PR #10): Fixed a bug where the selected path in the tree visualization was not highlighted correctly.

### Changed

- **Removed redundant duplicate `Scholar` records** (PR #17): Ran a cleanup migration to eliminate duplicate entries introduced during the initial AHA data import.
- **Merged detail and list view templates** (PR #28): Consolidated scattered view and template files into a coherent structure under `templates/dissertations/`.

### Documentation

- Added `README.md` with quick-start, data management, API usage, and project structure sections.
- Added `DEVNOTES.md` documenting the duplicate detection algorithm, workflow, and potential enhancements.