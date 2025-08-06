# brb-open-data

This repository contains an automated data pipeline for collecting, processing, and analyzing import data from the Bank of the Republic of Burundi ([BRB](https://www.brb.bi/)). The project transforms raw Excel files from BRB into structured datasets and provides web-based visualizations.

## Overview

The project follows a standard ETL (Extract, Transform, Load) pipeline to process BRB import data:

1. **Extract**: Downloads Excel files from BRB website
2. **Transform**: Parses and standardizes the data
3. **Load**: Generates web-ready visualization data

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

1. **Download data**:
```bash
poetry run download-all
```

2. **Parse data**:
```bash
poetry run python src/parse/<source>/parser.py
```

3. **Transform data**:
```bash
poetry run python src/parse/<source>/transform.py
```

4. **Generate website data**:
```bash
poetry run python src/parse/<source>/load.py
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
│           └── importation_categories/   # Category-based import data
└── website/                # Data visualization
    ├── data/               # Chart data files
    ├── js/                 # JavaScript charts
    └── index.html          # Main dashboard
```

## Data Sources

Currently configured sources:

- **Import by Countries**: Data from https://www.brb.bi/node/477
- **Import by Categories**: Data from https://www.brb.bi/node/343

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

3. **Load**: Generates website-ready data
   - Creates chart configurations
   - Outputs JSON files for web visualization

## Technical Details

- **Language**: Python 3.12+
- **Package Management**: Poetry
- **Data Processing**: pandas for Excel/CSV manipulation
- **Output Formats**: CSV, JSON
- **Web Visualization**: Custom JavaScript charts
- **Configuration**: YAML-based source definitions

## Troubleshooting

Common issues and solutions:

1. **"No module named 'something'"** - Always use `poetry run` before commands
2. **Can't find Poetry command** - Add Poetry to your PATH or use full path
3. **Can't find input files** - Verify download step completed successfully

## Documentation

For detailed setup and usage instructions, see:
- [How to Run Scripts](analytics/docs/how_to_run_scripts.md) - Complete setup and usage guide
- [Running Local Server](analytics/docs/running_local_server.md) - Instructions for running and accessing the website locally

## Contributing

The project uses Poetry for dependency management. Always use `poetry run` when executing Python scripts to ensure proper environment isolation.
