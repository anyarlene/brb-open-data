# BRB Analytics Pipeline

ETL pipeline for processing Burundi Central Bank (BRB) import data.

## Project Structure

- `src/` - Source code
  - `etl/` - Data extraction tools
  - `parse/` - Data parsing tools
- `config/` - Configuration files
  - `sources.yml` - Data source definitions
- `data/` - Data storage
  - `raw/` - Downloaded Excel files
  - `parsed/` - Processed data files

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

3. **Load**: Generates visualization data
   - Continent-based aggregations
   - Time series processing
   - JSON output for charts

## Available Commands

```bash
# Download all data sources
poetry run download-all

# Process specific data source
poetry run python src/parse/<source>/parser.py
poetry run python src/parse/<source>/transform.py
poetry run python src/parse/<source>/load.py
```

## Technical Details

- Python 3.12+
- pandas for data processing
- YAML configuration
- Output: CSV, JSON formats