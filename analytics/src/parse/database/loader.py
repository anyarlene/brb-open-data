"""
Database loader for BRB analytics pipeline.
Handles loading data from CSV/JSON files into SQLite database.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """
    Handles loading data into the SQLite database.
    """

    def __init__(self, db_path: Path):
        """
        Initialize the database loader.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

    def load_countries_data(self, csv_path: Path) -> None:
        """
        Load countries import data from CSV into database.

        Args:
            csv_path: Path to the CSV file with countries data
        """
        logger.info(f"Loading countries data from: {csv_path}")

        # Read CSV file
        df = pd.read_csv(csv_path)

        # Prepare data for database
        records = []

        # Get date columns (excluding 'continent' and 'country')
        date_cols = [col for col in df.columns if col not in ['continent', 'country']]

        for _, row in df.iterrows():
            continent = row['continent']
            country = row['country']

            for date_col in date_cols:
                year, month = date_col.split('-')
                value = row[date_col]

                if pd.notna(value) and value > 0:
                    records.append({
                        'year': int(year),
                        'month': int(month),
                        'continent': continent,
                        'country': country,
                        'category': None,
                        'value': float(value),
                        'source_type': 'countries'
                    })

        # Insert into database
        self._insert_records(records)
        logger.info(f"Loaded {len(records)} records from countries data")

    def load_categories_data(self, json_path: Path) -> None:
        """
        Load categories import data from JSON into database.

        Args:
            json_path: Path to the JSON file with categories data
        """
        logger.info(f"Loading categories data from: {json_path}")

        import json
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Prepare data for database
        records = []

        for year, year_data in data.items():
            for month_name, month_data in year_data.items():
                month_num = self._get_month_number(month_name)

                for category, value in month_data.items():
                    if value > 0:
                        records.append({
                            'year': int(year),
                            'month': month_num,
                            'continent': None,
                            'country': None,
                            'category': category,
                            'value': float(value),
                            'source_type': 'categories'
                        })

        # Insert into database
        self._insert_records(records)
        logger.info(f"Loaded {len(records)} records from categories data")

    def _insert_records(self, records: list) -> None:
        """
        Insert records into the database.

        Args:
            records: List of dictionaries with record data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert records
            cursor.executemany("""
                INSERT INTO imports (year, month, continent, country, category, value, source_type)
                VALUES (:year, :month, :continent, :country, :category, :value, :source_type)
            """, records)

            conn.commit()

    def _get_month_number(self, month_name: str) -> int:
        """
        Convert month name to number.

        Args:
            month_name: Month name (e.g., 'January')

        Returns:
            Month number (1-12)
        """
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        return months.get(month_name, 1)

    def update_metadata(self, key: str, value: str) -> None:
        """
        Update metadata table.

        Args:
            key: Metadata key
            value: Metadata value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))

            conn.commit()

    def get_metadata(self, key: str) -> Optional[str]:
        """
        Get metadata value.

        Args:
            key: Metadata key

        Returns:
            Metadata value or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            result = cursor.fetchone()

            return result[0] if result else None

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary of data in the database.

        Returns:
            Dictionary with data summary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get total records
            cursor.execute("SELECT COUNT(*) FROM imports")
            total_records = cursor.fetchone()[0]

            # Get year range
            cursor.execute("SELECT MIN(year), MAX(year) FROM imports")
            min_year, max_year = cursor.fetchone()

            # Get continents
            cursor.execute("SELECT DISTINCT continent FROM imports WHERE continent IS NOT NULL")
            continents = [row[0] for row in cursor.fetchall()]

            # Get categories
            cursor.execute("SELECT DISTINCT category FROM imports WHERE category IS NOT NULL")
            categories = [row[0] for row in cursor.fetchall()]

            return {
                'total_records': total_records,
                'year_range': (min_year, max_year),
                'continents': continents,
                'categories': categories
            }
