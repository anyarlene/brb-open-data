import json
import random
import os

def generate_color():
    """Generate a random hex color."""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"

def transform_data():
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    analytics_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))

    # Read the source data
    input_path = os.path.join(analytics_dir, "data/parsed/importation_bif/2025-08-03-monthly-transformed.json")
    with open(input_path, "r") as f:
        source_data = json.load(f)

    # Month mapping
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    # Define continent colors (using consistent colors for better visualization)
    continent_colors = {
        "AFRIQUE": "#2ecc71",  # Green
        "AMERIQUE": "#3498db",  # Blue
        "ASIE": "#e74c3c",     # Red
        "EUROPE": "#f1c40f",   # Yellow
        "OCEANIE": "#9b59b6"   # Purple
    }

    # Get all continents across all years
    continents = set()
    for year_data in source_data.values():
        for month_data in year_data.values():
            continents.update(month_data.keys())
    continents = sorted(list(continents))

    # Transform data for visualization
    chart_data = {
        "type": "bar",
        "title": "Imports by Continent",
        "description": "Monthly import values grouped by continent",
        "years": sorted(source_data.keys()),  # Available years for filtering
        "data": {},  # Will contain data for each year
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Monthly Imports by Continent"
                },
                "legend": {
                    "position": "top"
                },
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { const value = context.raw.toFixed(2); return `${context.dataset.label}: ${value}`; }"
                    }
                }
            },
            "scales": {
                "x": {
                    "stacked": True,
                    "title": {
                        "display": True,
                        "text": "Month"
                    }
                },
                "y": {
                    "stacked": True,
                    "title": {
                        "display": True,
                        "text": "Import Value"
                    }
                }
            }
        }
    }

    # Process data for each year
    for year in sorted(source_data.keys()):
        year_data = source_data[year]

        # Prepare datasets for each continent
        datasets = []
        for continent in continents:
            dataset = {
                "label": continent,
                "data": [year_data.get(month, {}).get(continent, 0) for month in months],
                "backgroundColor": continent_colors.get(continent, generate_color())
            }
            datasets.append(dataset)

        # Add year data
        chart_data["data"][year] = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "datasets": datasets
        }

    # Save the output
    project_root = os.path.dirname(analytics_dir)
    output_path = os.path.join(project_root, "website/data/monthly_imports_by_continent.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(chart_data, f, indent=2)

if __name__ == "__main__":
    transform_data()
