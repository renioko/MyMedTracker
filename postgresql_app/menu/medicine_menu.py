from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from menu.main_menu import Menu
from repos.medicine_repo import MedicineDB

class MedicineMenu(Menu, MedicineDB):
    pass