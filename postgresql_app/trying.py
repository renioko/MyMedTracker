class PatientDB:
    @staticmethod
    def get_details_to_add_patient() -> tuple[str, str, str]:
        first_name = input('Enter patients first name: ')
        last_name = input('Enter patients last name: ')
        email = input('Enter patients email: ')
        # validate email
        return (first_name, last_name, email)

    @classmethod
    def add_patient_to_database(cls, connection, cursor, patient_details: tuple[str, str, str] = None) -> None:
        if not patient_details:
            patient_details = cls.get_details_to_add_patient()
        try:
            cursor.execute('''
            INSERT INTO new_patients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            ''', patient_details            
            )
            connection.commit()
            print('Patient added.')
        except Exception as e:
            print(f'Error occurred while adding new patient: {e}.')


class PatientMenu(PatientDB, Menu):
    def __init__(self, choice_option):
        super().__init__(0, {}, {})
        self.functions = {
            1: self.add_patient,
            2: self.delete_patient,
            3: self.alter_patient_details_in_db,
            4: self.print_patient,
            5: self.assign,  # not working
            6: self.view_patient_medicines_list,  # utworzyc
            7: self.exit
        }
        # Create database connection
        self.connection, self.cursor = connect_to_database()
        # Run the selected function
        self.run(choice_option)
    
    def add_patient(self):
        """Wrapper method for add_patient_to_database"""
        self.add_patient_to_database(self.connection, self.cursor)
    
    def delete_patient(self):
        # Implementation
        print("Delete patient functionality not yet implemented")
    
    def alter_patient_details_in_db(self):
        # Implementation
        print("Alter patient details functionality not yet implemented")
    
    def print_patient(self):
        # Implementation
        print("Print patient functionality not yet implemented")
    
    def assign(self):
        # Implementation
        print("Assign functionality not yet implemented")
    
    def view_patient_medicines_list(self):
        # Implementation
        print("View patient medicines list functionality not yet implemented")
    
    def exit(self):
        print("Exiting patient menu")
        self.connection.close()
    
    def run(self, choice_option):
        '''runs function chosen by user in menu options'''
        func = self.functions.get(choice_option)
        if func:
            func()
        else:
            print("Invalid option selected.")


def main() -> None:
    # Work with menu:
    menu = Menu(0, {}, {})
    menu.display_menu()
    menu_object = menu.choose_menu_object()
    menu.choice = menu_object
    
    menu.display_options(menu_object)
    choice_option = menu.choose_option()
    menu.activate_menu_child_class(menu_object, choice_option)


# ###################3

