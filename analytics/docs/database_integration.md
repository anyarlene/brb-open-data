# Database Integration for BRB Analytics

This document describes the SQLite database integration for the BRB analytics pipeline.

## Overview

The database integration allows you to:

- Store all import data in a normalized SQLite database
- Write SQL queries to analyze and explore data
- Generate chart JSON files from SQL queries
- Practice SQL skills with real data

## Database Schema

### Main Table: `imports`

```sql
CREATE TABLE imports (
    id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    continent TEXT,
    country TEXT,
    category TEXT,
    value REAL NOT NULL,
    source_type TEXT NOT NULL,  -- 'countries' or 'categories'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_imports_year_month ON imports(year, month);
CREATE INDEX idx_imports_continent ON imports(continent);
CREATE INDEX idx_imports_category ON imports(category);
CREATE INDEX idx_imports_source ON imports(source_type);
```

### Metadata Table: `metadata`

```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Pipeline Integration

### Current Pipeline

```
BRB Website → Excel Files → CSV (parser.py) → JSON (transform.py) → Chart JSON (load.py) → Website
```

### New Pipeline with Database

```
BRB Website → Excel Files → CSV (parser.py) → Database (db_load.py) → Chart JSON (sql_load.py) → Website
```

## Usage

### 1. Load Data into Database

```bash
# From analytics directory
poetry run load-database
```

This will:

- Create the database schema
- Load countries data from CSV files
- Load categories data from JSON files
- Update metadata

### 2. Generate Charts from SQL

```bash
# From analytics directory
poetry run generate-sql-charts
```

This will:

- Query the database using SQL
- Generate chart JSON files for the website
- Save to `website/data/` directory

### 3. Complete Pipeline

```bash
# Download data
poetry run download-all

# Parse countries data
poetry run python src/parse/importation_countries/parser.py
poetry run python src/parse/importation_countries/transform.py

# Parse categories data
poetry run python src/parse/importation_categories/parser.py
poetry run python src/parse/importation_categories/transform.py

# Load into database
poetry run load-database

# Generate charts from SQL
poetry run generate-sql-charts
```

## SQL Queries for Training

### Basic Queries

```sql
-- Get all years
SELECT DISTINCT year FROM imports ORDER BY year;

-- Get all continents
SELECT DISTINCT continent FROM imports WHERE continent IS NOT NULL ORDER BY continent;

-- Get all categories
SELECT DISTINCT category FROM imports WHERE category IS NOT NULL ORDER BY category;
```

### Analysis Queries

```sql
-- Monthly imports by continent for 2023
SELECT
    continent,
    month,
    SUM(value) as total_imports
FROM imports
WHERE year = 2023
    AND source_type = 'countries'
    AND continent IS NOT NULL
GROUP BY continent, month
ORDER BY month, continent;

-- Top 10 countries by import value in 2023
SELECT
    country,
    SUM(value) as total_imports
FROM imports
WHERE year = 2023
    AND source_type = 'countries'
    AND country IS NOT NULL
GROUP BY country
ORDER BY total_imports DESC
LIMIT 10;

-- Yearly totals by continent
SELECT
    year,
    continent,
    SUM(value) as total_imports
FROM imports
WHERE source_type = 'countries'
    AND continent IS NOT NULL
GROUP BY year, continent
ORDER BY year, total_imports DESC;
```

### Custom Queries

```sql
-- Find countries with highest growth
SELECT
    country,
    SUM(CASE WHEN year = 2022 THEN value ELSE 0 END) as imports_2022,
    SUM(CASE WHEN year = 2023 THEN value ELSE 0 END) as imports_2023,
    (SUM(CASE WHEN year = 2023 THEN value ELSE 0 END) -
     SUM(CASE WHEN year = 2022 THEN value ELSE 0 END)) as growth
FROM imports
WHERE source_type = 'countries'
    AND year IN (2022, 2023)
GROUP BY country
HAVING imports_2022 > 0 AND imports_2023 > 0
ORDER BY growth DESC;

-- Monthly trends by source type
SELECT
    year,
    month,
    source_type,
    SUM(value) as total_imports
FROM imports
GROUP BY year, month, source_type
ORDER BY year, month;
```

## Database Location

The SQLite database is stored at:

```
website/data/brb_database.db
```

This location allows the website to access the database file directly.

## Benefits for Training

1. **Real SQL Practice**: Write actual SQL queries on real data
2. **Data Exploration**: Use SQL to understand data structure and patterns
3. **Performance**: SQL queries can be more efficient than JSON processing
4. **Flexibility**: Easy to modify queries for different analyses
5. **Learning**: See how SQL integrates with data pipelines

## Development Workflow

1. **Data Ingestion**: Use `load-database` to populate the database
2. **SQL Exploration**: Write custom queries to explore data
3. **Chart Generation**: Use `generate-sql-charts` to create visualizations
4. **Website Updates**: The website automatically uses the generated JSON files

## File Structure

```
analytics/src/parse/database/
├── __init__.py          # Module exports
├── schema.py            # Database schema definitions
├── loader.py            # Database loading functions
├── queries.py           # SQL query templates
├── db_load.py           # Main database loading script
└── sql_load.py          # SQL-based chart generation
```

## Troubleshooting

### Database not found

```bash
# Make sure you've run the database loading script
poetry run load-database
```

### No data in database

```bash
# Check if CSV/JSON files exist
ls analytics/data/parsed/importation_countries/
ls analytics/data/parsed/importation_categories/

# Run the full pipeline
poetry run download-all
poetry run python src/parse/importation_countries/parser.py
poetry run python src/parse/importation_countries/transform.py
poetry run load-database
```

### Reset database

```python
from src.parse.database.schema import reset_database, get_database_path
from pathlib import Path

project_root = Path(__file__).parents[3]
db_path = get_database_path(project_root)
reset_database(db_path)
```
