import pandas as pd
from urllib3.exceptions import NotOpenSSLWarning
from inflation_data_model import InflationDataModel

import warnings
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

if __name__ == "__main__":
    # Suppress FutureWarnings for cleaner output
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # Create an instance of the data model
    model = InflationDataModel()

    # Download data from the provided URL
    excel_path = model.download_data()

    # Load the original data from the Excel file for display
    original_data = pd.read_excel(excel_path)
    print("Original Data:")
    print(original_data.head())
    print("\n" + "="*80 + "\n")  # Separator for clarity

    # Clean and structure the data for further analysis
    processed_data = model.clean_data()

    # Display the cleaned data
    print("Cleaned Data:")
    print(processed_data.head())  # Assuming cleaned_data is an attribute of the model

    # Save the cleaned data as a CSV file
    csv_path = model.save_csv()

    # Print successful message
    print(f"Cleaned CSV saved to {csv_path}")
