import pandas as pd
import re
import numpy as np

# Read the CSV file using the correct delimiter
df_original = pd.read_csv("cleaned_data/processed_importations_tonnes.csv", sep=";")

# Split the single column into multiple columns
df_original[['destination_country', 'date', 'value']] = df_original['     Pays de destination,Date,Value'].str.split(',', expand=True)
df_original.drop(columns=['     Pays de destination,Date,Value'], inplace=True)

# Replace 'nd' and '…' with NaN and Convert Value column to float
df_original['value'] = df_original['value'].replace(['nd', '…'], np.nan).astype(float)

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

    # If the row represents the TOTAL for the month
    if destination == 'TOTAL':
        current_monthly_total = row['value']
        month_year = row['date']

        # Assign monthly_total to previous rows of the same month
        df_original.loc[df_original['date'] == month_year, 'monthly_total'] = current_monthly_total

    # Check for main header (continent)
    elif re.match(r"^[IVX]+\.", destination):
        current_continent = destination
        current_total = row['value']
        current_subregion = None
        current_subtotal = None
        continue

    # Check for sub-header
    elif re.match(r"^[0-9]+\.", destination):
        current_subregion = destination
        current_subtotal = row['value']
        continue

    # For individual countries
    df_original.at[idx, 'continent'] = current_continent
    df_original.at[idx, 'subcontinent'] = current_subregion if current_subregion else 'None'
    df_original.at[idx, 'continent_total'] = current_total
    df_original.at[idx, 'subcontinent_total'] = current_subtotal if current_subtotal else current_total

# Drop rows that are continent headers, subregion headers, or TOTAL rows
problematic_strings = ['I. EUROPE', 'II. ASIE', 'III. AFRIQUE', 'IV. AMERIQUE', 'V. OCEANIE', 'VI. PAYS NON SPECIFIES', '1. Union Européenne', '2. AUTRES', 'TOTAL']
df_final = df_original[~df_original['destination_country'].str.strip().isin(problematic_strings)].copy()

# Reset index for the final dataframe
df_final.reset_index(drop=True, inplace=True)

# Convert the 'date' column to a datetime object
df_final['date'] = pd.to_datetime(df_final['date'])

# Extract month and year and add them to new columns
df_final['month'] = df_final['date'].dt.month
df_final['year'] = df_final['date'].dt.year

# Rearrange columns
desired_columns = ['date', 'month', 'year', 'destination_country', 'value', 'continent', 
                   'subcontinent', 'continent_total', 'subcontinent_total', 'monthly_total']
df_final = df_final[desired_columns]


# Display the first few rows of the final dataframe for verification
#print(df_final.head(50))

# Display the last few rows of the final dataframe for verification
print(df_final.tail(50))

# Save to CSV
df_final.to_csv('cleaned_data/cleaned_importations_tonnes.csv', index=False)