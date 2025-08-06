#!/usr/bin/env python3
"""
Test script for database integration.
Run this to verify the database setup and data loading works correctly.
"""

import sqlite3
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database():
    """Test the database integration."""

    # Get project root and database path
    project_root = Path(__file__).parent
    db_path = project_root / "website" / "data" / "brb_database.db"

    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        logger.error("Please run 'poetry run load-database' first")
        return False

    logger.info(f"Testing database: {db_path}")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Test basic queries
            logger.info("Testing basic queries...")

            # Get total records
            cursor.execute("SELECT COUNT(*) FROM imports")
            total_records = cursor.fetchone()[0]
            logger.info(f"Total records: {total_records}")

            # Get year range
            cursor.execute("SELECT MIN(year), MAX(year) FROM imports")
            min_year, max_year = cursor.fetchone()
            logger.info(f"Year range: {min_year} - {max_year}")

            # Get continents
            cursor.execute("SELECT DISTINCT continent FROM imports WHERE continent IS NOT NULL")
            continents = [row[0] for row in cursor.fetchall()]
            logger.info(f"Continents: {', '.join(continents)}")

            # Get categories
            cursor.execute("SELECT DISTINCT category FROM imports WHERE category IS NOT NULL")
            categories = [row[0] for row in cursor.fetchall()]
            logger.info(f"Categories: {', '.join(categories)}")

            # Test sample queries
            logger.info("Testing sample queries...")

            # Monthly imports by continent for 2023
            cursor.execute("""
                SELECT continent, month, SUM(value) as total_imports
                FROM imports
                WHERE year = 2023
                    AND source_type = 'countries'
                    AND continent IS NOT NULL
                GROUP BY continent, month
                ORDER BY month, continent
                LIMIT 10
            """)

            sample_results = cursor.fetchall()
            logger.info(f"Sample query results (first 10): {len(sample_results)} rows")

            # Test metadata
            cursor.execute("SELECT key, value FROM metadata")
            metadata = cursor.fetchall()
            logger.info(f"Metadata entries: {len(metadata)}")
            for key, value in metadata:
                logger.info(f"  {key}: {value}")

            logger.info("Database test completed successfully!")
            return True

    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False

def test_sql_queries():
    """Test SQL query templates."""

    from src.parse.database.queries import SQLQueries

    logger.info("Testing SQL query templates...")

    # Test basic queries
    queries = [
        SQLQueries.GET_ALL_YEARS,
        SQLQueries.GET_CONTINENTS,
        SQLQueries.GET_CATEGORIES,
        SQLQueries.MONTHLY_IMPORTS_BY_CONTINENT,
        SQLQueries.MONTHLY_IMPORTS_BY_CATEGORY
    ]

    for i, query in enumerate(queries, 1):
        logger.info(f"Query {i}: {query.strip()[:50]}...")

    # Test custom query builder
    custom_query = SQLQueries.build_custom_query(
        conditions=["year = 2023", "source_type = 'countries'"],
        limit=10
    )
    logger.info(f"Custom query: {custom_query.strip()[:50]}...")

    logger.info("SQL query templates test completed!")
    return True

if __name__ == "__main__":
    logger.info("Starting database integration tests...")

    # Test database
    db_success = test_database()

    # Test SQL queries
    query_success = test_sql_queries()

    if db_success and query_success:
        logger.info("All tests passed! Database integration is working correctly.")
    else:
        logger.error("Some tests failed. Please check the setup.")
