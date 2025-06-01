from __future__ import annotations
from collections import defaultdict


from dataclasses import dataclass
import bcrypt
import sys
from typing import Optional, List, Any, Tuple
from datetime import datetime, date
# from time import strftime, strptime
import psycopg2
from config import config_file

from models import User
from database_connection import DatabaseHandler

class UserDB(DatabaseHandler, User):
    def __init__(self):
        super().__init__()

    def get_user_details(self) -> Tuple[str, str, str, str, str, int]:
        """Takes user details and returns raw password (hashing later)."""
        username = input('Enter username: ') 
        email = input('Enter email:')
        password = input('Enter password: ')
        first_name = input('Enter first_name: ') 
        last_name = input('Enter last name: ')
        role_id = int(input('Choose role: enter 1 for patient, 2 for professional, 3 for admin: '))
        return (username, email, password, first_name, last_name, role_id)
    
    def correct_user_role(self, role_id:int) -> bool:
        """Correct role_id will be True."""
        try:
            role_id = int(role_id)
            if role_id in [1, 2, 3]:
                return True
            else:
                return False
        except ValueError:
            print('Incorrect iput.')
            return False

    def generate_password_hash(self, password: str) -> str:
        """Hash password using bcrypt and return it as UTF-8 string."""
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()) # Hash password (bytes input/output)
        # Store the decoded version in database (PostgreSQL expects str, not bytes)
        password_hash = password_hash.decode('utf-8')
        return password_hash

    def check_user_details(self, username: str, email: str, password: str,  role_id: int, first_name: str, last_name: str) -> Tuple[str, str, str, str, str, int]|None:
        username_taken = self.check_username_taken(username)
        if username_taken:
            print('Username taken.')
            return None
        invalid_email = self.check_email_format(email)
        if invalid_email:
            print('Invalid email.')
            return None
        password_hash = self.generate_password_hash(password)
        if not self.correct_user_role(role_id):
            return None
        if not first_name.isalpha():
            print('Incorrect first name.')
            return None
        if not last_name.isalpha():
            print('Incorrect surname.')
            return None

        return username, email, password_hash, role_id, first_name, last_name


    def add_user_to_database(self, username, email, password, role_id, first_name, last_name) -> None:
        # user = User()
        user_data = self.check_user_details(username, email, password, role_id, first_name, last_name)
        if user_data:
            username, email, password_hash, role_id, first_name, last_name = user_data
            self.cursor.execute('''
        INSERT INTO users (username, email, password_hash, role_id, first_name, last_name) 
        VALUES (%s, %s, %s, %s, %s, %s)''', (username, email, password_hash, role_id, first_name, last_name))
        # self.connection.commit()
        print('User added to database.')

    def get_user_id(self, username:str) -> Optional[int]:
        try:
            self.cursor.execute('''
        SELECT user_id from users WHERE username = %s''', (username,))
            result = self.cursor.fetchone()
            if result:
                user_id = int(result[0])
                print(f'User id: {user_id}')
                return user_id
            else:
                print('User not found')
                return None
        except Exception as e:
            print('User not found.')
            return None

    def delete_user(self, user_id, confirmation=False) -> None:
        if not confirmation:
            confirm = input(f'Do you want to delete user with id: {user_id}? Press Y for Yes.')
            if confirm.upper() == 'Y':
                confirmation = True
        if confirmation:
            self.cursor.execute('''
            DELETE FROM users WHERE user_id = %s ''', (user_id,))
            self.connection.commit()
            print('User deleted.')

    def update_user(self, user_id, update_column=None, update_value=None) -> None:
        if not update_column:
            choice= input('Choose which column to update:\n '
            'Press 1 for email.\n'
            'Press 2 for first name.\n'
            'Press 3 for last name\n'
            'Press other key to exit.')
            if choice == '1':
                update_column = 'email'
            elif choice == '2':
                update_column = 'first_name'
            elif choice == '3':
                update_column = 'last_name'
            else:
                print('Invalid choice.')
                return None

        if not update_value:
            update_value = input('Enter new value: ')
        
        self.cursor.execute(f'''
        UPDATE TABLE users SET {update_column} = %s WHERE user_id = %s''', (update_value, user_id))
        self.connection.commit()
        print(f'User detail {update_column} changed to: {update_value}.')

    def view_user(self, user_id=None):
        if not user_id:
            try:
                user_id = int(input('Enter user id:'))
            except (ValueError, TypeError):
                print('Invalid entry.')
                return None
        
        self.cursor.execute('''
        SELECT * FROM users WHERE user_id = %s''', (user_id,))
        user_column = self.cursor.fetchone()
        user = User(*user_column)
        print(user)

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
    def check_email_format(self, email) -> bool:
        chars = '@.'
        return True if chars in email else False
