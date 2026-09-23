"""
Database Module for Taiwan Weather Forecast Application.
Corresponds to Steps 8, 9, 10, 12, 20 in the curriculum:
- SQLite database initialization (`data.db`)
- Schema design for TemperatureForecasts
- De-duplication using UNIQUE constraint and INSERT OR REPLACE
- SQL query helpers for Streamlit integration
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional

DB_NAME = "data.db"


def get_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    """Establish and return a SQLite database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_NAME) -> None:
    """
    Initialize SQLite database and create TemperatureForecasts table if not exists.
    Step 8 & 9: Database & Table design.
    Step 20: UNIQUE(regionName, dataDate) ensures idempotent runs without duplicate records.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate TEXT NOT NULL,
            minT REAL NOT NULL,
            maxT REAL NOT NULL,
            UNIQUE(regionName, dataDate)
        );
        """
    )
    conn.commit()
    conn.close()


def insert_forecasts(data: Any, db_path: str = DB_NAME) -> int:
    """
    Insert or replace weather forecast records into SQLite.
    Accepts pandas DataFrame or list of dicts.
    Step 20: Uses INSERT OR REPLACE to prevent duplicate insertions upon re-execution.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    records = []
    if isinstance(data, pd.DataFrame):
        for _, row in data.iterrows():
            records.append((
                str(row["regionName"]),
                str(row["dataDate"]),
                float(row["minT"]),
                float(row["maxT"])
            ))
    elif isinstance(data, list):
        for item in data:
            records.append((
                str(item["regionName"]),
                str(item["dataDate"]),
                float(item["minT"]),
                float(item["maxT"])
            ))

    cursor.executemany(
        """
        INSERT OR REPLACE INTO TemperatureForecasts (regionName, dataDate, minT, maxT)
        VALUES (?, ?, ?, ?);
        """,
        records
    )
    conn.commit()
    inserted_count = cursor.rowcount
    conn.close()
    return inserted_count


def get_regions(db_path: str = DB_NAME) -> List[str]:
    """
    Step 10: SELECT DISTINCT regionName FROM TemperatureForecasts
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [row["regionName"] for row in rows]


def get_dates(db_path: str = DB_NAME) -> List[str]:
    """
    Step 18: Fetch all distinct forecast dates for date selector.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT dataDate FROM TemperatureForecasts ORDER BY dataDate ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [row["dataDate"] for row in rows]


def get_forecast_by_region(region_name: str, db_path: str = DB_NAME) -> pd.DataFrame:
    """
    Step 12: Query forecast data for a specific region.
    SELECT * FROM TemperatureForecasts WHERE regionName = ...
    """
    conn = get_connection(db_path)
    query = """
        SELECT dataDate, minT, maxT, ROUND((minT + maxT) / 2.0, 1) AS avgT
        FROM TemperatureForecasts
        WHERE regionName = ?
        ORDER BY dataDate ASC;
    """
    df = pd.read_sql_query(query, conn, params=(region_name,))
    conn.close()
    return df


def get_forecast_by_date(data_date: str, db_path: str = DB_NAME) -> pd.DataFrame:
    """
    Step 18: Query forecast data across all regions for a specific date (used by Folium map).
    """
    conn = get_connection(db_path)
    query = """
        SELECT regionName, dataDate, minT, maxT, ROUND((minT + maxT) / 2.0, 1) AS avgT
        FROM TemperatureForecasts
        WHERE dataDate = ?
        ORDER BY regionName ASC;
    """
    df = pd.read_sql_query(query, conn, params=(data_date,))
    conn.close()
    return df


def get_all_forecasts(db_path: str = DB_NAME) -> pd.DataFrame:
    """
    Retrieve all records as a DataFrame.
    """
    conn = get_connection(db_path)
    df = pd.read_sql_query(
        "SELECT id, regionName, dataDate, minT, maxT FROM TemperatureForecasts ORDER BY dataDate ASC, regionName ASC;",
        conn
    )
    conn.close()
    return df


def get_record_count(db_path: str = DB_NAME) -> int:
    """Return total number of records in TemperatureForecasts table."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM TemperatureForecasts;")
    count = cursor.fetchone()[0]
    conn.close()
    return count
