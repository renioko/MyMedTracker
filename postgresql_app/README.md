# MyMedTracker

**MyMedTracker** is a medical tracking application designed to manage patients, medicines, and prescriptions. It allows healthcare providers to add, edit, and view patient records and their assigned medications. The backend is powered by PostgreSQL, while the web interface is built using Flask.

## 🔧 Features

- Add, update, and delete patient records
- View list of medicines assigned to patients
- Assign medicines to specific patients
- PostgreSQL database support
- Web-based interface using Flask
- Object-oriented architecture with clear class structure

## 🗃️ Project Structure
MyMedTracker/

│
├──config/
│ ├── config_file.py
│
├── menu/ # Menu logic and interface classes
│ ├── main_menu.py # tMenu class
│ ├── medicine_menu.py # MedicineMenu class
│ ├── patient_menu.py # PatientMenu class
│ ├── prescription_menu.py # PrescriptionMenu class
│
├──models/
│ ├── models.py # classes: Medicine, Patient, Prescription
│
├──repos/
│ ├── medicine_repo.py
│ ├── patient_medicine_view_repo.py
│ ├── patient_repo.py
│ ├── prescription_repo.py
│
├── UI/ # HTML templates and static files
│ ├── templates/ # Jinja2 template files (e.g., base.html, menu.html)
│ ├── static/ # JCSS template files (e.g.style.css)
│
├── app.py # Main Flask application
├── database_connection.py  # PostgreSQL database handling
├── main.py
├── requirements.txt # List of dependencies
├── README.md # This file
├── run.py (will be useful for testing)
└── utils.py

## ▶️ Getting Started

1. Create and activate a virtual environment:
   ```bash'''
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows

2. Install dependencies:

'''bash'''
pip install -r requirements.txt

1. Run the application:

'''bash'''
flask run

🧠 Requirements
- Python 3.9+

- PostgreSQL

- Flask

- psycopg2

📌 Project Status
The project is under active development. Some features may still be in progress.

📄 License
This project is licensed under the MIT License.

🩺 MyMedTracker — Manage health with clarity and control!