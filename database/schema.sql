-- =========================================================
-- HELIOS DATABASE SCHEMA
-- =========================================================

DROP TABLE IF EXISTS optimization_runs CASCADE;
DROP TABLE IF EXISTS demand_predictions CASCADE;
DROP TABLE IF EXISTS surge_events CASCADE;
DROP TABLE IF EXISTS resource_allocations CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;
DROP TABLE IF EXISTS beds CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS departments CASCADE;


-- =========================================================
-- 1. DEPARTMENTS
-- =========================================================

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,

    name VARCHAR(100) UNIQUE NOT NULL,

    capacity INTEGER NOT NULL
        CHECK (capacity >= 0),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. PATIENTS
-- =========================================================

CREATE TABLE patients (
    id SERIAL PRIMARY KEY,

    patient_code VARCHAR(30) UNIQUE NOT NULL,

    arrival_time TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    department_id INTEGER
        REFERENCES departments(id),

    severity INTEGER NOT NULL
        CHECK (severity BETWEEN 1 AND 5),

    required_bed BOOLEAN DEFAULT TRUE,

    required_ventilator BOOLEAN DEFAULT FALSE,

    priority_score DOUBLE PRECISION DEFAULT 0,

    status VARCHAR(30) DEFAULT 'WAITING'
);


-- =========================================================
-- 3. STAFF
-- =========================================================

CREATE TABLE staff (
    id SERIAL PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    role VARCHAR(30) NOT NULL
        CHECK (role IN ('DOCTOR', 'NURSE')),

    department_id INTEGER
        REFERENCES departments(id),

    status VARCHAR(30) DEFAULT 'AVAILABLE',

    shift VARCHAR(30)
);


-- =========================================================
-- 4. BEDS
-- =========================================================

CREATE TABLE beds (
    id SERIAL PRIMARY KEY,

    bed_code VARCHAR(30) UNIQUE NOT NULL,

    department_id INTEGER
        REFERENCES departments(id),

    bed_type VARCHAR(30) NOT NULL
        CHECK (
            bed_type IN (
                'GENERAL',
                'ICU',
                'EMERGENCY'
            )
        ),

    status VARCHAR(30) DEFAULT 'AVAILABLE'
);


-- =========================================================
-- 5. MEDICAL EQUIPMENT
-- =========================================================

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,

    equipment_code VARCHAR(30) UNIQUE NOT NULL,

    equipment_type VARCHAR(50) NOT NULL,

    department_id INTEGER
        REFERENCES departments(id),

    status VARCHAR(30) DEFAULT 'AVAILABLE'
);


-- =========================================================
-- 6. RESOURCE ALLOCATIONS
-- =========================================================

CREATE TABLE resource_allocations (
    id SERIAL PRIMARY KEY,

    resource_type VARCHAR(50) NOT NULL,

    from_department_id INTEGER
        REFERENCES departments(id),

    to_department_id INTEGER
        REFERENCES departments(id),

    quantity INTEGER NOT NULL
        CHECK (quantity > 0),

    reason TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 7. SURGE EVENTS
-- =========================================================

CREATE TABLE surge_events (
    id SERIAL PRIMARY KEY,

    department_id INTEGER
        REFERENCES departments(id),

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    arrival_rate DOUBLE PRECISION,

    expected_rate DOUBLE PRECISION,

    z_score DOUBLE PRECISION,

    severity VARCHAR(20),

    status VARCHAR(30) DEFAULT 'ACTIVE'
);


-- =========================================================
-- 8. DEMAND PREDICTIONS
-- =========================================================

CREATE TABLE demand_predictions (
    id SERIAL PRIMARY KEY,

    department_id INTEGER
        REFERENCES departments(id),

    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    horizon_minutes INTEGER,

    predicted_arrivals DOUBLE PRECISION,

    predicted_beds DOUBLE PRECISION,

    predicted_doctors DOUBLE PRECISION,

    predicted_nurses DOUBLE PRECISION
);


-- =========================================================
-- 9. OPTIMIZATION RUNS
-- =========================================================

CREATE TABLE optimization_runs (
    id SERIAL PRIMARY KEY,

    triggered_by VARCHAR(100),

    objective_value DOUBLE PRECISION,

    status VARCHAR(30),

    recommendations JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);