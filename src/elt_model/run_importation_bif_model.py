import os
import pandas as pd

from importation_bif_data_model import ImportationBifDataModel 

if __name__ == "__main__":
    # Create an instance of the model
    model = ImportationBifDataModel()
    
    # Ensure the 'data' and 'processed_data' folders exist
    for folder in [model.DATA_FOLDER, model.PROCESSED_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Fetch, process, and save the data
    excel_path = model.fetch_excel()

    # Load the original data from the Excel file for display
    original_data = pd.read_excel(excel_path, sheet_name="Mensuelle", header=7)
    print("Original Data:")
    print(original_data.head())
    print("\n" + "="*80 + "\n")  # Separator for clarity

    processed_data = model.process_data(excel_path)

    # Display the first few rows of the processed data
    print("Processed Data:")
    print(processed_data.head())

    model.save_processed_data(processed_data)

    # Print successful message
    print("Data successfully fetched, processed, and saved!")


