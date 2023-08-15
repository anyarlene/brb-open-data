import os
import pandas as pd

# Define the continent_markers dictionary
continent_markers = {
    "I. EUROPE": "EUROPE",
    "II. ASIE": "ASIE",
    "III. AFRIQUE": "AFRIQUE",
    "IV. AMERIQUE": "AMERIQUE",
    "V. OCEANIE": "OCEANIE",
    "VI. PAYS NON SPECIFIES": "PAYS NON SPECIFIES"
}

# Load the data using row 7 (0-indexed) as the header
data_mensuelle = pd.read_excel("data/IV.6.Importations par pays de provenance (en T)_9.xlsx", sheet_name="Mensuelle ", header=7)

# Identify columns that are likely dates (exclude columns that start with 'Unnamed')
date_columns = [col for col in data_mensuelle.columns if not str(col).startswith("Unnamed")]

# Melt the dataframe using the exact column name for 'Pays de destination' with leading spaces
data_long = pd.melt(data_mensuelle, id_vars=['     Pays de destination'], value_vars=date_columns, var_name='Date', value_name='Value')

# Convert the 'Date' column to datetime format
data_long['Date'] = pd.to_datetime(data_long['Date'])

# Convert "Value" column to numeric, setting any non-numeric values to NaN
data_long['Value'] = pd.to_numeric(data_long['Value'], errors='coerce')

# Drop rows with NaN values in the "Value" column
data_long.dropna(subset=['Value'], inplace=True)

# Populate the "continent" column using the continent markers
current_continent = None
for idx, row in data_long.iterrows():
    if row['     Pays de destination'] in continent_markers:
        current_continent = continent_markers[row['     Pays de destination']]
    if current_continent:
        data_long.at[idx, 'continent'] = current_continent

# Recompute the "Continent Total" column
continent_totals = data_long.groupby('continent')['Value'].sum().to_dict()
data_long['Continent Total'] = data_long['continent'].map(continent_totals)

# Create the 'cleaned_data' folder if it doesn't exist
cleaned_folder = "cleaned_data"
if not os.path.exists(cleaned_folder):
    os.makedirs(cleaned_folder)

# Construct path to save the processed CSV
csv_path = os.path.join(cleaned_folder, 'processed_data.csv')

# Save the processed data to a CSV file
data_long.to_csv(csv_path, index=False)

# Display the restructured data
print(data_long.head(20))
