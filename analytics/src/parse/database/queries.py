"""
SQL query templates for BRB analytics.
Common queries for data analysis and visualization.
"""


class SQLQueries:
    """
    Collection of SQL queries for BRB data analysis.
    """

    # Basic data queries
    GET_ALL_YEARS = """
        SELECT DISTINCT year
        FROM imports
        ORDER BY year
    """

    GET_CONTINENTS = """
        SELECT DISTINCT continent
        FROM imports
        WHERE continent IS NOT NULL
        ORDER BY continent
    """

    GET_CATEGORIES = """
        SELECT DISTINCT category
        FROM imports
        WHERE category IS NOT NULL
        ORDER BY category
    """

    # Monthly imports by continent
    MONTHLY_IMPORTS_BY_CONTINENT = """
        SELECT
            continent,
            month,
            SUM(value) as total_imports
        FROM imports
        WHERE year = ?
            AND source_type = 'countries'
            AND continent IS NOT NULL
        GROUP BY continent, month
        ORDER BY month, continent
    """

    # Monthly imports by category
    MONTHLY_IMPORTS_BY_CATEGORY = """
        SELECT
            category,
            month,
            SUM(value) as total_imports
        FROM imports
        WHERE year = ?
            AND source_type = 'categories'
            AND category IS NOT NULL
        GROUP BY category, month
        ORDER BY month, category
    """

    # Top countries by import value
    TOP_COUNTRIES_BY_YEAR = """
        SELECT
            country,
            SUM(value) as total_imports
        FROM imports
        WHERE year = ?
            AND source_type = 'countries'
            AND country IS NOT NULL
        GROUP BY country
        ORDER BY total_imports DESC
        LIMIT ?
    """

    # Yearly totals by continent
    YEARLY_TOTALS_BY_CONTINENT = """
        SELECT
            year,
            continent,
            SUM(value) as total_imports
        FROM imports
        WHERE source_type = 'countries'
            AND continent IS NOT NULL
        GROUP BY year, continent
        ORDER BY year, total_imports DESC
    """

    # Yearly totals by category
    YEARLY_TOTALS_BY_CATEGORY = """
        SELECT
            year,
            category,
            SUM(value) as total_imports
        FROM imports
        WHERE source_type = 'categories'
            AND category IS NOT NULL
        GROUP BY year, category
        ORDER BY year, total_imports DESC
    """

    # Monthly trends
    MONTHLY_TRENDS = """
        SELECT
            year,
            month,
            SUM(value) as total_imports
        FROM imports
        WHERE source_type = ?
        GROUP BY year, month
        ORDER BY year, month
    """

    # Data summary
    DATA_SUMMARY = """
        SELECT
            source_type,
            COUNT(*) as record_count,
            MIN(year) as min_year,
            MAX(year) as max_year,
            SUM(value) as total_value
        FROM imports
        GROUP BY source_type
    """

    # Custom query template
    CUSTOM_QUERY = """
        SELECT
            year,
            month,
            continent,
            country,
            category,
            value,
            source_type
        FROM imports
        WHERE 1=1
            {conditions}
        ORDER BY year, month
    """

    @staticmethod
    def build_custom_query(conditions: list = None, limit: int = None) -> str:
        """
        Build a custom query with optional conditions.

        Args:
            conditions: List of WHERE conditions
            limit: Optional LIMIT clause

        Returns:
            SQL query string
        """
        query = SQLQueries.CUSTOM_QUERY

        if conditions:
            condition_clause = " AND ".join(conditions)
            query = query.replace("{conditions}", f"AND {condition_clause}")
        else:
            query = query.replace("{conditions}", "")

        if limit:
            query += f" LIMIT {limit}"

        return query

    @staticmethod
    def get_monthly_imports_query(source_type: str, year: int) -> str:
        """
        Get monthly imports query for a specific source type and year.

        Args:
            source_type: 'countries' or 'categories'
            year: Year to filter by

        Returns:
            SQL query string
        """
        if source_type == 'countries':
            return SQLQueries.MONTHLY_IMPORTS_BY_CONTINENT
        elif source_type == 'categories':
            return SQLQueries.MONTHLY_IMPORTS_BY_CATEGORY
        else:
            raise ValueError(f"Invalid source_type: {source_type}")
