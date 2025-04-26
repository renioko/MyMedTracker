from ast import Tuple
from typing import List, Any
import pickle
import sys
import click
from dataclasses import dataclass
from csv import DictReader, DictWriter
import sqlite3


DB_MEDICATIONS = 'MyMedTracker.db'
SQL_DB = 'Medicines-click.db'

@dataclass
class Medication:
    '''Class representing a single medication
    id - unique identifier, added automatically
    name - name of the medication  
    dose - dose of the medication. required format: 'number unit' (e.g. '2 pills', '1 ml')
    frequency - frequency of taking the medication. required format: 'number unit' (e.g. '3 times/day', '1 time/week')
    quantity - quantity of the medication in stock. cannot be negative

    is_low() - returns True if quantity is less than 10, False otherwise
    '''
    id: int
    name: str
    dose: str
    frequency: str
    quantity: int

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError('ERROR! You entered a negative number.')
        
    def is_low(self) -> bool:
        return self.quantity < 10
    
    def __str__(self):
        return f"()'{self.id}', '{self.name}', '{self.dose}', '{self.frequency}', '{self.quantity}');"
    
    def add_item_to_sqlite(self, sql_table, cursor, connection):
        try:
            cursor.execute(f'INSERT INTO {sql_table} VALUES' + self.__str__())
            connection.commit()
            print('Medicine added.')
        except sqlite3.Error as e:
            print(f'Error occured while adding an item: {e}.')


class Prescription:
    id: int
    patient_name: str 
    patient_surname: str
    patient_pesel: str
    medications: List[Medication]   
    last_issued: dataclass

def generate_id(items: List[Any] =None, ids: set[int] =None) -> int:
    '''
    Generate a unique ID for a new item.
    If provided list of items having id set of ids will be created. 
    If there's no set of ids then empty set created. 
    Returns:
    - int: A unique ID not present in the provided items or ids.
    '''
    if items:
        try:
            ids = {i.id for i in items if hasattr(i, 'id')}
        except:
            ids = set()
    
    new_id = max(ids) + 1
    # new_id = 1
    # while new_id in ids:
    #     new_id += 1
    return new_id

def calculate_days_of_supply(medication: Medication) -> int:
    '''Calculate the number of remaining days of medication.'''
    dosage = int(medication.dose.split(' ')[0])
    frequency = int(medication.frequency.split('/')[0])
    remaining_days = medication.quantity / (frequency * dosage)
    return remaining_days

# not sure how to implement this function yet
def display_warning(medication: Medication) -> None: 
    remaining_days = calculate_days_of_supply(medication)
    if remaining_days < 7:
        click.echo(f'Warning! Only {remaining_days} days of {medication.name} left! Time to order new prescription!')
    elif medication.is_low():
        click.echo(f'Warning! Quantity of {medication.name} is low!')
    

def load_or_init() -> List[Medication]:
    '''Tries to load list of medications from file MyMedTracker.db using pickle.
    If file not found creates empty list of medications. '''
    try:
        with open(DB_MEDICATIONS, 'rb') as stream:
            medications = pickle.load(stream)
    except FileNotFoundError:
        medications = []
    return medications

def save_medications(medications: List[Medication]) -> None:
    '''Saves medication in file MyMedTracker.db using pickle.'''
    with open(DB_MEDICATIONS, 'wb') as stream:
        pickle.dump(medications, stream)

def create_medication(name: str, dose: str, frequency: str, quantity: int, id: int =None, medications: List[Medication] = None, sqlite_table=None, ids: set[int] =None) -> Medication:
    medication = Medication(
        id = generate_id(medications, sqlite_table, ids),
        name = name,
        dose = dose,
        frequency = frequency,
        quantity = quantity
    )
    return medication

def print_medications(medications: List[Medication]) -> None:
    for m in medications:
        if m.is_low():
            is_low = 'LOW!'
        else:
            is_low = ''
    list_of_shortages = []
    for m in medications:
        short_supply = calculate_days_of_supply(m)
        if short_supply < 7:
            list_of_shortages.append(m.name)
    for m in medications:
        click.echo('--ID--  --NAME--  --DOSE--  --FREQUENCY--  --QUANTITY--')
        click.echo(f'{m.id}: {m.name} - {m.dose} - {m.frequency} - {m.quantity} left. {is_low}')
        click.echo('Shortages: ')
        for i in list_of_shortages:
            click.echo(i)

# def add_item_to_sqlite_table(cursor, medicine):
#     text = medicine.add_item_to_sqlite()
#     cursor.execute(text)
#     click.echo('Medicine added to the table.')

def create_sqlite_table(sqlite_table: str, cursor: sqlite3.Cursor, table: str):
    try:
        cursor.execute(table)
        print(f'{sqlite_table} table is created.')
    except sqlite3.Error as e:
        print(f'Error occured while creating a table: {e}.')
 
def load_or_init_sqlite(sqlite_table='Medicines') -> List[Tuple]:
    '''Creates table with given name that contains list of medicines. 
    If not table name is given then created table is named "Medicines". '''

    table = f'''CREATE TABLE {sqlite_table}(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   name VARCHAR(255) NOT NULL,
                   dose VARCHAR(10) NOT NULL,
                   frequency VARCHAR(25) NOT NULL,
                   quantity INT 
                   );'''
    
    if not sqlite_table.isidentifier(): # do poprawienia na injections
        raise ValueError("Invalid table name. Table names must be alphanumeric and cannot contain special characters.")

            
    with sqlite3.connect(SQL_DB, check_same_thread=False) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM {sqlite_table};")
            data = cursor.fetchall()
            return data
        except sqlite3.OperationalError:
            print(f"Table {sqlite_table} does not exist. Creating a table...")
            try:
                create_sqlite_table(sqlite_table, cursor, table)
                connection.commit()
                print(f"Table {sqlite_table} created successfully.")
                cursor.execute(f"SELECT * FROM {sqlite_table};")
                data = cursor.fetchall()
                return data
            except sqlite3.Error as e:
                raise sqlite3.Error(f"Error occurred while loading data from a table: {e}.") from e


