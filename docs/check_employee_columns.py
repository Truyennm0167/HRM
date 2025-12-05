import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT column_name, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = 'app_employee' 
    AND data_type = 'character varying' 
    ORDER BY ordinal_position
""")

print('Column lengths in app_employee (varchar only):')
for col in cursor.fetchall():
    length = col[1] if col[1] else 'unlimited'
    marker = ' ⚠️ SHORT' if col[1] and col[1] <= 100 else ''
    print(f'  {col[0]}: {length}{marker}')
