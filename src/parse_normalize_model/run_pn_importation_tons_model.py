import os
from pn_importation_tons_model import ImportationTonsParseNormalizeModel

def main():
    # Create an instance of the model
    model = ImportationTonsParseNormalizeModel()

    # Ensure the 'cleaned_data' and 'processed_data' folders exist
    for folder in [model.input_folder, model.output_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Load, process, and save the data
    df_original = model.load_data()

    # Display first few rows of the original data
    print("Original Data:")
    print(df_original.head())
    print("\n" + "="*80 + "\n")  # Just to separate the printed sections

    df_final = model.process_data(df_original)

    # Display first few rows of the processed data
    print("Cleaned Data:")
    print(df_final.head())

    model.save_data(df_final)

    # Print a successful message
    print("\nData successfully loaded, processed, and saved!")

if __name__ == "__main__":
    main()
