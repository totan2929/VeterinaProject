-- ============================================================================
-- VETERINARY CLINIC DATABASE SCHEMATICS
-- ============================================================================

CREATE DATABASE IF NOT EXISTS veterinary_clinic_db
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE veterinary_clinic_db;


-- ============================================================================
-- PHASE 1: Primary Independent Entities
-- Description: Base lookup and parent tables with no foreign key dependencies.
-- ============================================================================

-- Table 1: Clinics (Stores headquarters and branch locations)
CREATE TABLE clinics (
    clinic_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(150) NOT NULL,
    city VARCHAR(60) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    opening_hours VARCHAR(100) NOT NULL,
    services_offered TEXT
) ENGINE=InnoDB;

-- Table 2: Owners (Stores pet owner personal details and contact info)
CREATE TABLE owners (
    owner_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    doc_type VARCHAR(10) NOT NULL,
    doc_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    birth_date DATE NOT NULL,
    address VARCHAR(100) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(70) NOT NULL UNIQUE,
    status VARCHAR(15) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table 3: Services (Catalog of available clinical procedures and rates)
CREATE TABLE services (
    service_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    type ENUM('consultation', 'emergency', 'vaccination', 'deworming', 'surgery', 'lab', 'imaging', 'hospitalization', 'other') NOT NULL,
    description TEXT,
    duration_min INT UNSIGNED NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    status ENUM('Active', 'Inactive') DEFAULT 'Active'
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 2: Infrastructure, Staff, and Patients
-- Description: Core operational entities referencing primary parent tables.
-- ============================================================================

-- Table 4: Rooms (Physical spaces within each clinic location)
CREATE TABLE rooms (
    room_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    clinic_id INT UNSIGNED NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    type ENUM('single', 'general', 'ICU') NOT NULL,
    status ENUM('available', 'occupied', 'cleaning', 'maintenance') DEFAULT 'available',
    capacity INT UNSIGNED DEFAULT 1,
    daily_cost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 5: Employee Users (System accounts for administrative and clinical staff)
CREATE TABLE employee_users (
    employee_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    clinic_id INT UNSIGNED NOT NULL,
    doc_type ENUM('CC', 'CE', 'TI', 'PASSPORT') NOT NULL,
    doc_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
     email VARCHAR(70) NOT NULL UNIQUE,
    role ENUM('Administrator', 'Veterinarian', 'Receptionist', 'Cashier') NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Table 6: Pets (Patient records linked to their respective owners)
CREATE TABLE pets (
    pet_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    owner_id INT UNSIGNED NOT NULL,
    name VARCHAR(60) NOT NULL,
    species ENUM('dog', 'cat', 'bird', 'reptile', 'rodent', 'other') NOT NULL,
    breed VARCHAR(60) NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    estimated_birth_date DATE NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL,
    color VARCHAR(50),
    coat VARCHAR(50),
    has_chip BOOLEAN DEFAULT FALSE,
    chip_number VARCHAR(30) UNIQUE NULL,
    is_neutered BOOLEAN DEFAULT FALSE,
    is_alive BOOLEAN DEFAULT TRUE,
    photo_url VARCHAR(255) NULL,
    FOREIGN KEY (owner_id) REFERENCES owners(owner_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 3: Medical Personnel and Scheduling
-- Description: Specialized veterinary profile extension and work schedules.
-- ============================================================================

-- Table 7: Veterinarians (Professional licensing and specialties linked to employees)
CREATE TABLE veterinarians (
    veterinarian_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_id INT UNSIGNED NOT NULL UNIQUE,
    professional_license VARCHAR(30) NOT NULL UNIQUE,
    specialty ENUM('general', 'surgeon', 'dermatologist', 'ophthalmologist', 'oncologist') NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee_users(employee_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 8: Schedules (Time slots assigned to veterinarians for consultations)
CREATE TABLE schedules (
    schedule_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    veterinarian_id INT UNSIGNED NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status ENUM('available', 'occupied', 'disabled') DEFAULT 'available',
    allowed_appointment_type ENUM('general', 'followup', 'emergency', 'vaccination') NOT NULL,
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 4: Clinical Appointments and Service Details
-- Description: Appointment booking and itemized service allocation.
-- ============================================================================

-- Table 9: Appointments (Scheduled medical sessions connecting patients, vets, and slots)
CREATE TABLE appointments (
    appointment_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id INT UNSIGNED NOT NULL,
    clinic_id INT UNSIGNED NOT NULL,
    veterinarian_id INT UNSIGNED NOT NULL,
    schedule_id INT UNSIGNED NOT NULL UNIQUE,
    appointment_type ENUM('general', 'followup', 'emergency', 'vaccination') NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('scheduled', 'confirmed', 'in_progress', 'completed', 'canceled', 'no_show') DEFAULT 'scheduled',
    arrival_time DATETIME NULL,
    consultation_start_time DATETIME NULL,
    completion_time DATETIME NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
) ENGINE=InnoDB;

-- Table 10: Appointment Details (Breakdown of performed services and pricing)
CREATE TABLE appointment_details (
    detail_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NOT NULL,
    service_id INT UNSIGNED NOT NULL,
    quantity INT UNSIGNED DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0.00,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(service_id)
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 5: Medical History, Treatments, and Diagnostics
-- Description: Detailed medical records, prescriptions, vaccines, and lab tests.
-- ============================================================================

-- Table 11: Medical Records (Clinical diagnosis and progress notes per appointment)
CREATE TABLE medical_records (
    record_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NOT NULL UNIQUE,
    pet_id INT UNSIGNED NOT NULL,
    veterinarian_id INT UNSIGNED NOT NULL,
    anamnesis TEXT NOT NULL,
    physical_exam TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    prognosis TEXT,
    care_instructions TEXT,
    next_appointment_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id)
) ENGINE=InnoDB;

-- Table 12: Prescriptions (Medications and dosage instructions issued in consultations)
CREATE TABLE prescriptions (
    prescription_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    record_id INT UNSIGNED NOT NULL,
    medication VARCHAR(120) NOT NULL,
    dosage VARCHAR(80) NOT NULL,
    frequency VARCHAR(80) NOT NULL,
    duration_days INT UNSIGNED NOT NULL,
    instructions TEXT,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 13: Administered Vaccines (Vaccination logs and booster scheduling)
CREATE TABLE administered_vaccines (
    vaccine_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id INT UNSIGNED NOT NULL,
    record_id INT UNSIGNED NULL,
    veterinarian_id INT UNSIGNED NOT NULL,
    vaccine_name ENUM('rabies', 'hexavalente', 'quintuple', 'other') NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(80) NOT NULL,
    batch_number VARCHAR(80) NOT NULL,
    application_date DATE NOT NULL,
    booster_date DATE NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id),
    FOREIGN KEY (veterinarian_id) REFERENCES veterinarians(veterinarian_id)
) ENGINE=InnoDB;

-- Table 14: Lab Exams (Diagnostic tests and uploaded clinical reports)
CREATE TABLE lab_exams (
    exam_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    record_id INT UNSIGNED NOT NULL,
    requesting_vet_id INT UNSIGNED NOT NULL,
    type ENUM('blood', 'urine', 'xray', 'ultrasound', 'other') NOT NULL,
    name VARCHAR(100) NOT NULL,
    result_date DATE NULL,
    result_value VARCHAR(100),
    reference_range VARCHAR(100),
    interpretation TEXT,
    file_url VARCHAR(255) NULL,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id),
    FOREIGN KEY (requesting_vet_id) REFERENCES veterinarians(veterinarian_id)
) ENGINE=InnoDB;


-- ============================================================================
-- PHASE 6: Inpatient Care and Billing
-- Description: Hospitalizations and payment invoice generation.
-- ============================================================================

-- Table 15: Hospitalizations (Inpatient admission tracking and room occupancy)
CREATE TABLE hospitalizations (
    hospitalization_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pet_id INT UNSIGNED NOT NULL,
    attending_vet_id INT UNSIGNED NOT NULL,
    room_id INT UNSIGNED NOT NULL,
    admission_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    estimated_discharge_date DATE NOT NULL,
    actual_discharge_datetime DATETIME NULL,
    reason TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    status ENUM('active', 'discharged') DEFAULT 'active',
    observations TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (attending_vet_id) REFERENCES veterinarians(veterinarian_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
) ENGINE=InnoDB;

-- Table 16: Invoices (Billing records for appointments and hospital stays)
CREATE TABLE invoices (
    invoice_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT UNSIGNED NULL,
    hospitalization_id INT UNSIGNED NULL,
    cashier_id INT UNSIGNED NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discounts DECIMAL(10,2) DEFAULT 0.00,
    tax DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'debit_card', 'credit_card', 'wire_transfer') NOT NULL,
    payment_status ENUM('pending', 'paid', 'canceled') DEFAULT 'paid',
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (hospitalization_id) REFERENCES hospitalizations(hospitalization_id),
    FOREIGN KEY (cashier_id) REFERENCES employee_users(employee_id)
) ENGINE=InnoDB;