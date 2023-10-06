import os
import pandas as pd
from decouple import config
import requests

class ImportationBifDataModel:
    def __init__(self):
        # Initializing the base and relative URLs from configuration
        self.BASE_URL = config("BASE_URL")
        self.RELATIVE_PATH_IMPORTATION_BIF = config("RELATIVE_PATH_IMPORTATION_BIF")
        self.DATA_FOLDER = os.path.join("..", "..", "data")
        self.PROCESSED_FOLDER = os.path.join("..", "..", "processed_data")
        self.CORE_NAME = "importation_bif"

    def fetch_excel(self):
        full_url = self.BASE_URL + self.RELATIVE_PATH_IMPORTATION_BIF
        response = requests.get(full_url)

        # Ensure the request was successful
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch the Excel file. HTTP Status Code: {response.status_code}")

        # Extract the filename and save the Excel content
        excel_filename = os.path.basename(self.RELATIVE_PATH_IMPORTATION_BIF).replace('%', '_')
        full_save_path = os.path.join(self.DATA_FOLDER, excel_filename)
        with open(full_save_path, 'wb') as file:
            file.write(response.content)

        return full_save_path

    def process_data(self, excel_path):
        data_mensuelle = pd.read_excel(excel_path, sheet_name="Mensuelle", header=7)
        date_columns = [col for col in data_mensuelle.columns if not str(col).startswith("Unnamed")]
        data_long = pd.melt(data_mensuelle, id_vars=['     Pays de destination'], value_vars=date_columns, var_name='Date', value_name='Value')
        data_long['Date'] = pd.to_datetime(data_long['Date'])
        data_long.dropna(subset=['Value'], inplace=True)

        return data_long

    def save_processed_data(self, data):
        csv_filename = f"processed_{self.CORE_NAME}.csv"
        csv_path = os.path.join(self.PROCESSED_FOLDER, csv_filename)
        data.to_csv(csv_path, index=False)
