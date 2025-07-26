from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import datetime, date, timedelta
import boto3
import uuid
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# AWS Configuration
region = 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=region)
sns = boto3.client('sns', region_name=region)

# Your SNS Topic ARN
sns_topic_arn = 'arn:aws:sns:us-east-1:253490749648:medtrack-alerts'

# DynamoDB Tables
users_table = dynamodb.Table('medtrack_users')
medicines_table = dynamodb.Table('medtrack_medicines')
tasks_table = dynamodb.Table('medtrack_tasks')
doctor_details_table = dynamodb.Table('medtrack_doctor_details')
doctor_list_table = dynamodb.Table('medtrack_doctor_list')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        users_table.put_item(Item={
            'user_id': user_id,
            'name': name,
            'email': email,
            'password': password
        })

        session['user'] = name
        session['user_id'] = user_id
        session['email'] = email

        # Subscribe to SNS topic
        try:
            sns.subscribe(TopicArn=sns_topic_arn, Protocol='email', Endpoint=email)
        except Exception as e:
            print("SNS subscription failed:", e)

        return redirect('/dashboard')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        response = users_table.scan(
            FilterExpression='email = :email AND password = :pw',
            ExpressionAttributeValues={':email': email, ':pw': password}
        )

        if response['Items']:
            user = response['Items'][0]
            session['user'] = user['name']
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            return redirect('/dashboard')
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    today = str(date.today())

    meds = medicines_table.scan(FilterExpression='user_id = :uid', ExpressionAttributeValues={':uid': user_id})['Items']
    today_meds = [m for m in meds if m['start_date'] <= today <= m['end_date']]

    tasks = tasks_table.scan(FilterExpression='user_id = :uid', ExpressionAttributeValues={':uid': user_id})['Items']

    quotes = [
        "Every dose you take brings you one step closer to better health!",
        "Small steps every day lead to big results.",
        "Health is the first wealth.",
        "Stay strong, the journey is worth it!",
        "Your consistency is your strength.",
        "Healing is a process—keep going!"
    ]

    motivation_quote = random.choice(quotes)

    return render_template("dashboard.html", username=session['user'], medicines=meds,
                           today_medicines=today_meds, tasks=tasks, motivation_quote=motivation_quote)


@app.route("/add-medicine", methods=["GET", "POST"])
def add_medicine():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        medicine_id = str(uuid.uuid4())
        medicine_name = request.form["medicine_name"]
        dose_count = request.form["dose_count"]
        dose_time = request.form["dose_time"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        frequency = request.form["frequency"]

        medications_table.put_item(Item={
            "user_id": session["user_id"],
            "medicine_id": medicine_id,
            "medicine_name": medicine_name,
            "dose_count": dose_count,
            "dose_time": dose_time,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency
        })

        user_id = session["user_id"]
        user_response = users_table.get_item(Key={'user_id': user_id})
        user = user_response.get("Item")

        if user and "email" in user:
            user_email = user["email"]
            try:
                already_subscribed = user.get("sns_subscribed", False)

                if not already_subscribed:
                    sns_client.subscribe(
                        TopicArn=sns_topic_arn,
                        Protocol='email',
                        Endpoint=user_email
                    )
                    print(f"✅ First-time SNS subscription email sent to {user_email}")

                    users_table.update_item(
                        Key={'user_id': user_id},
                        UpdateExpression="set sns_subscribed = :val",
                        ExpressionAttributeValues={':val': True}
                    )
                else:
                    print(f"✅ User {user_email} already subscribed, skipping subscription")

                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Subject="💊 MedTrack - Medicine Added",
                    Message=(
                        f"Hello {user['name']},\n\n"
                        f"You have successfully added the medicine '{medicine_name}' to your MedTrack account.\n"
                        f"Start Date: {start_date}\n"
                        f"End Date: {end_date}\n"
                        f"Dose Time: {dose_time}\n\n"
                        f"Stay healthy!\n– MedTrack"
                    )
                )

            except Exception as e:
                print("❌ SNS Error:", str(e))

        return redirect(url_for("dashboard"))

    return render_template("add_medicine.html")

