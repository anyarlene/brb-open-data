# brb-open-data

This repository contains an automated data pipeline for collecting, processing, and analyzing economic data from the Bank of the Republic of Burundi ([BRB](https://brb.bi/)). The project focuses on transforming raw economic indicators into structured, analyzable datasets with a particular emphasis on importation data and inflation rates.

## Project Structure

The project is organized into several key components:

### 1. Data Collection (ETL Pipeline)

The ETL (Extract, Transform, Load) pipeline automatically:

- Downloads data from BRB's website using configurable source definitions
- Versions and stores raw data files with timestamps
- Processes multiple economic indicators including:
  - Importation data in BIF (Burundian Franc)
  - Importation data in Tons
  - Inflation rates

### 2. Data Processing

The processing pipeline includes:

#### Parsing and Normalization

- Handles complex Excel file structures with multiple sheets
- Normalizes French abbreviations and special characters
- Processes hierarchical data (continents, subcontinents, countries)
- Generates both structured (CSV/Excel) and JSON outputs

#### Data Models

- `importation_bif_data_model.py`: Processes importation data in BIF
- `importation_tons_data_model.py`: Processes importation data in metric tons
- `inflation_data_model.py`: Processes inflation rate data

### 3. Data Analysis & Visualization

The project includes several visualization tools for analyzing the processed data:

#### Inflation Analysis

- `annual_and_monthly_inflation_dashboard.py`: Combined view of annual and monthly trends
- `monthly_inflation_dashboard.py`: Detailed monthly inflation analysis

#### Import Analysis

- `importation_tons_time_series.py`: Time series analysis of import volumes
- `heatmap_importation_tons.py`: Heatmap visualization of import patterns

## Technical Details

- Built with Python using pandas for data processing
- Automated data downloads with configurable source definitions
- Secure HTTPS connections with certificate verification
- Structured data output in multiple formats (Excel, CSV, JSON)
- Versioned data storage with timestamp-based naming

## Data Sources

Currently configured data sources:

- BRB Importation Data (https://www.brb.bi/node/477)
- Additional sources can be configured in `config/sources.yml`

## Getting Started

For information on how to run the scripts and process data, please refer to the documentation in `docs/how_to_run_scripts.md`.
