from flask import Blueprint, session,render_template, request, redirect, url_for

from menu.prescription_menu import PrescriptionMenu
from repos.prescription_repo import PrescriptionDB
from models.models import Prescription
from datetime import datetime


prescription_bp = Blueprint('prescription', __name__, url_prefix='/prescription')

@prescription_bp.route("/")
def prescription():
    return render_template("prescription_menu.html")

# @prescription_bp.route("/add_prescription", methods = ["GET", "POST"])
# def add_prescription():
#     presription_db = PrescriptionDB()
#     if request.method == "POST":
#         pat_id = request.form.get("pat_id")
#         issue_date = request.form.get("issue_date")
#         prescription_details = (pat_id, issue_date)
#         meds = []
#         while True:
#             med_name = request.form.get("med_name")
#             meds.append(med_name)
#             no_more_meds = request.form.get("no_more_meds")
#             if no_more_meds:
#                 break
#             return render_template("get_med_name_form.html")
#         result = presription_db.add_prescription_to_database(meds, prescription_details)
#         return render_template("result.html", title="Prescription added", result=result)
#     return render_template("get_pat_id_date_form.html")

# @prescription_bp.route("add_medicines_rescription")
# def add_medicines_prescription():
#         if request.method == "POST":
#             meds = []
#             while True:
#                 med_name = request.form.get("med_name")
#                 meds.append(med_name)
#                 no_more_meds = request.form.get("no_more_meds")
#                 if no_more_meds:
#                     break
#             return render_template("get_med_name_form.html")
@prescription_bp.route("/add_prescription", methods=["GET", "POST"])
def add_prescription():
    if request.method == "POST":
        session["pat_id"] = request.form.get("pat_id")
        session["issue_date"] = request.form.get("issue_date")
        session["medicines"] = []  # Start empty list
        return redirect(url_for("prescription.add_medicines_prescription"))
    return render_template("get_pat_id_date_form.html")


@prescription_bp.route("/add_medicines_prescription", methods=["GET", "POST"])
def add_medicines_prescription():
    if request.method == "POST":
        med_name = request.form.get("med_name")
        if med_name:
            medicines = session.get("medicines", [])
            medicines.append(med_name)
            session["medicines"] = medicines  # Save back

        if request.form.get("no_more_meds"):
            pat_id = session.get("pat_id")
            issue_date = session.get("issue_date")
            meds = session.get("medicines", [])

            # Save to DB
            prescription_db = PrescriptionDB()
            

            med_ids = [prescription_db.get_medicine_id_for_prescription(med) for med in meds]
            result = prescription_db.add_prescription_to_database(med_ids, (pat_id, issue_date))

            # Clear session
            session.pop("pat_id", None)
            session.pop("issue_date", None)
            session.pop("medicines", None)

            view= prescription_db.get_prescription_view(pat_id) # nie działa
            if not view:
                view = ''
            result = result + ' \n' + view

            return render_template("result.html", title="Prescription added", result=result)
            # return redirect(url_for("prescription.view_prescription"))

    return render_template("get_med_name_form.html")

@prescription_bp.route("/view_prescription", methods = ["GET", "POST"])
def view_prescription():
    if request.method == "POST":
        presc_id = request.form.get("presc_id")
        prescription_db = PrescriptionDB()
        result = prescription_db.get_prescription_view(presc_id)
        return render_template("result.html", title="Prescription view", result=result)
    return render_template("get_presc_id_form.html")

