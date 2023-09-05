import pandas as pd
import re
import numpy as np
import os

# Define directories
input_folder = "processed_data"
output_folder = "cleaned_data"

# Create the 'cleaned_data' and 'processed_data' folders if they don't exist
for folder in [input_folder, output_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# List all files in the processed_data directory that start with "processed" and end with "_bif.csv"
target_files = [file for file in os.listdir(input_folder) if file.startswith("processed") and file.endswith("_bif.csv")]

# Ensure there's at least one such file and select it
if target_files:
    input_filename = target_files[0]
else:
    raise ValueError("No file matching the specified pattern found in the processed_data directory.")

# Define input path
input_path = os.path.join(input_folder, input_filename)

# Replace the known input prefix with the desired output prefix for output filename
output_filename = input_filename.replace("processed_", "cleaned_")
output_path = os.path.join(output_folder, output_filename)

# Read the CSV file using the correct delimiter
df_original = pd.read_csv(input_path, sep=";")

# Split the single column into multiple columns
df_original[['destination_country', 'date', 'value']] = df_original['     Pays de destination,Date,Value'].str.split(',', expand=True)
df_original.drop(columns=['     Pays de destination,Date,Value'], inplace=True)

# Replace problematic strings with NaN and Convert Value column to float
df_original['value'] = df_original['value'].replace(['nd', '…', '-', '0-'], np.nan).astype(float)

# Initialize empty columns for Continent, Subregion, Total, Subtotal, and monthly_total
df_original['continent'] = None
df_original['subcontinent'] = None
df_original['continent_total'] = None
df_original['subcontinent_total'] = None
df_original['monthly_total'] = None

# Initialize variables to store current continent, subregion, total, and subtotal values
current_continent = None
current_subregion = None
current_total = None
current_subtotal = None

# Iterate over the dataframe to populate Continent, Subregion, Total, Subtotal, and monthly_total
for idx, row in df_original.iterrows():
    destination = row['destination_country'].strip()

    if destination == 'TOTAL':
        current_monthly_total = row['value']
        month_year = row['date']
        df_original.loc[df_original['date'] == month_year, 'monthly_total'] = current_monthly_total

    elif re.match(r"^[IVX]+\.", destination):
        current_continent = destination
        current_total = row['value']
        current_subregion = None
        current_subtotal = None
        continue

    elif re.match(r"^[0-9]+\.", destination):
        current_subregion = destination
        current_subtotal = row['value']
        continue

    df_original.at[idx, 'continent'] = current_continent
    df_original.at[idx, 'subcontinent'] = current_subregion if current_subregion else 'None'
    df_original.at[idx, 'continent_total'] = current_total
    df_original.at[idx, 'subcontinent_total'] = current_subtotal if current_subtotal else current_total

# Remove prefixes from 'continent' and 'subcontinent' columns
df_original['continent'] = df_original['continent'].str.replace(r"^[IVX]+\.", "", regex=True).str.strip()
df_original['subcontinent'] = df_original['subcontinent'].str.replace(r"^[0-9]+\.", "", regex=True).str.strip()

# Drop rows that are continent headers, subregion headers, or TOTAL rows
problematic_strings_with_prefixes = ['I. EUROPE', 'II. ASIE', 'III. AFRIQUE', 'IV. AMERIQUE', 'V. OCEANIE', 'VI. PAYS NON SPECIFIES', '1. Union Européenne', '2. AUTRES', 'TOTAL']
df_final = df_original[~df_original['destination_country'].str.strip().isin(problematic_strings_with_prefixes)].copy()

# Reset index
df_final.reset_index(drop=True, inplace=True)

# Convert the 'date' column to a datetime object and extract month and year
df_final['date'] = pd.to_datetime(df_final['date'])
df_final['month'] = df_final['date'].dt.month
df_final['year'] = df_final['date'].dt.year

# Rearrange columns
desired_columns = ['date', 'month', 'year', 'destination_country', 'value', 'continent', 
                   'subcontinent', 'continent_total', 'subcontinent_total', 'monthly_total']
df_final = df_final[desired_columns]

# Save to CSV
df_final.to_csv(output_path, index=False)
