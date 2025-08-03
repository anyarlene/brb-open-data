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

    # Transform data for each year
    chart_data = {
        "yearly": {},  # For year-by-year view
        "timeline": {  # For timeline view
            "type": "bar",
            "title": "Imports by Continent Over Time",
            "description": "Yearly import values grouped by continent",
            "data": {
                "labels": sorted(source_data.keys()),  # Years as labels
                "datasets": []
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Total Imports by Continent Over Time"
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
                            "text": "Year"
                        }
                    },
                    "y": {
                        "stacked": True,
                        "title": {
                            "display": True,
                            "text": "Total Imports"
                        }
                    }
                }
            }
        }
    }

    # First, get all continents across all years
    continents = set()
    for year_data in source_data.values():
        for month_data in year_data.values():
            continents.update(month_data.keys())
    continents = sorted(list(continents))

    # Initialize timeline datasets
    timeline_datasets = {
        continent: {
            "label": continent,
            "data": [],
            "backgroundColor": continent_colors.get(continent, generate_color())
        }
        for continent in continents
    }

    # Process data for both views
    for year in sorted(source_data.keys()):
        year_data = source_data[year]

        # For yearly view
        datasets = []
        for continent in continents:
            dataset = {
                "label": continent,
                "data": [year_data.get(month, {}).get(continent, 0) for month in months],
                "backgroundColor": continent_colors.get(continent, generate_color())
            }
            datasets.append(dataset)

            # Calculate yearly total for timeline view
            yearly_total = sum(dataset["data"])
            timeline_datasets[continent]["data"].append(yearly_total)

        # Add to yearly view
        chart_data["yearly"][year] = {
            "type": "bar",
            "title": "Imports by Continent",
            "description": "Monthly import values grouped by continent",
            "data": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"Imports by Continent – {year}"
                    },
                    "legend": {
                        "position": "top"
                    }
                },
                "scales": {
                    "x": {"stacked": True},
                    "y": {"stacked": True}
                }
            }
        }

    # Add timeline datasets to timeline view
    chart_data["timeline"]["data"]["datasets"] = list(timeline_datasets.values())

    # Save the output
    project_root = os.path.dirname(analytics_dir)
    output_path = os.path.join(project_root, "website/data/monthly_imports_by_continent.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(chart_data, f, indent=2)

if __name__ == "__main__":
    transform_data()
