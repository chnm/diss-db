# Developer Notes: Duplication Detection System

## Overview

The dissertation database includes a duplication detection system designed to identify potential duplicate scholar records. The system combines automated string similarity algorithms with a manual review workflow to ensure data quality. We rely on `difflib.SequenceMatcher` for identification detection.

## Architecture

### Components

1. **Detection Algorithm** (`dissdb/management/commands/find_duplicates.py`)
2. **Database Model** (`dissdb/models.py` - `DuplicateCandidate`)
3. **Admin Interface** (`dissdb/admin.py` - `DuplicateCandidateAdmin`)

## How Duplicate Detection Works

### 1. String Similarity Algorithm

The system uses a multi-factor similarity calculation:

```python
def calculate_similarity(scholar1, scholar2):
    # 1. Normalize names (remove punctuation, lowercase)
    # 2. Calculate similarity scores for:
    #    - Full normalized names
    #    - Last names (weighted double - most important)
    #    - First names
    #    - Middle names (special initial handling)
    #    - AHA names (if available)
    # 3. Return average of all scores
```

**Key Features:**
- **Last name priority**: Last name similarity is weighted double since it's the most reliable identifier
- **Middle name intelligence**: Handles cases where one record has initials and another has full middle names
- **Normalization**: Removes punctuation and converts to lowercase for consistent comparison
- **AHA integration**: Uses original AHA dataset names when available

### 2. Performance Optimizations

- **Quick filter**: Only performs full comparison if last names have >60% similarity
- **Batch processing**: Processes scholars in chunks with progress reporting
- **Duplicate prevention**: Uses `get_or_create()` to avoid duplicate candidate entries

### 3. Database Schema

```sql
CREATE TABLE dissdb_duplicatecandidate (
    id INTEGER PRIMARY KEY,
    scholar_1_id INTEGER REFERENCES dissdb_scholar(id),
    scholar_2_id INTEGER REFERENCES dissdb_scholar(id),
    confidence_score REAL,  -- 0.0 to 1.0
    created_at DATETIME,
    reviewed BOOLEAN DEFAULT FALSE,
    is_duplicate BOOLEAN NULL,  -- NULL=pending, TRUE/FALSE=reviewed
    notes TEXT,
    UNIQUE(scholar_1_id, scholar_2_id)
);
```

## Usage Workflow

### 1. Running Detection

**Note**: Running detection on the full database may take quite some time.

```bash
# Basic usage - finds all duplicates above 90% threshold
poetry run python manage.py find_duplicates

# Custom threshold
poetry run python manage.py find_duplicates --threshold 0.85

# Dry run to preview results
poetry run python manage.py find_duplicates --dry-run

# Limit for testing
poetry run python manage.py find_duplicates --limit 1000

# Combine for various checks
poetry run python manage.py find_duplicates --limit 1000 --dry-run --threshold 0.9
```

### 2. Manual Review

If `--dry-run` is not passed to `find_duplicates`, the duplicate records are written to the `DuplicateCandidate` model for review within Django Admin.

1. **Access Admin**: Navigate to Django admin → Duplicate Candidates
2. **Review Queue**: Candidates sorted by confidence score (highest first)
3. **Compare Details**: Admin interface shows:
   - Side-by-side name comparison with highlighting
   - Full scholar details for both candidates
   - Dissertation and committee activity
   - ORCID conflict warnings
4. **Make Decision**: Mark as duplicate/not duplicate with notes
5. **Track Progress**: Filter by reviewed/unreviewed status

## Technical Implementation Details

### String Similarity Method

Uses Python's `difflib.SequenceMatcher` for character-level similarity scoring.

### Middle Name Handling

```python
def check_middle_name_similarity(middle1, middle2):
    # Special logic for comparing:
    # - "J" vs "John"
    # - "M.K." vs "Michael Kenneth"
    # - Empty vs populated middle names
```

### Default Settings
- **Similarity Threshold**: 0.9 (90%)
- **Last Name Pre-filter**: 0.6 (60%)
- **Progress Reporting**: Every 1,000 scholars

### Customization Points
- Adjust similarity weights in `calculate_similarity()`
- Modify normalization rules in `normalize_name()`
- Change threshold defaults in management command
- Extend admin interface comparison fields

## Database Maintenance

### Cleanup Old Candidates
```python
# Remove reviewed candidates older than 6 months
DuplicateCandidate.objects.filter(
    reviewed=True,
    created_at__lt=timezone.now() - timedelta(days=180)
).delete()
```

### Re-run Detection
Safe to run multiple times - duplicate candidates won't be created due to unique constraints.

## Potential Enhancements

### Potential Improvements
1. **Machine Learning**: Train classification model on reviewed candidates
2. **Institution Matching**: Use institutional affiliations as similarity factors
3. **Date Range Filtering**: Focus on scholars from overlapping time periods
4. **Handle merging duplicates**: Build a method in django-admin for merging duplicate records.

### Performance Optimizations
1. **Database Indexing**: Add indexes on commonly queried fields
2. **Parallel Processing**: Multi-threading for large datasets
3. **Incremental Updates**: Only check new scholars against existing ones
4. **Caching**: Cache normalized names and similarity calculations
