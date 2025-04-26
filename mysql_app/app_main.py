from dataclasses import dataclass, field
from datetime import datetime
from time import strftime, strptime
from typing import Optional, List, Any
import click
import _mysql_connector
import mysql
import mysql.connector
import mysql.connector.cursor
from app3 import init_database, check_table_name


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
            self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        else:
            self.date = datetime.now().date()
        if self.description is None:
            self.description = ''
        
    def __str__(self):
        return f"({self.id}, '{self.name}', '{self.dosage}', {self.quantity}, '{self.date.isoformat()}', '{self.description}')"

    def add_item(self, cursor: mysql.connector.cursor.MySQLCursor , connection: mysql.connector.MySQLConnection, sql_table: str ='Medicines_mysql') -> None:
        try:
            cursor.execute(f'INSERT INTO {sql_table} (id, name, dosage, quantity, date, description) VALUES {self.__str__()};')
            connection.commit()
            print('Item added.')
        except mysql.connector.Error as e:
            print(f'Error adding item: {e}')
    
    def delete_item(self, cursor: mysql.connector.cursor.MySQLCursor , connection: mysql.connector.MySQLConnection, sql_table: str ='Medicines_mysql') -> None:
        try:
            cursor.execute(f'DELETE FROM {sql_table} WHERE id = {self.id};')
            connection.commit()
            print('Item deleted.')
        except mysql.connector.Error as e:
            print(f'Error deleting item: {e}')

    def is_low(self) -> bool:
        return self.quantity <= 10
    
def generate_id(sql_table='Medicines_mysql') -> int:
    """Generate a new ID for the medication"""
    check_table_name(sql_table)
    my_db, cursor = init_database()
    cursor.execute(f"USE {my_db};")
    cursor.execute(f'SELECT MAX(id) FROM {sql_table}')
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
def main():
    pass

if __name__ == "__main__":
    main()