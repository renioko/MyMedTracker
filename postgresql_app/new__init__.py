from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
import config

# from patiens_repository import PatienDB

# CO MUSZĘ JESZCZE ZROBIĆ:
# zmodyfikowac Menu - usunac int (self.choice) ✅
# usunac niepotrzebne elementy - in progress    ✅
#  WYWALIC kolumne presc_tab z bazy danych  ✅
# nie wiem czy sie automatycznie connection zamyka 🚩 - może użyc with? // na końcu main connection.close ✅// PatientMenu - w opcji exit wywołuje connection_close ✅
# dodac assign - zeby w pelni móc przypisywac pacjentów i recepty
# moze przeniesc slowniki do toml?
# zbudowac jakis basic interface - moze we flasku? 
# poprawic id w tabelach jako PK - postanowilam, że zostawie jak jest i dopisze wyjasnienie w documentacji 💡
# zmienic nazwy FK np presc_id na pełne prescription_id - postanowilam, że tylko dopisze'Fk' na końcu foreign keys 💡
# podzial na pliki
# dodac rollback przy errorach zw z baza danych

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
class DatabaseHandler:
    '''This class is responsible for connecting and disconnecting to database.'''
    def __init__(self):
        self.connection, self.cursor = connect_to_database()

    def close_connection(self):
        """Close connection with database"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("Database connection closed.")

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

class MedicineMenu(Menu, MedicineDB):
    pass

@ dataclass
class Patient: # zaczac uzywac w princie!!
    pat_id: int
    first_name: str
    last_name: str
    email: str

    def __str__(self):
        return (f'{self.pat_id:^4} {self.first_name:12} {self.last_name:25}, {self.email}')
    
    # na razie nieppotrzebne:
    def create_patient(self, patient_details: tuple[int, str, str, str]) -> Patient:
        # pat_id, first_name, last_name, email = patient_details
        patient = Patient(*patient_details)
        return patient
    # na razie nieppotrzebne:
    def add_patient(self, patients: list) -> None:
        patients.append(self)
        print('Patient added.')

class PatientDB(DatabaseHandler):
    '''This class manages database operations and Patient logic'''
    
    def __init__(self):
        # Inicjalizujemy klasę bazową DatabaseHandler
        super().__init__(self)

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
        
    @staticmethod
    def get_details_to_add_patient() -> tuple[str, str, str]:
        first_name = input('Enter patients first name: ')
        last_name = input('Enter patients last name: ')
        email = input('Enter patients email: ')
        # validate email
        return (first_name, last_name, email)
    
    @classmethod # albo @staticmethod?
    def get_pat_id_from_patient_details(cls, self, patient_details: tuple[str, str, str]) -> int | None:
        self.cursor.execute('''
        SELECT pat_id FROM new_patients
        WHERE first_name = %s AND last_name = %s AND email = %s
        ''', patient_details)
        result = self.cursor.fetchone() # zwraca krotkę
        if result:
            try:
                pat_id = int(result[0])
                return pat_id
            except (ValueError, TypeError):
                print('Value received as pat_id is incorrect.')
                return None
        else:
            print('Patient with given details not found.')
            return None

        # result = self.cursor.fetchone()
        # return result[0] if result else None

    @classmethod
    def add_patient_to_database(cls, self, patient_details: tuple[str, str, str] = None) -> None:
        if not patient_details:
            patient_details = cls.get_details_to_add_patient()
        try:
            self.cursor.execute('''
            INSERT INTO new_patients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            ''', patient_details            
            )
            self.connection.commit()
            print('Patient added.')
            pat_id = cls.get_pat_id_from_patient_details(self, patient_details)
            cls.print_patient(self, pat_id)
            
        except Exception as e:  # Używamy ogólnego Exception zamiast psycopg2.Error
            print(f'Error occurred while adding new patient: {e}.')

    def delete_patient(self, pat_id: int = None) -> None:
        if not pat_id:
            try:
                pat_id = int(input('Enter patient id to delete this patient: '))
            except ValueError:
                print('You entered incorrect id.')
                return

        # Sprawdzenie: Czy pacjent istnieje?
        self.cursor.execute('SELECT * FROM new_patients WHERE pat_id = %s', (pat_id,))
        patient = self.cursor.fetchone()
        if not patient:
            print(f'Patient with ID {pat_id} does not exist.')
            return

        # Potwierdzenie usunięcia
        validation = input(f'Are you sure you want to delete patient with id {pat_id}? Y/N ')
        if validation.lower() == 'y':
            try:
                self.cursor.execute('DELETE FROM new_patients WHERE pat_id = %s', (pat_id,))
                self.connection.commit()
                print('Patient deleted.')
            except Exception as e:
                print(f'Error occurred while deleting patient: {e}')
        else:
            print('Deleting aborted.')

    @classmethod
    def alter_patient_details_in_db(cls, self, pat_id: int = None, column_to_change: str = None, new_details: str = None) -> None:
        if pat_id is None or column_to_change is None or new_details is None:
            try:
                pat_id = int(input('Enter patients id: '))
            except ValueError:
                print('Id must be a number. Try again.')
                return
                
            allowed_columns = ['first_name', 'last_name', 'email']
            column_to_change = input('What column you want to change? Enter "first_name", "last_name" or "email": ')
            if column_to_change not in allowed_columns:
                print('Invalid column name.')
                return
                
            new_details = input('Enter a new value: ')
            
        try:
            query = f'''
            UPDATE new_patients SET {column_to_change} = %s
            WHERE pat_id = %s
            '''
            self.cursor.execute(query, (new_details, pat_id))
            self.connection.commit()
            print('Patient detail changed. New details:')
            cls.print_patient(self, pat_id)
        except Exception as e:
            print(f'Error occurred while changing patient details: {e}')

    @classmethod
    def print_patient(cls, self, pat_id=None) -> None:
        if not pat_id:
            pat_id = input('Enter patient id (or empty space to exit): ')
            if pat_id == ' ':
                print('Exiting the program. Good bye!')
                sys.exit(0)
        try:
            pat_id = int(pat_id)

        except ValueError:
            print('Invalid patient ID format. Try again or enter empty space to exit.')
            return cls.print_patient(self)
        
        try:
            self.cursor.execute('SELECT * FROM new_patients WHERE pat_id = %s', (pat_id,))
            patient_details = self.cursor.fetchone()
            
            if patient_details:
                patient = Patient(*patient_details)
                print('\n--PATIENT DETAILS---')
                print('-id- -first_name- -last_name-------------- --email-------------')
                # print(f'{patient_details[0]:^4} {patient_details[1]:12} {patient_details[2]:25}, {patient_details[3]}')
                print(patient)
            else:
                print(f'No patient found with ID {pat_id}.')
                return cls.print_patient(self)

        except Exception as e:
            print(f'Error retrieving patient details: {e}')

    def view_patient_medicines_list(self) -> None:
        try:
            medicines = Patient_Medicines_View.load_patient_medicines(self.cursor)
            if medicines:
                Patient_Medicines_View.print_patient_medicines_view(medicines)
        except Exception as e:
            print(f"Error occurred while viewing patient's medicines: {e}")

class PatientMenu(Menu, PatientDB):
    '''This class manages navigation and interface logic related to Patient'''
    
    def __init__(self, choice_option: int):
        # Inicjalizujemy prawidłowo każdą klasę bazową
        Menu.__init__(self, 0, 0)
        PatientDB.__init__(self)  # To inicjalizuje również DatabaseHandler
        
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
        self.run(choice_option)
    
    def run(self, choice_option):
        """Runs chosen option"""
        func = self.menu_functions.get(choice_option)
        if func:
            func()
            main()
        else:
            print("Invalid option selected.")

    def menu_add_patient(self):
        # PatienDB.add #########
        self.add_patient_to_database(self)

    def menu_delete_patient(self):
        self.delete_patient()

    def menu_alter_patient_details(self):
        self.alter_patient_details_in_db(self)

    def menu_print_patient(self):
        self.print_patient(self)

    def menu_assign_patient(self): # nie działa
        print("Asign not working write now. Sorry")

    def menu_view_patient_medicines(self): # nie działa
        self.view_patient_medicines_list()

    def menu_exit(self):
        print("Exiting patient menu")
        self.close_connection()

@ dataclass
class Patient_Medicines_View:
    pat_id: int 
    first_name: str 
    last_name: str 
    med_id: int 
    med_name: str 
    last_issued: datetime.date

    def __post_init__(self):
        # Tu mozna by dodac jakas logikę po inicjalizacji, np. formatowanie daty
        pass
    @classmethod
    def load_patient_medicines(cls, cursor, patient_id = None) -> list[Patient_Medicines_View] | None:
        '''this funktion will print one patients view if id given. otherwise will ask for id or email'''
        querry = '''
            SELECT * FROM view_patient_medicines 
                WHERE patient_id = %s'''
        if patient_id:
            try:
                cursor.execute(querry, (patient_id,))
                records = cursor.fetchall()
            except psycopg2.Error as e:
                print(f'Error occured: {e}.')
                return None

        else: 
            column, value = PatientDB.get_patient_details_to_load()
            allowed_columns = ['pat_id', 'email']
            querry = f'''
            SELECT * FROM view_patient_medicines 
                WHERE {column} = %s'''
            if column not in allowed_columns:
                raise ValueError('Indalid action.')
            try:
                cursor.execute(querry, (value,))
                records = cursor.fetchall()
            except psycopg2.Error as e:
                print(f'Error ocurred: {e}')
                return None
          
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
        print("PATIENT'S MEDICINES VIEW:")
        for (pat_id, first_name, last_name), meds in grouped.items():
            print('-pat_id- -first_name- -last_name- ')
            print(f'{pat_id :^8} {first_name :12} {last_name}')
            print('-med_id- -medicine_name----------- -last_issued- ')
            for med_id, med_name, last_issued in meds:
                print(f'{med_id :^8} {med_name :25} {last_issued}')
            print('---')


@ dataclass
class Prescription:
    presc_id: int
    presc_to_patient_id: int 
    issue_date: date # zmienilam na date zamiast datetime.date

    def __post_init__(self):
        if self.issue_date:
            if isinstance(self.issue_date, str):
                try:
                    self.issue_date = datetime.strptime(self.issue_date, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Warning: Invalid date format for '{self.issue_date}'. Setting to today's date.")
                    self.issue_date = datetime.now().date()
            elif isinstance(self.issue_date, datetime):
                self.issue_date = self.issue_date.date()
        else:
            self.issue_date = datetime.now().date()

    def add_prescription(self, prescriptions: list) -> None:
        prescriptions.append(self)
        print('Prescription added.')

    def create_prescription(self, prescription_details):
        prescription = Prescription(*prescription_details)
        return prescription
# alternatywnie:
    # def __post_init__(self):
    #     if isinstance(self.issue_date, str):
    #         try:
    #             self.issue_date = datetime.strptime(self.issue_date, '%Y-%m-%d').date()
    #         except ValueError:
    #             print(f"Warning: Invalid date format. Setting to today's date.")
    #             self.issue_date = date.today()
    #     elif isinstance(self.issue_date, datetime):
    #         self.issue_date = self.issue_date.date()


class PrescriptionDB(DatabaseHandler):
    '''This class manages database operations and Prescription logic'''
    def __init__(self):
        # Inicjalizujemy klasę bazową DatabaseHandler
        super().__init__()

    def get_presc_id_from_prescription_details(self, pat_id: int, issue_date: date) -> Optional[int]: # czy datetime.datetime?

        self.cursor.execute('''
    SELECT presc_id FROM new_prescriptions WHERE pat_id = %s AND issue_date = %s
''', (pat_id, issue_date))
        result = self.cursor.fetchone()
        if result:
            try: 
                presc_id = int(result[0])
                return presc_id
        # return int(result[0]) if result else None  /moze tak?/
            except (ValueError, TypeError):
                print('Value received as presc_id is incorrect.')
                return None
        else:
            print('Prescription with given details not found.')
            return None

    def get_date_from_user(self) -> date:
        while True:
            date_input = input('Enter issue date in format YYYY-MM-DD: ').strip()
            
            if not date_input: 
                print('Date cannot be empty. Try again.')
                continue
                
            try:
                # Parsowanie daty i konwersja do date
                parsed_date = datetime.strptime(date_input, '%Y-%m-%d').date()
                
                # Dodatkowa walidacja - data nie może być z przyszłości
                if parsed_date > date.today():
                    print('Issue date cannot be in the future. Try again.')
                    continue      

                return parsed_date
                
            except ValueError:
                print('Incorrect date format. Please use YYYY-MM-DD format (e.g., 2024-12-31). Try again.')
                continue
    
    def get_prescription_details(self) -> tuple[int, date]|None:
        # moge zostawic date pusta, pozniej utworzyc obiekt Prescription i tam jus w selfie jest formatowanie daty*
        while True:

            pat_id_input = input('Enter patient id: (or enter space to exit)').strip()
            if pat_id_input == ' ':
                Menu.display_menu()
                return None

            try:
                pat_id = int(pat_id_input)
                if pat_id <= 0:
                    print('Patient ID must be a positive number. Try again.')
                    continue
                break
            except (TypeError, ValueError):
                print('You entered incorrect data. Try again.')
                # return self.get_prescription_details() #  uzytkownik może wpisac ' ' to exit
                continue

        date_option = input('If you want to set prescription issue datepress Y').strip().upper()
        if date_option == 'Y':
            issue_date = self.get_date_from_user()

        else:
            issue_date = date.today()
            print(f'Default date set to: {issue_date}')

        return pat_id, issue_date
    
    def get_medicine_id_for_prescription(self) -> int|None:

        medicine_name = input('Enter medicine name you are looking for: ')
        try:
            self.cursor.execute('''
            SELECT med_id FROM new_medicines 
            WHERE med_name = %s
            ''', (medicine_name,))
            result = self.cursor.fetchone()
            if result:
                med_id = int(result[0])
                print(f"med_id: {med_id}")
                return med_id
            else:
                print('medicine not found')
        except Exception as e:
            print(f'Error looking for medicine: {e}')
            return None

    def complete_list_of_medicines_id(self) -> list[int]:
        medicine_ids = []
        while True:
            med_id = self.get_medicine_id_for_prescription()
            medicine_ids.append(med_id)
            print(f'Medicine id: {med_id} added to the list')
            continuation_choice = input('Do you want to add more medicines id? Y/N ').strip().upper()
            if continuation_choice == 'N':
                break

        return medicine_ids
    
    def add_medicines_to_prescription(self, presc_id: int, medicine_ids: list[int]) -> None:
        for med_id in medicine_ids:
            self.cursor.execute(f'''
        INSERT INTO new_prescriptions_medicines (presc_id, med_id)
        VALUES ({presc_id}, {med_id})
''')
            self.connection.commit()
        print('Medicines added to prescription.')

    def create_new_prescription(self, pat_id, issue_date) -> int:
        '''creates new prescriptions in database by adding patient id and date of issue. Returns id of the new prescription.'''
        try:
            self.cursor.execute('''
            INSERT INTO new_prescriptions (pat_id, issue_date)
            VALUES (%s, %s)
            ''', (pat_id, issue_date))

            self.connection.commit()
            print("Prescription added")

            # get new presc_id:
            presc_id = self.get_presc_id_from_prescription_details(pat_id, issue_date)

            print(f"Prescription id: {presc_id}")
            return presc_id

            # print presc id or presc details
        except Exception as e:
            self.connection.rollback()
            print(f'Error adding prescription: {e}')
    
    def add_prescription_to_database(self, medicines_ids: list[int]=None, prescription_details: tuple[int, date]=None): # or datetime?
        if not prescription_details:
            prescription_details = self.get_prescription_details()
        pat_id, issue_date = prescription_details



        # adding medicines to relational table (n:n)
        if not medicines_ids:
            medicines_ids = self.complete_list_of_medicines_id()
            print(f'medicines_ids: {medicines_ids}')
        self.add_medicines_to_prescription(presc_id, medicines_ids)

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
        if func:
            func()
            main()
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


# ________________________________________________________________________
# @staticmethod
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

# funkcje dla administratora:
def select_all_from_table_ordered_by_id(cursor: Any, table_name: str, id_name: str) -> None:
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
    # Praca z menu:
    menu = Menu(0, 0)
    menu.display_menu()
    menu_object = menu.choose_menu_object()
    menu.object_choice = menu_object
    
    menu.display_options(menu_object)
    choice_option = menu.choose_option(menu_object)
    menu.activate_menu_child_class(menu_object, choice_option)

    # connection, cursor = connect_to_database()
    # load_or_print_patients_medicines_from_view(cursor)
    # select_all_from_table_ordered_by_id(cursor, 'new_patients', 'pat_id')
    # prescription_connection = PrescriptionDB()
    # prescription_connection.get_medicine_id_for_prescription()
    # connection.close()
    # print('Connection closed')

if __name__ == '__main__':
    main()