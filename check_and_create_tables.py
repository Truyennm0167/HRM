"""
Script kiểm tra và tạo các tables còn thiếu
"""
import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')

import django
django.setup()

from django.db import connection
from django.apps import apps

cursor = connection.cursor()

# Get all existing tables
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
existing_tables = set(t[0] for t in cursor.fetchall())

print("="*60)
print(" KIỂM TRA TABLES THIẾU")
print("="*60)

# Get all model tables from app
app_models = apps.get_app_config('app').get_models()

missing_tables = []
for model in app_models:
    table_name = model._meta.db_table
    if table_name not in existing_tables:
        missing_tables.append((table_name, model))
    
    # Check M2M tables
    for field in model._meta.get_fields():
        if hasattr(field, 'remote_field') and hasattr(field.remote_field, 'through'):
            through = field.remote_field.through
            if through and hasattr(through, '_meta'):
                m2m_table = through._meta.db_table
                if m2m_table not in existing_tables:
                    missing_tables.append((m2m_table, through))

print(f"\nThiếu {len(missing_tables)} tables:")
for table, model in missing_tables:
    print(f"  - {table}")

# Tạo các tables thiếu bằng cách chạy SQL trực tiếp
print("\n" + "="*60)
print(" TẠO CÁC TABLES THIẾU")
print("="*60)

create_statements = []

# app_appraisalperiod_applicable_job_titles (M2M)
if 'app_appraisalperiod_applicable_job_titles' not in existing_tables:
    create_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisalperiod_applicable_job_titles (
        id BIGSERIAL PRIMARY KEY,
        appraisalperiod_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
        jobtitle_id BIGINT NOT NULL REFERENCES app_jobtitle(id) ON DELETE CASCADE,
        UNIQUE (appraisalperiod_id, jobtitle_id)
    )
    """)

# app_appraisalperiod_applicable_departments (M2M) 
if 'app_appraisalperiod_applicable_departments' not in existing_tables:
    create_statements.append("""
    CREATE TABLE IF NOT EXISTS app_appraisalperiod_applicable_departments (
        id BIGSERIAL PRIMARY KEY,
        appraisalperiod_id BIGINT NOT NULL REFERENCES app_appraisalperiod(id) ON DELETE CASCADE,
        department_id BIGINT NOT NULL REFERENCES app_department(id) ON DELETE CASCADE,
        UNIQUE (appraisalperiod_id, department_id)
    )
    """)

for sql in create_statements:
    try:
        cursor.execute(sql)
        print(f"✓ Created table")
    except Exception as e:
        print(f"✗ Error: {e}")

connection.commit()

# Re-check
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
existing_tables = set(t[0] for t in cursor.fetchall())

print("\n" + "="*60)
print(" KIỂM TRA LẠI")  
print("="*60)

still_missing = []
for model in app_models:
    table_name = model._meta.db_table
    if table_name not in existing_tables:
        still_missing.append(table_name)
    
    for field in model._meta.get_fields():
        if hasattr(field, 'remote_field') and hasattr(field.remote_field, 'through'):
            through = field.remote_field.through
            if through and hasattr(through, '_meta'):
                m2m_table = through._meta.db_table
                if m2m_table not in existing_tables:
                    still_missing.append(m2m_table)

if still_missing:
    print(f"Còn thiếu {len(still_missing)} tables:")
    for t in still_missing:
        print(f"  - {t}")
else:
    print("✓ Tất cả tables đã có đủ!")
