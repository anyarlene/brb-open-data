import os
import pandas as pd

# Load the data using row 7 (0-indexed) as the header
data_mensuelle = pd.read_excel("data/IV.6.Importations par pays de provenance (en T)_9.xlsx", sheet_name="Mensuelle ", header=7)

# Identify columns that are likely dates (exclude columns that start with 'Unnamed')
date_columns = [col for col in data_mensuelle.columns if not str(col).startswith("Unnamed")]

# Melt the dataframe using the exact column name for 'Pays de destination' with leading spaces
data_long = pd.melt(data_mensuelle, id_vars=['     Pays de destination'], value_vars=date_columns, var_name='Date', value_name='Value')

# Convert the 'Date' column to datetime format
data_long['Date'] = pd.to_datetime(data_long['Date'])

# Remove rows with NaN in 'Value' column
data_long.dropna(subset=['Value'], inplace=True)

# Create the 'cleaned_data' folder if it doesn't exist
cleaned_folder = "cleaned_data"
if not os.path.exists(cleaned_folder):
    os.makedirs(cleaned_folder)


# Construct path to save the processes CSV
csv_path = os.path.join(cleaned_folder, 'processed_data.csv')
# Save the processed data to a CSV file
data_long.to_csv(csv_path, index=False)

# Display the restructured data
print(data_long)
