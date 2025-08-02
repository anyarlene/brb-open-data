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

To download the latest data from the BRB website, you can run either of these commands:

```bash
poetry run download-all
```

or

```bash
poetry run python src/brb_open_data/etl/download_manager.py
```

This will:

- Connect to the BRB website
- Find the newest data file
- Download it to your computer in the `data/raw/importation_bif` folder

## Step 2: Processing the Data

After downloading the data, you need to process it into a more useful format. Run this command:

```bash
poetry run python src/brb_open_data/parse/importation_bif_parser.py -i PATH_TO_EXCEL_FILE
```

Replace `PATH_TO_EXCEL_FILE` with the path to the Excel file that was just downloaded. For example:

```bash
poetry run python src/brb_open_data/parse/importation_bif_parser.py -i data/raw/importation_bif/29686_IV.5.Importations_20_20par_20pays_20de_20provenance_20_28en_20BIF_29_20250802.xlsx
```

This will:

- Read the Excel file
- Convert it into several easy-to-use formats
- Save the processed data in the `data/parsed/importation_bif` folder as:
  - Excel file (`.xlsx`)
  - CSV files (`.csv`)
  - JSON files (`.json`)

## Common Problems and Solutions

1. **Error: "No module named 'something'"**

   - This means you're not using Poetry to run the script
   - Always use `poetry run` before your command

2. **Can't find Poetry command**

   - You might need to add Poetry to your PATH
   - Run this command:
     ```bash
     export PATH="/Users/YOUR_USERNAME/.local/bin:$PATH"
     ```

3. **Can't find the input file**
   - Make sure you're using the correct path to the Excel file
   - Look in the `data/raw/importation_bif` folder for the latest downloaded file

## Need Help?

If you have any problems:

1. Make sure you're using `poetry run` before your commands
2. Check that all files exist in the correct folders
3. Make sure you installed all packages with `poetry install`
