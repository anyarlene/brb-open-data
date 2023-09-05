# brb-open-data

This repository contains codes for performing ETL (Extract, Transform, Load) operations on data from [BRB](https://brb.bi/) and creating visualizations based on the cleaned data.

## ELT (Extract, Load, Transform)
The ELT process involves extracting data from an external source, cleaning and transforming it, and then loading it into a structured format for further analysis and visualization. In this repository, we have scripts that performs the ELT process on each specific dataset:

- `elt_taux_inflation.py`
- `elt_importation_tons.py`
- `elt_importation_bif.py`

#### Automated Data Processing (parsing and normalization)
Data is reorganized in order to be used for further queries and analysis. We have scripts that peroforms necessary transformations on each specific dataset:

- `parse_normalize_importation_tons.py`
- `parse_normalize_importation_bif.py`

## Visualizations
Once the data has been processed and cleaned, we can create visualizations to gain insights and better understand the data. The repository contains Python scripts that creates various charts and plots based on the cleaned data:

- `annual_and_monthly_inflation_dashboard.py`
- `monthly_inflation_dashboard.py`
-`importation_tons_time_series.py`
- `heatmap_importation_tons.py`


