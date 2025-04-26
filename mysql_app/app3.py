from calendar import c
import mysql.connector
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime
from time import strftime, strptime
from typing import Optional, List, Any
import _mysql_connector
import mysql
import mysql.connector
import mysql.connector.cursor

@dataclass
class Medication:
    id: int
    name: str
    dosage: str
    quantity: int
    date: Optional[datetime.date] # datetime.strptime('%Y-%m-%d')  # in 'YYYY-MM-DD' format
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

    def add_item(self, cursor: mysql.connector.cursor.MySQLCursor , connection: mysql.connector.MySQLConnection, table_name: str ='Medicines_mysql') -> None:
        try:
            cursor.execute(f'INSERT INTO {table_name} (id, name, dosage, quantity, date, description) VALUES {self.__str__()};')
            connection.commit()
            print('Item added.')
        except mysql.connector.Error as e:
            print(f'Error adding item: {e}')
    
    def delete_item(self, cursor: mysql.connector.cursor.MySQLCursor , connection: mysql.connector.MySQLConnection, table_name: str ='Medicines_mysql') -> None:
        try:
            cursor.execute(f'DELETE FROM {table_name} WHERE id = {self.id};')
            connection.commit()
            print('Item deleted.')
        except mysql.connector.Error as e:
            print(f'Error deleting item: {e}')

    def is_low(self) -> bool:
        return self.quantity <= 10 # nie dziala poprawnie

def calculate_days_left(medicine: Medication, cursor: mysql.connector.cursor.MySQLCursor, table_name='Medicines_mysql') -> int:
    cursor.execute(f'SELECT date FROM {table_name} WHERE id = {medicine.id};')
    date = cursor.fetchone()[0]
    # Assuming date is in 'YYYY-MM-DD' format
    date_format = '%Y-%m-%d'
    try:
        date_obj = datetime.strptime(date, date_format)
    except TypeError:
        date_obj = date
    days_difference = (datetime.now().date() - date_obj).days
    days_left = medicine.quantity - days_difference
    print(f'Days left for {medicine.name}: {days_left}')
    return days_left

def display_warning(medicine: Medication, cursor: mysql.connector.cursor.MySQLCursor, table_name='Medicines_mysql' ) -> None:
    days_left = calculate_days_left(medicine, cursor, table_name='Medicines_mysql')
    if days_left < 7:
        print(f'Warning! Medicine {medicine.name} is expired by {days_left} days.')


def generate_id(table_name='Medicines_mysql') -> int:
    """Generate a new ID for the medication"""
    check_table_name(table_name)
    my_db, cursor = init_database()
    cursor.execute(f"USE {my_db};")
    cursor.execute(f'SELECT MAX(id) FROM {table_name}')
    max_id = cursor.fetchone()[0]
    return max_id + 1 if max_id is not None else 1
    
def create_medicine(name: str, dosage: str, quantity: int, date: Optional[str], description: Optional[str], table_name='Medicines_mysql') -> Medication:
    """Create a medication object"""
    check_table_name(table_name)
    return Medication(
        id=generate_id(table_name),
        name=name,
        dosage=dosage,
        quantity=quantity,
        date=date,
        description=description
    )
def load_server_login() -> tuple[str, str, str]:
    """loads server login"""
    load_dotenv()
    try:
        host = os.getenv('host')
        user = os.getenv('user')
        password = os.getenv('password')
    except KeyError:
        print('problem with HOST, MYSQL_USER or MYSQL_PASSWORD')
    return host, user, password

def init_database() -> tuple[ mysql.connector.MySQLConnection, mysql.connector.cursor.MySQLCursor]:
    """Initialize the database"""
    host, user, password = load_server_login()

    my_db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        # database="MyMedTracker\\MyMedTracker-mysql"
    )

    if my_db.is_connected():
        print("Connected to MySQL Server")
    else:
        print("Connection failed")

    cursor = my_db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS MyApp_MYSQL;")
    cursor.execute("USE MyApp_MYSQL;")
    print("Database is active")
    return my_db, cursor

def create_table(my_db, cursor,table_name='Medicines_mysql') -> None:
    """Create a table"""
    check_table_name(table_name)
    my_db, cursor = init_database()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (" \
    "id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, " \
    "name VARCHAR(255) NOT NULL, " \
    "dosage VARCHAR(25) NOT NULL, " \
    "quantity INT, " \
    "date DATE, " \
    "description TEXT);")

    my_db.commit()

    print("Table created.")
    cursor.close()
    my_db.close()

def insert_values(my_db, cursor, values, table_name='Medicines_mysql') -> None:
    """Insert values into the table"""
    my_db, cursor = init_database()
    check_table_name(table_name)
    sql = f"INSERT INTO {table_name}(name, dosage, quantity, date, description) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, values)
    my_db.commit()
    print("Values inserted.")
    cursor.close()
    my_db.close()

def show_table(my_db, cursor, table_name='Medicines_mysql') -> None:
    """Show the table"""
    check_table_name(table_name)
    my_db, cursor = init_database()
    cursor.execute(f"SELECT * FROM {table_name}")
    result = cursor.fetchall()
    for row in result:
        print(row)
    cursor.close()
    my_db.close()

def load_medicines(my_db, cursor, table_name='Medicines_mysql') -> list[Medication]:
    """Load the table into a list"""
    check_table_name(table_name)
    my_db, cursor = init_database()
    cursor.execute(f"SELECT * FROM {table_name}")
    result = cursor.fetchall()
    medicines = []
    for row in result:
        medicines.append(Medication(
            id=row[0],
            name=row[1],
            dosage=row[2],
            quantity=row[3],
            date=row[4],
            description=row[5]
        ))
    cursor.close()
    my_db.close()
    return medicines

def check_table_name(table_name='Medicines_mysql') -> str:
    """Check if the table exists"""
    if isinstance(table_name, str):
        return table_name
    else:
        raise ValueError("Table name must be a string")
    
def print_medicines(my_db: mysql.connector.CMySQLConnection, cursor: mysql.connector.cursor.MySQLCursor, table_name: str='Medicines_mysql') -> None:
    """Print the medicines"""
    check_table_name(table_name)
    medicines = load_medicines(my_db, cursor, table_name)
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
        display_warning(med, cursor, table_name='Medicines')
    print('-----END-----')

def main():
    my_db, cursor = init_database()
    table_name = 'Medicines_mysql'
    create_table(my_db, cursor, table_name)
    # insert_values(my_db, cursor, ('Aspirin', '500mg', 20, '2023-10-01', 'Pain reliever'), 'Medicines_mysql')
    show_table(my_db, cursor, table_name)
    print_medicines(my_db, cursor, table_name)
    cursor.close()
    my_db.close()

if __name__ == "__main__":
    main()
