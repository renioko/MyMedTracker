from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import sys
from typing import Optional, List, Any
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

@ dataclass
class Medicine:
    med_id: int
    name: str
    dosage: str
    quantity: int
    # date: Optional[datetime.date] # data musi byc pobrana z view przez fk
    description: Optional[str] = None

   
    def __post_init__(self):
        if self.dosage is None:
            self.dosage = ''
        if int(self.quantity) < 0:
            raise ValueError('ERROR! You entered a negative number.')
        # if self.date:
        #     if isinstance(self.date, str):
        #         self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        #     elif isinstance(self.date, datetime):
        #         self.date = self.date.date()
        # else:
        #     self.date = datetime.now().date()
        if self.description is None:
            self.description = ''
        
    def __str__(self):
        return f'''
        Medicine_id: {self.med_id},
        Medicine name:{self.name}, 
        Dosage: {self.dosage}, 
        Quantity: {self.quantity}, 
        Description: '{self.description}'''

    def is_low(self) -> bool:
        return self.quantity <= 10 # nie dziala poprawnie
    
    def add_medicine(self, medicines: list) -> None:
        medicines.append(self)
        print('Medicine added.')

        
@ dataclass
class Patient: # zaczac uzywac w princie!!
    pat_id: int
    first_name: str
    last_name: str
    email: str

    def __str__(self):
        return (f'{self.pat_id:^4} {self.first_name:12} {self.last_name:25}, {self.email}')
    
    # na razie nieppotrzebne:
    def create_patient(self, patient_details: tuple[int, str, str, str]) -> Patient:
        # pat_id, first_name, last_name, email = patient_details
        patient = Patient(*patient_details)
        return patient
    # na razie nieppotrzebne:
    def add_patient(self, patients: list) -> None:
        patients.append(self)
        print('Patient added.')

@dataclass
class Patient_View:
    pat_id: int 
    username: str
    first_name: str 
    last_name: str 
    email: str
    emergency_contact: str
    medical_info: str

    def __str__(self):
        return (f"""PATIENT DETAILS:
============================================
PAT_ID: {self.pat_id}
USERNAME: {self.username}
FIRST NAME: {self.first_name}
LAST NAME: {self.last_name}
EMAIL: {self.email}
EMERGENCY CONTACT: {self.emergency_contact}
MEDICAL INFO: {self.medical_info}""")
    

@ dataclass
class Patient_Medicines_View:
    pat_id: int 
    first_name: str 
    last_name: str 
    med_id: int 
    med_name: str 
    last_issued: datetime.date

    def __post_init__(self):
        # Tu mozna by dodac jakas logikę po inicjalizacji, np. formatowanie daty
        pass

    def __str__(self):
        return (f"""
        PATIENT'S MEDICINES VIEW:
        -pat_id- -first_name- -last_name- 
        {self.pat_id :^8} {self.first_name :12} {self.last_name}
        -med_id- -medicine_name----------- -last_issued- 
        {self.med_id :^8} {self.med_name :25} {self.last_issued}""")

@dataclass
class User:
    user_id: int
    username: str
    email: str
    password_hash: str
    role_id: int
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    last_login: datetime

    def __str__(self):
        roles = {1: 'patient', 2: 'professional', 3: 'admin'}
        role = roles.get(self.role_id)
        # print('USER DETAILS:')
        # print('-ID- ----USERNAME- -----EMAIL------------  ---ROLE------- -FIRST_NAME- --LAST_NAME--------')
        # print(f'{self.user_id :^4} {self.username :^13} {self.email :^22} {role :^14} {self.first_name :12} {self.last_name}')
        return(f'USER DETAILS:\n -ID- ----USERNAME- -----EMAIL------------  ---ROLE------- -FIRST_NAME- --LAST_NAME--------\n {self.user_id :^4} {self.username :^13} {self.email :^22} {role :^14} {self.first_name :12} {self.last_name}')

@ dataclass
class Prescription:
    presc_id: int
    presc_to_patient_id: int 
    issue_date: date # zmienilam na date zamiast datetime.date

    def __post_init__(self):
        if self.issue_date:
            if isinstance(self.issue_date, str):
                try:
                    self.issue_date = datetime.strptime(self.issue_date, '%Y-%m-%d').date()
                except ValueError:
                    print(f"Warning: Invalid date format for '{self.issue_date}'. Setting to today's date.")
                    self.issue_date = datetime.now().date()
            elif isinstance(self.issue_date, datetime):
                self.issue_date = self.issue_date.date()
        else:
            self.issue_date = datetime.now().date()

    def add_prescription(self, prescriptions: list) -> None:
        prescriptions.append(self)
        print('Prescription added.')

    def create_prescription(self, prescription_details):
        prescription = Prescription(*prescription_details)
        return prescription
# alternatywnie:
    # def __post_init__(self):
    #     if isinstance(self.issue_date, str):
    #         try:
    #             self.issue_date = datetime.strptime(self.issue_date, '%Y-%m-%d').date()
    #         except ValueError:
    #             print(f"Warning: Invalid date format. Setting to today's date.")
    #             self.issue_date = date.today()
    #     elif isinstance(self.issue_date, datetime):
    #         self.issue_date = self.issue_date.date()