# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

History Dissertation Database — a Django web application developed by RRCHNM at George Mason University to track history dissertations and explore scholarly genealogies (advisor/advisee networks).

## Commands

```bash
# Development server
make preview                          # poetry run python manage.py runserver

# Database
make mm                               # makemigrations
make migrate                          # migrate
poetry run python manage.py loaddata db.json   # load initial data

# CSS (run in a separate terminal during development)
make tailwind-start                   # watch mode
make tailwind-build                   # one-time build

# Testing
pytest
pytest dissdb/tests.py::TestName      # single test

# Linting / formatting
ruff check .
ruff format .
isort .
djhtml templates/                     # format HTML templates

# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Data management
poetry run python manage.py import_aha_data /path/to/aha-data/
poetry run python manage.py find_duplicates --threshold 0.9 --dry-run
```

## Environment

Copy `.env` and configure:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` — PostgreSQL connection
- `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`

Node.js version is pinned via Volta (`node: 18.15.0`) in `package.json`.

## Architecture

### Django project layout

- `config/` — Django project settings, root URL conf, ASGI/WSGI
- `dissdb/` — sole Django app containing all models, views, admin, API
- `theme/` — Tailwind CSS app (managed by `django-tailwind`)
- `templates/` — Django templates (top-level, plus `dissertations/` subdirectory)
- `aha-data/` — source CSV files from the American Historical Association

### Data model

All models carry two cross-cutting concerns:
1. **`source` FK → `Source`** — records data provenance (organization, person, etc.)
2. **`history = HistoricalRecords()`** — full audit trail via `django-simple-history`

Core models (`dissdb/models.py`):
- `School` — institutions; holds AHA school ID
- `Scholar` — researchers; name split into `name_first/middle/last/suffix`; optional ORCID; `aha_name` stored read-only as received from AHA data
- `ScholarWebsite` — web presence (personal, department, social media)
- `Dissertation` — linked to one `Scholar` (author) and one `School`; AHA IDs stored read-only
- `DissertationLink` — ProQuest/PDF/institutional URLs for a dissertation
- `CommitteeMember` — join between `Scholar` and `Dissertation` with `role` = `chair` | `reader`; the **chair role encodes the advisor relationship** used for genealogy traversal
- `DuplicateCandidate` — pairs of potentially duplicate `Scholar` records with confidence score and review status

### Scholarly genealogy / visualization

The advisor–advisee tree is built from `CommitteeMember` records where `role="chair"`. Two endpoints serve tree data for a given scholar PK:
- `get_viz_data` (`views.py`) — shallow: advisor → scholar → direct advisees
- `get_viz_data_complex` (`views.py`) — deep: walks up to the root ancestor via `traverse()`, then traverses the full subtree downward; returns slash-delimited path strings

### API

Django REST Framework powers two endpoints under `/scholars/api/`:
- `ScholarListAPI` — paginated scholar list
- `ScholarDetailAPI` — single scholar detail

### Duplicate detection

`dissdb/management/commands/find_duplicates.py` uses `difflib.SequenceMatcher` with last-name weighting (2×) and a 60% last-name pre-filter to efficiently scan for near-duplicate `Scholar` records. Results are written to `DuplicateCandidate` for manual review in Django Admin. See `DEVNOTES.md` for full details.

### Admin

`dissdb/admin.py` provides rich `SimpleHistoryAdmin` subclasses for all models. `DuplicateCandidateAdmin` includes side-by-side name comparison, ORCID conflict warnings, and inline dissertation activity for both candidates.
