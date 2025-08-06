"""
Database schema definitions for BRB analytics.
"""

import sqlite3
from pathlib import Path
from typing import Optional


def create_database_schema(db_path: Path) -> None:
    """
    Create the database schema and tables.

    Args:
        db_path: Path to the SQLite database file
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Create imports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                continent TEXT,
                country TEXT,
                category TEXT,
                value REAL NOT NULL,
                source_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_imports_year_month
            ON imports(year, month)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_imports_continent
            ON imports(continent)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_imports_category
            ON imports(category)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_imports_source
            ON imports(source_type)
        """)

        # Create metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def get_database_path(project_root: Path) -> Path:
    """
    Get the database file path.

    Args:
        project_root: Root directory of the project

    Returns:
        Path to the SQLite database file
    """
    return project_root / "website" / "data" / "brb_database.db"


def reset_database(db_path: Path) -> None:
    """
    Reset the database by dropping all tables and recreating schema.

    Args:
        db_path: Path to the SQLite database file
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS imports")
        cursor.execute("DROP TABLE IF EXISTS metadata")

        conn.commit()

    # Recreate schema
    create_database_schema(db_path)
