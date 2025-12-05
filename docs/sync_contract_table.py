"""
Script để đồng bộ table app_contract với model Contract
"""
import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')

import django
django.setup()

from django.db import connection

cursor = connection.cursor()

print("="*60)
print(" SYNC CONTRACT TABLE")
print("="*60)

# Các thay đổi cần thực hiện:
# 1. Đổi tên contract_number -> contract_code
# 2. Đổi tên salary -> base_salary  
# 3. Thêm department_id
# 4. Đổi tên workplace -> work_location
# 5. Đổi tên contract_file -> attachment

alterations = [
    # Rename columns
    ("ALTER TABLE app_contract RENAME COLUMN contract_number TO contract_code", "Rename contract_number -> contract_code"),
    ("ALTER TABLE app_contract RENAME COLUMN salary TO base_salary", "Rename salary -> base_salary"),
    ("ALTER TABLE app_contract RENAME COLUMN workplace TO work_location", "Rename workplace -> work_location"),
    ("ALTER TABLE app_contract RENAME COLUMN contract_file TO attachment", "Rename contract_file -> attachment"),
    
    # Add missing columns
    ("ALTER TABLE app_contract ADD COLUMN IF NOT EXISTS department_id BIGINT REFERENCES app_department(id) ON DELETE SET NULL", "Add department_id"),
    
    # Drop columns not in model
    ("ALTER TABLE app_contract DROP COLUMN IF EXISTS salary_coefficient", "Drop salary_coefficient"),
    ("ALTER TABLE app_contract DROP COLUMN IF EXISTS job_description", "Drop job_description"),
    ("ALTER TABLE app_contract DROP COLUMN IF EXISTS benefits", "Drop benefits"),
    ("ALTER TABLE app_contract DROP COLUMN IF EXISTS insurance_info", "Drop insurance_info"),
    ("ALTER TABLE app_contract DROP COLUMN IF EXISTS termination_reason", "Drop termination_reason"),
    ("ALTER TABLE app_contract DROP COLUMN IF EXISTS termination_date", "Drop termination_date"),
]

for sql, desc in alterations:
    try:
        cursor.execute(sql)
        print(f"✓ {desc}")
    except Exception as e:
        print(f"✗ {desc}: {e}")

connection.commit()

print("\n" + "="*60)
print(" KIỂM TRA SAU KHI SỬA")
print("="*60)

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'app_contract' ORDER BY ordinal_position")
columns = [c[0] for c in cursor.fetchall()]
print("Columns in app_contract:")
for col in columns:
    print(f"  - {col}")

print("\n✓ Hoàn tất đồng bộ table app_contract!")
