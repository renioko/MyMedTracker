# run.py
import sys
import os
from datetime import date

# Dodaj bieżący katalog do sys.path, aby importy działały
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Przykład: testowanie funkcji z repozytorium
from repos.patient_medicine_view_repo import Patient_Medicines_ViewDB
def main():
    print("Uruchamiam test...")
    # view = Patient_Medicines_ViewDB(0, '', '', 0, '', date.today())
    view = Patient_Medicines_ViewDB()  # Inicjalizacja klasy
    view.view_patient_medicines_list()  # <-- tu wykonujesz test

if __name__ == '__main__':
    main()
