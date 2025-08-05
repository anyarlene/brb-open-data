import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ImportationCategoriesParser:
    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)
        self.raw_dir = self.data_root / "data" / "raw" / "importation_categories"
        self.parsed_dir = self.data_root / "data" / "parsed" / "importation_categories"
        self.parsed_dir.mkdir(parents=True, exist_ok=True)

        # Load category reference data
        categories_file = Path(__file__).parent / "categories.csv"
        self.category_map = pd.read_csv(categories_file, sep='\t', dtype={'code': str})
        # Clean the codes in the mapping file
        self.category_map['code'] = self.category_map['code'].str.strip()
        # Handle decimal numbers in codes
        self.category_map['code'] = self.category_map['code'].apply(lambda x: x.split(',')[0] if ',' in x else x)
        self.category_map = self.category_map.set_index('code')['description'].to_dict()

    def format_column_name(self, col: str) -> str:
        """Format column name to YYYY-MM format if it's a date"""
        if isinstance(col, pd.Timestamp):
            return col.strftime('%Y-%m')

        # Skip non-date columns
        if col == 'code' or col == 'description':
            return col

        try:
            # Try to parse as timestamp
            dt = pd.to_datetime(col)
            return dt.strftime('%Y-%m')
        except:
            return col

    def normalize_code(self, code) -> str:
        """Normalize category codes to match our reference format"""
        if pd.isna(code):
            return ''
        
        # Convert to string and strip whitespace
        code_str = str(code).strip()
        
        # Handle decimal numbers (like "3,0" -> "3")
        if ',' in code_str:
            code_str = code_str.split(',')[0].strip()
        
        # Filter out metadata rows
        if code_str.startswith('Source:') or code_str.startswith('('):
            return ''
            
        return code_str

    def parse_excel(self, excel_path: Path) -> pd.DataFrame:
        logger.info(f"Processing file: {excel_path}")

        # Read the Excel file
        df = pd.read_excel(excel_path, sheet_name="Mensuelle", header=None)

        # Find the header row (contains "Rubriques douanières")
        header_row = df[df[0].str.contains("Rubriques douanières", na=False)].index
        if len(header_row) == 0:
            raise ValueError("Could not find header row with 'Rubriques douanières'")

        # Read the data with the correct header
        df = pd.read_excel(excel_path, sheet_name="Mensuelle", header=header_row[0])
        df.columns = df.columns.astype(str)

        # Rename first column and clean category codes
        df = df.rename(columns={df.columns[0]: "code"})
        df['code'] = df['code'].apply(self.normalize_code)

        # Filter out empty codes and metadata rows
        df = df[df['code'].str.len() > 0].copy()

        # Filter rows to only include categories from our reference list
        df = df[df['code'].isin(self.category_map.keys())].copy()

        # Add description column
        df['description'] = df['code'].map(self.category_map)

        # Convert numeric columns to float, replacing non-numeric and empty values with 0.0
        numeric_cols = [col for col in df.columns if col not in ['code', 'description']]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # Format column names (convert to YYYY-MM format)
        df.columns = [self.format_column_name(col) for col in df.columns]

        # Reorder columns to put code and description first
        date_cols = sorted([col for col in df.columns if col not in ['code', 'description']])
        final_cols = ['code', 'description'] + date_cols
        
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
        parser = ImportationCategoriesParser(project_root)
        
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