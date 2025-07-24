from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from datetime import date, datetime, timedelta
import mysql.connector
import random
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "medtrack"
}

db = mysql.connector.connect(**db_config)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session["user"] = user[1]  # name
            session["user_id"] = user[0]  # user_id
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        db.commit()
        session["user"] = name
        return redirect("/dashboard")

    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        username = session["user"]
        user_id = session.get("user_id")

        cursor.execute("""
            DELETE FROM tasks 
            WHERE completed = TRUE AND task_date < CURDATE() AND user_id = %s
        """, (user_id,))
        db.commit()

        cursor.execute("SELECT * FROM medicines WHERE user_id = %s", (user_id,))
        medicines = cursor.fetchall()

        medicine_data = []
        today = date.today()
        today_meds = []

        for row in medicines:
            med = {
                'id': row[0],
                'user_id': row[1],
                'name': row[2],
                'dosage': row[3],
                'start_date': row[5] if isinstance(row[5], date) else row[5].date(),
                'end_date': row[6] if isinstance(row[6], date) else row[6].date(),
                'time': row[4]
            }

            medicine_data.append(med)

            if med['start_date'] <= today <= med['end_date']:
                today_meds.append(med)

        cursor.execute("SELECT id, title, time, completed, task_date FROM tasks WHERE user_id = %s", (user_id,))
        task_rows = cursor.fetchall()

        tasks = []
        for t in task_rows:
            tasks.append({
                "id": t[0],
                "title": t[1],
                "time": t[2],
                "completed": t[3],
                "task_date": t[4]
            })

        quotes = [
            "Every dose you take brings you one step closer to better health!",
            "Small steps every day lead to big results.",
            "Health is the first wealth.",
            "Stay strong, the journey is worth it!",
            "Your consistency is your strength.",
            "Healing is a process—keep going!"
        ]

        motivation_quote = random.choice(quotes)

        return render_template("dashboard.html", 
            username=username, 
            medicines=medicine_data, 
            today_medicines=today_meds, 
            tasks=tasks,
            motivation_quote=motivation_quote
        )

    return redirect("/")

@app.route('/add-medicine', methods=['GET', 'POST'])
def add_medicine():
    if "user" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == 'POST':
        name = request.form['name']
        dosage = request.form['dosage']
        time = request.form['time']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cursor.execute("""
            INSERT INTO medicines (user_id, name, dosage, time, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, name, dosage, time, start_date, end_date))

        db.commit()
        return redirect('/dashboard')

    return render_template('add_medicine.html')

@app.route("/edit/<int:med_id>", methods=["GET", "POST"])
def edit_medicine(med_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        dosage = request.form["dosage"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        time = request.form["time"]

        cursor.execute("""
            UPDATE medicines 
            SET name = %s, dosage = %s, start_date = %s, end_date = %s, time = %s
            WHERE id = %s AND user_id = %s
        """, (name, dosage, start_date, end_date, time, med_id, user_id))

        db.commit()
        return redirect("/dashboard")

    cursor.execute("SELECT * FROM medicines WHERE id = %s AND user_id = %s", (med_id, user_id))
    medicine = cursor.fetchone()

    if not medicine:
        return "Medicine not found", 404

    medicine_data = {
        "id": medicine[0],
        "user_id": medicine[1],
        "name": medicine[2],
        "dosage": medicine[3],
        "time": medicine[4],
        "start_date": medicine[5],
        "end_date": medicine[6]
    }

    return render_template("edit_medicine.html", medicine=medicine_data)

@app.route("/delete/<int:med_id>")
def delete_medicine(med_id):
    if "user" not in session:
        return redirect("/login")

    user_id = session.get("user_id")

    cursor.execute("DELETE FROM medicines WHERE id = %s AND user_id = %s", (med_id, user_id))
    db.commit()
    return redirect("/dashboard")

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if "user" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == 'POST':
        title = request.form['title']
        time = request.form['time']
        task_date = request.form['task_date']

        cursor.execute("""
            INSERT INTO tasks (user_id, title, time, task_date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, title, time, task_date))
        db.commit()
        return redirect("/dashboard")

    return render_template("add_task.html")

@app.route('/edit-task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    if "user" not in session:
        return redirect("/login")

    cursor.execute("SELECT title, time FROM tasks WHERE id = %s", (id,))
    task = cursor.fetchone()

    if not task:
        return "Task not found"

    if request.method == "POST":
        new_title = request.form["title"]
        new_time = request.form["time"]

        cursor.execute("""
            UPDATE tasks
            SET title = %s, time = %s
            WHERE id = %s
        """, (new_title, new_time, id))
        db.commit()
        return redirect("/dashboard")

    task_data = {"title": task[0], "time": task[1]}
    return render_template("edit_task.html", task=task_data)

@app.route("/delete-task/<int:id>")
def delete_task(id):
    cursor.execute("DELETE FROM tasks WHERE id = %s", (id,))
    db.commit()
    return redirect("/dashboard")

@app.route("/complete-task/<int:id>", methods=['POST'])
def complete_task(id):
    cursor.execute("UPDATE tasks SET completed = NOT completed WHERE id = %s", (id,))
    db.commit()
    return '', 204

@app.route('/doctor')
def doctor():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctor_details WHERE user_id = %s", (user_id,))
    doctor = cursor.fetchone()

    return render_template("doctor.html", doctor=doctor)

@app.route('/save_doctor', methods=['POST'])
def save_doctor():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    data = (
        request.form['doctor_name'],
        request.form['specialization'],
        request.form['phone'],
        request.form['clinic_name'],
        request.form['clinic_address'],
        request.form['next_appointment_date'],
        user_id
    )

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctor_details WHERE user_id = %s", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE doctor_details
            SET doctor_name=%s, specialization=%s, phone=%s,
                clinic_name=%s, clinic_address=%s, next_appointment_date=%s
            WHERE user_id=%s
        """, data)
    else:
        cursor.execute("""
            INSERT INTO doctor_details 
            (doctor_name, specialization, phone, clinic_name, clinic_address, next_appointment_date, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)

    db.commit()
    return redirect('/doctor')

@app.route("/appointments", methods=["GET"])
def appointments():
    if "user_id" not in session:
        return redirect("/login")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT speciality FROM doctor_list")
    specialities = [row["speciality"] for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM doctor_list")
    doctors = cursor.fetchall()

    return render_template("appointments.html", doctors=doctors, specialities=specialities)

@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    doctor_name = request.form.get("doctor_name")

    # Generate random date within the next 7 days
    days_ahead = random.randint(1, 7)
    appointment_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%B %d, %Y")

    flash(f"✅ Appointment booked with Dr. {doctor_name} on {appointment_date}!", "success")
    return redirect(url_for("appointments"))

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    return render_template("profile.html", user=user)

@app.route("/save_user", methods=["POST"])
def save_user():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    name = request.form.get("name")
    email = request.form.get("email")
    age = request.form.get("age") or None
    gender = request.form.get("gender") or None
    blood_group = request.form.get("blood_group") or None
    medical_conditions = request.form.get("medical_conditions") or None
    smoking = True if request.form.get("smoking") == "on" else False
    drinking = True if request.form.get("drinking") == "on" else False

    cursor = db.cursor()
    cursor.execute("""
        UPDATE users SET
            name=%s, email=%s, age=%s, gender=%s, blood_group=%s,
            medical_conditions=%s, smoking=%s, drinking=%s
        WHERE id=%s
    """, (name, email, age, gender, blood_group, medical_conditions, smoking, drinking, user_id))

    db.commit()
    return redirect("/profile")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)