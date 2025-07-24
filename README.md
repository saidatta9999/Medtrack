
# 💊 MedTrack – Cloud-Based Patient Medication & Task Tracker

**MedTrack** is a cloud-integrated, full-stack medication and task tracking system designed for patients, caretakers, and healthcare professionals. It allows users to track medicines, tasks, appointments, and manage personal and doctor information seamlessly through a modern, interactive dashboard.

---

## 📌 Features

- 🧾 User authentication (Sign up/Login)
- 🧬 Add and manage medications with reminder times
- ✅ Track and update daily medication & health-related tasks
- 📅 Appointment scheduling with doctor info
- 📄 Dynamic user profile management
- 🛎️ Email reminders via AWS SNS (cloud version)
- ☁️ AWS DynamoDB and S3 integration (cloud version)
- 📊 Dashboard with daily stats, upcoming reminders, and streaks

---

## 🛠️ Tech Stack

| Component     | Technology              |
|---------------|--------------------------|
| Backend       | Flask (Python)           |
| Frontend      | HTML, CSS, JavaScript, Tailwind |
| Database      | MySQL (Local) / DynamoDB (AWS) |
| Notification  | AWS SNS (Email alerts)   |
| ORM/Driver    | `mysql-connector-python` |
| Hosting       | AWS EC2 (Linux Ubuntu)   |

---

## ⚙️ Project Structure

```
medtrack/
│
├── templates/            # HTML files (login, dashboard, add_medicine, tasks, doctor, etc.)
│
├── app.py                # Flask local app (MySQL)
├── awsapp.py             # Flask cloud app (DynamoDB + SNS)
├── tables.sql            # MySQL schema (table structures only)
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
```

---

## 🧑‍💻 How to Run (Local Version)

### 1. Clone the Repository
```bash
git clone https://github.com/saidatta9999/Medtrack.git
cd Medtrack
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up MySQL
```sql
CREATE DATABASE medtrack;
USE medtrack;
-- Then run the schema
SOURCE tables.sql;
```

### 4. Run the Flask App
```bash
python app.py
```
Visit: [http://localhost:5000](http://localhost:5000)

---

## 🧾 Database Schema

### users Table
| Column     | Type          | Description              |
|------------|---------------|--------------------------|
| id         | INT (PK)      | Auto increment ID        |
| email      | VARCHAR(100)  | User email               |
| password   | VARCHAR(100)  | User password (hashed)   |
| name       | VARCHAR(100)  | Full name                |
| age        | INT           | Age                      |
| gender     | VARCHAR(10)   | Gender                   |
| address    | VARCHAR(255)  | User address             |
| contact    | VARCHAR(20)   | Contact number           |

### doctor_list Table
| Column     | Type          | Description              |
|------------|---------------|--------------------------|
| id         | INT (PK)      | Doctor ID                |
| name       | VARCHAR(100)  | Doctor Name              |
| specialization | VARCHAR(100) | Field of Expertise     |
| location   | VARCHAR(100)  | Doctor Location          |

### doctor_details Table
| Column     | Type          | Description              |
|------------|---------------|--------------------------|
| id         | INT (PK)      | Record ID                |
| user_id    | INT           | Linked to users table    |
| doctor_id  | INT           | Linked to doctor_list    |
| date       | DATE          | Appointment date         |
| notes      | TEXT          | Visit notes              |

### medicines Table
| Column     | Type          | Description              |
|------------|---------------|--------------------------|
| id         | INT (PK)      | Medicine ID              |
| user_id    | INT           | Linked to users table    |
| name       | VARCHAR(100)  | Medicine Name            |
| dosage     | VARCHAR(100)  | Dosage details           |
| time       | TIME          | Reminder time            |
| date_added | DATETIME      | When medicine was added  |

### tasks Table
| Column     | Type          | Description              |
|------------|---------------|--------------------------|
| id         | INT (PK)      | Task ID                  |
| user_id    | INT           | Linked to users table    |
| description| TEXT          | Task details             |
| task_time  | TIME          | Time of task             |
| status     | VARCHAR(20)   | Pending/Completed        |

---

## 📦 Requirements

```
Flask
mysql-connector-python
boto3
werkzeug
uuid
```

---

## ☁️ Cloud Deployment

For AWS version (`awsapp.py`), ensure you set up:

- AWS DynamoDB tables for `users`, `medicines`, `tasks`, `doctor_list`, etc.
- AWS SNS topic for email notifications
- Proper IAM roles and credentials

---

## 🤝 Contributing

Feel free to fork and submit pull requests or report issues.

---

## 📝 License

This project is under the MIT License.
