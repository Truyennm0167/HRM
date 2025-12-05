import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT column_name, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = 'auth_user' 
    AND data_type = 'character varying'
    ORDER BY ordinal_position
""")

print("Column lengths in auth_user (varchar only):")
for row in cursor.fetchall():
    col_name, max_len = row
    print(f"  {col_name}: {max_len}")
