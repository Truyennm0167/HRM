import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()
from django.db import connection
cursor = connection.cursor()

print("Columns in app_contract:")
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'app_contract' ORDER BY ordinal_position")
for col in cursor.fetchall():
    print(f"  {col[0]}: {col[1]}")

print("\n\nModel Contract fields:")
from app.models import Contract
for field in Contract._meta.get_fields():
    if hasattr(field, 'get_internal_type'):
        print(f"  {field.name}: {field.get_internal_type()}")