@app.route('/edit/<string:med_id>', methods=['GET', 'POST'])
def edit_medicine(med_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    if request.method == 'POST':
        medicines_table.put_item(Item={
            'id': med_id,
            'user_id': user_id,
            'name': request.form['name'],
            'dosage': request.form['dosage'],
            'time': request.form['time'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date']
        })
        return redirect('/dashboard')

    med = medicines_table.get_item(Key={'id': med_id})['Item']
    return render_template('edit_medicine.html', medicine=med)


@app.route('/delete/<string:med_id>')
def delete_medicine(med_id):
    if 'user_id' not in session:
        return redirect('/login')

    medicines_table.delete_item(Key={'id': med_id})
    return redirect('/dashboard')


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        task_id = str(uuid.uuid4())
        task = {
            'task_id': task_id,
            'user_id': session['user_id'],
            'title': request.form['title'],
            'time': request.form['time'],
            'task_date': request.form['task_date'],
            'completed': False
        }
        tasks_table.put_item(Item=task)
        return redirect('/dashboard')

    return render_template('add_task.html')


@app.route('/edit-task/<string:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        tasks_table.update_item(
            Key={'user_id': session['user_id'], 'task_id': task_id},
            UpdateExpression='SET title = :t, time = :tm',
            ExpressionAttributeValues={':t': request.form['title'], ':tm': request.form['time']}
        )
        return redirect('/dashboard')

    task = tasks_table.get_item(Key={'user_id': session['user_id'], 'task_id': task_id})['Item']
    return render_template('edit_task.html', task=task)


@app.route('/delete-task/<string:task_id>')
def delete_task(task_id):
    tasks_table.delete_item(Key={'user_id': session['user_id'], 'task_id': task_id})
    return redirect('/dashboard')


@app.route('/complete-task/<string:task_id>', methods=['POST'])
def complete_task(task_id):
    current = tasks_table.get_item(Key={'user_id': session['user_id'], 'task_id': task_id})
    current_completed = current['Item'].get('completed', False)

    tasks_table.update_item(
        Key={'user_id': session['user_id'], 'task_id': task_id},
        UpdateExpression='SET completed = :val',
        ExpressionAttributeValues={':val': not current_completed}
    )

    # Send SNS email
    try:
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject='📌 Task Status Updated',
            Message=f"Hello {session['user']},\n\nA task was marked as {'completed' if not current_completed else 'incomplete'} in your MedTrack dashboard."
        )
    except Exception as e:
        print("SNS publish failed:", e)

    return '', 204


@app.route('/doctor')
def doctor():
    if 'user_id' not in session:
        return redirect('/login')
    doc = doctor_details_table.get_item(Key={'user_id': session['user_id']})
    return render_template('doctor.html', doctor=doc.get('Item'))


@app.route('/save_doctor', methods=['POST'])
def save_doctor():
    if 'user_id' not in session:
        return redirect('/login')

    doctor_details_table.put_item(Item={
        'user_id': session['user_id'],
        'doctor_name': request.form['doctor_name'],
        'specialization': request.form['specialization'],
        'phone': request.form['phone'],
        'clinic_name': request.form['clinic_name'],
        'clinic_address': request.form['clinic_address'],
        'next_appointment_date': request.form['next_appointment_date']
    })
    return redirect('/doctor')


@app.route("/appointments", methods=["GET"])
def appointments():
    if "user_id" not in session:
        return redirect("/login")

    response = doctor_list_table.scan()
    doctors = response.get('Items', [])
    specialities = list(set([doc.get("speciality", "General") for doc in doctors]))

    return render_template("appointments.html", doctors=doctors, specialities=specialities)


@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    doctor_name = request.form.get("doctor_name")
    days_ahead = random.randint(1, 7)
    appointment_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%B %d, %Y")
    flash(f"✅ Appointment booked with Dr. {doctor_name} on {appointment_date}!", "success")
    return redirect(url_for("appointments"))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    prof = users_table.get_item(Key={'user_id': session['user_id']})
    return render_template('profile.html', user=prof.get('Item'))


@app.route('/save_user', methods=['POST'])
def save_user():
    if 'user_id' not in session:
        return redirect('/login')

    users_table.put_item(Item={
        'user_id': session['user_id'],
        'name': request.form['name'],
        'email': request.form['email'],
        'age': request.form.get('age'),
        'gender': request.form.get('gender'),
        'blood_group': request.form.get('blood_group'),
        'medical_conditions': request.form.get('medical_conditions'),
        'smoking': request.form.get('smoking') == 'on',
        'drinking': request.form.get('drinking') == 'on'
    })
    return redirect('/profile')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
