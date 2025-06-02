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
from repos.patient_repo import PatientDB
from repos.patient_medicine_view_repo import Patient_Medicines_ViewDB
from repos.user_repo import UserDB

class PatientMenu(Menu, PatientDB, Patient_Medicines_ViewDB, UserDB):
    '''This class manages navigation and interface logic related to Patient'''
    
    def __init__(self, choice_option: int, auto_run=True):
        # Inicjalizujemy prawidłowo każdą klasę bazową
        Menu.__init__(self, 0, 0)
        PatientDB.__init__(self)  # To inicjalizuje również DatabaseHandler
        Patient_Medicines_ViewDB.__init__(self)
        
        self.menu_functions = {
            1: self.menu_add_patient,
            2: self.menu_delete_patient,
            3: self.menu_alter_patient_details,
            4: self.menu_print_patient,
            5: self.menu_assign_patient,
            6: self.menu_view_patient_medicines,
            7: self.menu_exit
        }        
        # Uruchamiamy od razu wybraną funkcję
        if auto_run:
            self.run(choice_option)
    
    def run(self, choice_option):
        """Runs chosen option"""
        func = self.menu_functions.get(choice_option)
        if func:
            from main import main  # Importujemy tutaj, aby uniknąć circular import error?
            func()
            # main()  ## tutaj nie wiem czy to nie jest circular import error
        else:
            print("Invalid option selected.")

    def menu_add_patient(self, patient_details=None, verbose=True):
        # PatienDB.add #########
        # return self.add_patient_to_database(self, patient_details, verbose=True)
        return self.add_patient_and_user_one_connection(patient_details, verbose)

    def menu_delete_patient(self):
        self.delete_patient()

    def menu_alter_patient_details(self):
        self.alter_patient_details_in_db(self)

    def menu_print_patient(self):
        # self.print_patient(self)
        self.get_patient_view(pat_id=None)

    def menu_assign_patient(self): # nie działa
        print("Asign not working write now. Sorry")

    def menu_view_patient_medicines(self): # nie działa
        self.view_patient_medicines_list()

    def menu_exit(self):
        print("Exiting patient menu")
        self.close_connection()