-- Create database (optional, if not already created)
CREATE DATABASE IF NOT EXISTS medtrack;
USE medtrack;

-- users table
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    age INT DEFAULT NULL,
    gender VARCHAR(10) DEFAULT NULL,
    blood_group VARCHAR(10) DEFAULT NULL,
    medical_conditions TEXT,
    smoking TINYINT(1) DEFAULT 0,
    drinking TINYINT(1) DEFAULT 0
);

-- list of doctors in locality
CREATE TABLE doctor_list (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) DEFAULT NULL,
    speciality VARCHAR(100) DEFAULT NULL,
    clinic_name VARCHAR(100) DEFAULT NULL,
    location VARCHAR(100) DEFAULT NULL,
    phone VARCHAR(15) DEFAULT NULL
);

-- personal doctor details
CREATE TABLE doctor_details (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    doctor_name VARCHAR(100) DEFAULT NULL,
    specialization VARCHAR(100) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    clinic_name VARCHAR(100) DEFAULT NULL,
    clinic_address TEXT,
    next_appointment_date DATE DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- medications
CREATE TABLE medicines (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    name VARCHAR(100) DEFAULT NULL,
    dosage VARCHAR(50) DEFAULT NULL,
    time TIME DEFAULT NULL,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- tasks
CREATE TABLE tasks (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    time TIME NOT NULL,
    completed TINYINT(1) DEFAULT 0,
    task_date DATE DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
