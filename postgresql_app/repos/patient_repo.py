from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any, Tuple
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import Patient, User
from database_connection import DatabaseHandler
from .user_repo import UserDB

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

    def check_username_taken(self, username) -> bool:
        try:
            self.cursor.execute('''SELECT 1 FROM users WHERE username = %s''', (username,))
            response = self.cursor.fetchone()
        except psycopg2.Error as e:
            print(f'Error: {e}.')
        if response:
            print('This username is taken.')
            return True
        else:
            print('This username is free.')
            return False

    
    def get_details_to_add_patient(self) -> Tuple[str, str, str, int, str, str, str, str]:
        """Takes standars user details and adds details specific for patients."""
        user_db = UserDB()
        username, email, password, first_name, last_name, role_id = user_db.get_user_details()

        pat_details = user_db.check_user_details(username, email, password, role_id, first_name, last_name) #dodałam self w nawiasie
        if not pat_details:
            print('Invalid user details.')
            return None
        username, email, password_hash, role_id, first_name, last_name = pat_details

        #additional for patients:
        emergency_contact = input('Enter emergency contact name and number: ')
        medical_info = input('Enter important medical informations: ')

        patient_details = username, email, password_hash, role_id, first_name, last_name, emergency_contact, medical_info
        return patient_details
    

    def get_pat_id_from_user_id(self, user_id: int) -> int | None:
        self.cursor.execute('''
        SELECT pat_id FROM new_patients
        WHERE user_id = %s ''', (user_id,))
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

    @classmethod
    def add_patient_to_database(cls, self, patient_details: Tuple[str, str, str, int, str, str, str, str] = None, verbose: bool=True) -> str:
        """Takes patients (user details included) if those details are not provided. Adds user to database, returns user_id then adds all patients details to new_patients table. Returns string with user_id and patient_id. """
        if not patient_details:
            patient_details = cls.get_details_to_add_patient()
        username, email, password_hash, role_id, first_name, last_name, emergency_contact, medical_info = patient_details
        try:
            UserDB.add_user_to_database(username, email, password_hash, role_id, first_name, last_name)
            # result = 'User added.'
            self.connection.commit()
        except Exception as e:  
            print(f'Error occurred while adding new user: {e}.')
            # result =  f"Error occurred while adding new user: {e}."

        user_id = UserDB.get_user_id(username, email)
        try:
            self.cursor.execute('''
            INSERT INTO new_patients (user_id, emergency_contact, medical_info)
            VALUES (%s, %s)'''(user_id, emergency_contact, medical_info))
        except Exception as e:
            print(f'Error occurred while adding new patient: {e}.')()
        pat_id = PatientDB.get_pat_id_from_user_id(self, user_id)
            # cls.print_patient(self, pat_id)
        added_patient_info = cls.print_patient(self,pat_id) # po zmianie przez verbose zwraca str
        result = f"Patient added. Patient details:\n {added_patient_info}"
        if verbose:
            print(result)
        return result

