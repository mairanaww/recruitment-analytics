CREATE TABLE departments (
    department_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id VARCHAR(50) REFERENCES departments(department_id),
    title VARCHAR(100),
    start_date DATE NOT NULL,
    end_date DATE,
    status VARCHAR(50) -- 'Active', 'Terminated'
);

CREATE TABLE headcount_plan (
    department_id VARCHAR(50) REFERENCES departments(department_id),
    fiscal_period VARCHAR(20), -- e.g., '2023-Q1'
    planned_headcount INT,
    planned_hires INT,
    PRIMARY KEY (department_id, fiscal_period)
);

CREATE TABLE requisitions (
    req_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department_id VARCHAR(50) REFERENCES departments(department_id),
    status VARCHAR(50), -- 'Open', 'Closed', 'On Hold'
    open_date DATE NOT NULL,
    close_date DATE,
    target_hire_date DATE
);

CREATE TABLE candidates (
    candidate_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    source VARCHAR(100)
);

CREATE TABLE applications (
    application_id VARCHAR(50) PRIMARY KEY,
    req_id VARCHAR(50) REFERENCES requisitions(req_id),
    candidate_id VARCHAR(50) REFERENCES candidates(candidate_id),
    apply_date DATE NOT NULL,
    UNIQUE (req_id, candidate_id)
);

CREATE TABLE stage_events (
    event_id VARCHAR(50) PRIMARY KEY,
    application_id VARCHAR(50) REFERENCES applications(application_id),
    stage_name VARCHAR(100) NOT NULL, -- 'Applied', 'Recruiter Screen', 'Hiring Manager Interview', 'Onsite', 'Offer', 'Hired', 'Rejected'
    event_date DATE NOT NULL,
    status VARCHAR(50) -- 'Pass', 'Fail', 'In Progress'
);

CREATE TABLE offers (
    offer_id VARCHAR(50) PRIMARY KEY,
    application_id VARCHAR(50) REFERENCES applications(application_id),
    offer_date DATE NOT NULL,
    status VARCHAR(50), -- 'Extended', 'Accepted', 'Declined', 'Rescinded'
    accepted_date DATE,
    amount DECIMAL(10,2)
);
