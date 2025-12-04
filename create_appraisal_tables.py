import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

print("Creating Appraisal tables...")

# 1. Create AppraisalPeriod
cursor.execute("""
CREATE TABLE app_appraisalperiod (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    self_assessment_deadline DATE NOT NULL,
    manager_review_deadline DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_by_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
""")
print("✓ Created app_appraisalperiod")

# 2. Create M2M for applicable_departments
cursor.execute("""
CREATE TABLE app_appraisalperiod_applicable_departments (
    id BIGSERIAL PRIMARY KEY,
    appraisalperiod_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
    department_id BIGINT NOT NULL REFERENCES app_department(id) ON DELETE CASCADE,
    UNIQUE (appraisalperiod_id, department_id)
)
""")
print("✓ Created app_appraisalperiod_applicable_departments")

# 3. Create M2M for applicable_job_titles
cursor.execute("""
CREATE TABLE app_appraisalperiod_applicable_job_titles (
    id BIGSERIAL PRIMARY KEY,
    appraisalperiod_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
    jobtitle_id BIGINT NOT NULL REFERENCES app_jobtitle(id) ON DELETE CASCADE,
    UNIQUE (appraisalperiod_id, jobtitle_id)
)
""")
print("✓ Created app_appraisalperiod_applicable_job_titles")

# 4. Create AppraisalCriteria
cursor.execute("""
CREATE TABLE app_appraisalcriteria (
    id BIGSERIAL PRIMARY KEY,
    period_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category VARCHAR(20) NOT NULL,
    weight DECIMAL(5,2) NOT NULL DEFAULT 1.0,
    max_score INTEGER NOT NULL DEFAULT 5,
    "order" INTEGER NOT NULL DEFAULT 0
)
""")
print("✓ Created app_appraisalcriteria")

# 5. Create Appraisal
cursor.execute("""
CREATE TABLE app_appraisal (
    id BIGSERIAL PRIMARY KEY,
    period_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
    employee_id BIGINT NOT NULL REFERENCES app_employee(id) ON DELETE CASCADE,
    manager_id BIGINT REFERENCES app_employee(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending_self',
    self_assessment_date TIMESTAMP WITH TIME ZONE,
    manager_review_date TIMESTAMP WITH TIME ZONE,
    final_review_date TIMESTAMP WITH TIME ZONE,
    self_overall_score DECIMAL(5,2),
    self_comments TEXT DEFAULT '',
    self_achievements TEXT DEFAULT '',
    self_challenges TEXT DEFAULT '',
    self_development_plan TEXT DEFAULT '',
    company_feedback TEXT DEFAULT '',
    manager_overall_score DECIMAL(5,2),
    manager_comments TEXT DEFAULT '',
    manager_strengths TEXT DEFAULT '',
    manager_weaknesses TEXT DEFAULT '',
    manager_recommendations TEXT DEFAULT '',
    final_score DECIMAL(5,2),
    overall_rating VARCHAR(20),
    hr_comments TEXT DEFAULT '',
    salary_adjustment DECIMAL(15,2),
    promotion_recommended BOOLEAN DEFAULT FALSE,
    training_recommended TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (period_id, employee_id)
)
""")
print("✓ Created app_appraisal")

# 6. Create AppraisalScore
cursor.execute("""
CREATE TABLE app_appraisalscore (
    id BIGSERIAL PRIMARY KEY,
    appraisal_id BIGINT NOT NULL REFERENCES app_appraisal(id) ON DELETE CASCADE,
    criteria_id BIGINT NOT NULL REFERENCES app_appraisalcriteria(id) ON DELETE CASCADE,
    self_score INTEGER,
    self_comment TEXT DEFAULT '',
    manager_score INTEGER,
    manager_comment TEXT DEFAULT '',
    final_score INTEGER,
    UNIQUE (appraisal_id, criteria_id)
)
""")
print("✓ Created app_appraisalscore")

# 7. Create AppraisalComment
cursor.execute("""
CREATE TABLE app_appraisalcomment (
    id BIGSERIAL PRIMARY KEY,
    appraisal_id BIGINT NOT NULL REFERENCES app_appraisal(id) ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES app_employee(id) ON DELETE CASCADE,
    author_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
""")
print("✓ Created app_appraisalcomment")

# Create indexes
cursor.execute("CREATE INDEX IF NOT EXISTS app_appraisalperiod_status_idx ON app_appraisalperiod(status, start_date DESC)")
cursor.execute("CREATE INDEX IF NOT EXISTS app_appraisal_period_status_idx ON app_appraisal(period_id, status)")
cursor.execute("CREATE INDEX IF NOT EXISTS app_appraisal_employee_idx ON app_appraisal(employee_id, created_at DESC)")
print("✓ Created indexes")

connection.commit()
print("\n✓ All Appraisal tables created successfully!")
