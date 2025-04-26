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

def insert_test_data(connection, cursor: Any) -> None:
    """Insert test data into the database"""
    medicines = [
        (str(uuid.uuid4()), 'Aspirin', '500mg', 20, ''),
        (str(uuid.uuid4()), 'Ibuprofen', '200mg', 15, 'Anti-inflammatory pain reliever'),
        (str(uuid.uuid4()), 'Paracetamol', '500mg', 30, 'Pain reliever and fever reducer'),
        (str(uuid.uuid4()), 'Levothyroxine 100', '100mg/day', 28, 'Take one pill every morning before food'),
        (str(uuid.uuid4()), 'Metformin', '500mg', 60, 'Take one pill twice a day with meals'),
        (str(uuid.uuid4()), 'Lisinopril', '10mg', 30, 'Take one pill every day at the same time'),
        (str(uuid.uuid4()), 'Amoxicillin', '500mg/8h', 21, 'Take one pill every 8 hours for 7 days'),
        (str(uuid.uuid4()), 'Cetirizine', '10mg/day', 30, 'Take one pill daily for allergies'),
        (str(uuid.uuid4()), 'Pulmicort', '200mg', 30, 'Take one puff twice a day for asthma'),
        (str(uuid.uuid4()), 'Mometasone', '200mg', 30, 'Take one puff every nostril once a day for allergies'),
        (str(uuid.uuid4()), 'Hydrocortizone cream 1%', '10mg/1g', 1 , 'Corticosteroid ointment for skin irritation'),
        (str(uuid.uuid4()), 'Salbutamol', '100mg', 30, 'Take one puff as needed for asthma attacks'),
    ]
    cursor.executemany(
        """
        INSERT INTO medicines (med_id, med_name, dosage, quantity, description)
        VALUES (%s, %s, %s, %s, %s)
        """,
        medicines
    )

    patients = [
        (str(uuid.uuid4()), 'John', 'Doe', 'johndoe@gmail.com'),
        (str(uuid.uuid4()), 'Jane', 'Smith', 'jane_smith@x.com'),
        (str(uuid.uuid4()), 'Alice', 'Johnson', 'alicee@yahoo.com'),
        (str(uuid.uuid4()), 'Bob', 'Brown', 'lol_123@hotmail.com'),
        (str(uuid.uuid4()), 'Charlie', 'Davis', 'hey_charlie@lol.pl'),
        (str(uuid.uuid4()), 'Anna', 'Kowalska', 'kowalska@o2.pl'),
        (str(uuid.uuid4()), 'Jan', 'Nowak', 'doctorek@gmail.com'),
        (str(uuid.uuid4()), 'Piotr', 'Wiśniewski', 'ja_wisnia@onet.pl'),
        (str(uuid.uuid4()), 'Katarzyna', 'Wójcik', 'wojcikkk@lol.pl'),
        (str(uuid.uuid4()), 'Max', 'Kowalczyk', 'max_kowal@x.com')
    ]

    
    cursor.executemany(
        """
        INSERT INTO patients (pat_id, first_name, last_name, email)
        VALUES (%s, %s, %s, %s)
        """,
        patients
    )
    prescriptions = [
        (str(uuid.uuid4()), patients[0][0], date(2025, 4, 25)),  # John Doe
        (str(uuid.uuid4()), patients[2][0], date(2025, 4, 24)),  # Alice Johnson
        (str(uuid.uuid4()), patients[4][0], date(2025, 4, 23)),  # Charlie Davis
        (str(uuid.uuid4()), patients[5][0], date(2025, 4, 22)),  # Anna Kowalska
        (str(uuid.uuid4()), patients[7][0], date(2025, 4, 21)),  # Piotr Wiśniewski
    ]

    # Tworzymy powiązania prescriptions_medicines
    prescriptions_medicines = [
        # Recepta 1: John Doe
        (prescriptions[0][0], medicines[0][0]),  # Aspirin
        (prescriptions[0][0], medicines[4][0]),  # Metformin

        # Recepta 2: Alice Johnson
        (prescriptions[1][0], medicines[2][0]),  # Paracetamol
        (prescriptions[1][0], medicines[7][0]),  # Cetirizine

        # Recepta 3: Charlie Davis
        (prescriptions[2][0], medicines[1][0]),  # Ibuprofen
        (prescriptions[2][0], medicines[5][0]),  # Lisinopril

        # Recepta 4: Anna Kowalska
        (prescriptions[3][0], medicines[3][0]),  # Levothyroxine 100
        (prescriptions[3][0], medicines[10][0]), # Hydrocortizone cream

        # Recepta 5: Piotr Wiśniewski
        (prescriptions[4][0], medicines[8][0]),  # Pulmicort
        (prescriptions[4][0], medicines[11][0]), # Salbutamol
    ]

    # Teraz możesz wrzucić dane do bazy np. tak:
    cursor.executemany(
        """
        INSERT INTO prescriptions (presc_id, pat_id, issue_date)
        VALUES (%s, %s, %s)
        """,
        prescriptions
    )

    cursor.executemany(
        """
        INSERT INTO prescriptions_medicines (presc_id, med_id)
        VALUES (%s, %s)
        """,
        prescriptions_medicines
    )

    connection.commit()
    print("Data added!")

def main() -> None:
    # menu = Menu(0, {}, {})
    # menu.display_menu()
    # choice = menu.choose_menu_object()
    # menu.choice = choice  # Set the choice in the Menu instance
    # menu.__post_init__()  # Initialize options and functions based on the choice
    # menu.display_options()
    # option = menu.choose_option()
    # function = menu.get_function(option)
    # print(f'You selected action: {function}')

    connection, cursor = connect_to_database()
    # insert_test_data(connection, cursor) # Uncomment this line to insert test data
    cursor.close()
    connection.close()
# ++++++++++++++++++++++++++++++

if __name__ == "__main__":
    main()