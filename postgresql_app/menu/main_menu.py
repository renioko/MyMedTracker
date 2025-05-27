from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2

from config import config_file

# import config_file


OBJECTS = {
    1: 'Medicine',
    2: 'Patient',
    3: 'Prescription',
    4: 'EXIT' # jesli wybrano uzyc connection.close
}
DISPLAY_OPTIONS = {
    1: f'Add new ',
    2: f'Delete ',
    3: f'Update ',
    4: f'View ',
    5: f'Assign ',
    6: 'View Patient Medicines list',
    7: 'Exit' # jesli wybrano uzyc powrot do glownego menu
}

class Menu:
    def __init__(self, object_choice: int, option_choice_to_display) -> None:
        self.object_choice = 0  
        self.option_choice_to_display = 0

    def display_menu(self) -> None:
        print("Welcome to MyMedTracker!")
        for key, value in OBJECTS.items():
            print(f'Press {key} for {value}')

    @classmethod
    def choose_menu_object(cls) -> int | None:    
        '''returns int that represents object user wants to work with i.e Medicine, Patient, Prescription'''
        while True:
            menu_object = input('Enter your choice: ')
            if menu_object.isdigit() and int(menu_object) in range(1, 4):
                print('You chose:', OBJECTS[int(menu_object)])
                menu_object = int(menu_object) 
                return menu_object
            elif menu_object == '4':
                print('Exiting the program. Goodbye!')
                sys.exit(0)
            else:
                print('Invalid choice. Please try again.')
                return cls.choose_menu_object() # recurssion
    
    def activate_menu_child_class(self, menu_object: int, choice_option: int) -> Any:
        '''this function activates medu for chosen object. called menu will then run function chosen by user'''
        # moze to nie spowoduje circular import error? 
        from .medicine_menu import MedicineMenu
        from .patient_menu import PatientMenu
        from .prescription_menu import PrescriptionMenu

        menu_classes = {
            1: lambda: MedicineMenu(choice_option),
            2: lambda: PatientMenu(choice_option),
            3: lambda: PrescriptionMenu(choice_option)
        }
        if menu_object in OBJECTS: #
            menu_class = menu_classes[menu_object]()
            # return menu_class.run(choice_option)
            return menu_class
        else:
            print('Incorrect menu class.')
            sys.exit() # w przyszlosci mozna dodac recursion
    
    def display_options(self, menu_object) -> None: 
        print('Options:')
        try:
            menu_object = int(menu_object)
        except ValueError:
            print('Invalid menu object. Please select a valid option.')
            sys.exit(1)
        if menu_object in OBJECTS:
            for key, value in DISPLAY_OPTIONS.items():
                if key in range(1, 6):
                    print(f'Press {key} for {value} {OBJECTS[menu_object]}')
                elif key in range(6,8):
                    print(f"Press {key} for {value}")
                else:
                    print('Something is wrong.')

    @classmethod
    def choose_option(cls, menu_object) -> int | None:
        while True:
            option = input('Choose an action: ')
            if option.isdigit() and int(option) in range(1, 7):
                print('You selected:', DISPLAY_OPTIONS[int(option)], OBJECTS[menu_object])
                return int(option)
            elif option == '7':
                print('Exiting the program. Goodbye!')
                sys.exit(1)               
            else:
                print('Invalid choice. Please try again.')
                return cls.choose_option(menu_object)