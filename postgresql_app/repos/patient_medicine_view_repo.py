from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import Patient_Medicines_View
from postgresql_app.database_connection import DatabaseHandler

class Patient_Medicines_ViewDB(Patient_Medicines_View, DatabaseHandler):
    '''This class manages database operations and Patient_Medicines_View logic'''
    def __init__(self):
        # Inicjalizujemy klasę bazową DatabaseHandler
        DatabaseHandler.__init__(self)
        Patient_Medicines_View.__init__(self, 0, '', '', 0, '', date.today())
        # super().__init__()

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
            column, value = cls.get_patient_details_to_load()
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

    def view_patient_medicines_list(self) -> None:
        try:
            medicines = Patient_Medicines_ViewDB.load_patient_medicines(self.cursor)
            if medicines:
                Patient_Medicines_ViewDB.print_patient_medicines_view(medicines)
        except Exception as e:
            print(f"Error occurred while viewing patient's medicines: {e}")


def main():
    db = DatabaseHandler()
    view = Patient_Medicines_ViewDB()
    view.view_patient_medicines_list()

if __name__ == '__main__':
    main()