"""
Setup test users for RBAC testing.
Run: python manage.py shell < setup_test_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User, Group
from app.models import Employee, Department, JobTitle

print("🔧 Setting up test users for RBAC...")

# Get or create groups
hr_group, _ = Group.objects.get_or_create(name='HR')
manager_group, _ = Group.objects.get_or_create(name='Manager')
employee_group, _ = Group.objects.get_or_create(name='Employee')

# Get or create departments
it_dept, _ = Department.objects.get_or_create(
    name='IT Department',
    defaults={
        'description': 'Information Technology',
        'date_establishment': '2020-01-01'
    }
)

sales_dept, _ = Department.objects.get_or_create(
    name='Sales Department',
    defaults={
        'description': 'Sales and Marketing',
        'date_establishment': '2020-01-01'
    }
)

# Get or create job titles
hr_title, _ = JobTitle.objects.get_or_create(
    name='HR Manager',
    defaults={
        'description': 'Human Resources Manager',
        'salary_coefficient': 4.5
    }
)

manager_title, _ = JobTitle.objects.get_or_create(
    name='Department Manager',
    defaults={
        'description': 'Department Manager',
        'salary_coefficient': 5.0
    }
)

staff_title, _ = JobTitle.objects.get_or_create(
    name='Staff',
    defaults={
        'description': 'Staff Member',
        'salary_coefficient': 2.5
    }
)

# 1. Create HR User
print("\n👤 Creating HR User...")
hr_user, created = User.objects.get_or_create(
    username='hr_user',
    defaults={
        'email': 'hr@company.com',
        'first_name': 'HR',
        'last_name': 'Manager',
        'is_staff': True,
    }
)
if created:
    hr_user.set_password('hr123456')
    hr_user.save()
    print(f"  ✅ Created user: {hr_user.username}")
else:
    print(f"  ℹ️  User already exists: {hr_user.username}")

# Add to HR group
hr_user.groups.add(hr_group)
print(f"  ✅ Added to HR group")

# Create corresponding Employee
hr_employee, created = Employee.objects.get_or_create(
    email='hr@company.com',
    defaults={
        'employee_code': 'HR001',
        'name': 'HR Manager',
        'gender': 0,
        'phone': '0123456789',
        'birthday': '1985-01-01',
        'place_of_birth': 'Hanoi',
        'place_of_origin': 'Hanoi',
        'place_of_residence': 'Hanoi',
        'identification': '001085123456',
        'date_of_issue': '2020-01-01',
        'place_of_issue': 'Hanoi',
        'nationality': 'Vietnam',
        'nation': 'Kinh',
        'religion': 'None',
        'address': 'Hanoi',
        'marital_status': 0,
        'school': 'University',
        'major': 'Human Resources',
        'education_level': 3,
        'job_position': 'HR Manager',
        'department': it_dept,
        'job_title': hr_title,
        'salary': 20000000,
        'contract_start_date': '2020-01-01',
        'contract_duration': 12,
        'status': 2,
        'is_manager': False,
    }
)
if created:
    print(f"  ✅ Created employee: {hr_employee.name}")
else:
    print(f"  ℹ️  Employee already exists: {hr_employee.name}")

# 2. Create Manager User (IT Department)
print("\n👤 Creating Manager User (IT Department)...")
manager_user, created = User.objects.get_or_create(
    username='manager_user',
    defaults={
        'email': 'manager.it@company.com',
        'first_name': 'IT',
        'last_name': 'Manager',
        'is_staff': True,
    }
)
if created:
    manager_user.set_password('manager123456')
    manager_user.save()
    print(f"  ✅ Created user: {manager_user.username}")
else:
    print(f"  ℹ️  User already exists: {manager_user.username}")

# Add to Manager group
manager_user.groups.add(manager_group)
print(f"  ✅ Added to Manager group")

# Create corresponding Employee
manager_employee, created = Employee.objects.get_or_create(
    email='manager.it@company.com',
    defaults={
        'employee_code': 'MGR001',
        'name': 'IT Manager',
        'gender': 0,
        'phone': '0123456790',
        'birthday': '1980-01-01',
        'place_of_birth': 'Hanoi',
        'place_of_origin': 'Hanoi',
        'place_of_residence': 'Hanoi',
        'identification': '001080123456',
        'date_of_issue': '2020-01-01',
        'place_of_issue': 'Hanoi',
        'nationality': 'Vietnam',
        'nation': 'Kinh',
        'religion': 'None',
        'address': 'Hanoi',
        'marital_status': 1,
        'school': 'University',
        'major': 'Computer Science',
        'education_level': 3,
        'job_position': 'IT Manager',
        'department': it_dept,
        'job_title': manager_title,
        'salary': 25000000,
        'contract_start_date': '2020-01-01',
        'contract_duration': 12,
        'status': 2,
        'is_manager': True,
    }
)
if created:
    print(f"  ✅ Created employee: {manager_employee.name}")
    # Set as department manager
    it_dept.manager = manager_employee
    it_dept.save()
    print(f"  ✅ Set as IT Department manager")
else:
    print(f"  ℹ️  Employee already exists: {manager_employee.name}")

# 3. Create Manager User (Sales Department)
print("\n👤 Creating Manager User (Sales Department)...")
manager_sales_user, created = User.objects.get_or_create(
    username='manager_sales',
    defaults={
        'email': 'manager.sales@company.com',
        'first_name': 'Sales',
        'last_name': 'Manager',
        'is_staff': True,
    }
)
if created:
    manager_sales_user.set_password('manager123456')
    manager_sales_user.save()
    print(f"  ✅ Created user: {manager_sales_user.username}")
else:
    print(f"  ℹ️  User already exists: {manager_sales_user.username}")

# Add to Manager group
manager_sales_user.groups.add(manager_group)
print(f"  ✅ Added to Manager group")

# Create corresponding Employee
manager_sales_employee, created = Employee.objects.get_or_create(
    email='manager.sales@company.com',
    defaults={
        'employee_code': 'MGR002',
        'name': 'Sales Manager',
        'gender': 0,
        'phone': '0123456791',
        'birthday': '1982-01-01',
        'place_of_birth': 'Hanoi',
        'place_of_origin': 'Hanoi',
        'place_of_residence': 'Hanoi',
        'identification': '001082123456',
        'date_of_issue': '2020-01-01',
        'place_of_issue': 'Hanoi',
        'nationality': 'Vietnam',
        'nation': 'Kinh',
        'religion': 'None',
        'address': 'Hanoi',
        'marital_status': 1,
        'school': 'University',
        'major': 'Business Administration',
        'education_level': 3,
        'job_position': 'Sales Manager',
        'department': sales_dept,
        'job_title': manager_title,
        'salary': 25000000,
        'contract_start_date': '2020-01-01',
        'contract_duration': 12,
        'status': 2,
        'is_manager': True,
    }
)
if created:
    print(f"  ✅ Created employee: {manager_sales_employee.name}")
    # Set as department manager
    sales_dept.manager = manager_sales_employee
    sales_dept.save()
    print(f"  ✅ Set as Sales Department manager")
else:
    print(f"  ℹ️  Employee already exists: {manager_sales_employee.name}")

# 4. Create Employee User (IT Department)
print("\n👤 Creating Employee User (IT Department)...")
employee_user, created = User.objects.get_or_create(
    username='employee_user',
    defaults={
        'email': 'employee.it@company.com',
        'first_name': 'IT',
        'last_name': 'Staff',
        'is_staff': True,
    }
)
if created:
    employee_user.set_password('employee123456')
    employee_user.save()
    print(f"  ✅ Created user: {employee_user.username}")
else:
    print(f"  ℹ️  User already exists: {employee_user.username}")

# Add to Employee group
employee_user.groups.add(employee_group)
print(f"  ✅ Added to Employee group")

# Create corresponding Employee
staff_employee, created = Employee.objects.get_or_create(
    email='employee.it@company.com',
    defaults={
        'employee_code': 'EMP001',
        'name': 'IT Staff Member',
        'gender': 0,
        'phone': '0123456792',
        'birthday': '1995-01-01',
        'place_of_birth': 'Hanoi',
        'place_of_origin': 'Hanoi',
        'place_of_residence': 'Hanoi',
        'identification': '001095123456',
        'date_of_issue': '2020-01-01',
        'place_of_issue': 'Hanoi',
        'nationality': 'Vietnam',
        'nation': 'Kinh',
        'religion': 'None',
        'address': 'Hanoi',
        'marital_status': 0,
        'school': 'University',
        'major': 'Computer Science',
        'education_level': 3,
        'job_position': 'Staff',
        'department': it_dept,
        'job_title': staff_title,
        'salary': 15000000,
        'contract_start_date': '2020-01-01',
        'contract_duration': 12,
        'status': 2,
        'is_manager': False,
    }
)
if created:
    print(f"  ✅ Created employee: {staff_employee.name}")
else:
    print(f"  ℹ️  Employee already exists: {staff_employee.name}")

# Summary
print("\n" + "="*60)
print("✅ Test users setup complete!")
print("="*60)
print("\n📋 Test Credentials:")
print("\n1️⃣  HR User (Full Access):")
print("   Username: hr_user")
print("   Password: hr123456")
print("   Email: hr@company.com")
print("   Group: HR")
print("   Department: IT Department")
print("\n2️⃣  Manager User - IT (Department Access):")
print("   Username: manager_user")
print("   Password: manager123456")
print("   Email: manager.it@company.com")
print("   Group: Manager")
print("   Department: IT Department")
print("\n3️⃣  Manager User - Sales (Department Access):")
print("   Username: manager_sales")
print("   Password: manager123456")
print("   Email: manager.sales@company.com")
print("   Group: Manager")
print("   Department: Sales Department")
print("\n4️⃣  Employee User (Self-Service Only):")
print("   Username: employee_user")
print("   Password: employee123456")
print("   Email: employee.it@company.com")
print("   Group: Employee")
print("   Department: IT Department")
print("\n" + "="*60)
print("🧪 Testing Instructions:")
print("="*60)
print("\n✓ HR User should:")
print("  - See all contracts from all departments")
print("  - Have Create/Edit/Delete/Renew buttons visible")
print("  - Access expiring contracts report")
print("\n✓ Manager User (IT) should:")
print("  - See only IT Department contracts")
print("  - View contracts but NOT edit/delete")
print("  - Access expiring contracts report for their department")
print("\n✓ Manager User (Sales) should:")
print("  - See only Sales Department contracts")
print("  - View contracts but NOT edit/delete")
print("  - NOT see IT Department contracts")
print("\n✓ Employee User should:")
print("  - NOT access Contract Management pages")
print("  - Get 403 Forbidden or redirect messages")
print("  - Only access self-service features")
print("\n" + "="*60)
print("🌐 Test at: http://127.0.0.1:8000/contracts/")
print("="*60)
