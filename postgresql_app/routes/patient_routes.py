from flask import Blueprint, render_template, request

from menu.patient_menu import PatientMenu
from repos.patient_repo import PatientDB
from repos.patient_medicine_view_repo import Patient_Medicines_ViewDB

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

# @patient_bp.route("/result")
# def result():
#     return render_template("result.html")

@patient_bp.route("/")
def patient():
    return render_template("patient_menu.html")

@patient_bp.route("/patient/add_patient", methods=["GET", "POST"])
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

@patient_bp.route("/patient/view_patient", methods=["GET", "POST"])
def view_patient():
    if request.method == "POST":
        pat_id = (
            request.form.get("pat_id")
        )
        patient_menu = PatientMenu(0, auto_run=False)
        result = patient_menu.get_patient_view(pat_id)
        return render_template("result.html", title="Patient view:", result=result)
    return render_template("get_patient_id_form.html")

@patient_bp.route("/patient/alter_patient_details", methods=["GET", "POST"]) 
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

@patient_bp.route("/patient/delete_patient", methods=["GET", "POST"])
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

@patient_bp.route("/patient/view_patient_medicines", methods=["GET", "POST"])
def view_patient_medicines():
    if request.method == "POST":
        user_id = (request.form.get("user_id"))
        # pat_id = (request.form.get("pat_id"))

        try:
            user_id = int(user_id)
        except ValueError:
            return "incorrect user id."
        patient_db = PatientDB()
        pat_id = patient_db.get_pat_id_from_user_id(user_id)

        if pat_id:
            patient_medicines_view = Patient_Medicines_ViewDB()
            patient_medicines_list = patient_medicines_view.get_patient_medicine_view(pat_id)
            result = patient_medicines_view.format_medicines_for_web(patient_medicines_list)
            return render_template("result.html", title="Patient medicines:", result=result)
        else:
            return "Patient not found."
    return render_template("get_user_id_form.html") # zmienic forme by pacjent mógł podac tez pat_id
        
