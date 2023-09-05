import os
import pandas as pd
from decouple import config
import requests
from io import BytesIO

# Base URL and relative path
BASE_URL = config("BASE_URL")
RELATIVE_PATH_IMPORTATION_BIF = config("RELATIVE_PATH_IMPORTATION_BIF")
full_url = BASE_URL + RELATIVE_PATH_IMPORTATION_BIF

# Fetch the Excel file
response = requests.get(full_url)

# Ensure the request was successful
if response.status_code != 200:
    raise ValueError(f"Failed to fetch the Excel file. HTTP Status Code: {response.status_code}")

# Extract the original filename from the URL and replace '%' with '_'
excel_filename = os.path.basename(RELATIVE_PATH_IMPORTATION_BIF).replace('%', '_')

# Create the 'data' folder if it doesn't exist and construct the full path for saving
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
full_save_path = os.path.join(data_folder, excel_filename)

# Save the Excel file content to the specified path
with open(full_save_path, 'wb') as file:
    file.write(response.content)

# Load the data using row 7 (0-indexed) as the header
data_mensuelle = pd.read_excel(full_save_path, sheet_name="Mensuelle", header=7)

# Identify columns that are likely dates (exclude columns that start with 'Unnamed')
date_columns = [col for col in data_mensuelle.columns if not str(col).startswith("Unnamed")]

# Melt the dataframe using the exact column name for 'Pays de destination' with leading spaces
data_long = pd.melt(data_mensuelle, id_vars=['     Pays de destination'], value_vars=date_columns, var_name='Date', value_name='Value')

# Convert the 'Date' column to datetime format
data_long['Date'] = pd.to_datetime(data_long['Date'])

# Remove rows with NaN in 'Value' column
data_long.dropna(subset=['Value'], inplace=True)

# Create the 'cleaned_data' folder if it doesn't exist
cleaned_folder = "cleaned_data"
if not os.path.exists(cleaned_folder):
    os.makedirs(cleaned_folder)

# Construct path to save the processed CSV
csv_path = os.path.join(cleaned_folder, 'processed_importation_bif.csv')

# Save the processed data to a CSV file
data_long.to_csv(csv_path, index=False)

# Optional: Display the restructured data
#print(data_long)
