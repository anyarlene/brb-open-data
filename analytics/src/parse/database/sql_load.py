"""
SQL-based data loading for BRB analytics.
Generates chart JSON files from SQL queries.
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any, List

from .schema import get_database_path
from .queries import SQLQueries

logger = logging.getLogger(__name__)


class SQLDataLoader:
    """
    Loads data from SQLite database and generates chart JSON files.
    """

    def __init__(self, db_path: Path):
        """
        Initialize the SQL data loader.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

    def generate_continent_chart_data(self) -> Dict[str, Any]:
        """
        Generate chart data for monthly imports by continent.

        Returns:
            Chart data dictionary
        """
        logger.info("Generating continent chart data from SQL...")

        # Get all years
        years = self._get_all_years()

        # Define continent colors
        continent_colors = {
            "AFRIQUE": "#2ecc71",
            "AMERIQUE": "#3498db",
            "ASIE": "#e74c3c",
            "EUROPE": "#f1c40f",
            "OCEANIE": "#9b59b6"
        }

        # Get all continents
        continents = self._get_continents()

        # Build chart data
        chart_data = {
            "type": "bar",
            "title": "Monthly Imports by Continent (Million BIF)",
            "description": "Monthly import values in Million Burundian Francs (BIF) grouped by continent",
            "years": years,
            "data": {},
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Monthly Imports by Continent (Million BIF)"
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

        # Generate data for each year
        for year in years:
            year_data = self._get_monthly_imports_by_continent(year)
            chart_data["data"][str(year)] = self._format_continent_data(year_data, continents, continent_colors)

        return chart_data

    def generate_category_chart_data(self) -> Dict[str, Any]:
        """
        Generate chart data for monthly imports by category.

        Returns:
            Chart data dictionary
        """
        logger.info("Generating category chart data from SQL...")

        # Get all years
        years = self._get_all_years()

        # Define category colors
        category_colors = {
            "Food Products": "#2ecc71",
            "Industrial Goods": "#3498db",
            "Raw Materials": "#e74c3c",
            "Consumer Goods": "#f1c40f",
            "Machinery": "#9b59b6"
        }

        # Get all categories
        categories = self._get_categories()

        # Build chart data
        chart_data = {
            "type": "bar",
            "title": "Monthly Imports by Category (Million BIF)",
            "description": "Monthly import values in Million Burundian Francs (BIF) grouped by category",
            "years": years,
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

        # Generate data for each year
        for year in years:
            year_data = self._get_monthly_imports_by_category(year)
            chart_data["data"][str(year)] = self._format_category_data(year_data, categories, category_colors)

        return chart_data

    def _get_all_years(self) -> List[int]:
        """Get all available years from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLQueries.GET_ALL_YEARS)
            return [row[0] for row in cursor.fetchall()]

    def _get_continents(self) -> List[str]:
        """Get all continents from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLQueries.GET_CONTINENTS)
            return [row[0] for row in cursor.fetchall()]

    def _get_categories(self) -> List[str]:
        """Get all categories from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLQueries.GET_CATEGORIES)
            return [row[0] for row in cursor.fetchall()]

    def _get_monthly_imports_by_continent(self, year: int) -> List[tuple]:
        """Get monthly imports by continent for a specific year."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLQueries.MONTHLY_IMPORTS_BY_CONTINENT, (year,))
            return cursor.fetchall()

    def _get_monthly_imports_by_category(self, year: int) -> List[tuple]:
        """Get monthly imports by category for a specific year."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLQueries.MONTHLY_IMPORTS_BY_CATEGORY, (year,))
            return cursor.fetchall()

    def _format_continent_data(self, year_data: List[tuple], continents: List[str], colors: Dict[str, str]) -> Dict[str, Any]:
        """Format continent data for Chart.js."""
        # Initialize monthly data
        monthly_data = {continent: [0] * 12 for continent in continents}

        # Fill in the data
        for continent, month, value in year_data:
            if continent in monthly_data:
                monthly_data[continent][month - 1] = value

        # Create datasets
        datasets = []
        for continent in continents:
            datasets.append({
                "label": continent,
                "data": monthly_data[continent],
                "backgroundColor": colors.get(continent, "#95a5a6")
            })

        return {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "datasets": datasets
        }

    def _format_category_data(self, year_data: List[tuple], categories: List[str], colors: Dict[str, str]) -> Dict[str, Any]:
        """Format category data for Chart.js."""
        # Initialize monthly data
        monthly_data = {category: [0] * 12 for category in categories}

        # Fill in the data
        for category, month, value in year_data:
            if category in monthly_data:
                monthly_data[category][month - 1] = value

        # Create datasets
        datasets = []
        for category in categories:
            datasets.append({
                "label": category,
                "data": monthly_data[category],
                "backgroundColor": colors.get(category, "#95a5a6")
            })

        return {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "datasets": datasets
        }

    def save_chart_data(self, chart_data: Dict[str, Any], output_path: Path) -> None:
        """
        Save chart data to JSON file.

        Args:
            chart_data: Chart data dictionary
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(chart_data, f, indent=2)

        logger.info(f"Chart data saved to: {output_path}")


def main():
    """Main function for SQL-based data loading."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Get project root and database path
        project_root = Path(__file__).parents[4]
        db_path = get_database_path(project_root)

        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            logger.error("Please run the database loading script first")
            return

        # Initialize SQL data loader
        loader = SQLDataLoader(db_path)

        # Generate continent chart data
        continent_data = loader.generate_continent_chart_data()
        continent_output = project_root / "website" / "data" / "monthly_imports_by_continent.json"
        loader.save_chart_data(continent_data, continent_output)

        # Generate category chart data
        category_data = loader.generate_category_chart_data()
        category_output = project_root / "website" / "data" / "monthly_imports_by_category.json"
        loader.save_chart_data(category_data, category_output)

        logger.info("SQL-based data loading completed successfully!")

    except Exception as e:
        logger.error(f"Error in SQL data loading: {e}")
        raise


if __name__ == "__main__":
    main()
