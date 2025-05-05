from __future__ import annotations
from collections import defaultdict

from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
from time import strftime, strptime
import psycopg2
import config


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

class MedicineDB:
    def get_medicine_details(cls):
        pass
    def load_medicines(cls, cursor) -> list[Medicine]:
        pass
    def print_medicines(medicines) -> None:
        pass

@ dataclass
class Patient:
    pat_id: int
    first_name: str
    last_name: str
    email: str

    def __str__(self):
        return (f'{self.pat_id:^4} {self.first_name:12} {self.last_name:25}, {self.email}')


    def add_patient(self, patients: list) -> None:
        patients.append(self)
        print('Patient added.')

class PatientDB:

    @classmethod
    def get_patient_details_to_load(cls) -> tuple[str, str]:
        choice = input('You want to load patient data. Do you know patient id? Y/N')
        if choice.lower() == 'y':
            try:
                pat_id = int(input('Enter patient id: '))
            except TypeError:
                print('You entered incorrect data. Try again')
                return cls.get_patient_details_to_load() # recursion / rekurencja
            return ('pat_id', str(pat_id))
        elif choice.lower() == 'n':
            choice_2 = input('Do you know patient email? Y/N')
            if choice_2.lower() == 'y':
                pat_email = input('Enter patient email.')
                if not '@' in pat_email:
                    print('Email must contain @ character.')
                    return cls.get_patient_details_to_load()
                return ('email', pat_email)
            else:
                print('You can not load patient details without id or email.')
                sys.exit()
        else:
            print('Incorrect answer. Try again.')
            return cls.get_patient_details_to_load()
            
    @classmethod
    def load_patients_details(cls, cursor) -> list[Patient]:
        column, value = cls.get_patient_details_to_load()
        allowed_columns = ['pat_id', 'email']
        if column not in allowed_columns:
            raise ValueError('Indalid action.')
        querry = f'''
    SELECT pat_id, first_name, last_name, email
    FROM new_patients WHERE {column} = %s'''
        
        try:
            cursor.execute(querry, (value,))
        except psycopg2.Error as e:
            print(f'Error occured: {e}.')
            return []
        patient_data = cursor.fetchall()
        return [Patient(*row) for row in patient_data] # usunelam str
    
    @classmethod
    def get_details_to_add_patient(cls) -> tuple[str, str, str]:
        first_name = input('Enter patients first name: ')
        last_name = input('Enter patients last name: ')
        email = input('Enter patients email: ')
        # validate email
        return (first_name, last_name, email)

    @classmethod
    def add_patient_to_database(cls, patient_details: tuple[str, str, str] = None) -> None:
        connection, cursor = connect_to_database()
        if not patient_details:
            patient_details = cls.get_details_to_add_patient()
        try:
            cursor.execute('''
            INSERT INTO new_patients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            ''', patient_details            
            )
            connection.commit()
            print('Patient added.')
        except psycopg2.Error as e:
            print(f'Error occured while adding new patient: {e}.')

    @classmethod
    def get_patient_update_input(cls, ) -> tuple:
        try:
            pat_id = int(input('Enter patients id: '))
        except ValueError:
            print('Id must be a number. Try again.')
            return cls.get_patient_update_input()
        allowed_columns = ['first_name', 'last_name', 'email']
        column_to_change = input('What column you want to change? Enter "first_name", "last_name" or "email": ')
        if column_to_change not in allowed_columns:
            print('Invalid column name. Try again.')
            return cls.get_patient_update_input()
        new_details = input('Enter a new value: ')
        return (pat_id, column_to_change, new_details)
                
    @classmethod
    def alter_patient_details_in_db(cls, connection, cursor, pat_id: int = None, column_to_change: str = None, new_details: str = None) -> None:
        if pat_id is None or column_to_change is None or  new_details == None:
            pat_id, column_to_change, new_details = cls.get_patient_update_input()
        allowed_columns = ['first_name', 'last_name', 'email']
        if column_to_change not in allowed_columns:
            raise ValueError('Invalid column name.')
        if not isinstance(pat_id, int):
            raise ValueError('Invalid id.')
        
        querry = f'''
    UPDATE new_patients SET {column_to_change} = %s
    WHERE pat_id = %s
    '''
        try:
            cursor.execute(querry, (new_details, pat_id))
            connection.commit()
            print('Patient detail changed.')
        except psycopg2.Error as e:
            print(f'Error ocurred while changing patient details: {e}')

    @classmethod
    def get_patient_id_to_delete() -> int:
        try:
            pat_id = int(input('Enter patient id to delete this patient: '))
            return pat_id
        except ValueError:
            print('You entered incorrect id.')


    @classmethod
    def print_patients(cls, patients) -> None:
        if patients:
            for patient in patients:
                print('--PATIENTS---')
                print('-id- -first_name- -last_name-------------- --email-------------')
                print(patient)
        else:
            print('List of patients is empty.')
    

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

    @classmethod
    def load_patient_medicines(cls, cursor, patient_id = None) -> list[Patient_Medicines_View] | None:
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
        
    @classmethod
    def print_patient_medicines_view(cls, data: List[Patient_Medicines_View]) -> None:
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


def select_all_from_table_by_id(cursor: Any, table_name: str, id_name: str) -> None:
    """Select all records from a given table"""
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY {id_name} ASC;")
    records = cursor.fetchall()
    for record in records:
        print(record)

def load_or_print_patients_medicines_from_view(cursor: Any) -> None:
    """Select all records from the view and prints records as in thhe table - as tuples"""
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
    print(option)

    connection, cursor = connect_to_database()
    # select_all_from_table_by_id(cursor, 'view_patient_medicines', 'pat_id')
    # print('load_or_print_patients_medicines_from_view:')
    # load_or_print_patients_medicines_from_view(cursor)
    print('---*---------*-----------*---------*--')
    data = Patient_Medicines_View.load_patient_medicines(cursor, 6)
    Patient_Medicines_View.print_patient_medicines_view(data)

    print('-------------------')
    patients = PatientDB().load_patients_details(cursor)
    PatientDB.print_patients(patients)

    PatientDB.add_patient_to_database(patient_details=('Szczadowazy', 'Sikadomiski', 'szczadowazysikadomiski@gmail.com'))

    cursor.close()
    connection.close()
# ++++++++++++++++++++++++++++++

if __name__ == "__main__":
    main()
