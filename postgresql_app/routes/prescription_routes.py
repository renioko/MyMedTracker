from flask import Blueprint, render_template, request

from menu.prescription_menu import PrescriptionMenu
from repos.prescription_repo import PrescriptionDB
from models.models import Prescription


prescription_bp = Blueprint('prescription', __name__, url_prefix='/prescription')

@prescription_bp.route("/")
def prescription():
    return render_template("prescription_menu.html")
