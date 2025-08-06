import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ImportationCategoriesParser:
    # Category mapping for visualization
    category_mapping = {
        '01': 'Food Products',  # Animals
        '02': 'Food Products',  # Meat
        '3,0': 'Food Products',  # Fish
        '04': 'Food Products',  # Dairy
        '07': 'Food Products',  # Vegetables
        '08': 'Food Products',  # Fruits
        '1001': 'Food Products',  # Wheat
        '1005': 'Food Products',  # Corn
        '1006': 'Food Products',  # Rice
        '1101': 'Food Products',  # Flour
        '1107': 'Food Products',  # Malt
        '1209': 'Food Products',  # Seeds
        '1302': 'Food Products',  # Plant extracts
        '1507-1515': 'Food Products',  # Vegetable oils
        '1517': 'Food Products',  # Margarine
        '16': 'Food Products',  # Meat and fish preparations
        '17019110-9910': 'Food Products',  # Sugar
        '1704': 'Food Products',  # Confectionery
        '190110': 'Food Products',  # Baby food
        '1902': 'Food Products',  # Pasta
        '190531,0': 'Food Products',  # Biscuits
        '20': 'Food Products',  # Vegetable and fruit preparations
        '21': 'Food Products',  # Various food preparations
        '2203': 'Food Products',  # Beer
        '2204': 'Food Products',  # Wine
        '2205': 'Food Products',  # Vermouth
        '2207-08': 'Food Products',  # Liquors
        '2401': 'Food Products',  # Tobacco
        '240220': 'Food Products',  # Cigarettes

        '28': 'Industrial Goods',  # Inorganic chemicals
        '29': 'Industrial Goods',  # Organic chemicals
        '31': 'Industrial Goods',  # Fertilizers
        '32': 'Industrial Goods',  # Dyes
        '37': 'Industrial Goods',  # Photographic products
        '380810': 'Industrial Goods',  # Insecticides
        '380840': 'Industrial Goods',  # Disinfectants
        '39': 'Industrial Goods',  # Plastics
        '48': 'Industrial Goods',  # Paper and cardboard
        '5206-12': 'Industrial Goods',  # Cotton fabrics
        '5407- 08': 'Industrial Goods',  # Synthetic fabrics
        '5512-16': 'Industrial Goods',  # Synthetic fiber fabrics
        '5607': 'Industrial Goods',  # Ropes
        '5903': 'Industrial Goods',  # Impregnated fabrics

        '2501': 'Raw Materials',  # Salt
        '252310': 'Raw Materials',  # Clinker cement
        '252329': 'Raw Materials',  # Portland cement
        '2710113-14-1911': 'Raw Materials',  # Aviation fuel
        '27101111-15': 'Raw Materials',  # Other fuel
        '27101921-23-31-39': 'Raw Materials',  # Gas oil and fuel oil
        '27101912-14': 'Raw Materials',  # Petroleum
        '2710119-1910-19-26': 'Raw Materials',  # Oils and greases
        '271091-99-1941-42': 'Raw Materials',  # Oil waste
        '2711-2715': 'Raw Materials',  # Asphalt, bitumen
        '44': 'Raw Materials',  # Wood
        '72': 'Raw Materials',  # Iron and steel
        '76': 'Raw Materials',  # Aluminum

        '30': 'Consumer Goods',  # Pharmaceuticals
        '33': 'Consumer Goods',  # Perfumery
        '3401-05': 'Consumer Goods',  # Soaps
        '3605': 'Consumer Goods',  # Matches
        '42': 'Consumer Goods',  # Leather goods
        '49': 'Consumer Goods',  # Books
        '61': 'Consumer Goods',  # Knitted clothing
        '62': 'Consumer Goods',  # Other clothing
        '6308-10': 'Consumer Goods',  # Used clothing
        '64': 'Consumer Goods',  # Footwear
        '8212': 'Consumer Goods',  # Razors
        '9401-04': 'Consumer Goods',  # Furniture
        '95': 'Consumer Goods',  # Toys and sports
        '9603': 'Consumer Goods',  # Brooms
        '9608': 'Consumer Goods',  # Pens
        '9610': 'Consumer Goods',  # Slates and boards

        '84': 'Machinery',  # Mechanical equipment
        '8501': 'Machinery',  # Generators
        '8504': 'Machinery',  # Transformers
        '8506-07': 'Machinery',  # Batteries
        '8525-29': 'Machinery',  # Radio equipment
        '8701': 'Machinery',  # Tractors
        '8702-03': 'Machinery',  # Cars
        '8704': 'Machinery',  # Trucks
        '8708': 'Machinery',  # Vehicle parts
        '8711-14': 'Machinery',  # Bikes and motorcycles
        '90': 'Machinery',  # Optical equipment
        '92': 'Machinery'  # Musical instruments
    }

    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)
        self.raw_dir = self.data_root / "data" / "raw" / "importation_categories"
        self.parsed_dir = self.data_root / "data" / "parsed" / "importation_categories"
        self.parsed_dir.mkdir(parents=True, exist_ok=True)

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

        # Filter rows to only include categories from our mapping
        df = df[df['code'].isin(self.category_mapping.keys())].copy()

        # Add description column using our category mapping
        df['description'] = df['code'].map(self.category_mapping)

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