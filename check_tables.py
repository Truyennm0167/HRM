import os
import sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')

import django
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
tables = [t[0] for t in cursor.fetchall()]

print('='*60)
print('Tables trong database:')
print('='*60)
for t in sorted(tables):
    print(f'  - {t}')
print(f'\nTổng: {len(tables)} tables')

# Check if app_appraisal exists
if 'app_appraisal' in tables:
    print('\n✓ app_appraisal EXISTS')
else:
    print('\n✗ app_appraisal NOT FOUND')
