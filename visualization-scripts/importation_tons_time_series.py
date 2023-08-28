import os
import pandas as pd
import matplotlib.pyplot as plt

try:
    # Adjust the file_path to point to the 'cleaned_data' folder
    file_path = os.path.join("cleaned_data", "cleaned_importation_tons.csv")

    # Read the dataset
    df = pd.read_csv(file_path)

    # Convert the 'date' column to a datetime object for plotting
    df['date'] = pd.to_datetime(df['date'])

    # Group the data by date, continent, and then sum the continent_total values
    continent_time_series_data = df.groupby(['date', 'continent'])['continent_total'].first().unstack()

    # Define the path to save the heatmap and create the directory if it doesn't exist
    dashboard_folder = "importation_dashboards"
    if not os.path.exists(dashboard_folder):
        os.makedirs(dashboard_folder)

    # Define distinct colors for each continent
    colors = {
        'EUROPE': 'blue',
        'ASIE': 'red',
        'AFRIQUE': 'green',
        'AMERIQUE': 'purple',
        'OCEANIE': 'orange',
        'PAYS NON SPECIFIES': 'brown'
    }

    # Plotting the time series data for each continent
    plt.figure(figsize=(15, 10))
    for continent in continent_time_series_data.columns:
        plt.plot(continent_time_series_data.index, continent_time_series_data[continent], label=continent, color=colors[continent])

    plt.title('Valeur Totale des Importations par Continent')
    plt.xlabel('Année')
    plt.ylabel('Valeur Totale des Importations')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to the 'importation_dashboards' folder
    save_path = os.path.join(dashboard_folder, 'continent_time_series_plot.png')
    plt.savefig(save_path)
    print(f"Plot saved successfully at: {save_path}")
    #plt.show()

except FileNotFoundError:
    print("Error: The file 'cleaned_importation_tons.csv' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
