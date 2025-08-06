import json
import os
from pathlib import Path

def transform_data():
    # Get the script directory
    script_dir = Path(__file__).parent
    analytics_dir = script_dir.parents[3]
    
    # Find the most recent transformed file
    parsed_dir = analytics_dir / "analytics/data/parsed/importation_categories"
    json_files = list(parsed_dir.glob("*-monthly-transformed.json"))
    if not json_files:
        raise FileNotFoundError(f"No transformed JSON files found in {parsed_dir}")
    
    # Get the most recent file
    input_path = sorted(json_files)[-1]
    print(f"Reading data from: {input_path}")
    
    # Read the source data
    with open(input_path, "r") as f:
        source_data = json.load(f)
    
    # Month mapping
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    # Define category colors (using a consistent color scheme)
    category_colors = {
        "Food Products": "#2ecc71",      # Green
        "Industrial Goods": "#3498db",    # Blue
        "Raw Materials": "#e74c3c",       # Red
        "Consumer Goods": "#f1c40f",      # Yellow
        "Machinery": "#9b59b6"           # Purple
    }
    
    # Transform data for visualization
    chart_data = {
        "type": "bar",
        "title": "Monthly Imports by Category (Million BIF)",
        "description": "Monthly import values in Million Burundian Francs (BIF) grouped by category",
        "years": sorted(source_data.keys()),
        "data": {},
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": "Monthly Imports by Category (Million BIF)"
                },
                "legend": {
                    "position": "top"
                },
                "tooltip": {
                    "callbacks": {
                        "label": "function(context) { const value = context.raw.toLocaleString('en-US', { maximumFractionDigits: 0 }); return `${context.dataset.label}: ${value} M BIF`; }"
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
                        "text": "Import Value (Million BIF)"
                    }
                }
            }
        }
    }
    
    # Process data for each year
    for year in sorted(source_data.keys()):
        year_data = source_data[year]
        
        # Prepare datasets for each category
        datasets = []
        for category, color in category_colors.items():
            dataset = {
                "label": category,
                "data": [year_data.get(month, {}).get(category, 0) for month in months],
                "backgroundColor": color
            }
            datasets.append(dataset)
        
        # Add year data
        chart_data["data"][year] = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "datasets": datasets
        }
    
    # Save the output
    output_path = analytics_dir / "website/data/monthly_imports_by_category.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(chart_data, f, indent=2)
    print(f"Visualization data saved to: {output_path}")

if __name__ == "__main__":
    transform_data()