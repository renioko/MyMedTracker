from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import Patient
from database_connection import DatabaseHandler

class PatientDB(DatabaseHandler, Patient):
    '''This class manages database operations and Patient logic'''
    
    def __init__(self):
        # Inicjalizujemy klasę bazową DatabaseHandler
        super().__init__()

    # @classmethod
    # def get_patient_details_to_load(cls) -> tuple[str, str]:
    #     choice = input('You want to load patient data. Do you know patient id? Y/N')
    #     if choice.lower() == 'y':
    #         try:
    #             pat_id = int(input('Enter patient id: '))
    #         except TypeError:
    #             print('You entered incorrect data. Try again')
    #             return cls.get_patient_details_to_load() # recursion / rekurencja
    #         return ('pat_id', str(pat_id))
    #     elif choice.lower() == 'n':
    #         choice_2 = input('Do you know patient email? Y/N')
    #         if choice_2.lower() == 'y':
    #             pat_email = input('Enter patient email.')
    #             if not '@' in pat_email:
    #                 print('Email must contain @ character.')
    #                 return cls.get_patient_details_to_load()
    #             return ('email', pat_email)
    #         else:
    #             print('You can not load patient details without id or email.')
    #             sys.exit()
    #     else:
    #         print('Incorrect answer. Try again.')
    #         return cls.get_patient_details_to_load()
        
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
    def add_patient_to_database(cls, self, patient_details: tuple[str, str, str] = None, verbose: bool=True) -> str:
        if not patient_details:
            patient_details = cls.get_details_to_add_patient()
        try:
            self.cursor.execute('''
            INSERT INTO new_patients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            ''', patient_details            
            )
            self.connection.commit()
            # print('Patient added.')
            # result = 'Patient added.'
            pat_id = cls.get_pat_id_from_patient_details(self, patient_details)
            # cls.print_patient(self, pat_id)
            added_patient_info = cls.print_patient(self,pat_id) # po zmianie przez verbose zwraca str
            result = f"Patient added. Patient details:\n {added_patient_info}"

        except Exception as e:  # Używamy ogólnego Exception zamiast psycopg2.Error
            # print(f'Error occurred while adding new patient: {e}.')
            result =  f"Error occurred while adding new patient: {e}."

        if verbose:
            print(result)
        return result

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
    def print_patient(cls, self, pat_id=None, verbose: bool=True) -> Optional[str]:
        """Prints patient if verbose = True, else returns str with patient info to print"""
        if not pat_id and verbose is True:
            pat_id = input('Enter patient id (or empty space to exit): ')
            if pat_id == ' ':
                print('Exiting the program. Good bye!')
                return None # tu zmieniłam
        

        try:
            pat_id = int(pat_id)

        except ValueError:
            result = 'Invalid patient ID format. Try again or enter empty space to exit.'
            # return cls.print_patient(self)
        
        try:
            self.cursor.execute('SELECT * FROM new_patients WHERE pat_id = %s', (pat_id,))
            patient_details = self.cursor.fetchone()
            
            if patient_details:
                patient = Patient(*patient_details)
                # print('\n--PATIENT DETAILS---')
                # print('-id- -first_name- -last_name-------------- --email-------------')
                # print(patient)
                # print(f'{patient_details[0]:^4} {patient_details[1]:12} {patient_details[2]:25}, {patient_details[3]}')

                result = f"'\n--PATIENT DETAILS---'\n'-id- -first_name- -last_name-------------- --email-------------'\n{patient}"

            else:
                # print(f'No patient found with ID {pat_id}.')
                # return cls.print_patient(self)
                result = f'No patient found with ID {pat_id}.'

        except Exception as e:
            result = f'Error retrieving patient details: {e}'

        if verbose:
            print(result)
        return result


            