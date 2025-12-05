"""
Script tạo các tables Appraisal bị thiếu
"""
import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')

import django
django.setup()

from django.db import connection

# Check which tables are missing
cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
existing_tables = [t[0] for t in cursor.fetchall()]

required_appraisal_tables = [
    'app_appraisalperiod',
    'app_appraisalcriteria',
    'app_appraisal',
    'app_appraisalscore',
    'app_appraisalcomment',
    'app_systemsettings'
]

missing_tables = [t for t in required_appraisal_tables if t not in existing_tables]
print(f"Missing tables: {missing_tables}")

if not missing_tables:
    print("Tất cả tables đã tồn tại!")
    exit(0)

# SQL to create missing tables
sql_statements = []

if 'app_appraisalperiod' in missing_tables:
    sql_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisalperiod (
        id BIGSERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        self_assessment_deadline DATE NOT NULL,
        manager_review_deadline DATE NOT NULL,
        hr_review_deadline DATE,
        status VARCHAR(20) NOT NULL DEFAULT 'draft',
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL
    )
    """)

if 'app_appraisalcriteria' in missing_tables:
    sql_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisalcriteria (
        id BIGSERIAL PRIMARY KEY,
        period_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        weight INTEGER NOT NULL DEFAULT 10,
        max_score INTEGER NOT NULL DEFAULT 5,
        order_index INTEGER NOT NULL DEFAULT 0
    )
    """)

if 'app_appraisal' in missing_tables:
    sql_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisal (
        id BIGSERIAL PRIMARY KEY,
        period_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
        employee_id BIGINT NOT NULL REFERENCES app_employee(id) ON DELETE CASCADE,
        manager_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL,
        self_assessment TEXT,
        self_score DECIMAL(5,2),
        manager_comment TEXT,
        manager_score DECIMAL(5,2),
        hr_comment TEXT,
        final_score DECIMAL(5,2),
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        self_submitted_at TIMESTAMP WITH TIME ZONE,
        manager_submitted_at TIMESTAMP WITH TIME ZONE,
        hr_approved_at TIMESTAMP WITH TIME ZONE,
        company_feedback TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    """)

if 'app_appraisalscore' in missing_tables:
    sql_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisalscore (
        id BIGSERIAL PRIMARY KEY,
        appraisal_id BIGINT NOT NULL REFERENCES app_appraisal(id) ON DELETE CASCADE,
        criteria_id BIGINT NOT NULL REFERENCES app_appraisalcriteria(id) ON DELETE CASCADE,
        self_score INTEGER,
        manager_score INTEGER,
        comment TEXT
    )
    """)

if 'app_appraisalcomment' in missing_tables:
    sql_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisalcomment (
        id BIGSERIAL PRIMARY KEY,
        appraisal_id BIGINT NOT NULL REFERENCES app_appraisal(id) ON DELETE CASCADE,
        author_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    """)

if 'app_systemsettings' in missing_tables:
    sql_statements.append("""
    CREATE TABLE IF NOT EXISTS app_systemsettings (
        id BIGSERIAL PRIMARY KEY,
        company_name VARCHAR(200) NOT NULL DEFAULT 'Công ty ABC',
        company_address TEXT,
        company_phone VARCHAR(20),
        company_email VARCHAR(254),
        company_website VARCHAR(200),
        company_logo VARCHAR(100),
        work_start_time TIME DEFAULT '08:00:00',
        work_end_time TIME DEFAULT '17:00:00',
        lunch_break_start TIME DEFAULT '12:00:00',
        lunch_break_end TIME DEFAULT '13:00:00',
        working_days VARCHAR(20) DEFAULT '2,3,4,5,6',
        late_threshold_minutes INTEGER DEFAULT 15,
        early_leave_threshold_minutes INTEGER DEFAULT 15,
        overtime_rate DECIMAL(3,1) DEFAULT 1.5,
        social_insurance_rate DECIMAL(5,2) DEFAULT 8.00,
        health_insurance_rate DECIMAL(5,2) DEFAULT 1.50,
        unemployment_insurance_rate DECIMAL(5,2) DEFAULT 1.00,
        company_social_insurance_rate DECIMAL(5,2) DEFAULT 17.50,
        company_health_insurance_rate DECIMAL(5,2) DEFAULT 3.00,
        company_unemployment_insurance_rate DECIMAL(5,2) DEFAULT 1.00,
        email_notifications_enabled BOOLEAN DEFAULT TRUE,
        email_leave_request BOOLEAN DEFAULT TRUE,
        email_expense_request BOOLEAN DEFAULT TRUE,
        email_payroll_ready BOOLEAN DEFAULT TRUE,
        email_announcement BOOLEAN DEFAULT TRUE,
        smtp_host VARCHAR(200),
        smtp_port INTEGER DEFAULT 587,
        smtp_username VARCHAR(200),
        smtp_password VARCHAR(200),
        smtp_use_tls BOOLEAN DEFAULT TRUE,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_by_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL
    )
    """)

print(f"\nTạo {len(sql_statements)} tables...")

for sql in sql_statements:
    try:
        cursor.execute(sql)
        print(f"✓ Created table")
    except Exception as e:
        print(f"✗ Error: {e}")

connection.commit()
print("\n✓ Hoàn tất tạo tables!")

# Verify
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'app_appraisal%' OR tablename = 'app_systemsettings'")
created = [t[0] for t in cursor.fetchall()]
print(f"\nAppraisal tables hiện có: {created}")
