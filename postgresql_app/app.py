from flask import  Blueprint, Flask, render_template, request
from routes.patient_routes import patient_bp
from routes.medicine_routes import medicine_bp
from routes.prescription_routes import prescription_bp

import os

app = Flask(__name__, template_folder='UI/templates', static_folder='UI/static') # tworze instancje aplikacji,  tworzymy aplikację. __name__ mówi Flaskowi, gdzie szuka plików.

app.register_blueprint(patient_bp)
app.register_blueprint(medicine_bp)
app.register_blueprint(prescription_bp)

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


if __name__ == "__main__":
    app.run(debug=True) # tryb deweloperski: automatyczny reload + błędy pokazują się na stronie.







