import os

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
    processed_data = model.process_data(excel_path)
    model.save_processed_data(processed_data)


    # Print successful message
    print("Data successfully fetched, processed, and saved!")


