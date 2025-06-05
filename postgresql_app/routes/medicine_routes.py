from flask import Blueprint, render_template, request

from menu.medicine_menu import MedicineMenu
from repos.medicine_repo import MedicineDB
from models.models import Medicine

medicine_bp = Blueprint('medicine', __name__, url_prefix='/medicine')

medicine_bp.route("/medicine")
def medicine():
    render_template("medicine_menu.html")

medicine_bp.route("/medicine/add_medicine", methods=["GET", "POST"])
def add_medicine():
    render_template("add_medicine_form.html")
