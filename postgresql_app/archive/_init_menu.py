from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime
from time import strftime, strptime



'''
First user will choose an object on which he wants to perform an operation.
Then he will choose an operation on that object.'''

OBJECTS = {
        1: 'Medication',
        2: 'Patient',
        3: 'Prescription',
        4: 'Appointment',
        5: 'EXIT'
}

# OPTIONS = {
#             1: f'Add new ',
#             2: f'Delete ',
#             3: f'Update ',
#             4: f'View all ',
#             5: f'Assign ',
#             6: 'Exit'
#         }
@dataclass
class Menu:
    def __init__(self, choice, option, function) -> None:
        choice: int = 0  # number 
        option: dict  = {} # name of the operation on the object[choice-number]
        function: dict = {}  # function to be executed

    def __post_init__(self) -> None:

        self.option = {
            1: f'Add new {OBJECTS[self.choice]}', # to w nawiasie moze byc zbedne
            2: f'Delete {OBJECTS[self.choice]}',
            3: f'Update {OBJECTS[self.choice]}',
            4: f'View all {OBJECTS[self.choice]}',
            5: f'Assign {OBJECTS[self.choice]}',
            6: 'Exit'
        }

        self.function = {
            1: 'add',
            2: 'delete',
            3: 'update',
            4: 'view',
            5: 'assign',
            6: 'exit'
        }

    def display_menu(self) -> None:
        print("Welcome to MyMedTracker!")
        for key, value in OBJECTS.items():
            print(f'{key}. {value}')

    def choose_menu_object(self) -> int | None:    # zwraca mi liczbe, ktora odpowiada obiektowi, jaki bedzie obrabiany
        while True:
            choice = input('Enter your choice: ')
            if choice.isdigit() and int(choice) in range(1, 5):
                print('You selected object:', OBJECTS[int(choice)])
                print('choice:', choice)
                return int(choice)
            elif choice == '5':
                print('Exiting the program. Goodbye!')
                sys.exit(1)
            else:
                print('Invalid choice. Please try again.')

    def display_options(self) -> None:
        print('Options:')
        for key, value in self.option.items():
            print(f'{key}. {value}')

    def choose_option(self) -> int | None:
        while True:
            option = input('Choose an action: ')
            if option.isdigit() and int(option) in range(1, 6):
                print('You selected:', self.option[int(option)])
                return option
            elif option == '6':
                print('Exiting the program. Goodbye!')
                sys.exit(1)
            else:
                print('Invalid choice. Please try again.')

    def get_function(self, option) -> str | None:
        if option in self.function:
            return self.function[int(option)]() #czy to zadziała?
        else:
            sys.exit(1)

# @staticmethod
# def add_new_object() -> None:
#     """Add a new object to the database"""
#     # Implement the logic to add a new medication here
#     pass
# @staticmethod
# def delete_object() -> None:
#     """Delete a object from the database"""
#     # Implement the logic to delete a medication here
#     pass
# @staticmethod
# def update_object() -> None:
#     """Update a object in the database"""
#     # Implement the logic to update a medication here
#     pass
# @staticmethod
# def view_all_objects() -> None:
#     """View all objects in the database"""
#     # Implement the logic to view all medications here
#     pass
# @staticmethod
# def assign_object() -> None:
#     """Assign a object to a user"""
#     # Implement the logic to assign a medication here
#     pass
# @staticmethod
# def exit_program() -> None:
#     """Exit the program"""
#     print("Exiting the program. Goodbye!")
#     exit(0)
# ====================================
@ dataclass
class Medication:
    id: int
    name: str
    dosage: str
    quantity: int
    date: Optional[datetime.date]
    description: Optional[str] = None

   
    def __post_init__(self):
        if self.dosage is None:
            self.dosage = ''
        if int(self.quantity) < 0:
            raise ValueError('ERROR! You entered a negative number.')
        if self.date:
            if isinstance(self.date, str):
                self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
            elif isinstance(self.date, datetime):
                self.date = self.date.date()
        else:
            self.date = datetime.now().date()
        if self.description is None:
            self.description = ''
        
    def __str__(self):
        return f"({self.id}, '{self.name}', '{self.dosage}', {self.quantity}, '{self.date.isoformat()}', '{self.description}')"

    def is_low(self) -> bool:
        return self.quantity <= 10 # nie dziala poprawnie
    
    def add_item(self, medicines: list) -> None:
        medicines.append(self)
        print('Item added.')
     

# mozna uzyc klasy do tego, ale czy warto?
class Medicines: # czy to ma sens?
    '''list of medications'''
    def __init__(self) -> None:
        self.medicines = list(Medication)  # Initialize with an empty list of medications

    def add_item_to_medicines(self, medication: Medication) -> list[Medication]:
        self.medicines.append(medication)
        print('Item added.')
        return self.medicines

    def delete_item_from_medicines(self, medication_id: int) -> None:
        for med in self.medicines:
            if med.id == medication_id:
                self.medicines.remove(med)
                print('Item deleted.')
            else:
                print('Item not found.')



def main() -> None:
    menu = Menu(0, {}, {})
    menu.display_menu()
    choice = menu.choose_menu_object()
    menu.choice = choice  # Set the choice in the Menu instance
    menu.__post_init__()  # Initialize options and functions based on the choice
    menu.display_options()
    option = menu.choose_option()
    function = menu.get_function(option)
    print(f'You selected action: {function}')

if __name__ == "__main__":
    main()