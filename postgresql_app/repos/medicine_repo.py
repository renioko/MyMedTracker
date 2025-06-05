from __future__ import annotations
from collections import defaultdict
from typing import List, Tuple, Any, Optional


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import Medicine
from database_connection import DatabaseHandler

class MedicineDB(DatabaseHandler, Medicine):
    '''This class manages database operations and Medicine logic'''
    # def get_medicine_details(self, med_name: str =None) -> Tuple[int, str, str, int, str]:
    def get_medicine(self, med_name: str =None) -> Medicine:
        """Uses medicine name to search in database for given medicine and loads medicine id, name, dosage, quantity and description."""
        if not med_name:
            med_name = input('Enter medicine name:')
        
        try:
            self.cursor.execute("""
            SELECT med_id, med_name, dosage, quantity, description FROM new_medicines
            WHERE med_name = %s""", (med_name,))
            result = self.cursor.fetchone()
            if result:
                # med_id, med_name, dosage, quantity, description = result
                medicine = Medicine(*result)
                return medicine
            else:
                print('Medicine not found.')
                return 'Medicine not found.'
        except Exception as e:
            print(f'Error occurred: {e}.')
            return f'Error occurred: {e}.'

    def get_medicine_by_id(self, med_id: int =None) -> Medicine|None:
            """Uses medicine name to search in database for given medicine and loads medicine id, name, dosage, quantity and description."""
            if not med_id:
                med_id = input('Enter medicine id:')
            
            try:
                self.cursor.execute("""
                SELECT med_id, med_name, dosage, quantity, description FROM new_medicines
                WHERE med_id = %s""", (med_id,))
                result = self.cursor.fetchone()
                if result:
                    # med_id, med_name, dosage, quantity, description = result
                    medicine = Medicine(*result)
                    return medicine
                else:
                    print('Medicine not found.')
                    return 'Medicine not found.'
            except Exception as e:
                print(f'Error occurred: {e}.')
                return f'Error occurred: {e}.'

    def load_medicines(self) -> list[Medicine]:
        pass

    def print_medicine(self, medicine) -> None:
        pass

    def add_medicine_to_database(self, med_name:str, dosage: str, quantity:int =0, description: str =None) -> str:
        """Adds medicine to database and returns string with statement."""
        self.cursor.execute("""
        INSERT INTO new_medicines (med_name, dosage, quantity, description)
        VALUES (%s, %s, %s, %s)""", (med_name, dosage, quantity, description))

        self.connection.commit()
        print('Medicine added.')

        medicine = self.get_medicine(med_name)
        if medicine:
            return f"Medicine added to database with id: {medicine.med_id}.\n {str(medicine)}" #str medicine nie dzisała :/
        else:
            return "Something is wrong. Medicine details could not be retrieved."
        
    def delete_medicine(self, med_id):
        try:
            med_id = int(med_id)
        except ValueError:
            return 'Invalid medicine id.'
        try:
            self.cursor.execute('''
            DELETE FROM new_medicines WHERE med_id = %s''', (med_id,))
            self.connection.commit()
            # return 'Medicine deleted.'
        
        except Exception as e:
            return f'Exception: {e}'
        
        result = self.get_medicine_by_id(med_id)
        if not result:
            return 'Medicine deleted.'
        else:
            return 'Something went wrong. Medicine not deleted.'