import os
import requests
import pandas as pd
from decouple import config

class InflationDataModel:

    def __init__(self):

        # Set up variables for BASE URL and relative path to inflation data
        self.BASE_URL = config('BASE_URL')
        self.RELATIVE_PATH_INFLATION = config('RELATIVE_PATH_INFLATION')

        # Constructing the full URL for the data source
        self.full_url = self.BASE_URL + self.RELATIVE_PATH_INFLATION
        # Initialize the DataFrame to store data
        self.data_folder = os.path.join("..", "..", "data")
        self.cleaned_folder = os.path.join("..", "..", "processed_data")

        # Initializing other instance variables
        self.excel_filename = os.path.basename(self.RELATIVE_PATH_INFLATION).replace('%', '_')
        self.df = None

    def download_data(self):
        # Construct the full URL to fetch the file
        #file_url = f"{self.BASE_URL}{self.RELATIVE_PATH_INFLATION}"
        response = requests.get(self.full_url)

        # Ensure the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to download the file. HTTP Status Code: {response.status_code}")

        # Set path to 'data' folder located outside 'src'
        #data_folder = os.path.join("..", "..", "data")

        # Extract the filename from RELATIVE_PATH and replace '%' with '_'
        #self.excel_filename = os.path.basename(self.RELATIVE_PATH_INFLATION).replace('%', '_')
        self.excel_path = os.path.join(self.data_folder, self.excel_filename)

        # Save the downloaded file locally
        with open(self.excel_path, 'wb') as file:
            file.write(response.content)
        
        return self.excel_path  # Return the path to the downloaded file

    def clean_data(self):
        # Read the Excel data, skipping initial rows
        self.df = pd.read_excel(self.excel_path, skiprows=9, engine='openpyxl')

        # Extract headers and clean up the DataFrame structure
        headers = self.df.iloc[0]
        self.df = self.df[1:]
        self.df.columns = headers

        # Drop unnecessary rows and reset the index
        self.df.drop(1, inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        # Clean column names
        if self.df.columns[0] is pd.NA or pd.isna(self.df.columns[0]):
            self.df.columns.values[0] = "Annee"
        if 'Annuelle' in self.df.columns[-1]:
            self.df.columns.values[-1] = "Moyenne Annuelle"

        # Filter out rows without a year and convert data types
        self.df = self.df[self.df['Annee'].notna()]
        self.df['Annee'] = self.df['Annee'].astype(int)
        for column in self.df.columns[1:]:
            self.df[column] = self.df[column].astype(float)

        return self.df

    def save_csv(self):
        # Format the filename for the cleaned CSV
        base_name = os.path.splitext(os.path.basename(self.excel_path))[0]
        formatted_name = base_name.lower().replace('-', '_')
        csv_filename = f"processed_{formatted_name}.csv"

        # Set path to 'cleaned_data' folder
        #cleaned_folder = os.path.join("..", "..", "processed_data")

        # Save the cleaned DataFrame as a CSV
        csv_path = os.path.join(self.cleaned_folder, csv_filename)
        self.df.to_csv(csv_path, index=False)

        # Return the path to the saved CSV
        return csv_path
