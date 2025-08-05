# How to Run the BRB Data Scripts

This guide will show you how to download and process data from the Burundi Central Bank (BRB) website. We'll use two main scripts:

1. A script that downloads the data
2. A script that processes the data into a useful format

## Before You Start

You need to have these things on your computer:

- Python (version 3.12 or newer)
- Poetry (a tool that helps manage Python packages)

If you don't have Poetry, you can install it by running this command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installing Poetry, you need to install all the project's required packages. Do this by running:

```bash
poetry install
```

## Step 1: Downloading the Data

To download the latest data from the BRB website, run:

```bash
poetry run download-all
```

This will:

- Connect to the BRB website
- Find the newest data file
- Download it to your computer in the `data/raw/importation_countries` folder

## Step 2: Processing the Data

After downloading the data, you need to process it into a more useful format. This happens in two steps:

### Step 2.1: Parse Excel to CSV

The parser will automatically find and process the most recent Excel file in the `data/raw/importation_countries` folder.

Run this command:

```bash
poetry run python src/parse/importation_bif/parser.py
```

This will:

- Find the most recent Excel file in `data/raw/importation_countries`
- Extract data for countries specified in `countries.csv`
- Convert dates to YYYY-MM format
- Convert all numeric values to decimal format
- Save the processed data in `data/parsed/importation_countries` as:
  - A CSV file named with today's date (e.g., `2025-08-03-monthly.csv`)
  - Format: continent,country,YYYY-MM columns with decimal values

The output CSV will contain:

- Only data for countries listed in `countries.csv`
- All numeric values in decimal format
- Empty or invalid values replaced with 0.0
- Dates in YYYY-MM format

### Step 2.2: Transform CSV to JSON

After generating the CSV, you need to transform it into a JSON format grouped by continents. Run:

```bash
poetry run python src/parse/importation_bif/transform.py
```

This will:

- Find the most recent CSV file in `data/parsed/importation_countries`
- Group the data by continent, summing up values for all countries in each continent
- Save the transformed data as a JSON file with today's date (e.g., `2025-08-03-monthly-transformed.json`)
- Format: Hierarchical structure of year → month → continent → value

The output JSON will contain:

- Data grouped by continents (AFRIQUE, AMERIQUE, ASIE, EUROPE, OCEANIE)
- Monthly totals for each continent
- All values aggregated from country-level data
- Dates organized by year and month names

### Step 2.3: Generate Chart Data

Finally, transform the continent-grouped data into a format suitable for visualization. Run:

```bash
poetry run python src/parse/importation_bif/load.py
```

This will:

- Read the most recent transformed JSON file from `data/parsed/importation_countries`
- Generate chart configuration for each year's data
- Create datasets for each continent with consistent colors:
  - AFRIQUE (Green)
  - AMERIQUE (Blue)
  - ASIE (Red)
  - EUROPE (Yellow)
  - OCEANIE (Purple)
- Save the chart data to `website/data/monthly_imports_by_country.json`

The output chart configuration will include:

- Stacked bar charts showing monthly imports by continent
- Consistent color scheme for better visualization
- Monthly labels (Jan-Dec)
- Year-specific titles and descriptions
- Responsive chart settings
- Legend positioned at the top

## Common Problems and Solutions

1. **Error: "No module named 'something'"**

   - This means you're not using Poetry to run the script
   - Always use `poetry run` before your command

2. **Can't find Poetry command**

   - You might need to add Poetry to your PATH
   - Run this command:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```
   - For permanent setup, add this line to your `~/.zshrc` file

3. **Can't find the input file**
   - Make sure you're using the correct path to the Excel file
   - Look in the `data/raw/importation_countries` folder for the latest downloaded file

## Need Help?

If you have any problems:

1. Make sure you're using `poetry run` before your commands
2. Check that all files exist in the correct folders
3. Make sure you installed all packages with `poetry install`
