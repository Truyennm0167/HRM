"""
Script to setup admin user with proper permissions
Run: python manage.py shell < setup_admin.py
"""

from django.contrib.auth.models import User, Group, Permission
from app.models import Employee, Department, JobTitle
from django.utils import timezone

# Get or create admin user
username = input("Enter superuser username (default: admin): ").strip() or "admin"

try:
    user = User.objects.get(username=username)
    print(f"✓ Found user: {username}")
except User.DoesNotExist:
    print(f"✗ User '{username}' not found. Please create superuser first:")
    print("  python manage.py createsuperuser")
    exit(1)

# Check if user has Employee record
try:
    employee = Employee.objects.get(email=user.email)
    print(f"✓ Found Employee record: {employee.full_name}")
except Employee.DoesNotExist:
    # Create Employee record
    print(f"Creating Employee record for {username}...")
    
    # Get or create default department
    department, created = Department.objects.get_or_create(
        name="IT",
        defaults={
            'date_establishment': timezone.now().date(),
            'description': 'IT Department'
        }
    )
    
    # Get or create default job title
    job_title, created = JobTitle.objects.get_or_create(
        title="System Administrator",
        defaults={'description': 'System Administrator'}
    )
    
    # Create employee
    employee = Employee.objects.create(
        email=user.email,
        full_name=user.username.title(),
        phone_number="0123456789",
        address="Ha Noi",
        gender='male',
        birthday=timezone.now().date(),
        department=department,
        position=job_title,
        is_manager=True,
        employee_code="NV0001",
        salary=20000000
    )
    print(f"✓ Created Employee: {employee.full_name}")

# Add to HR group
hr_group, created = Group.objects.get_or_create(name='HR')
if created:
    print("✓ Created HR group")
else:
    print("✓ Found HR group")

if not user.groups.filter(name='HR').exists():
    user.groups.add(hr_group)
    print(f"✓ Added {username} to HR group")
else:
    print(f"✓ {username} already in HR group")

# Add to Manager group
manager_group, created = Group.objects.get_or_create(name='Manager')
if created:
    print("✓ Created Manager group")
else:
    print("✓ Found Manager group")

if not user.groups.filter(name='Manager').exists():
    user.groups.add(manager_group)
    print(f"✓ Added {username} to Manager group")
else:
    print(f"✓ {username} already in Manager group")

# Set as staff
if not user.is_staff:
    user.is_staff = True
    user.save()
    print("✓ Set user as staff")

# Update employee to be manager
if not employee.is_manager:
    employee.is_manager = True
    employee.save()
    print("✓ Set employee as manager")

print("\n" + "="*50)
print("✓ Setup complete!")
print(f"User: {user.username}")
print(f"Email: {user.email}")
print(f"Groups: {', '.join([g.name for g in user.groups.all()])}")
print(f"Staff: {user.is_staff}")
print(f"Superuser: {user.is_superuser}")
print(f"Employee: {employee.full_name} ({employee.employee_code})")
print(f"Manager: {employee.is_manager}")
print("="*50)
print("\nYou can now access:")
print("  - /management/ (Admin Portal)")
print("  - /portal/ (Employee Portal)")
print("  - /admin/ (Django Admin)")
