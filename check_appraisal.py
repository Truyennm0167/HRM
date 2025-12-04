import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

# Check Appraisal table columns
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'app_appraisal' ORDER BY ordinal_position")
db_columns = [col[0] for col in cursor.fetchall()]
print('DB Columns in app_appraisal:')
for col in db_columns:
    print(f'  - {col}')

# Check model columns
from app.models import Appraisal
print('\nModel Appraisal fields:')
model_columns = []
for field in Appraisal._meta.get_fields():
    if hasattr(field, 'column'):
        model_columns.append(field.column)
        print(f'  - {field.column}')

# Find missing columns
missing = set(model_columns) - set(db_columns)
extra = set(db_columns) - set(model_columns)

print(f'\nMissing in DB: {missing}')
print(f'Extra in DB: {extra}')
