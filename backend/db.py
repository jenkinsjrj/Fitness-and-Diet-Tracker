import os

import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_db_connection():
    """
    Create and return a connection
    to the MySQL database.
    """

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3307")),
        database=os.getenv("DB_NAME", "fitness_tracker"),
        user=os.getenv("DB_USER", "fitness_user"),
        password=os.getenv("MYSQL_PASSWORD")
    )

    return connection


def test_connection():
    """
    Test whether Python can connect to MySQL.
    """

    connection = None

    try:
        connection = get_db_connection()

        if connection.is_connected():
            print("Successfully connected to MySQL!")

    except mysql.connector.Error as error:
        print(f"Database connection failed: {error}")

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
