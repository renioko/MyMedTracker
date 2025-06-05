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
    pass
