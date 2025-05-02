from collections import defaultdict
from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
from time import strftime, strptime
import psycopg2
import config
import uuid

'''
First user will choose an object on which he wants to perform an operation.
Then he will choose an operation on that object.'''

OBJECTS = {
        1: 'Medicine',
        2: 'Patient',
        3: 'Prescription',
        4: 'EXIT'
}

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
            6: 'View Patient Medicines list',
            7: 'Exit'
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
            if choice.isdigit() and int(choice) in range(1, 4):
                print('You selected object:', OBJECTS[int(choice)])
                print('You chose:', OBJECTS[int(choice)])
                return int(choice)
            elif choice == '4':
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
            if option.isdigit() and int(option) in range(1, 7):
                print('You selected:', self.option[int(option)])
                return option
            elif option == '7':
                print('Exiting the program. Goodbye!')
                sys.exit(1)               
            else:
                print('Invalid choice. Please try again.')

    def get_function(self, option) -> str | None:
        if option in self.function:
            print(self.function[int(option)])
            # return self.function[int(option)]() #czy to zadziała?
        else:
            sys.exit(1)


@ dataclass
class Medicine:
    med_id: int
    name: str
    dosage: str
    quantity: int
    date: Optional[datetime.date] # data musi byc pobrana z view przez fk
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
        return f"({self.med_id}, '{self.name}', '{self.dosage}', {self.quantity}, '{self.date.isoformat()}', '{self.description}')"

    def is_low(self) -> bool:
        return self.quantity <= 10 # nie dziala poprawnie
    
    def add_medicine(self, medicines: list) -> None:
        medicines.append(self)
        print('Medicine added.')

@ dataclass
class Patient:
    pat_id: int
    first_name: str
    last_name: str
    email: str

    def add_patient(self, patients: list) -> None:
        patients.append(self)
        print('Patient added.')

@ dataclass
class Prescription:
    presc_id: int
    presc_to_patient_id: int 
    issue_date: datetime.date

    def __post_init__(self):
        if self.date:
            if isinstance(self.date, str):
                self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
            elif isinstance(self.date, datetime):
                self.date = self.date.date()
        else:
            self.date = datetime.now().date()

    def add_prescription(self, prescriptions: list) -> None:
        prescriptions.append(self)
        print('Prescription added.')

# class PatientMedicinesView:
#     '''to moze byc wrapper'''
#     medicine: Medicine
#     patient: Patient
#     prescription: Prescription
         
@ dataclass
class Patient_Medicines_View:
    pat_id: int 
    first_name: str 
    last_name: str 
    med_id: int 
    med_name: str 
    last_issued: datetime.date

    def __post_init__(self):
        # Możesz tu dodać logikę po inicjalizacji, np. formatowanie daty
        pass


def load_patient_data(cursor, patient_id = None) -> Patient_Medicines_View | None:
    if patient_id:
        cursor.execute('''
        SELECT * FROM view_patient_medicines 
            WHERE pat_id = %s ;''', (patient_id,))
        records = cursor.fetchall()
    else:
        cursor.execute('''
        SELECT * FROM view_patient_medicines;''')
        records = cursor.fetchall()
    if records:
        return [Patient_Medicines_View(*record) for record in records]
    else:
        print('Record not found.')
        return None

def print_patient_medicines_view(data: List[Patient_Medicines_View]) -> None:
    grouped = defaultdict(list)
    for record in data:
        key = (record.pat_id, record.first_name, record.last_name)
        grouped[key].append((record.med_id, record.med_name, record.last_issued))
    print('PATIENTS MEDICINES VIEW:')
    for (pat_id, first_name, last_name), meds in grouped.items():
        print('-pat_id- -first_name- -last_name- ')
        print(f'{pat_id :^8} {first_name :12} {last_name}')
        print('-med_id- -medicine_name----------- -last_issued- ')
        for med_id, med_name, last_issued in meds:
            print(f'{med_id :^8} {med_name :25} {last_issued}')
        print('---')


# mozna uzyc klasy do tego, ale czy warto?
class Medicines: # czy to ma sens?
    '''list of medicines'''
    def __init__(self) -> None:
        self.medicines = list(Medicine)  # Initialize with an empty list of medicines

    def add_item_to_medicines(self, medication: Medicine) -> list[Medicine]:
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

def connect_to_database() -> Any:
    """Create a database connection and cursor"""
    try:
        connection = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
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


def select_all_from_table(cursor: Any, table_name: str, id_name: str) -> None:
    """Select all records from a given table"""
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY {id_name} ASC;")
    records = cursor.fetchall()
    for record in records:
        print(record)

def select_patients_medicines_from_view(cursor: Any) -> None:
    """Select all records from the view"""
    cursor.execute("""
    SELECT pat_id, first_name, last_name, med_id, medicine_name, last_issued
    FROM view_patient_medicines
;
""")
    #     WHERE first_name = 'Anna'
    records = cursor.fetchall()
    if records:
        for record in records:
            print(record)
    else:
        print('No records found.')

def main() -> None:
    menu = Menu(0, {}, {})
    menu.display_menu()
    choice = menu.choose_menu_object()
    menu.choice = choice  # Set the choice in the Menu instance
    menu.__post_init__()  # Initialize options and functions based on the choice
    menu.display_options()
    option = menu.choose_option()


    connection, cursor = connect_to_database()
    # select_all_from_table(cursor, 'view_patient_medicines', 'pat_id')
    print('----------------------------------')
    data = load_patient_data(cursor, 6)
    print_patient_medicines_view(data)

    # select_patients_medicines_from_view(cursor)
    cursor.close()
    connection.close()
# ++++++++++++++++++++++++++++++

if __name__ == "__main__":
    main()
