import pandas as pd
import json
from datetime import datetime
from pathlib import Path

def transform_csv_to_json():
    # Get the project root directory
    project_root = Path(__file__).parents[3]

    # Find the most recent CSV file
    parsed_dir = project_root / "data" / "parsed" / "importation_bif"
    csv_files = list(parsed_dir.glob("*-monthly.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {parsed_dir}")

    csv_path = sorted(csv_files)[-1]

    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Create the result dictionary
    result = {}

    # Get all date columns (excluding 'continent' and 'country')
    date_cols = [col for col in df.columns if col not in ['continent', 'country']]

    # Dictionary to convert month numbers to names
    month_names = {
        '01': 'January', '02': 'February', '03': 'March',
        '04': 'April', '05': 'May', '06': 'June',
        '07': 'July', '08': 'August', '09': 'September',
        '10': 'October', '11': 'November', '12': 'December'
    }

    # Process each date column
    for date_col in date_cols:
        year, month = date_col.split('-')
        year = year
        month_name = month_names[month]

        # Create year entry if it doesn't exist
        if year not in result:
            result[year] = {}

        # Create month entry if it doesn't exist
        if month_name not in result[year]:
            result[year][month_name] = {}

        # Group by continent and sum values for this month
        continent_sums = df.groupby('continent')[date_col].sum().dropna()
        for continent, value in continent_sums.items():
            result[year][month_name][continent] = value

    # Generate output filename with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = parsed_dir / f"{today}-monthly-transformed.json"

    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Transformed data saved to: {output_file}")

if __name__ == "__main__":
    transform_csv_to_json()
