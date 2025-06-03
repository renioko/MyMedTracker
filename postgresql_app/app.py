from flask import  Flask, render_template, request
from menu.patient_menu import PatientMenu
import os

app = Flask(__name__, template_folder='UI/templates') # tworze instancje aplikacji,  tworzymy aplikację. __name__ mówi Flaskowi, gdzie szuka plików.

# dekorator mówi, że ta funkcja obsługuje adres główny (/).
@app.route("/") # tworzę ścieżkę - "jesli wchodzisz na adres...wywołaj funkcję ..."
def home():
    return render_template("home.html") # render_template() – Flask szuka pliku HTML w folderze templates/ i go renderuje.

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/patient")
def patient():
    return render_template("patient_menu.html")

@app.route("/patient/add_patient", methods=["GET", "POST"])
def add_patient():
    # username, email, password, first_name, last_name, role_id, emergency_contact, medical_info
    if request.method == "POST":
        patient_details = (
            request.form.get("username"), #
            request.form.get("email"),
            request.form.get("password"), #
            request.form.get("role_id"), #
            request.form.get("first_name"),
            request.form.get("last_name"),
            request.form.get("emergency_contact"), #
            request.form.get("medical_info") #
        )
        patient_menu = PatientMenu(0, auto_run=False)
        result = patient_menu.menu_add_patient(patient_details, verbose=False)
        # result = patient_menu.add_patient_and_user_one_connection(patient_details, verbose=False)
        return render_template("result.html", title='Adding patient', result=result)
    return render_template("add_patient_form.html")

@app.route("/patient/view_patient", methods=["GET", "POST"])
def view_patient():
    if request.method == "POST":
        pat_id = (
            request.form.get("pat_id")
        )
        patient_menu = PatientMenu(0, auto_run=False)
        result = patient_menu.get_patient_view(pat_id)
        return render_template("result.html", title="Patient view:", result=result)
    return render_template("get_patient_id_form.html")

@app.route("/patient/alter_patient_details", methods=["GET", "POST"]) 
# not restful = should be PATCH or PUT
def alter_patient_details():
    if request.method == "POST":
        user_id = (request.form.get("user_id"))
        column_to_change = (request.form.get("column_to_change"))
        new_details = (request.form.get("new_details"))
        patient_menu = PatientMenu(0, auto_run=False)
        result = patient_menu.alter_patient_details_in_db(user_id, column_to_change, new_details, verbose=False)
        # result = patient_menu.menu_alter_patient_details()
        return render_template("result.html", title="Patient view", result=result)
    return render_template("get_patient_details_to_change.html")

@app.route("/patient/delete_patient", methods=["GET", "POST"])
def delete_patient():
    if request.method == "POST":
        user_id = (request.form.get("user_id"))
        confirmation = (request.form.get("confirmation"))
        if not confirmation:
            result = 'If you want to delete user, confirmation is needed'
        else:
            try: 
                user_id = int(user_id)
            except ValueError:
                result = "Invalid user id."
        patient_menu = PatientMenu(0, auto_run=False)
        # result = patient_menu.menu_delete_patient_user(user_id, confirmation)
        result = patient_menu.delete_user(user_id, confirmation)
        return render_template("result.html", title="Delete patient", result=result)
    return render_template("get_patient_id_and_confirmation_to_delete_form.html")




@app.route("/medicine")
def medicine():
    return render_template("medicine_menu.html")

@app.route("/prescription")
def prescription():
    return render_template("prescription_menu.html")



if __name__ == "__main__":
    app.run(debug=True) # tryb deweloperski: automatyczny reload + błędy pokazują się na stronie.