######
    def add_patient_and_user_one_connection(self, patient_details: Tuple[str, str, str, int, str, str, str, str] = None, verbose: bool = True) -> Optional[str]:
        """Takes patients (user details included) if those details are not provided. Adds user to database, returns user_id then adds all patients details to new_patients table. Returns string with user_id and patient_id."""
        if not patient_details:
            patient_details = self.get_details_to_add_patient()
        username, email, password_hash, role_id, first_name, last_name, emergency_contact, medical_info = patient_details
        try:
            role_id = int(role_id)# nowa rzecz
        except TypeError:
            if verbose:
                print('Incorrect role id type.')
            return None
        
        try:
            self.cursor.execute('''
        INSERT INTO users (username, email, password_hash, role_id, first_name, last_name)
        VALUES (%s, %s, %s, %s, %s, %s)''', (username, email, password_hash, role_id, first_name, last_name))
            if verbose:
                print('User added.')
        
            self.cursor.execute('''
        SELECT user_id FROM users WHERE username = %s''', (username,))
            user_id = self.cursor.fetchone()[0]

            if not user_id:
                raise Exception('Could not get user_id.')
            
            if verbose:
                print(f'User id: {user_id}')
            
            self.cursor.execute('''
        INSERT INTO new_patients (user_id, emergency_contact, medical_info, medical_notes)
        VALUES (%s, %s, %s, %s)''', (user_id, emergency_contact, medical_info, 'initial note'))
            
            self.connection.commit()

            if verbose:
                print('Patient added to database.')
        except Exception as e:
            self.connection.rollback()
            print(f'Error occurred while adding patient user: {e}.')
            return None
        
        try:
            self.cursor.execute('''
        SELECT pat_id FROM new_patients WHERE user_id = %s''', (user_id,))
            pat_id = self.cursor.fetchone()[0]
            if not pat_id:
                raise Exception('Could not get pat_id.')
            
            if verbose:
                print(f'Patient id: {pat_id}')

            patient_view = self.get_patient_view(pat_id)
            if verbose:
                print(patient_view)
        except Exception as e:
            print(f'Error getting patient view: {e}.')

        result = f'Patient added succesfully and user account creaded. User id: {user_id}, patient id: {pat_id}.'
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


    # changed pat_id to user_id
    def alter_patient_details_in_db(self, user_id: int = None, column_to_change: str = None, new_details: str = None, verbose: bool = True) -> None:
        if verbose:
            if user_id is None or column_to_change is None or new_details is None:
                try:
                    user_id = int(input('Enter user id: '))
                except ValueError:
                    print('Id must be a number. Try again.')
                    return
            column_to_change = input('What column you want to change? Enter 1 for "first_name", 2 for "last_name", 3 for "email" or 4 for"password": ')
            new_details = input('Enter a new value: ')
            if column_to_change == '1':
                column_to_change = 'first_name'
            elif column_to_change == '2':
                column_to_change = 'last_name'
            elif column_to_change == '3':
                column_to_change = 'email'
            elif column_to_change == '4':
                column_to_change = 'password_hash'
                # password = UserDB.generate_password_hash(self, new_details)
                # new_details = password
            else:
                print('invalid choice')

        allowed_columns1 = ['first_name', 'last_name', 'email', 'password_hash', ]
        allowed_columns2 = ['emergency_contact', 'medical_info']

        # if column_to_change not in allowed_columns1 or allowed_columns2:
        #     print('Invalid column name.')
        #     return None
            
        user_id = int(user_id)
            
        if column_to_change in allowed_columns1:
            table = 'users'
        elif column_to_change in allowed_columns2:
            table = 'new_patients'
                
        if column_to_change == "password_hash":
            password = UserDB.generate_password_hash(self, new_details)
            new_details = password

        try:
            query = f'''
            UPDATE {table} SET {column_to_change} = %s
            WHERE user_id = %s;
            '''
            self.cursor.execute(query, (new_details, user_id))
            self.connection.commit()
            print('Patient detail changed. New details:')
            # cls.print_patient(self, pat_id)
            pat_id = self.get_pat_id_from_user_id(self, user_id)
            patient_view = self.get_patient_view(pat_id)
            if verbose:
                print('Patient details updated. New details:')
                print(patient_view)
            return f'Patient details updated. New details:\n{str(patient_view)}'
        except Exception as e:
            if verbose:
                print(f'Error occurred while changing patient details: {e}')
            return f'Error occurred while changing patient details: {e}'


    def get_patient_view(self, pat_id: int = None) -> str:
        from models import Patient_View
        if not pat_id:
            pat_id = input('Enter patient_id: ')
        try: 
            pat_id = int(pat_id)
        except ValueError:
            print('Invalid id.')
            return 'Invalid id.'
        self.cursor.execute('''
        SELECT * FROM patient_view WHERE pat_id = %s''', (pat_id,))
        result = self.cursor.fetchone()
        if result:
            patient_view = Patient_View(*result)
        else:
            print('Patient not found.')
            patient_view = 'Patient not found.'
        print(patient_view)
        return patient_view

# print patient will not longer work. use print_patient_view instead
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
            self.cursor.execute('SELECT pat_id, first_name, last_name, email FROM new_patients WHERE pat_id = %s', (pat_id,))
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


            