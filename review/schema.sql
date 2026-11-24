CREATE TABLE cohort (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE patient (
    patient_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    sex TEXT NOT NULL
);

CREATE TABLE cohort_member (
    cohort_id INTEGER NOT NULL REFERENCES cohort(id),
    patient_id TEXT NOT NULL REFERENCES patient(patient_id),
    added_at TEXT NOT NULL,
    PRIMARY KEY (cohort_id, patient_id)
);
