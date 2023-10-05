import os
import pandas as pd
from decouple import config
import requests

class ImportationTonsDataModel:
    def __init__(self):
        # Initializing the base and relative URLs from configuration
        self.BASE_URL = config("BASE_URL")
        self.RELATIVE_PATH_IMPORTATION_TONS = config("RELATIVE_PATH_IMPORTATION_TONS")
        
        # Constructing the full URL for the data source
        self.full_url = self.BASE_URL + self.RELATIVE_PATH_IMPORTATION_TONS
        
        # Setting paths to the existing 'data' and 'cleaned_data'
        self.data_folder = "../data"
        self.cleaned_folder = "../cleaned_data"
        
        # Initializing other instance variables
        self.excel_filename = None
        self.data_mensuelle = None
        self.data_long = None

    def fetchData(self):
        # Fetching data from the specified URL
        response = requests.get(self.full_url)
        
        # Raise an error if the request was unsuccessful
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch the Excel file. HTTP Status Code: {response.status_code}")
        
        # Extracting the filename and making any necessary replacements
        self.excel_filename = os.path.basename(self.RELATIVE_PATH_IMPORTATION_TONS).replace('%', '_')
        
        # Constructing the path to save the fetched data
        full_save_path = os.path.join(self.data_folder, self.excel_filename)
        
        # Saving the fetched data
        with open(full_save_path, 'wb') as file:
            file.write(response.content)
        
        return full_save_path

    def processData(self, path):
        # Loading the Excel data
        self.data_mensuelle = pd.read_excel(path, sheet_name="Mensuelle ", header=7)
        
        # Extracting date columns
        date_columns = [col for col in self.data_mensuelle.columns if not str(col).startswith("Unnamed")]
        
        # Transforming the data from wide to long format
        self.data_long = pd.melt(self.data_mensuelle, id_vars=['     Pays de destination'], value_vars=date_columns, var_name='Date', value_name='Value')
        
        # Converting the 'Date' column to datetime format
        self.data_long['Date'] = pd.to_datetime(self.data_long['Date'])
        
        # Removing rows with missing data
        self.data_long.dropna(subset=['Value'], inplace=True)

    def saveProcessedData(self):
        # Constructing the path to save the processed data
        csv_path = os.path.join(self.cleaned_folder, 'processed_importation_tons.csv')
        
        # Saving the processed data to CSV
        self.data_long.to_csv(csv_path, index=False)
        
        return csv_path

    def fetchAndProcess(self):
        # A convenience method to fetch and then process the data
        path = self.fetchData()
        self.processData(path)
        return self.data_long

    def displayData(self):
        # Returning the processed data
        return self.data_long
