import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()
from django.db import connection
cursor = connection.cursor()

# Create SystemSettings table with all fields
sql = """
CREATE TABLE IF NOT EXISTS app_systemsettings (
    id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL DEFAULT 'Công ty TNHH ABC',
    company_logo VARCHAR(100),
    company_address TEXT DEFAULT '',
    company_phone VARCHAR(20) DEFAULT '',
    company_email VARCHAR(254) DEFAULT '',
    company_website VARCHAR(200) DEFAULT '',
    company_tax_code VARCHAR(20) DEFAULT '',
    standard_working_days INTEGER DEFAULT 22,
    standard_working_hours DECIMAL(4,2) DEFAULT 8,
    work_start_time TIME DEFAULT '08:00:00',
    work_end_time TIME DEFAULT '17:00:00',
    lunch_break_start TIME DEFAULT '12:00:00',
    lunch_break_end TIME DEFAULT '13:00:00',
    timezone VARCHAR(50) DEFAULT 'Asia/Ho_Chi_Minh',
    tax_rate DECIMAL(5,2) DEFAULT 10,
    tax_deduction_personal DECIMAL(15,0) DEFAULT 11000000,
    tax_deduction_dependent DECIMAL(15,0) DEFAULT 4400000,
    social_insurance_rate DECIMAL(5,2) DEFAULT 8,
    health_insurance_rate DECIMAL(5,2) DEFAULT 1.5,
    unemployment_insurance_rate DECIMAL(5,2) DEFAULT 1,
    employer_social_insurance_rate DECIMAL(5,2) DEFAULT 17.5,
    employer_health_insurance_rate DECIMAL(5,2) DEFAULT 3,
    employer_unemployment_insurance_rate DECIMAL(5,2) DEFAULT 1,
    minimum_wage DECIMAL(15,0) DEFAULT 4960000,
    social_insurance_max_salary DECIMAL(15,0) DEFAULT 46800000,
    email_host VARCHAR(200) DEFAULT 'smtp.gmail.com',
    email_port INTEGER DEFAULT 587,
    email_use_tls BOOLEAN DEFAULT TRUE,
    email_use_ssl BOOLEAN DEFAULT FALSE,
    email_host_user VARCHAR(200) DEFAULT '',
    email_host_password VARCHAR(200) DEFAULT '',
    email_from_name VARCHAR(100) DEFAULT 'HRM System',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL
)
"""

cursor.execute(sql)
connection.commit()
print('Created app_systemsettings table')

# Also fake the migration
cursor.execute("UPDATE django_migrations SET applied = NOW() WHERE app = 'app' AND name = '0003_appraisal_company_feedback_systemsettings'")
if cursor.rowcount == 0:
    cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('app', '0003_appraisal_company_feedback_systemsettings', NOW())")
connection.commit()
print('Migration marked as applied')
