"""
Test actual conversion with Django Test Client
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from app.models import Application, Employee

print("=" * 80)
print("TESTING ACTUAL CONVERT TO EMPLOYEE")
print("=" * 80)

# Get accepted application
app = Application.objects.filter(status='accepted', converted_to_employee=False).first()

if not app:
    print("✗ No accepted application found")
else:
    print(f"\n📋 Application Details:")
    print(f"  Code: {app.application_code}")
    print(f"  Name: {app.full_name}")
    print(f"  Email: {app.email}")
    print(f"  Job: {app.job.title}")
    print(f"  Job Title: {app.job.job_title}")
    print(f"  Department: {app.job.department}")
    
    # Get employee count before
    emp_count_before = Employee.objects.count()
    print(f"\n📊 Employees before: {emp_count_before}")
    
    # Create test client and login
    client = Client()
    admin_user = User.objects.filter(username='admin').first()
    
    if not admin_user:
        print("✗ Admin user not found")
    else:
        client.force_login(admin_user)
        print(f"✓ Logged in as: {admin_user.username}")
        
        # Test conversion
        print(f"\n🔄 Attempting conversion...")
        response = client.post(f'/recruitment/applications/{app.id}/convert/')
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect
            print(f"✓ Redirect to: {response.url}")
            
            # Check if employee was created
            app.refresh_from_db()
            emp_count_after = Employee.objects.count()
            
            print(f"\n📊 Employees after: {emp_count_after}")
            print(f"New employees: {emp_count_after - emp_count_before}")
            
            if app.converted_to_employee:
                print(f"\n✅ Conversion successful!")
                print(f"  Application converted: {app.converted_to_employee}")
                if app.employee:
                    emp = app.employee
                    print(f"  Employee created: {emp.employee_code}")
                    print(f"  Employee name: {emp.name}")
                    print(f"  Employee email: {emp.email}")
                    print(f"  Employee department: {emp.department}")
                    print(f"  Employee job_title: {emp.job_title}")
                    print(f"  Employee salary: {emp.salary:,.0f} VNĐ")
                else:
                    print(f"  ⚠️ Application marked as converted but employee link is null")
            else:
                print(f"\n✗ Conversion failed")
                print(f"  Application.converted_to_employee: {app.converted_to_employee}")
                
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content[:500]}")

print("\n" + "=" * 80)
