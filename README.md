# brb-open-data

This repository contains models and scripts for performing ELT (Extract, Load, Transform) operations on data from [BRB](https://brb.bi/) and creating visualizations based on the cleaned data.

## ELT (Extract, Load, Transform)

### Models responsible for Extracting, Loading, and Transforming data.

- `importation_tons_data_model.py`
- `inflation_data_model.py`


### Scripts used to run the complete ELT models

- `run_importations_tons_model.py`
- `run_inflation_model.py`


### Handle parsing and normalization to achieve a final structured format of the data

- `parse_normalize_importation_tons.py`
- `parse_normalize_importation_bif.py`


## Visualizations
Once the data has been processed and cleaned, we can create visualizations to gain insights and better understand the data. The repository contains Python scripts that creates various charts and plots based on the cleaned data:

- `annual_and_monthly_inflation_dashboard.py`
- `monthly_inflation_dashboard.py`
- `importation_tons_time_series.py`
- `heatmap_importation_tons.py`


