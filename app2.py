from ast import Tuple
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from time import strftime, strptime
from typing import List, Any, Optional
import click
import sys

DB_SQL = 'MyMedTracker\\MEDICINES.db'

@dataclass
class Medication:
    id: int
    name: str
    dosage: str
    quantity: int
    date: datetime.date # datetime.strptime('%Y-%m-%d')  # in 'YYYY-MM-DD' format
    description: Optional[str] = None

    def __post_init__(self):
        if self.dosage is None:
            self.dosage = ''
        if self.quantity < 0:
            raise ValueError('ERROR! You entered a negative number.')
        if self.date:
            self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        else:
            self.date = datetime.now().date()
        if self.description is None:
            self.description = ''
        
    def __str__(self):
        return f"({self.id}, '{self.name}', '{self.dosage}', {self.quantity}, '{self.date.isoformat()}', '{self.description}')"

    def add_item(self, cursor: sqlite3.Cursor, connection: sqlite3.Connection, sql_table: str ='Medicines') -> None:
        try:
            cursor.execute(f'INSERT INTO {sql_table} (id, name, dosage, quantity, date, description) VALUES {self.__str__()};')
            connection.commit()
            print('Item added.')
        except sqlite3.Error as e:
            print(f'Error adding item: {e}')
    
    def delete_item(self, 
                    cursor: sqlite3.Cursor, 
                    connection: sqlite3.Connection, 
                    sql_table: str='Medicines'
) -> None:
        try:
            cursor.execute(f'DELETE FROM {sql_table} WHERE id = {self.id};')
            connection.commit()
            print('Item deleted.')
        except sqlite3.Error as e:
            print(f'Error deleting item: {e}')

    def is_low(self) -> bool:
        return self.quantity <= 10
    
# not in use currently
def change_column_name(cursor: sqlite3.Cursor, old_column_name: str, new_column_name: str, sql_table: str='Medicines', connection: sqlite3.Connection=None
) -> None:  
    cursor.execute(f'ALTER TABLE {sql_table} RENAME COLUMN {old_column_name} TO {new_column_name};')
    connection.commit()
    print(f'Column {old_column_name} changed to {new_column_name}.')

def add_column(cursor: sqlite3.Cursor, column_name: str, column_type: str, sql_table: str='Medicines'
) -> None:
    cursor.execute(f'ALTER TABLE {sql_table} ADD COLUMN {column_name} {column_type};')
    print(f'Column {column_name} added.')    
    
def create_table(cursor, 
                 sql_table='Medicines', 
                 connection=None
) -> None:
    cursor.execute(f'DROP TABLE IF EXISTS {sql_table}')
    cursor.execute(f'''CREATE TABLE {sql_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name VARCHAR(255) NOT NULL,
        dosage VARCHAR(25) NOT NULL,
        quantity INTEGER,
        date TEXT,
        description TEXT
    );''')
    if connection:
        connection.commit()
    print('Table created.')
    
def generate_id(cursor, sql_table='Medicines') -> int:
    cursor.execute(f'SELECT MAX(id) FROM {sql_table}')
    max_id = cursor.fetchone()[0]
    return max_id + 1 if max_id is not None else 1

def calculate_days_left(medicine: Medication, cursor, sql_table='Medicines') -> int:
    cursor.execute(f'SELECT date FROM {sql_table} WHERE id = {medicine.id};')
    date = cursor.fetchone()[0]
    # Assuming date is in 'YYYY-MM-DD' format
    date_format = '%Y-%m-%d'
    date_obj = datetime.strptime(date, date_format)
    days_left = (datetime.now() - date_obj).days
    return days_left

def display_warning(medicine: Medication, cursor, sql_table='Medicines' ) -> None:
    days_left = calculate_days_left(medicine, cursor, sql_table='Medicines')
    if days_left < 7:
        print(f'Warning! Medicine {medicine.name} is expired by {datetime.now().date()-days_left} days.')

# not in use currently
def show_table(cursor, sql_table='Medicines') -> None:
    table = cursor.execute(f'PRAGMA table_info ({sql_table});')
    table = cursor.fetchall()
    if not table:
        print('Table not found.')
    print('Table structure:')
    for column in table:
        print(f'Column: {column[1]}')

def load_table(cursor, sql_table='Medicines') -> List[tuple]:
    try:
        cursor.execute(f'SELECT * FROM {sql_table}')
        medicines = cursor.fetchall()
    except sqlite3.Error:
        medicines = []
    return medicines


def create_medicine(cursor, name: str, dosage: str, quantity: int, date: str, description: Optional[str] = None, sql_table='Medicines') -> Medication:
    try:
        medicine = Medication(
            id=generate_id(cursor, sql_table),
            name=name,
            dosage=dosage,
            quantity=quantity,
            date=date,
            description=description
        )
        print (f'Created medicine: {medicine}')
        return medicine
    except ValueError as e:
        print(f'Error creating medicine: {e}')

def print_medicines(medicines: List[Medication], cursor, sql_table='Medicines') -> None:
    if medicines:
        print('--ID--  --------NAME--------  -DOSAGE-  -QUANTITY-  -LOW?-  ---DATE---  -DESCRIPTION-----')
        for med in medicines:
            if med.is_low():
                low = '(!)'
            else:
                low = ''
            print(f'{med.id:6}  {med.name:20}  {med.dosage:8}  {med.quantity:^10}  {low:6}  {med.date}  {med.description}')
    print('Warnings:')
    for med in medicines:
        display_warning(med, cursor, sql_table='Medicines')
    print('-----END-----')

  


def main(): # do usuniecia jak bedzie cli()
    connection = sqlite3.connect(DB_SQL)
    cursor = connection.cursor()

    sql_table = 'Medicines'

    try:
        cursor.execute(f'SELECT id FROM {sql_table} WHERE id = 1;') # Check if the table exists
        print('Table exists.')

    except sqlite3.Error:
        create_table(cursor, sql_table, connection)
    print('Table is ready.')

    # show_table(cursor, sql_table)

    # medicine = create_medicine(cursor, 'Pulmicord400', '400mg', 50, '2023-12-31', 'Take 2 puffs daily ')
    # medicine.add_item(cursor, connection, sql_table)

    # medicine2 = Medication(2, '', '', 0, '', '')
    # medicine3 = Medication(3, '', '', 0, '', '')


    # medicine2.delete_item(cursor, connection, sql_table)
    # medicine3.delete_item(cursor, connection, sql_table)

    data = load_table(cursor, sql_table)
    medicines = []
    for med in data:
        med = Medication(*med)
        medicines.append(med)

    if medicines:
        print_medicines(medicines, cursor, sql_table)
    else:
        print('No medicines found.')
    connection.close()

#     # Example usage:
#     # medicine = create_medicine(cursor, 'Aspirin', '500mg', 20, '2023-12-31', 'Pain reliever')
#     # medicine.add_item(cursor, connection, sql_table)
#     # medicine.delete_item(cursor, connection, sql_table)
#     # medicines = load_table(cursor, sql_table)
#     # print_medicines(medicines, cursor, sql_table)     

if __name__ == '__main__':
    main()
