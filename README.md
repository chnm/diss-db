# History Dissertation Database

A Django web application developed by the [Roy Rosenzweig Center for History and New Media](https://rrchnm.org/) at George Mason University to track history dissertations and explore scholarly genealogies. The database enables researchers to discover academic networks, mentorship relationships, and institutional connections within the field of history.

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL
- Node.js (for Tailwind CSS compilation)
- Poetry (recommended) or pip

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd diss-db
   ```

2. **Install Python dependencies**
   ```bash
   # Using Poetry (recommended)
   poetry install
   poetry shell

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

4. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py loaddata db.json  # Load initial data
   ```

5. **Install and compile Tailwind CSS**
   ```bash
   python manage.py tailwind install
   python manage.py tailwind build
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to view the application.

### Docker Development

```bash
docker-compose up --build
```

## Data Management

### Loading AHA Data

The application includes management commands for importing American Historical Association (AHA) dissertation data:

```bash
# Import dissertation data from CSV files
python manage.py import_aha_data /path/to/aha-data/
```

### Duplicate Detection

Run the duplicate detection system to identify potential duplicate author records:

```bash
# Find duplicates with default 90% similarity threshold
python manage.py find_duplicates

# Custom threshold and dry-run mode
python manage.py find_duplicates --threshold 0.85 --dry-run

# Limit processing for testing
python manage.py find_duplicates --limit 1000
```

## API Usage

The application provides REST API endpoints for accessing data programmatically:

- **Scholars**: `/api/scholars/` - List and search scholar records
- **Dissertations**: `/api/dissertations/` - Access dissertation data
- **Committee Members**: `/api/committee-members/` - Committee relationships

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black .
djhtml templates/

# Run lints
pylint dissdb/
```

### Pre-commit Hooks

Install pre-commit hooks for automated code quality checks:

```bash
pre-commit install
```

### Testing

Run tests using pytest:

```bash
pytest
```

## Project Structure

```
diss-db/
├── config/              # Django project configuration
├── dissdb/              # Main Django application
│   ├── management/      # Custom management commands
│   │   └── commands/    # Including find_duplicates.py
│   ├── migrations/      # Database migrations
│   ├── models.py        # Data models
│   ├── views.py         # Web views and API
│   └── admin.py         # Django admin customizations
├── theme/               # Tailwind CSS theme app
├── templates/           # Django templates
├── static/              # Static files
├── aha-data/           # AHA dataset CSV files
└── DEVNOTES.md         # Developer documentation for duplicate detection
```

## About

This project is developed by the Roy Rosenzweig Center for History and New Media at George Mason University. Data provided by the American Historical Association.

### Project team

- Savannah Scott, developer
- Lincoln Mullen, project lead
- Jason Heppler, developer
