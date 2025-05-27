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
from repos.prescription_repo import PrescriptionDB


class PrescriptionMenu(Menu, PrescriptionDB):
    '''This class manages navigation and interface logic related to Patient'''
    
    def __init__(self, choice_option: int):
        # Inicjalizujemy prawidłowo każdą klasę bazową
        Menu.__init__(self, 0, 0)
        PrescriptionDB.__init__(self)  # To inicjalizuje również DatabaseHandler
    
        self.menu_functions = {
            1: self.menu_add_prescription,
            2: self.menu_delete_prescription,
            3: self.menu_alter_prescription_details,
            4: self.menu_print_prescription,
            5: self.menu_assign_prescription,
            6: self.menu_view_patient_medicines,
            7: self.menu_exit
        }        
        # Uruchamiamy od razu wybraną funkcję
        self.run(choice_option)

    def run(self, choice_option):
        """Runs chosen option"""
        func = self.menu_functions.get(choice_option)
        from main import main
        # Importujemy tutaj, aby uniknąć circular import error?
        if func:
            func()
            # main() # tutaj nie wiem czy to nie jest circular import error
        else:
            print("Invalid option selected.")

    def menu_add_prescription(self):
        self.add_prescription_to_database(prescription_details=None)
    def menu_delete_prescription(self):
        pass
    def menu_alter_prescription_details(self):
        pass
    def menu_print_prescription(self):
        pass
    def menu_assign_prescription(self):
        pass
    def menu_view_patient_medicines(self):
        pass
    def menu_exit(self):
        self.close_connection()