def load_ids_sqlite(sqlite_table: str) -> set[int]:
    '''Returns distinct values of id from given sqlite table.
    Returns set of ids.'''
    with sqlite3.connect(SQL_DB) as connection:
        cursor = connection.cursor()
        cursor.execute(F'SELECT DISTINCT id FROM {sqlite_table}')
        data = cursor.fetchall()
        ids = []
        for id_tuple in data:
            ids.append(int(id_tuple[0]))
    return set(ids) # transforming to set because another function takes sets

def execute_sql_query(query: str) -> None:
    '''Executes a SQL query, restricted to SELECT statements for safety.'''
    if not query.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    connection = sqlite3.connect(SQL_DB)
    cursor = connection.cursor()
    try:
        result = cursor.execute(query)
        for row in result:
            print(row)
    except sqlite3.Error as e:
        print(f'Problem: {e}')

@click.group()
def cli():
    pass
@cli.command()
def report():
    medications = load_or_init()
    if medications:
        print_medications(medications)
    else:
        click.echo('You have not entered any medications yet!')
        sys.exit()

@cli.command()
@click.argument('name')
@click.argument('dose')
@click.argument('frequency')
@click.argument('quantity', type=int)
def add_med (name: str, dose: str, frequency: str, quantity: int) -> None:
    medications = load_or_init()
    medication = create_medication(medications, name, dose, frequency, quantity)
    medications.append(medication)
    save_medications(medications)
    click.echo('New medication added.')

@cli.command()
@click.argument('name')
def remove_med(name: str) -> None:
    medications = load_or_init()
    medications = [m for m in medications if m.name != name]
    save_medications(medications)
    click.echo('Medication removed.')

@cli.command()
@click.argument('csv_file')
def import_csv(csv_file: str) -> None:
    medications = load_or_init()
    try:
        with open(csv_file, 'r') as stream:
            reader = DictReader(stream)
            for row in reader:
                medication = create_medication(medications, row['name'], row['dose'], row['frequency'], row['quantity'])
                medications.append(medication)
        save_medications(medications)
        click.echo('Medications imported.')
    except FileNotFoundError:
        click.echo('File not found.')
        sys.exit()

@cli.command()
@click.argument('csv_file')
def export_csv(csv_file: str) -> None:
    medications = load_or_init()
    with open(csv_file, 'w', newline='') as stream:
        writer = DictWriter(stream, fieldnames=['id', 'name', 'dose', 'frequency', 'quantity'])
        writer.writeheader()
        for m in medications:
            writer.writerow({
                'id': m.id,
                'name': m.name,
                'dose': m.dose,
                'frequency': m.frequency,
                'quantity': m.quantity
            })
        click.echo('Medications exported.')

@cli.command()
@click.argument('sqlite_table')
def print_table(sqlite_table: str) -> None:
    '''Takes sqlite table as 'sqlite_table'. 
    Calls function load or init sqlite that returns content of a given table, create list of Medication objects then print it.'''

    # click.echo('-ID-- --NAME------------- --DOSE-- --FREQUENCY-- -QUANTITY- -IS LOW')
    data = load_or_init_sqlite(sqlite_table)
    if data:
        medications = []
        for row in data:
            id, name, dose, frequency, quantity = row
            medicine = create_medication(name, dose, quantity, frequency, id)
            medications.append(medicine)
    else:
        print('Medicines table is empty.')
        medications = []
    print_medications(medications)


@cli.command()
@click.argument('sqlite_db')
@click.argument('name')
@click.argument('dose')
@click.argument('frequency')
@click.argument('quantity', type=int)
def add_med_to_table(sqlite_table: str, name: str, dose: str, frequency: str, quantity: int) -> None:
    '''Adds medicine to sqlite table: 
    Opens connection with a sqlite3 database and given table, fetches the list list of ids and generate new id for medicine that is being add. 
    Takes variables:
    - name of a sqlite table as 'sqlite_table', 
    - name of medicine as 'name',
    - dosage of medicine as 'dose '- required format: 'number unit' (e.g. '2 pills', '1 ml'),
    - frequency of taking the medication as 'frequency' - required format: 'number unit' (e.g. '3 times/day', '1 time/week'), 
    - quantity of the medication in stock as 'quantity' - cannot be negative
    Creates Medication object and adds it to given sqlite table. 
    '''

    ids = load_ids_sqlite(sqlite_table) 
    medicine = create_medication(name, dose, frequency, quantity, sqlite_table, ids)
    # medicine = Medication(
    #     id = max(ids) + 1, # if this is used then function create medicine and generate id might be simpler.
    #     name = name,
    #     dose = dose,
    #     frequency = frequency,
    #     quantity = quantity
    # )
    connection = sqlite3.connect(SQL_DB) 
    cursor = connection.cursor()
    try:
        medicine.add_item_to_sqlite(sqlite_table, cursor, connection)
    except sqlite3.Error as e:
        load_or_init_sqlite(sqlite_table)
        medicine.add_item_to_sqlite(sqlite_table, cursor, connection)
    connection.close()
         

# I need to add function tontrack quantity
def main():
    data = load_or_init_sqlite(sqlite_table='Medicines')
    query = '''
    SELECT * FROM Medicines
    '''
    execute_sql_query(query)


if __name__ == '__main__':
    main()

    # medicine = Medication(1, 'Pulmicort400', '1 puff', '2 /day', 50 )
    # cli()



