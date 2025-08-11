# BRB Analytics Pipeline

ETL pipeline for processing Burundi Central Bank (BRB) import data with SQLite database integration.

## Project Structure

- `src/` - Source code
  - `etl/` - Data extraction tools
  - `parse/` - Data parsing tools
    - `database/` - Database integration module
      - `schema.py` - Database schema definitions
      - `loader.py` - Data loading functions
      - `queries.py` - SQL query templates
      - `db_load.py` - Database loading script
      - `sql_load.py` - SQL-based chart generation
- `config/` - Configuration files
  - `sources.yml` - Data source definitions
- `data/` - Data storage
  - `raw/` - Downloaded Excel files
  - `parsed/` - Processed data files
- `docs/` - Documentation
  - `database_integration.md` - Database setup and usage guide

## Data Sources

Currently configured sources:
- **Import by Countries**: Data from https://www.brb.bi/node/477
  - Monthly import values by country
  - Grouped by continent
  - Values in Million BIF (Burundian Francs)

- **Import by Categories**: Data from https://www.brb.bi/node/343
  - Monthly import values by category
  - Economic sector classification
  - Values in Million BIF (Burundian Francs)

## Pipeline Steps

1. **Extract**: Downloads Excel files from BRB website
   - Automated download with retry logic
   - Version tracking for downloaded files

2. **Transform**: Standardizes raw data
   - Country name validation
   - Continent mapping
   - French text normalization

3. **Load**: Stores data in database and generates visualization data
   - Loads data into SQLite database
   - Generates chart data from SQL queries
   - JSON output for charts

## Available Commands

```bash
# Download all data sources
poetry run download-all

# Process specific data source
poetry run python src/parse/<source>/parser.py
poetry run python src/parse/<source>/transform.py

# Database operations
poetry run load-database
poetry run generate-sql-charts
```

## Database Integration

The pipeline now includes SQLite database integration:

- **Database Location**: `website/data/brb_database.db`
- **Main Table**: `imports` - stores all import data with normalized schema
- **Benefits**:
  - SQL queries for data analysis
  - Better performance for large datasets
  - Practice SQL skills with real data
  - Flexible data exploration

## Complete Pipeline Example

```bash
# Download data
poetry run download-all

# Parse countries data
poetry run python src/parse/importation_countries/parser.py
poetry run python src/parse/importation_countries/transform.py

# Parse categories data
poetry run python src/parse/importation_categories/parser.py
poetry run python src/parse/importation_categories/transform.py

# Load into database and generate charts
poetry run load-database
poetry run generate-sql-charts
```

## Technical Details

- Python 3.12+
- pandas for data processing
- SQLite for data storage
- YAML configuration
- Output: CSV, JSON, SQLite formats