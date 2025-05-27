from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import Medicine
from postgresql_app.database_connection import DatabaseHandler

class MedicineDB(DatabaseHandler, Medicine):
    '''This class manages database operations and Medicine logic'''
    def get_medicine_details(cls):
        pass
    def load_medicines(cls, cursor) -> list[Medicine]:
        pass
    def print_medicines(medicines) -> None:
        pass