import os
import pandas as pd
from urllib3.exceptions import NotOpenSSLWarning
from importation_tons_data_model import ImportationTonsDataModel

import warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


if __name__ == "__main__":
    model = ImportationTonsDataModel()

    # Ensure the 'data' and 'processed_data' folders exist
    for folder in [model.data_folder, model.processed_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    excel_path = model.fetchData()

    # Load the original data from the Excel file for display
    original_data = pd.read_excel(excel_path, sheet_name="Mensuelle ", header=7)
    print("Original Data:")
    print(original_data.head())
    print("\n" + "="*80 + "\n")  # Separator for clarity


    processed_data = model.fetchAndProcess()

    # Display the first few rows of the processed data
    print("Processed Data:")
    print(processed_data.head())

    model.saveProcessedData()

    print(model.displayData())

    # Print successful message
    print("Data successfully fetched, processed, and saved!")
