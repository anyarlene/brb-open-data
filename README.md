# brb-open-data

This repository contains an automated data pipeline for collecting, processing, and analyzing import data from the Bank of the Republic of Burundi ([BRB](https://www.brb.bi/)). The project transforms raw Excel files from BRB into structured datasets, stores them in a SQLite database, and provides web-based visualizations.

## Overview

The project follows a standard ETL (Extract, Transform, Load) pipeline to process BRB import data:

1. **Extract**: Downloads Excel files from BRB website
2. **Transform**: Parses and standardizes the data
3. **Load**: Stores data in SQLite database and generates web-ready visualization data

## Quick Start

### Prerequisites

- Python 3.12 or newer
- Poetry (package manager)
- Git Bash (recommended for Windows)

### Setup

1. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

### Running the Pipeline

1. **Generate export files**:
```bash
cd website
poetry run python js/utils/export_data.py
```
This will generate CSV and XLSX files for the website's download functionality.

2. **Download data**:
```bash
poetry run download-all
```

3. **Parse data**:
```bash
poetry run python src/parse/<source>/parser.py
```

4. **Transform data**:
```bash
poetry run python src/parse/<source>/transform.py
```

5. **Load data into database and generate charts**:
```bash
poetry run load-database
poetry run generate-sql-charts
```

## Project Structure

```
├── analytics/              # Data processing pipeline
│   ├── config/             # Configuration files
│   │   └── sources.yml     # Data source definitions
│   ├── data/               # Data files
│   │   ├── raw/            # Downloaded Excel files
│   │   └── parsed/         # Processed CSV/JSON files
│   ├── docs/               # Documentation
│   └── src/                # Source code
│       ├── etl/            # Download scripts
│       └── parse/          # Data parsing scripts
│           ├── importation_countries/    # Country-based import data
│           ├── importation_categories/   # Category-based import data
│           └── database/                 # Database integration
│               ├── schema.py            # Database schema
│               ├── loader.py            # Data loading functions
│               ├── queries.py           # SQL query templates
│               ├── db_load.py           # Database loading script
│               └── sql_load.py          # SQL-based chart generation
└── website/                # Data visualization
    ├── data/               # Chart data files and SQLite database
    ├── js/                 # JavaScript charts
    └── index.html         # Main dashboard
```

## Data Processing

### Pipeline Steps

Each data source follows the same three-step process:

1. **Parser**: Converts Excel → standardized CSV
   - Validates country names against reference data
   - Maps countries to continents
   - Handles French text normalization

2. **Transform**: Converts CSV → aggregated JSON
   - Groups data by continent and time period
   - Calculates aggregations and trends

3. **Load**: Stores in database and generates website-ready data
   - Loads data into SQLite database
   - Creates chart configurations from SQL queries
   - Outputs JSON files for web visualization

### Database Integration

The project now includes SQLite database integration for enhanced data analysis:

- **Database Location**: `website/data/brb_database.db`
- **Main Table**: `imports` - stores all import data with normalized schema
- **SQL Queries**: Generate chart data using SQL for better performance and flexibility
- **Training**: Practice SQL skills with real data

## Technical Details

- **Language**: Python 3.12+
- **Package Management**: Poetry
- **Data Processing**: pandas for Excel/CSV manipulation
- **Database**: SQLite for data storage and querying
- **Output Formats**: CSV, JSON, SQLite
- **Web Visualization**: Custom JavaScript charts
- **Configuration**: YAML-based source definitions

## Troubleshooting

Common issues and solutions:

1. **"No module named 'something'"** - Always use `poetry run` before commands
2. **Can't find Poetry command** - Add Poetry to your PATH or use full path
3. **Can't find input files** - Verify download step completed successfully
4. **Database not found** - Run `poetry run load-database` to create the database
5. **No data in charts** - Ensure both countries and categories data are loaded

## Documentation

For detailed setup and usage instructions, see:
- [How to Run Scripts](analytics/docs/how_to_run_scripts.md) - Complete setup and usage guide
- [Running Local Server](analytics/docs/running_local_server.md) - Instructions for running and accessing the website locally
- [Database Integration](analytics/docs/database_integration.md) - SQLite database setup and usage

## Contributing

The project uses Poetry for dependency management. Always use `poetry run` when executing Python scripts to ensure proper environment isolation.