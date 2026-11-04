
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Locate .env relative to the repository root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_db_connection():
    """Create a new MySQL connection."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3307")),
        database=os.getenv("DB_NAME", "fitness_tracker"),
        user=os.getenv("DB_USER", "fitness_user"),
        password=os.getenv("MYSQL_PASSWORD")
    )


def execute_select(query, params=()):
    """
    Execute a parameterized SELECT query.

    Returns a list of dictionaries.
    """
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params)
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
