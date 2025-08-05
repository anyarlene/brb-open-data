# How to Run the BRB Data Scripts

This guide explains how to process data from the Burundi Central Bank (BRB) website using our ETL (Extract, Transform, Load) pipeline.

## Before You Start

Required tools:

- Python (version 3.12 or newer)
- Poetry (package manager)
- Git Bash (for Windows users)

Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Install project dependencies:
```bash
poetry install
```

## ETL Pipeline

Our data processing follows a standard ETL (Extract, Transform, Load) pipeline:

### 1. Extract (Download)

Download the latest data from BRB:
```bash
poetry run download-all
```

This downloads all required files into their respective directories under `data/raw/`.

### 2. Transform (Parse)

The transformation happens in two steps:

#### 2.1 Parse Raw Data

Run the parsers to convert raw data into a standardized CSV format:
```bash
poetry run python src/parse/<source>/parser.py
```

Each parser:
- Reads raw data from `data/raw/<source>`
- Applies source-specific transformations
- Validates against reference data in `src/parse/<source>/`
- Outputs to `data/parsed/<source>/<date>-monthly.csv`

#### 2.2 Transform Data

Transform parsed data into aggregated JSON format:
```bash
poetry run python src/parse/<source>/transform.py
```

This step:
- Reads the latest parsed CSV
- Applies grouping and aggregations
- Outputs to `data/parsed/<source>/<date>-monthly-transformed.json`

### 3. Load (Website Data)

Generate website-ready visualization data:
```bash
poetry run python src/parse/<source>/load.py
```

This final step:
- Reads transformed JSON data
- Generates chart configurations
- Outputs to `website/data/` for the website to consume

## Project Structure

```
analytics/
├── config/           # Configuration files
├── data/            # Data files
│   ├── raw/         # Raw downloaded data
│   └── parsed/      # Processed data files
├── docs/            # Documentation
└── src/             # Source code
    ├── etl/         # Data download scripts
    └── parse/       # Data parsing scripts
        └── <source> # Source-specific parsers
```

## Common Problems and Solutions

1. **Error: "No module named 'something'"**
   - Always use `poetry run` before commands

2. **Can't find Poetry command**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
   Add to `~/.zshrc` for permanent setup

3. **Can't find input files**
   - Check raw data folders
   - Verify download step completed successfully

## Need Help?

Troubleshooting steps:
1. Use `poetry run` for all commands
2. Verify file paths and folder structure
3. Check `poetry install` completed successfully
4. Use Git Bash on Windows