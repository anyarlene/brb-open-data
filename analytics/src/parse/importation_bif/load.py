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

    # Transform data for each year
    chart_data = {}
    for year, year_data in source_data.items():
        # Get top 10 countries by total value
        country_totals = {}
        for month_data in year_data.values():
            for country, value in month_data.items():
                country_totals[country] = country_totals.get(country, 0) + value

        top_countries = sorted(country_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        top_country_names = [c[0] for c in top_countries]

        # Prepare datasets
        datasets = []
        for country in top_country_names:
            dataset = {
                "label": country,
                "data": [year_data.get(month, {}).get(country, 0) for month in months],
                "backgroundColor": generate_color()
            }
            datasets.append(dataset)

        # Create chart configuration
        chart_data[year] = {
            "type": "bar",
            "title": "Top Trading Partners",
            "description": "Import values from top trading partner countries",
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
                        "text": f"Top Trading Partners – {year}"
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

    # Save the output
    project_root = os.path.dirname(analytics_dir)
    output_path = os.path.join(project_root, "website/data/monthly_imports_by_country.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(chart_data, f, indent=2)

if __name__ == "__main__":
    transform_data()
