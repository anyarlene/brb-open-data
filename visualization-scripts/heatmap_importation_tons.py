import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

try:
    # Adjust the file_path to point to the 'cleaned_data' folder
    file_path = os.path.join("cleaned_data", "cleaned_importation_tons.csv")

    # Read the dataset
    df = pd.read_csv(file_path)
    
    # Extract year and month from the date
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month
    
    # Group the data by year and month to prepare data for the heatmap
    heatmap_data = df.groupby(['year', 'month'])['monthly_total'].first().unstack()
    
    # Define the path to save the heatmap and create the directory if it doesn't exist
    dashboard_folder = "importation_dashboards"
    if not os.path.exists(dashboard_folder):
        os.makedirs(dashboard_folder)
    
    # Plot the heatmap
    plt.figure(figsize=(15, 10))
    sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt=".0f", linewidths=.5)
    plt.title('Valeurs Mensuelles des Importations (en tonnes) pour chaque Année')


    # Rotate the labels
    plt.xlabel('Mois')
    plt.ylabel('Année')
    plt.xticks(rotation=0)  # Rotate the month labels to horizontal orientation
    plt.yticks(rotation=0)    # Rotate the year labels to horizontal orientation

    plt.tight_layout()
    
    # Save the heatmap to the specified path
    heatmap_path = os.path.join(dashboard_folder, 'monthly_importation_tons_heatmap.png')
    plt.savefig(heatmap_path)
    print(f"Heatmap saved successfully at: {heatmap_path}")
    # Uncomment below if you want to display the plots
    plt.show()

except FileNotFoundError:
    print("Error: The file 'cleaned_importation_tons.csv' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
