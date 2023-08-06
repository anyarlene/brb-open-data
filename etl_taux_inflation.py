import os
import requests
from decouple import config
import pandas as pd

# Suppress FutureWarnings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

BASE_URL = config('BASE_URL')
RELATIVE_PATH = config('RELATIVE_PATH')

# Construct the full URL to fetch the file
file_url = f"{BASE_URL}{RELATIVE_PATH}"

response = requests.get(file_url)

# Save the Excel file under the 'data' folder
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Using a static filename without current date for the Excel file
excel_filename = "Taux d'Inflation Juin 2023.xlsx"
excel_path = os.path.join(data_folder, excel_filename)

with open(excel_path, 'wb') as file:
    file.write(response.content)

# Read, clean, and save the structured data to a CSV file
file_path = os.path.join(data_folder, excel_filename)
df = pd.read_excel(file_path, skiprows=9, engine='openpyxl')

headers = df.iloc[0]
df = df[1:]
df.columns = headers

df.drop(1, inplace=True)
df.reset_index(drop=True, inplace=True)

if df.columns[0] is pd.NA or pd.isna(df.columns[0]):
    df.columns.values[0] = "Annee"
if 'Annuelle' in df.columns[-1]:
    df.columns.values[-1] = "Moyenne Annuelle"

df = df[df['Annee'].notna()]
df['Annee'] = df['Annee'].astype(int)

for column in df.columns[1:]:
    df[column] = df[column].astype(float)

base_name = os.path.splitext(excel_filename)[0]
formatted_name = base_name.lower().replace(' ', '_').replace('-', '_')
csv_filename = f"cleaned_{formatted_name}.csv"

# Create the 'cleaned_data' folder if it doesn't exist
cleaned_folder = "cleaned_data"
if not os.path.exists(cleaned_folder):
    os.makedirs(cleaned_folder)

# Construct path to save the cleaned CSV
csv_path = os.path.join(cleaned_folder, csv_filename)
df.to_csv(csv_path, index=False)
print(f"Cleaned CSV saved to {csv_path}")
