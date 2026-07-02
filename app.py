from flask import Flask, render_template, request, redirect
import sqlite3


import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("API Key:", os.getenv("GEMINI_API_KEY"))   # Temporary for testing

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")



import re
from datetime import datetime
 

app = Flask(__name__)
# model = joblib.load("health_model.pkl")

# Create Database and Table

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        dob TEXT NOT NULL,
        email TEXT NOT NULL,
        glucose REAL,
        haemoglobin REAL,
        cholesterol REAL,
        remarks TEXT
    )
    """)


    conn.commit()
    conn.close()

# AI Health Prediction

def predict_health(glucose, haemoglobin, cholesterol):

    prompt = f"""
You are a medical assistant.

Patient values:
Glucose: {glucose}
Haemoglobin: {haemoglobin}
Cholesterol: {cholesterol}

If all values are within normal range, reply:
"Normal - No significant health risk detected."

Otherwise, mention one possible health risk in one short sentence.
"""
    response = model.generate_content(prompt)

    return response.text.strip()


# Home Page

@app.route('/')
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()

    return render_template("index.html", patients=patients)


# Add Patient
@app.route('/add', methods=['POST'])
def add_patient():

    full_name = request.form['full_name']
    dob = request.form['dob']
    email = request.form['email']
    glucose = request.form['glucose']
    haemoglobin = request.form['haemoglobin']
    cholesterol = request.form['cholesterol']

    # Email Validation
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_pattern, email):
        return "Invalid Email Address"

    # Future DOB Validation
    dob_date = datetime.strptime(dob, "%d/%m/%Y").date()

    if dob_date > datetime.today().date():
        return "Date of Birth cannot be in the future"

    # AI Prediction
    remarks = predict_health(glucose, haemoglobin, cholesterol)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients
    (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks
    ))

    conn.commit()
    conn.close()

    return redirect('/')

# Edit Patient

@app.route('/edit/<int:id>')
def edit_patient(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = list(cursor.fetchone())

    patient[2] = datetime.strptime(patient[2], "%d/%m/%Y").strftime("%Y-%m-%d")

    return render_template("edit_patient.html", patient=patient)


# Update Patient

@app.route('/update/<int:id>', methods=['POST'])
def update_patient(id):

    full_name = request.form['full_name']
    dob = request.form['dob']
    email = request.form['email']
    glucose = request.form['glucose']
    haemoglobin = request.form['haemoglobin']
    cholesterol = request.form['cholesterol']


    # Email Validation
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(email_pattern, email):
        return "Invalid Email Address"

    # Future DOB Validation
    dob_date = datetime.strptime(dob, "%d/%m/%Y").date()

    if dob_date > datetime.today().date():
        return "Date of Birth cannot be in the future"
    
    

    remarks = predict_health(glucose, haemoglobin, cholesterol)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE patients
    SET
        full_name=?,
        dob=?,
        email=?,
        glucose=?,
        haemoglobin=?,
        cholesterol=?,
        remarks=?
    WHERE id=?
    """,
    (
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks,
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/')


# Delete Patient

@app.route('/delete/<int:id>')
def delete_patient(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# Run Application

if __name__ == '__main__':
    init_db()
    app.run(debug=True)