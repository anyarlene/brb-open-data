"""
Database loading script for BRB analytics pipeline.
Integrates with existing parser and transform scripts.
"""

import logging
from pathlib import Path
from datetime import datetime

from .schema import create_database_schema, get_database_path
from .loader import DatabaseLoader

logger = logging.getLogger(__name__)


def load_data_to_database(project_root: Path, reset_db: bool = False) -> None:
    """
    Load all data into the database.

    Args:
        project_root: Root directory of the project
        reset_db: Whether to reset the database before loading
    """
    # Get database path
    db_path = get_database_path(project_root)

    # Create database schema
    create_database_schema(db_path)

    # Initialize database loader
    loader = DatabaseLoader(db_path)

    # Reset database if requested
    if reset_db:
        from .schema import reset_database
        logger.info("Resetting database...")
        reset_database(db_path)

    # Load countries data
    try:
        countries_csv = _find_latest_csv(project_root, "importation_countries")
        if countries_csv:
            loader.load_countries_data(countries_csv)
        else:
            logger.warning("No countries CSV file found")
    except Exception as e:
        logger.error(f"Error loading countries data: {e}")

    # Load categories data
    try:
        categories_json = _find_latest_json(project_root, "importation_categories")
        if categories_json:
            loader.load_categories_data(categories_json)
        else:
            logger.warning("No categories JSON file found")
    except Exception as e:
        logger.error(f"Error loading categories data: {e}")

    # Update metadata
    loader.update_metadata("last_updated", datetime.now().isoformat())
    loader.update_metadata("data_sources", "countries,categories")

    # Print summary
    summary = loader.get_data_summary()
    logger.info(f"Database loaded successfully:")
    logger.info(f"  Total records: {summary['total_records']}")
    logger.info(f"  Year range: {summary['year_range']}")
    logger.info(f"  Continents: {', '.join(summary['continents'])}")
    logger.info(f"  Categories: {', '.join(summary['categories'])}")


def _find_latest_csv(project_root: Path, source_dir: str) -> Path:
    """
    Find the latest CSV file in a source directory.

    Args:
        project_root: Root directory of the project
        source_dir: Source directory name

    Returns:
        Path to the latest CSV file
    """
    parsed_dir = project_root / "analytics" / "data" / "parsed" / source_dir
    csv_files = list(parsed_dir.glob("*-monthly.csv"))

    if not csv_files:
        return None

    return sorted(csv_files)[-1]


def _find_latest_json(project_root: Path, source_dir: str) -> Path:
    """
    Find the latest JSON file in a source directory.

    Args:
        project_root: Root directory of the project
        source_dir: Source directory name

    Returns:
        Path to the latest JSON file
    """
    parsed_dir = project_root / "analytics" / "data" / "parsed" / source_dir
    json_files = list(parsed_dir.glob("*-monthly-transformed.json"))

    if not json_files:
        return None

    return sorted(json_files)[-1]


def main():
    """Main function for database loading."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Get project root
        project_root = Path(__file__).parents[4]

        # Load data to database
        load_data_to_database(project_root, reset_db=True)

        logger.info("Database loading completed successfully!")

    except Exception as e:
        logger.error(f"Error loading database: {e}")
        raise


if __name__ == "__main__":
    main()
