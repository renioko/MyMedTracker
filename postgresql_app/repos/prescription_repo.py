from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import Prescription
from database_connection import DatabaseHandler

class PrescriptionDB(Prescription, DatabaseHandler):
    '''This class manages database operations and Prescription logic'''
    def __init__(self, pat_id: int = 0, med_id: int = 0, issue_date: date = None):
        DatabaseHandler.__init__(self) # Inicjalizujemy klasę bazową DatabaseHandler
        if issue_date is None:
            issue_date = date.today()
        Prescription.__init__(self, pat_id, med_id, issue_date)       


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
                # Menu.display_menu() - byl circular import error
                print('Exiting prescription creation. Goodbye!')
                sys.exit(1)
                # return None

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
        date_option = input('If you want to set prescription issue date press Y').strip().upper()
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
            if med_id is not None:
                medicine_ids.append(med_id)
                print(f'Medicine id: {med_id} added to the list')
            else:
                print('Medicine not found and not added to the list.')
            continuation_choice = input('Do you want to add more medicines id? Y/N ').strip().upper()
            if continuation_choice == 'N':
                break

        return medicine_ids
    
    def add_medicines_to_prescription(self, presc_id: int, medicine_ids: list[int]) -> None:
        for med_id in medicine_ids:
            if med_id is None:
                continue  # Skip if med_id is None
            self.cursor.execute(f'''
        INSERT INTO new_prescriptions_medicines (presc_id, med_id)
        VALUES ({presc_id}, {med_id})
''')
            self.connection.commit()
        print('Medicines added to prescription.')

    
    def add_prescription_to_database(self, medicines_ids: list[int]=None, prescription_details: tuple[int, date]=None) -> int:
        '''creates new prescriptions in database by adding patient id and date of issue. Returns id of the new prescription.'''

        if not prescription_details:
            prescription_details = self.get_prescription_details()

        if prescription_details is None:
            return  # Wyjście z metody, nie z całego programu
        pat_id, issue_date = prescription_details
        print(f"Patient ID: {pat_id}, Date: {issue_date}")

        # get new presc_id:
        try:
            self.cursor.execute('''
            INSERT INTO new_prescriptions (pat_id, issue_date)
            VALUES (%s, %s)
            ''', (pat_id, issue_date))

            self.connection.commit()
            print("Prescription added")

            # print presc id or presc details
        except Exception as e:
            self.connection.rollback()
            print(f'Error adding prescription: {e}')

        presc_id = self.get_presc_id_from_prescription_details(pat_id, issue_date)

        print(f"Prescription id: {presc_id}")
        
        # adding medicines to relational table (n:n)
        if not medicines_ids:
            medicines_ids = self.complete_list_of_medicines_id()
            print(f'medicines_ids: {medicines_ids}')
        self.add_medicines_to_prescription(presc_id, medicines_ids)
        return presc_id 
    

    # dodac logike drukowania prescription, usuwania prescription itd