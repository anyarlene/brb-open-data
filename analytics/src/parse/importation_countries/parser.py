import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ImportationParser:
    def __init__(self, data_root: Path, source_dir: str):
        self.data_root = Path(data_root)
        self.raw_dir = self.data_root / "data" / "raw" / source_dir
        self.parsed_dir = self.data_root / "data" / "parsed" / source_dir
        self.parsed_dir.mkdir(parents=True, exist_ok=True)

        # Load country reference data
        countries_file = Path(__file__).parent / "countries.csv"
        self.country_map = pd.read_csv(countries_file).set_index('country')['continent'].to_dict()

    def format_column_name(self, col: str) -> str:
        """Format column name to YYYY-MM format if it's a date"""
        if isinstance(col, pd.Timestamp):
            return col.strftime('%Y-%m')

        # Skip non-date columns
        if col == 'country' or col == 'continent':
            return col

        try:
            # Try to parse as timestamp
            dt = pd.to_datetime(col)
            return dt.strftime('%Y-%m')
        except:
            return col

    def parse_excel(self, excel_path: Path) -> pd.DataFrame:
        logger.info(f"Processing file: {excel_path}")

        # Read the Excel file
        df = pd.read_excel(excel_path, sheet_name="Mensuelle", header=None)

        # Find the header row (contains "Pays de destination")
        header_row = df[df[0].str.contains("Pays de destination", na=False)].index
        if len(header_row) == 0:
            raise ValueError("Could not find header row with 'Pays de destination'")

        # Read the data with the correct header
        df = pd.read_excel(excel_path, sheet_name="Mensuelle", header=header_row[0])
        df.columns = df.columns.astype(str)

        # Rename first column and clean country names
        df = df.rename(columns={df.columns[0]: "country"})
        df['country'] = df['country'].astype(str).str.strip()

        # Filter rows for countries in our reference list
        valid_countries = df['country'].isin(self.country_map.keys())
        unmatched = df[~valid_countries]['country'].unique()
        if len(unmatched) > 0:
            logger.warning(f"Unmatched countries: {', '.join(unmatched)}")

        df = df[valid_countries].copy()

        # Add continent column
        df['continent'] = df['country'].map(self.country_map)

        # Convert numeric columns to float, replacing non-numeric and empty values with 0.0
        numeric_cols = [col for col in df.columns if col not in ['country', 'continent']]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # Format column names
        df.columns = [self.format_column_name(col) for col in df.columns]

        # Reorder columns
        final_cols = ['continent', 'country'] + sorted([col for col in df.columns
                                                      if col not in ['continent', 'country']])
        return df[final_cols]

    def save_csv(self, df: pd.DataFrame):
        # Generate output filename with today's date
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = self.parsed_dir / f"{today}-monthly.csv"

        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"Saved parsed data to: {output_file}")

def main():
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        project_root = Path(__file__).parents[3]
        
        # Process importation_countries directory
        source_dir = "importation_countries"
        parser = ImportationParser(project_root, source_dir)
        
        if not parser.raw_dir.exists():
            logger.warning(f"Directory not found: {parser.raw_dir}")
            return

        excel_files = list(parser.raw_dir.glob("*.xls*"))  # matches both .xls and .xlsx
        if not excel_files:
            logger.warning(f"No Excel files found in {parser.raw_dir}")
            return

        # Process each file in the directory
        for excel_file in sorted(excel_files):
            try:
                df = parser.parse_excel(excel_file)
                parser.save_csv(df)
            except Exception as e:
                logger.error(f"Error processing {excel_file}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise

if __name__ == "__main__":
    main()