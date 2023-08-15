import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

# Adjust the file_path to point to the 'cleaned_data' folder
file_path = os.path.join("cleaned_data", "cleaned_taux_d'inflation_juin_2023.csv")

try:
    # Extract month_year from the CSV filename
    base_name = os.path.basename(file_path)
    match = re.search(r"_(\w+_\d{4})", base_name)
    if match:
        month_year = match.group(1)
    else:
        raise ValueError("Could not extract month and year from the filename!")

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Handle NaN values in the DataFrame
    df.fillna(0, inplace=True)

    # Number of rows and columns for subplots
    n_rows = 4
    n_cols = 3

    # Create a figure and a set of subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 12))

    # Flatten the 2D list of axes into 1D for easier indexing
    axes_flat = axes.flatten()

    # Loop through each month's column and plot it on its own subplot
    for idx, month in enumerate(df.columns[1:-1]):
        ax = axes_flat[idx]
        ax.plot(df['Annee'], df[month], marker='o', color='blue')
        ax.set_title(month)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_xlabel("Annee")
        ax.set_ylabel("% Annuel")

    # Adjust the layout of the plots to prevent overlap
    plt.tight_layout()
    fig.subplots_adjust(top=0.92)  # Adjust the top space
    fig.suptitle(f"Taux d'Inflation Mensuelle ({month_year})", fontsize=16)

    # Create a new folder (if it doesn't exist) to save the generated dashboard
    new_folder = "inflation_dashboards"
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    # Save the figure into the new folder using month_year
    save_path = os.path.join(new_folder, f"{month_year}_dashboard_2.png")
    fig.savefig(save_path)

    # Display the plots
    #plt.show()

except FileNotFoundError:
    print(f"File {file_path} not found.")
except Exception as e:
    print(f"Error: {e}")
