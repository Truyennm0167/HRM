import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')

import django
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check columns in app_contract
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'app_contract' ORDER BY ordinal_position")
columns = [c[0] for c in cursor.fetchall()]
print("Columns in app_contract:")
for col in columns:
    print(f"  - {col}")

# Check model fields
from app.models import Contract
print("\nModel Contract fields:")
for field in Contract._meta.get_fields():
    if hasattr(field, 'column'):
        print(f"  - {field.name} -> {field.column}")
