from flask import Blueprint, render_template, request

from menu.medicine_menu import MedicineMenu
from repos.medicine_repo import MedicineDB
from models.models import Medicine

medicine_bp = Blueprint('medicine', __name__, url_prefix='/medicine')

@medicine_bp.route("/")
def medicine():
    return render_template("medicine_menu.html")

@medicine_bp.route("/add_medicine", methods=["GET", "POST"])
def add_medicine():
    if request.method == "POST":
        med_name = request.form.get("med_name")
        dosage = request.form.get("dosage")
        quantity = request.form.get("quantity")
        description = request.form.get("description")
        medicine_db = MedicineDB()
        result = medicine_db.add_medicine_to_database(med_name, dosage, quantity, description)
        return render_template("result.html", title="Adding medicine", result=result)
    return render_template("add_medicine_form.html")

@medicine_bp.route("/delete_medicine", methods=["GET", "POST"])
def delete_medicine():
    if request.method == "POST":
        confirmation = request.form.get("confirmation")
        if not confirmation:
            result = 'Medicine cannot be deleted without confirmation.'
            return render_template("result.html", title="Deleting medicine", result=result)
        med_id = request.form.get("med_id")
        med_name = request.form.get("med_name") # added
        medicine_db = MedicineDB()
        if not med_id:
            medicine = medicine_db.get_medicine(med_name)
            try:
                med_id = medicine.med_id
            except AttributeError:
                result = "Medicine not found."
        result = medicine_db.delete_medicine(med_id)
        return render_template("result.html", title="Deleting medicine", result=result)
    return render_template("get_delete_med_id_and_name_form.html")
    pass # w trakcie

@medicine_bp.route("/view_medicine", methods=["GET", "POST"])
def view_medicine():
    if request.method == "POST":
        med_id = request.form.get("med_id")
        med_name = request.form.get("med_name")
        medicine_db = MedicineDB()
        if not med_id:
            medicine = medicine_db.get_medicine(med_name)
        elif not med_name and med_id:
            medicine = medicine_db.get_medicine_by_id(med_id)  
        result = str(medicine)
        return render_template("result.html", title="Medicine view", result=result)
    return render_template("get_med_id_and_name_form.html")
        
        