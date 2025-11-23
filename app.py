from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
from datetime import datetime
from triage import calculate_priority

app = Flask(__name__)
app.secret_key = "super-secret-key-change-this"   # change for production


def get_recommendation(notes):
    if not notes:
        return "No recommendation"

    notes = notes.lower()

    recommendations = {
        "cold": "Prescribe antihistamines and rest.",
        "fever": "Give paracetamol and monitor temperature.",
        "fracture": "Immobilize limb and send for X-ray.",
        "bleeding": "Apply pressure dressing and evaluate for transfusion.",
        "infection": "Start IV antibiotics immediately.",
        "asthma": "Use nebulizer bronchodilator and monitor breathing.",
        "heart attack": "Administer aspirin and prepare ECG & oxygen.",
        "burn": "Cool area with saline and apply sterile burn dressing.",
        "stroke": "Immediate CT scan and stroke protocol activation.",
        "covid": "Isolate patient, oxygen support, antiviral therapy."
    }

    for keyword, response in recommendations.items():
        if keyword in notes:
            return response

    return "No recommendation available"



# ------------- DB HELPERS -------------
def get_db():
    conn = sqlite3.connect("emergency.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            hr INTEGER,
            bp INTEGER,
            oxygen INTEGER,
            temp REAL,
            priority TEXT,
            time_of_death TEXT,
            notes TEXT,
            surgery_required INTEGER
        )
    """)

    # Add missing columns if existing database
    try: cur.execute("ALTER TABLE patients ADD COLUMN notes TEXT")
    except: pass
    try: cur.execute("ALTER TABLE patients ADD COLUMN surgery_required INTEGER DEFAULT 0")
    except: pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)

    cur.execute("SELECT * FROM users WHERE username='admin'")
    if cur.fetchone() is None:
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                    ("admin", password_hash))

    conn.commit()
    conn.close()
    
init_db()
print(">>> DATABASE INIT CREATED <<<")





# ------------- LOGIN REQUIRED DECORATOR -------------
def login_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


# ------------- ROUTES -------------
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == user["password_hash"]:
                session["user"] = username
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        name = request.form.get("name")
        hr = int(request.form.get("hr"))
        bp = int(request.form.get("bp"))
        oxygen = int(request.form.get("oxygen"))
        temp = float(request.form.get("temp"))
        notes = request.form.get("notes")
        surgery_required = 1 if request.form.get("surgery_required") == "on" else 0

        priority = calculate_priority(hr, bp, oxygen, temp)

        time_of_death = (
            datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            if priority == "Deceased"
            else None
        )

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO patients(name, hr, bp, oxygen, temp, priority, time_of_death, notes, surgery_required)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (name, hr, bp, oxygen, temp, priority, time_of_death, notes, surgery_required))
        conn.commit()
        conn.close()

        flash("Patient added successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("index.html")



@app.route("/edit/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cur.fetchone()

    if request.method == "POST":
        name = request.form.get("name")
        hr = int(request.form.get("hr"))
        bp = int(request.form.get("bp"))
        oxygen = int(request.form.get("oxygen"))
        temp = float(request.form.get("temp"))

        priority = calculate_priority(hr, bp, oxygen, temp)

        # Deceased timestamp handling
        time_of_death = patient["time_of_death"]
        if priority == "Deceased" and patient["priority"] != "Deceased":
            time_of_death = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        elif priority != "Deceased":
            time_of_death = None

        # NEW FIELDS
        notes = request.form.get("notes")
        surgery_required = 1 if request.form.get("surgery_required") == "on" else 0

        cur.execute("""
            UPDATE patients
            SET name=?, hr=?, bp=?, oxygen=?, temp=?, priority=?, time_of_death=?, notes=?, surgery_required=?
            WHERE id=?
        """, (name, hr, bp, oxygen, temp, priority, time_of_death, notes, surgery_required, patient_id))

        conn.commit()
        conn.close()

        flash("Patient updated successfully", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("edit.html", patient=patient)



@app.route("/delete/<int:patient_id>")
@login_required
def delete_patient(patient_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()
    flash("Patient removed.", "info")
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    # One unified list; Deceased first, then Critical, High, Medium, Low
    cur.execute(
        """
        SELECT * FROM patients
        ORDER BY
            CASE priority
                WHEN 'Deceased' THEN 0
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            id DESC
        """
    )
    patients = cur.fetchall()

    patients = [dict(row) for row in patients]  # Convert rows to editable dicts

    for p in patients:
        p["recommendation"] = get_recommendation(p.get("notes"))


    # Analytics data
    cur.execute("SELECT priority, COUNT(*) AS count FROM patients GROUP BY priority")
    raw = cur.fetchall()
    priorities = [r["priority"] for r in raw]
    counts = [r["count"] for r in raw]


    conn.close()

    return render_template(
        "dashboard.html",
        patients=patients,
        priorities=priorities,
        counts=counts,
    )


if __name__ == "__main__":
    app.run(debug=True)
