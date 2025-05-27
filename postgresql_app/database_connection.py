from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
# import config_file
from config import config_file


class DatabaseHandler:
    '''This class is responsible for connecting and disconnecting to database.'''
    def __init__(self):
        self.connection, self.cursor = connect_to_database()

    def close_connection(self):
        """Close connection with database"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("Database connection closed.")

# @staticmethod
def connect_to_database() -> Any:
    """Create a database connection and cursor"""
    try:
        connection = psycopg2.connect(
            dbname=config_file.DB_NAME,
            user=config_file.DB_USER,
            password=config_file.DB_PASSWORD,
            host=config_file.DB_HOST,
            port=config_file.DB_PORT
        )
        cursor = connection.cursor()
        print("Connected to the database successfully.")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        return connection, cursor
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)