class DatabaseHandler:
    """Klasa bazowa obsługująca połączenie z bazą danych"""
    
    def __init__(self):
        self.connection, self.cursor = connect_to_database()
        
    def close_connection(self):
        """Zamyka połączenie z bazą danych"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("Database connection closed.")


class PatientDB(DatabaseHandler):
    """Klasa implementująca logikę biznesową operacji na pacjentach"""
    
    @staticmethod
    def get_details_to_add_patient() -> tuple[str, str, str]:
        """Pobiera dane pacjenta od użytkownika"""
        first_name = input('Enter patients first name: ')
        last_name = input('Enter patients last name: ')
        email = input('Enter patients email: ')
        # validate email
        return (first_name, last_name, email)
    
    def add_patient_to_database(self, patient_details: tuple[str, str, str] = None) -> None:
        """Dodaje pacjenta do bazy danych"""
        if not patient_details:
            patient_details = self.get_details_to_add_patient()
        try:
            self.cursor.execute('''
            INSERT INTO new_patients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            ''', patient_details)
            self.connection.commit()
            print('Patient added.')
        except Exception as e:
            print(f'Error occurred while adding new patient: {e}.')
    
    def delete_patient(self, patient_id=None) -> None:
        """Usuwa pacjenta z bazy danych"""
        if not patient_id:
            patient_id = input('Enter patient ID to delete: ')
        try:
            self.cursor.execute('''
            DELETE FROM new_patients 
            WHERE id = %s
            ''', (patient_id,))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                print(f'Patient with ID {patient_id} deleted.')
            else:
                print(f'No patient found with ID {patient_id}.')
        except Exception as e:
            print(f'Error occurred while deleting patient: {e}.')
    
    def alter_patient_details_in_db(self, patient_id=None) -> None:
        """Modyfikuje dane pacjenta w bazie danych"""
        if not patient_id:
            patient_id = input('Enter patient ID to modify: ')
        
        # Najpierw sprawdź, czy pacjent istnieje
        try:
            self.cursor.execute('SELECT * FROM new_patients WHERE id = %s', (patient_id,))
            patient = self.cursor.fetchone()
            
            if not patient:
                print(f'No patient found with ID {patient_id}.')
                return
                
            # Pobierz nowe dane
            print("Leave blank if you don't want to change.")
            new_first_name = input(f'Current first name: {patient[1]}. New first name: ')
            new_last_name = input(f'Current last name: {patient[2]}. New last name: ')
            new_email = input(f'Current email: {patient[3]}. New email: ')
            
            # Użyj istniejących danych, jeśli użytkownik nie wprowadził nowych
            first_name = new_first_name if new_first_name else patient[1]
            last_name = new_last_name if new_last_name else patient[2]
            email = new_email if new_email else patient[3]
            
            # Aktualizuj dane
            self.cursor.execute('''
            UPDATE new_patients 
            SET first_name = %s, last_name = %s, email = %s 
            WHERE id = %s
            ''', (first_name, last_name, email, patient_id))
            
            self.connection.commit()
            print('Patient details updated.')
        except Exception as e:
            print(f'Error occurred while updating patient: {e}.')
    
    def print_patient(self, patient_id=None) -> None:
        """Wyświetla dane pacjenta"""
        if not patient_id:
            patient_id = input('Enter patient ID to display: ')
        
        try:
            self.cursor.execute('SELECT * FROM new_patients WHERE id = %s', (patient_id,))
            patient = self.cursor.fetchone()
            
            if patient:
                print("\n--- Patient Details ---")
                print(f"ID: {patient[0]}")
                print(f"First name: {patient[1]}")
                print(f"Last name: {patient[2]}")
                print(f"Email: {patient[3]}")
                print("---------------------\n")
            else:
                print(f'No patient found with ID {patient_id}.')
        except Exception as e:
            print(f'Error occurred while retrieving patient data: {e}.')
    
    def view_patient_medicines_list(self, patient_id=None) -> None:
        """Wyświetla listę leków przypisanych pacjentowi"""
        if not patient_id:
            patient_id = input('Enter patient ID to view medicines: ')
        
        try:
            # Sprawdź czy pacjent istnieje
            self.cursor.execute('SELECT * FROM new_patients WHERE id = %s', (patient_id,))
            patient = self.cursor.fetchone()
            
            if not patient:
                print(f'No patient found with ID {patient_id}.')
                return
                
            # Pobierz leki pacjenta (zakładając, że masz odpowiednią tabelę)
            self.cursor.execute('''
            SELECT m.id, m.name, m.dosage, m.instructions
            FROM medicines m
            JOIN patient_medicines pm ON m.id = pm.medicine_id
            WHERE pm.patient_id = %s
            ''', (patient_id,))
            
            medicines = self.cursor.fetchall()
            
            if medicines:
                print(f"\n--- Medicines for {patient[1]} {patient[2]} ---")
                for med in medicines:
                    print(f"ID: {med[0]}")
                    print(f"Name: {med[1]}")
                    print(f"Dosage: {med[2]}")
                    print(f"Instructions: {med[3]}")
                    print("----------")
            else:
                print(f'No medicines assigned to patient with ID {patient_id}.')
        except Exception as e:
            print(f'Error occurred while retrieving patient medicines: {e}.')

#     def run(self, choice_option):
#         '''runs funkction chosen by user in menu options'''
#         # # to z poziomu menu - wybór obiektu
#         # self.display_menu()
#         # self.choose_menu_object()
#         # # to z poziomu menu patient:
#         # self.display_options()
#         # choice_option = self.choose_option() 
# # dotad działa - wywolywane w main
#         method_name = self.functions.get(choice_option) 
#         if not method_name:
#             print("This option is not implemented.")
#             return
#         method = getattr(self, method_name, None)
#         if method:
#             connection, cursor = connect_to_database()
#             sig = inspect.signature(method)
#             num_params = len(sig.parameters)
#             try:
#                 if num_params == 1:
#                     method() #(self)
#                 elif num_params == 2: #(self, cursor)
#                     method(cursor)
#                 elif num_params == 3: #(self, connection, cursor)
#                     method(connection, cursor)
#                 else:
#                     print('Unsupported method')
#             except Exception as e:
#                 print(f'error during method execution: {e}')
#         else:
#             print(f"Function '{method_name}' not found.")

    # def run(self, choice_option):
    #     '''runs funkction chosen by user in menu options'''
    #     connection, cursor = connect_to_database()
        # method_name = self.functions.get(choice_option) 
    #     method = getattr(self, method_name, None)
    #     try:
    #         method()
    #     except TypeError:
    #         try:
    #             method(cursor)
    #         except TypeError:
    #             method(connection, cursor)
    #         except Error as e:
    #             print(f'Error: {e}')

    #     # Jeśli metoda wymaga połączenia z bazą danych:
    #     if ('connection', 'cursor') in method.__code__.co_varnames:
    #         method(connection, cursor)
    #     elif 'cursor' in method.__code__.co_varnames:
    #         method(cursor,)
    #     else:
    #         method()


    # @classmethod
    # def execute_patient_menu(cls, self):
    #     cls.display_options()
    #     option = cls.choose_option()
    #     method_name = self.function.get(option)
    #     print(method_name)