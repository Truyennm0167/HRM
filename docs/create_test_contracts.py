"""
Create test contracts for RBAC testing.
Run: python create_test_contracts.py
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from app.models import Contract, Employee, JobTitle, Department

print("📝 Creating test contracts for RBAC...")

# Get employees
try:
    hr_emp = Employee.objects.get(email='hr@company.com')
    it_manager = Employee.objects.get(email='manager.it@company.com')
    sales_manager = Employee.objects.get(email='manager.sales@company.com')
    it_staff = Employee.objects.get(email='employee.it@company.com')
    print("✅ Found test employees")
except Employee.DoesNotExist as e:
    print(f"❌ Error: {e}")
    print("Please run setup_test_users.py first!")
    exit(1)

# Get departments
it_dept = Department.objects.get(name='IT Department')
sales_dept = Department.objects.get(name='Sales Department')

# Create contracts for IT Department
print("\n📄 Creating IT Department contracts...")

# Contract 1: IT Manager - Active
contract1, created = Contract.objects.get_or_create(
    employee=it_manager,
    contract_type='indefinite',
    defaults={
        'start_date': date(2020, 1, 1),
        'end_date': None,
        'base_salary': 25000000,
        'allowances': {'housing': 5000000, 'transport': 2000000},
        'job_title': it_manager.job_title,
        'department': it_dept,
        'work_location': 'Hanoi Office',
        'working_hours': '8:00 - 17:00',
        'terms': 'Standard employment terms',
        'status': 'active',
        'created_by': hr_emp,
    }
)
if created:
    print(f"  ✅ Created: {contract1.contract_code} - {it_manager.name}")
else:
    print(f"  ℹ️  Exists: {contract1.contract_code} - {it_manager.name}")

# Contract 2: IT Staff - Active
contract2, created = Contract.objects.get_or_create(
    employee=it_staff,
    contract_type='fixed_term',
    defaults={
        'start_date': date(2023, 1, 1),
        'end_date': date(2024, 12, 31),
        'base_salary': 15000000,
        'allowances': {'lunch': 1000000},
        'job_title': it_staff.job_title,
        'department': it_dept,
        'work_location': 'Hanoi Office',
        'working_hours': '8:00 - 17:00',
        'terms': 'Fixed-term contract',
        'status': 'active',
        'created_by': hr_emp,
    }
)
if created:
    print(f"  ✅ Created: {contract2.contract_code} - {it_staff.name}")
else:
    print(f"  ℹ️  Exists: {contract2.contract_code} - {it_staff.name}")

# Contract 3: IT Staff - Expiring Soon (Different employee needed)
# Note: Using same employee twice may cause unique constraint issues
print("  ℹ️  Skipping duplicate contract for IT Staff")

# Create contracts for Sales Department
print("\n📄 Creating Sales Department contracts...")

# Contract 4: Sales Manager - Active
contract4, created = Contract.objects.get_or_create(
    employee=sales_manager,
    contract_type='indefinite',
    defaults={
        'start_date': date(2020, 1, 1),
        'end_date': None,
        'base_salary': 25000000,
        'allowances': {'housing': 5000000, 'transport': 2000000, 'phone': 1000000},
        'job_title': sales_manager.job_title,
        'department': sales_dept,
        'work_location': 'Hanoi Office',
        'working_hours': '8:00 - 17:00',
        'terms': 'Standard employment terms',
        'status': 'active',
        'created_by': hr_emp,
    }
)
if created:
    print(f"  ✅ Created: {contract4.contract_code} - {sales_manager.name}")
else:
    print(f"  ℹ️  Exists: {contract4.contract_code} - {sales_manager.name}")

# Contract 5: HR Employee - Active
contract5, created = Contract.objects.get_or_create(
    employee=hr_emp,
    contract_type='indefinite',
    defaults={
        'start_date': date(2020, 1, 1),
        'end_date': None,
        'base_salary': 20000000,
        'allowances': {'housing': 4000000, 'transport': 1500000},
        'job_title': hr_emp.job_title,
        'department': it_dept,
        'work_location': 'Hanoi Office',
        'working_hours': '8:00 - 17:00',
        'terms': 'HR Management contract',
        'status': 'active',
        'created_by': hr_emp,
    }
)
if created:
    print(f"  ✅ Created: {contract5.contract_code} - {hr_emp.name}")
else:
    print(f"  ℹ️  Exists: {contract5.contract_code} - {hr_emp.name}")

# Summary
print("\n" + "="*60)
print("✅ Test contracts created successfully!")
print("="*60)
print(f"\nTotal contracts: {Contract.objects.count()}")
print(f"IT Department: {Contract.objects.filter(employee__department=it_dept).count()}")
print(f"Sales Department: {Contract.objects.filter(employee__department=sales_dept).count()}")
print(f"Active: {Contract.objects.filter(status='active').count()}")
print(f"Expiring soon: {len([c for c in Contract.objects.all() if c.is_expiring_soon()])}")
print("\n" + "="*60)
print("🧪 Ready for RBAC testing!")
print("="*60)
