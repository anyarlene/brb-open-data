import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import urllib.parse

# Modify the file_path to point to the 'cleaned_data' folder
file_path = os.path.join("processed_data", "processed_taux_20d_27inflation_20juillet_202023.csv")

try:
    # Extract month_year from the CSV filename
    base_name = os.path.basename(file_path).replace(".csv", "")
    decoded_name = urllib.parse.unquote(base_name)
    parts = decoded_name.split("_")

    if len(parts) >= 2:
        month = parts[-2][2:]  # Remove the first 2 characters (e.g., "20")
        year = parts[-1][-4:]  # Extract the last 4 characters
        month_year = f"{month}_{year}"
    else:
        raise ValueError("Could not extract month and year from the filename!")

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Handle NaN values in the DataFrame by filling with 0
    df.fillna(0, inplace=True)

    # Initialize the figure with 2 subplots: one above the other
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(14, 16))

    # Plotting monthly inflation rates on the first subplot
    colors = plt.cm.viridis_r(np.linspace(0, 1, len(df.columns[1:-1])))
    for idx, month in enumerate(df.columns[1:-1]):
        axes[0].plot(df['Annee'], df[month], marker='o', label=month, color=colors[idx])
    axes[0].set_title(f"Taux d'Inflation Mensuelle ({month_year})")
    axes[0].set_xlabel("Annee")
    axes[0].set_ylabel("% Annuel")
    axes[0].grid(True, which='both', linestyle='--', linewidth=0.5)
    axes[0].legend(loc="upper left")

    # Adjust y-axis ticks for the first subplot
    min_val = df[df.columns[1:-1]].values.min()
    max_val = df[df.columns[1:-1]].values.max()
    if min_val != max_val and not (np.isnan(min_val) or np.isnan(max_val) or np.isinf(min_val) or np.isinf(max_val)):
        step_val = 1 if (max_val - min_val) < 5 else 5
        axes[0].set_yticks(np.arange(min_val, max_val + step_val, step_val))

    # Plotting the Moyenne Annuelle on the second subplot
    axes[1].plot(df['Annee'], df['Moyenne Annuelle'], marker='o', color='red', linewidth=2.5)
    axes[1].set_title(f"Moyenne Annuelle du Taux d'Inflation ({month_year})")
    axes[1].set_xlabel("Annee")
    axes[1].set_ylabel("% Moyenne Annuel")
    axes[1].grid(True, which='both', linestyle='--', linewidth=0.5)

    # Adjust y-axis ticks for the second subplot
    min_val = df['Moyenne Annuelle'].min()
    max_val = df['Moyenne Annuelle'].max()
    if min_val != max_val and not (np.isnan(min_val) or np.isnan(max_val) or np.isinf(min_val) or np.isinf(max_val)):
        step_val = 1 if (max_val - min_val) < 5 else 5
        axes[1].set_yticks(np.arange(min_val, max_val + step_val, step_val))

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Create a new folder (if it doesn't exist)
    new_folder = "inflation_dashboards"
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    # Save the figure into the new folder using month_year
    save_path = os.path.join(new_folder, f"{month_year}_dashboard_1.png")
    plt.savefig(save_path)

    # Display the plot
    plt.show()

# Catch specific file not found error
except FileNotFoundError:
    print(f"File {file_path} not found.")

# Catch any other general exceptions/errors
except Exception as e:
    print(f"Error: {e}")
