import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

# Modify the file_path to point to the 'cleaned_data' folder
file_path = os.path.join("cleaned_data", "cleaned_taux_d'inflation_juin_2023.csv")

try:
    # Extract month_year from the CSV filename
    base_name = os.path.basename(file_path)  # Extracts "cleaned_taux_d'inflation_juin_2023.csv"
    match = re.search(r"_(\w+_\d{4})", base_name)
    if match:
        month_year = match.group(1)  # e.g., "juin_2023"
    else:
        raise ValueError("Could not extract month and year from the filename!")

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Handle NaN values in the DataFrame
    # Filling NaN with 0
    df.fillna(0, inplace=True)

    # Plotting
    plt.figure(figsize=(14, 8))

    # Use a colormap to generate a list of distinct colors for each month
    colors = plt.cm.viridis_r(np.linspace(0, 1, len(df.columns[1:-1])))

    # Loop through each month's column and plot it with the color from the colormap
    for idx, month in enumerate(df.columns[1:-1]):
        plt.plot(df['Annee'], df[month], marker='o', label=month, color=colors[idx])

    # Customizing the plot
    plt.title("Taux d'Inflation Mensuelle par Annee")
    plt.xlabel("Annee")
    plt.ylabel("% Annuel")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(loc="upper left")

    # Fix for yticks issue
    min_val = df[df.columns[1:-1]].values.min()
    max_val = df[df.columns[1:-1]].values.max()

    print(f"min_val: {min_val}, max_val: {max_val}")

    # Check if min_val and max_val are the same or if they are NaN or infinite
    if min_val == max_val or np.isnan(min_val) or np.isnan(max_val) or np.isinf(min_val) or np.isinf(max_val):
        print("Invalid values for yticks detected. Using default yticks.")
    else:
        if max_val - min_val < 5:
            step_val = 1
        else:
            step_val = 5
        plt.yticks(np.arange(min_val, max_val + step_val, step_val))

    plt.tight_layout()

    # Create a new folder (if it doesn't exist)
    new_folder = "ti_charts_dashboards"
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    # Save the figure into the new folder using month_year
    save_path = os.path.join(new_folder, f"{month_year}_chart.png")
    plt.savefig(save_path)

    # Show the plot
    plt.show()
except FileNotFoundError:
    print(f"File {file_path} not found.")
except Exception as e:
    print(f"Error: {e}")
