from inflation_data_model import InflationDataModel

if __name__ == "__main__":
    # Suppress FutureWarnings for cleaner output
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # Create an instance of the data model
    model = InflationDataModel()

    # Download data from the provided URL
    model.download_data()

    # Clean and structure the data for further analysis
    model.clean_data()

    # Save the cleaned data as a CSV file
    csv_path = model.save_csv()

    # Notify the user about the saved CSV
    print(f"Cleaned CSV saved to {csv_path}")
