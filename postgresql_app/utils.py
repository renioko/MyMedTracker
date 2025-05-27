from typing import Any
from postgresql_app.database_connection import connect_to_database


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

def main():
    """Main function to connect to the database and execute queries"""
    try:
        connection, cursor = connect_to_database()
        print("Connected to the database successfully.")
        
        # Example usage
        select_all_from_table_ordered_by_id(cursor, 'new_patients', 'pat_id')
        load_or_print_patients_medicines_from_view(cursor)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Database connection closed.")