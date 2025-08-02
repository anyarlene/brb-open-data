# File: src/brb_open_data/parse/importation_bif_parser.py

import argparse
import logging
import re
import unicodedata
from pathlib import Path
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

# Month map for French abbreviations
_MONTH_MAP = {
    'janv':1, 'fevr':2, 'mars':3, 'avr':4, 'mai':5,
    'juin':6, 'juil':7, 'aout':8, 'sept':9, 'oct':10,
    'nov':11, 'dec':12,
}
_CONTINENT_PATTERN = re.compile(r'^[IVX]+\.', re.IGNORECASE)
_SUBCONT_PATTERN   = re.compile(r'^[0-9]+\.', re.IGNORECASE)

def _normalize_str(s:str) -> str:
    if not isinstance(s,str):
        return s
    s = unicodedata.normalize('NFKD', s.strip())
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).lower()

class ImportationBifParser:
    def __init__(self, excel_path:Path):
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel not found: {self.excel_path}")

    def parse_table_of_contents(self) -> pd.DataFrame:
        sheet = 'Table_de_matière'
        df0 = pd.read_excel(self.excel_path, sheet_name=sheet, header=None)
        header = next((
            i for i,row in df0.iterrows()
            if row.astype(str).str.contains('Nom des Feuilles', case=False, na=False).any()
        ), None)
        if header is None:
            raise ValueError(f"Cannot find ToC header in '{sheet}'")
        df = pd.read_excel(self.excel_path, sheet_name=sheet, header=header)
        col_map = {}
        for col in df.columns:
            cn = _normalize_str(str(col))
            if 'nom des feuilles' in cn: col_map[col] = 'sheet_name'
            elif 'description'    in cn: col_map[col] = 'description'
            elif 'frequence'      in cn: col_map[col] = 'frequency'
            elif 'derniere date'  in cn: col_map[col] = 'last_publication'
            elif 'nom du fichier' in cn: col_map[col] = 'excel_name'
            elif 'page web'       in cn: col_map[col] = 'source_url'
        df = df.rename(columns=col_map)
        for c in ('sheet_name','description','frequency',
                  'last_publication','excel_name','source_url'):
            if c in df.columns:
                df[c] = df[c].fillna('').astype(str).str.strip()
        df = df[df['sheet_name'].astype(bool)].copy()
        return df.reset_index(drop=True)

    def parse_mensuelle(self) -> pd.DataFrame:
        sheet = 'Mensuelle'
        df0 = pd.read_excel(self.excel_path, sheet_name=sheet, header=None)
        header = next((
            i for i,row in df0.iterrows()
            if 'pays de destination' in str(row.iloc[0]).lower()
        ), None)
        if header is None:
            raise ValueError(f"Cannot find 'Pays de destination' in '{sheet}'")
        df = pd.read_excel(self.excel_path, sheet_name=sheet, header=header)
        df = df.dropna(axis=1, how='all')
        df = df.rename(columns={df.columns[0]:'destination_country'})
        period_cols = [c for c in df.columns if c!='destination_country']
        df_long = (
            df.melt(
                id_vars=['destination_country'],
                value_vars=period_cols,
                var_name='period',
                value_name='value'
            )
            .dropna(subset=['period'])
            .reset_index(drop=True)
        )
        df_long['destination_country'] = df_long['destination_country'].astype(str).str.strip()

        def to_date(p):
            # If pandas already gave us a Timestamp/Datetime:
            if isinstance(p, (pd.Timestamp, datetime)):
                return p.replace(day=1)
            txt = str(p).strip()
            # Try to parse ISO style full datetime first
            try:
                dt = pd.to_datetime(txt)
                return dt.replace(day=1)
            except:
                pass
            # Fallback to French-abbrev logic
            t = txt.replace('.','').replace(' ','')
            parts = re.split(r'[-_/]', t)
            if len(parts)>=2:
                mon_raw,yr_raw = parts[0],parts[1]
            else:
                mon_raw,yr_raw = t[:-2],t[-2:]
            mon_norm = _normalize_str(mon_raw)
            month = _MONTH_MAP.get(mon_norm[:4]) or _MONTH_MAP.get(mon_norm[:3])
            try:
                year = (2000 + int(yr_raw)) if len(yr_raw)==2 else int(yr_raw)
            except:
                year = None
            if not month or not year:
                raise ValueError(f"Cannot parse period '{p}'")
            return pd.Timestamp(year,month,1)

        # apply and drop failures
        df_long['date'] = df_long['period'].map(lambda x: 
            to_date(x) if pd.notna(x) else pd.NaT
        )
        df_long = df_long.dropna(subset=['date']).reset_index(drop=True)
        df_long['value'] = pd.to_numeric(df_long['value'], errors='coerce')
        df_long = df_long.sort_values('date').reset_index(drop=True)

        # hierarchy columns
        for c in ('continent','subcontinent','continent_total','subcontinent_total','monthly_total'):
            df_long[c] = None

        cur_cont=cur_sub=None
        cur_ctot=cur_stot=None

        for dt,grp in df_long.groupby('date'):
            for idx,row in grp.iterrows():
                dest = row.destination_country or ''
                up = dest.upper()
                if up=='TOTAL' or 'TOTAL' in up:
                    df_long.loc[df_long.date==dt,'monthly_total'] = row.value
                elif _CONTINENT_PATTERN.match(dest):
                    cur_cont,cur_ctot,cur_sub,cur_stot = dest,row.value,None,None
                elif _SUBCONT_PATTERN.match(dest):
                    cur_sub,cur_stot = dest,row.value
                else:
                    df_long.at[idx,'continent']          = cur_cont
                    df_long.at[idx,'continent_total']    = cur_ctot
                    df_long.at[idx,'subcontinent']       = cur_sub
                    df_long.at[idx,'subcontinent_total'] = cur_stot or cur_ctot

        def strip_pref(s):
            if not isinstance(s,str): return None
            if _CONTINENT_PATTERN.match(s):
                return re.sub(r'^[IVXivx]+\.\s*','',s).strip()
            return re.sub(r'^[0-9]+\.\s*','',s).strip()

        df_long['continent']    = df_long['continent'].map(strip_pref)
        df_long['subcontinent'] = df_long['subcontinent'].map(strip_pref)
        df_long['year']         = df_long['date'].dt.year
        df_long['month']        = df_long['date'].dt.month

        out = df_long[[
            'date','year','month','destination_country','value',
            'continent','subcontinent','continent_total',
            'subcontinent_total','monthly_total'
        ]].reset_index(drop=True)

        drop_set = {
            'TOTAL','I. EUROPE','II. ASIE','III. AFRIQUE',
            'IV. AMERIQUE','V. OCEANIE','VI. PAYS NON SPECIFIES'
        }
        return out[~out.destination_country.isin(drop_set)].reset_index(drop=True)

    def save_parsed(self, df_toc:pd.DataFrame, df_mens:pd.DataFrame) -> Path:
        # Both must not be empty
        if ((df_toc is None or df_toc.empty) and 
            (df_mens is None or df_mens.empty)):
            raise RuntimeError("Both ToC and Mensuelle are empty – nothing to save.")

        project_root = self.excel_path.parents[3]
        target = project_root / "data" / "parsed" / "importation_bif"
        target.mkdir(parents=True, exist_ok=True)

        date_part = self.excel_path.stem.split("_",1)[0]
        if not (date_part.isdigit() and len(date_part)==8):
            date_part = datetime.now().strftime("%Y%m%d")
            logger.warning(f"Using today's date: {date_part}")

        xlsx      = target / f"{date_part}_parsed.xlsx"
        json_toc  = target / f"{date_part}__toc.json"
        csv_toc   = target / f"{date_part}__toc.csv"
        json_mens = target / f"{date_part}__mensuelle.json"
        csv_mens  = target / f"{date_part}__mensuelle.csv"


        # drop any “Unnamed…” columns that came from pandas indexes
        if df_toc is not None:
                df_toc = df_toc.loc[:, ~df_toc.columns.str.startswith("Unnamed")]
        if df_mens is not None:
            df_mens = df_mens.loc[:, ~df_mens.columns.str.startswith("Unnamed")]
        # Report which sheets will be written
        logger.info(f"About to write XLSX with sheets: "
                    f"{'Table_de_matière' if df_toc is not None and not df_toc.empty else ''} "
                    f"{'Mensuelle' if df_mens is not None and not df_mens.empty else ''}")

        # 1) Combined XLSX
        with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
            if df_toc is not None and not df_toc.empty:
                df_toc.to_excel(writer, sheet_name="Table_de_matière", index=False)
            if df_mens is not None and not df_mens.empty:
                df_mens.to_excel(writer, sheet_name="Mensuelle",      index=False)
        logger.info(f"Wrote combined XLSX → {xlsx}")

        # 2) Side car JSON/CSV
        if df_toc is not None and not df_toc.empty:
            df_toc.to_json (json_toc,  orient="records", date_format="iso", force_ascii=False, indent=2)
            df_toc.to_csv  (csv_toc,   index=False)
            logger.info(f"Wrote ToC JSON→{json_toc} CSV→{csv_toc}")
        if df_mens is not None and not df_mens.empty:
            df_mens.to_json(json_mens, orient="records", date_format="iso", force_ascii=False, indent=2)
            df_mens.to_csv (csv_mens,  index=False)
            logger.info(f"Wrote Mensuelle JSON→{json_mens} CSV→{csv_mens}")

        return xlsx


def main():
    p = argparse.ArgumentParser(description="Parse BIF importations → XLSX+JSON/CSV")
    p.add_argument("-i","--input",     required=True, help="raw .xlsx path")
    p.add_argument("-o","--output-dir", default=None, help="(not used yet)")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    raw = Path(args.input)
    if not raw.exists():
        logger.error(f"Input not found: {raw}")
        return

    parser = ImportationBifParser(raw)

    try:
        toc = parser.parse_table_of_contents()
        logger.info(f"Parsed ToC: {len(toc)} rows")
    except Exception as e:
        logger.error(f"Failed ToC parse: {e}")
        toc = None

    try:
        mens = parser.parse_mensuelle()
        logger.info(f"Parsed Mensuelle: {len(mens)} rows")
    except Exception as e:
        logger.error(f"Failed Mensuelle parse: {e}")
        mens = None

    try:
        out = parser.save_parsed(toc, mens)
        logger.info(f"All done – parsed file at: {out}")
    except Exception as e:
        logger.error(f"Could not save parsed output: {e}")

if __name__=="__main__":
    main()
