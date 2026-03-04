# CHANGELOG.md

> For feature specifications, business rules, and domain models, see [SPEC.md](./SPEC.md). For technical implementation details, architecture, and developer documentation, see [AGENTS.md](./AGENTS.md).

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

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