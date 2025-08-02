# BRB Analytics

This package contains the analytics tools for processing Burundi Central Bank (BRB) open data.

## Setup

1. Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:

```bash
poetry install
```

## Available Commands

- Download all data sources:

```bash
poetry run download-all
```

## Project Structure

- `src/` - Source code
  - `etl/` - Data extraction and loading tools
  - `parse/` - Data parsing tools
  - `ml/` - Machine learning models
- `config/` - Configuration files
  - `sources.yml` - Data source configurations
- `data/` - Data storage
  - `raw/` - Raw downloaded files
  - `parsed/` - Processed data files
