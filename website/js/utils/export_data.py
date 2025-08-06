#!/usr/bin/env python3
import json
import pandas as pd
from pathlib import Path
from openpyxl.styles import Font

def load_json_data():
    """Load the monthly imports data from JSON file."""
    data_path = Path(__file__).parent.parent.parent / "data" / "monthly_imports_by_continent.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten_data(json_data):
    """Convert hierarchical JSON data to flat structure."""
    rows = []
    
    for year in json_data['data'].keys():
        year_data = json_data['data'][year]
        months = year_data['labels']
        
        for dataset in year_data['datasets']:
            continent = dataset['label']
            for month_idx, value in enumerate(dataset['data']):
                rows.append({
                    'Year': year,
                    'Month': months[month_idx],
                    'Continent': continent,
                    'Value_Million_BIF': value
                })
    
    return pd.DataFrame(rows)

def export_data():
    """Export data to CSV and XLSX formats."""
    # Load and transform data
    json_data = load_json_data()
    df = flatten_data(json_data)
    
    # Sort the data
    df = df.sort_values(['Year', 'Month', 'Continent'])
    
    # Create exports directory if it doesn't exist
    export_dir = Path(__file__).parent.parent.parent / "data" / "exports"
    export_dir.mkdir(exist_ok=True)
    
    # Export to CSV
    csv_path = export_dir / "monthly_imports_by_continent.csv"
    df.to_csv(csv_path, index=False)
    
    # Export to Excel with formatting
    xlsx_path = export_dir / "monthly_imports_by_continent.xlsx"
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Monthly Imports')
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Monthly Imports']
        
        # Format the header
        header_font = Font(bold=True)
        for cell in worksheet[1]:
            cell.font = header_font
        
        # Format the Value column to use thousands separator
        for row in range(2, len(df) + 2):
            cell = worksheet.cell(row=row, column=4)  # Value column
            cell.number_format = '#,##0.00'
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

    print(f"Data exported to:\n{csv_path}\n{xlsx_path}")

if __name__ == "__main__":
    export_data()