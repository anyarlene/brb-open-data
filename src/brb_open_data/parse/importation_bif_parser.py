# File: src/brb_open_data/parse/importation_bif_parser.py

import argparse
import logging
import re
import unicodedata
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Map French month abbreviations (normalized) to month numbers
_MONTH_MAP = {
    'janv': 1,
    'fevr': 2,
    'mars': 3,
    'avr': 4,
    'mai': 5,
    'juin': 6,
    'juil': 7,
    'aout': 8,
    'sept': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}

# Patterns for continent/subcontinent rows
_CONTINENT_PATTERN = re.compile(r'^[IVX]+\.', re.IGNORECASE)
_SUBCONT_PATTERN = re.compile(r'^[0-9]+\.', re.IGNORECASE)

def _normalize_str(s: str) -> str:
    """
    Strip accents, trim whitespace, lowercase.
    """
    if not isinstance(s, str):
        return s
    s = s.strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()

class ImportationBifParser:
    def __init__(self, excel_path: Path):
        """
        excel_path: Path to the downloaded Excel file, e.g. data/raw/importation_bif/20250623_filename.xlsx
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

    def parse_table_of_contents(self) -> pd.DataFrame:
        """
        Parse the 'Table_de_matiere' sheet into a tidy DataFrame.
        Returns DataFrame with columns:
          sheet_name, description, frequency, last_publication (string), excel_name, source_url
        """
        sheet = 'Table_de_matiere'
        # Read without header first to locate header row
        try:
            df0 = pd.read_excel(self.excel_path, sheet_name=sheet, header=None)
        except Exception as e:
            raise ValueError(f"Failed to read sheet '{sheet}': {e}")

        header_row = None
        for idx, row in df0.iterrows():
            # look for the header keywords in row: 'Nom des Feuilles'
            # case-insensitive
            if row.astype(str).str.contains('Nom des Feuilles', case=False, na=False).any():
                header_row = idx
                break
        if header_row is None:
            raise ValueError(f"Cannot find header row in sheet '{sheet}' of {self.excel_path}")

        # Read again with proper header
        df = pd.read_excel(self.excel_path, sheet_name=sheet, header=header_row)
        # Rename columns to consistent keys
        col_map = {}
        for col in df.columns:
            cn = _normalize_str(str(col))
            if 'nom des feuilles' in cn:
                col_map[col] = 'sheet_name'
            elif 'description' in cn:
                col_map[col] = 'description'
            elif 'fréquence' in cn or 'frequence' in cn:
                col_map[col] = 'frequency'
            elif 'dernière date' in cn or 'derniere date' in cn:
                col_map[col] = 'last_publication'
            elif 'nom du fichier' in cn:
                col_map[col] = 'excel_name'
            elif 'disponible' in cn or 'page web' in cn:
                col_map[col] = 'source_url'
        df = df.rename(columns=col_map)

        # Keep only known columns if they exist
        expected = ['sheet_name','description','frequency','last_publication','excel_name','source_url']
        existing = [c for c in expected if c in df.columns]
        df = df[existing].copy()

        # Drop rows where sheet_name is NaN or empty
        df = df[df['sheet_name'].notna()]
        df['sheet_name'] = df['sheet_name'].astype(str).str.strip()

        # Clean up other columns
        for col in ['description','frequency','last_publication','excel_name','source_url']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace({'nan':''})

        return df.reset_index(drop=True)

    def parse_mensuelle(self) -> pd.DataFrame:
        """
        Parse the 'Mensuelle' sheet into a normalized long table.
        Returns DataFrame with columns:
          date (datetime), year (int), month (int), destination_country (str),
          value (float), continent (str), subcontinent (str or None),
          continent_total (float), subcontinent_total (float), monthly_total (float)
        """
        sheet = 'Mensuelle'
        # Read entire sheet without header to locate header row
        try:
            df0 = pd.read_excel(self.excel_path, sheet_name=sheet, header=None)
        except Exception as e:
            raise ValueError(f"Failed to read sheet '{sheet}': {e}")

        header_row = None
        for idx, row in df0.iterrows():
            first = str(row.iloc[0]).strip().lower()
            if 'pays de destination' in first:
                header_row = idx
                break
        if header_row is None:
            raise ValueError(f"Cannot find header row 'Pays de destination' in sheet '{sheet}'")

        # Read again with header row
        df = pd.read_excel(self.excel_path, sheet_name=sheet, header=header_row)
        # Drop completely empty columns
        df = df.dropna(axis=1, how='all')
        # Rename first column to 'destination_country'
        orig_first = df.columns[0]
        df = df.rename(columns={orig_first: 'destination_country'})

        # Melt all other columns as period columns
        period_cols = [c for c in df.columns if c != 'destination_country']
        df_long = df.melt(id_vars=['destination_country'], value_vars=period_cols,
                          var_name='period', value_name='value')
        # Drop rows where period is NaN
        df_long = df_long[df_long['period'].notna()].copy()
        df_long['destination_country'] = df_long['destination_country'].astype(str).str.strip()

        # Function to parse period string into a Timestamp (first of month)
        def parse_period_to_date(p: str):
            p0 = str(p).strip().replace('.', '').replace(' ', '').replace(' ', '')  # remove dots/spaces
            parts = re.split(r'[-_/]', p0)
            if len(parts) >= 2:
                mon_raw, yr_raw = parts[0], parts[1]
            else:
                mon_raw, yr_raw = p0[:-2], p0[-2:]
            mon_norm = _normalize_str(mon_raw)
            month = _MONTH_MAP.get(mon_norm[:4]) or _MONTH_MAP.get(mon_norm[:3])
            try:
                year = 2000 + int(yr_raw) if len(yr_raw) == 2 else int(yr_raw)
            except:
                year = None
            if month is None or year is None:
                raise ValueError(f"Cannot parse period string '{p}' into date")
            return pd.Timestamp(year=year, month=month, day=1)

        # Parse dates
        dates = []
        for p in df_long['period']:
            try:
                dt = parse_period_to_date(p)
                dates.append(dt)
            except Exception as e:
                dates.append(pd.NaT)
                logger.warning(f"Failed to parse period '{p}': {e}")
        df_long['date'] = dates
        # Drop rows without valid date
        df_long = df_long[df_long['date'].notna()].copy()

        # Convert value column to numeric
        df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')

        # Sort by date to ensure grouping order
        df_long = df_long.sort_values('date').reset_index(drop=True)

        # Initialize hierarchy columns
        df_long['continent'] = None
        df_long['subcontinent'] = None
        df_long['continent_total'] = None
        df_long['subcontinent_total'] = None
        df_long['monthly_total'] = None

        current_cont = None
        current_sub = None
        current_cont_total = None
        current_sub_total = None

        # Group by date to find TOTAL rows
        for date_val, group in df_long.groupby('date'):
            for idx, row in group.iterrows():
                dest = str(row['destination_country']).strip()
                # Detect TOTAL row
                if dest.upper() == 'TOTAL' or 'TOTAL' in dest.upper():
                    total_val = row['value']
                    df_long.loc[df_long['date'] == date_val, 'monthly_total'] = total_val
                    continue
                # Detect continent row: e.g. 'I. EUROPE'
                if _CONTINENT_PATTERN.match(dest):
                    current_cont = dest
                    current_cont_total = row['value']
                    current_sub = None
                    current_sub_total = None
                    continue
                # Detect subcontinent row: e.g. '1. Union Européenne'
                if _SUBCONT_PATTERN.match(dest):
                    current_sub = dest
                    current_sub_total = row['value']
                    continue
                # Else data row
                df_long.at[idx, 'continent'] = current_cont
                df_long.at[idx, 'subcontinent'] = current_sub if current_sub else None
                df_long.at[idx, 'continent_total'] = current_cont_total
                df_long.at[idx, 'subcontinent_total'] = (current_sub_total if current_sub else current_cont_total)

        # Strip prefixes from continent/subcontinent
        def strip_prefix(s: str):
            if not isinstance(s, str):
                return None
            if _CONTINENT_PATTERN.match(s):
                return re.sub(r'^[IVXivx]+\.\s*', '', s).strip()
            else:
                return re.sub(r'^[0-9]+\.\s*', '', s).strip()

        df_long['continent'] = df_long['continent'].apply(strip_prefix)
        df_long['subcontinent'] = df_long['subcontinent'].apply(strip_prefix)

        # Extract year/month columns
        df_long['year'] = df_long['date'].dt.year
        df_long['month'] = df_long['date'].dt.month

        # Select final columns in order
        df_final = df_long[[
            'date','year','month','destination_country','value',
            'continent','subcontinent','continent_total','subcontinent_total','monthly_total'
        ]].reset_index(drop=True)

        # Drop unwanted header-like rows if appear
        drop_vals = {'TOTAL', 'I. EUROPE', 'II. ASIE', 'III. AFRIQUE', 'IV. AMERIQUE',
                     'V. OCEANIE', 'VI. PAYS NON SPECIFIES'}
        df_final = df_final[~df_final['destination_country'].isin(drop_vals)].copy().reset_index(drop=True)

        return df_final

    def save_parsed(self, df_toc: pd.DataFrame, df_mens: pd.DataFrame) -> Path:
        """
        Save parsed DataFrames under data/parsed/importation_bif/
        Filename: <YYYYMMDD>_parsed.xlsx, where YYYYMMDD is derived from raw filename.
        Returns Path to saved parsed file.
        """
        # Derive project root: excel_path is project_root/data/raw/importation_bif/...
        # So project_root = excel_path.parents[2]
        project_root = self.excel_path.parents[2]
        source_name = "importation_bif"
        parsed_folder = project_root / "data" / "parsed" / source_name
        parsed_folder.mkdir(parents=True, exist_ok=True)

        # Derive date_str from raw filename: assume raw begins with YYYYMMDD
        stem = self.excel_path.stem  # e.g. "20250623_IV.5.Importations..."
        date_part = stem.split("_")[0]
        if not (len(date_part) == 8 and date_part.isdigit()):
            date_part = pd.Timestamp.now().strftime("%Y%m%d")
            logger.warning(f"Raw filename did not start with YYYYMMDD, using today: {date_part}")

        parsed_filename = f"{date_part}_parsed.xlsx"
        parsed_path = parsed_folder / parsed_filename

        # Write Excel with two sheets
        with pd.ExcelWriter(parsed_path, engine="openpyxl") as writer:
            if df_toc is not None and not df_toc.empty:
                df_toc.to_excel(writer, sheet_name="Table_de_matiere", index=False)
            if df_mens is not None and not df_mens.empty:
                df_mens.to_excel(writer, sheet_name="Mensuelle", index=False)
            # future: add trimestrielle, annuelle if implemented
            writer.save()

        logger.info(f"Saved parsed Excel to: {parsed_path}")
        return parsed_path

def main():
    """
    Entry point for CLI:
      poetry run parse-importation-bif --input <raw_excel> [--output-dir <dir>]
    """
    parser = argparse.ArgumentParser(
        description="Parse an Importation BIF Excel and save structured output"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to downloaded raw Excel file, e.g. data/raw/importation_bif/20250623_...xlsx"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Optional: custom output directory under which to save parsed Excel file."
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    excel_path = Path(args.input)
    if not excel_path.exists():
        logger.error(f"Input Excel file not found: {excel_path}")
        return

    # Instantiate parser
    try:
        parser_obj = ImportationBifParser(excel_path)
    except Exception as e:
        logger.error(f"Failed to initialize parser: {e}")
        return

    # Parse Table_of_contents
    try:
        df_toc = parser_obj.parse_table_of_contents()
        logger.info(f"Parsed Table_de_matiere: {len(df_toc)} rows")
    except Exception as e:
        logger.error(f"Failed to parse Table_de_matiere sheet: {e}")
        df_toc = None

    # Parse Mensuelle
    try:
        df_mens = parser_obj.parse_mensuelle()
        logger.info(f"Parsed Mensuelle: {len(df_mens)} rows")
    except Exception as e:
        logger.error(f"Failed to parse Mensuelle sheet: {e}")
        df_mens = None

    # If user provided custom output-dir, override default parsed location
    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        # Monkey-patch parser_obj.excel_path.parents so save_parsed picks correct root?
        # Simpler: call save_parsed logic manually here:
        # We write to out_dir/<YYYYMMDD>_parsed.xlsx
        # Derive date_part same as in save_parsed:
        stem = excel_path.stem
        date_part = stem.split("_")[0]
        if not (len(date_part)==8 and date_part.isdigit()):
            date_part = pd.Timestamp.now().strftime("%Y%m%d")
            logger.warning(f"Raw filename did not start with YYYYMMDD, using today: {date_part}")
        parsed_path = out_dir / f"{date_part}_parsed.xlsx"
        with pd.ExcelWriter(parsed_path, engine="openpyxl") as writer:
            if df_toc is not None and not df_toc.empty:
                df_toc.to_excel(writer, sheet_name="Table_de_matiere", index=False)
            if df_mens is not None and not df_mens.empty:
                df_mens.to_excel(writer, sheet_name="Mensuelle", index=False)
            writer.save()
        logger.info(f"Saved parsed Excel to custom output-dir: {parsed_path}")
    else:
        # Use built-in save_parsed
        try:
            out_path = parser_obj.save_parsed(df_toc, df_mens)
            logger.info(f"Parsed file saved at: {out_path}")
        except Exception as e:
            logger.error(f"Failed to save parsed output: {e}")

if __name__ == "__main__":
    main()
