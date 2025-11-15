#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Create app_contract table
cursor.execute('''
CREATE TABLE app_contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_code VARCHAR(20) UNIQUE NOT NULL,
    contract_type VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    signed_date DATE NULL,
    base_salary DECIMAL(15, 2) NOT NULL DEFAULT 0,
    allowances TEXT NOT NULL,
    job_title_id BIGINT NULL,
    department_id BIGINT NULL,
    work_location VARCHAR(255),
    working_hours VARCHAR(100) NOT NULL DEFAULT '8:00-17:00',
    terms TEXT,
    notes TEXT,
    attachment VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    employee_id BIGINT NOT NULL,
    created_by_id BIGINT NULL,
    renewed_from_id BIGINT NULL,
    FOREIGN KEY (employee_id) REFERENCES app_employee(id),
    FOREIGN KEY (created_by_id) REFERENCES app_employee(id),
    FOREIGN KEY (job_title_id) REFERENCES app_jobtitle(id),
    FOREIGN KEY (department_id) REFERENCES app_department(id),
    FOREIGN KEY (renewed_from_id) REFERENCES app_contract(id)
)
''')

# Create indexes
cursor.execute('CREATE INDEX app_contrac_employe_96c0b0_idx ON app_contract(employee_id, status)')
cursor.execute('CREATE INDEX app_contrac_end_dat_7559b0_idx ON app_contract(end_date)')
cursor.execute('CREATE INDEX app_contrac_status_b794cb_idx ON app_contract(status)')

# Create app_contracthistory table
cursor.execute('''
CREATE TABLE app_contracthistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    old_value TEXT NULL,
    new_value TEXT NULL,
    performed_at DATETIME NOT NULL,
    contract_id BIGINT NOT NULL,
    performed_by_id BIGINT NULL,
    FOREIGN KEY (contract_id) REFERENCES app_contract(id),
    FOREIGN KEY (performed_by_id) REFERENCES app_employee(id)
)
''')

print('✅ Created app_contract table')
print('✅ Created 3 indexes on app_contract')
print('✅ Created app_contracthistory table')
print('✅ Database ready for Contract Management!')
