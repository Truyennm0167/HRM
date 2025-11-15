"""
Test convert to employee functionality
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from app.models import Application, Employee, JobPosting, Department, JobTitle
from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from app.HodViews import convert_to_employee

print("=" * 80)
print("TESTING CONVERT TO EMPLOYEE FUNCTION")
print("=" * 80)

# 1. Check if we have an accepted application
print("\n1. Checking for accepted applications...")
accepted_apps = Application.objects.filter(status='accepted', converted_to_employee=False)
print(f"Found {accepted_apps.count()} accepted applications ready for conversion")

if accepted_apps.exists():
    app = accepted_apps.first()
    print(f"\nApplication to test:")
    print(f"  Code: {app.application_code}")
    print(f"  Name: {app.full_name}")
    print(f"  Email: {app.email}")
    print(f"  Status: {app.get_status_display()}")
    print(f"  Can convert: {app.can_convert_to_employee()}")
    
    # 2. Check method implementation
    print("\n2. Checking can_convert_to_employee() method...")
    try:
        can_convert = app.can_convert_to_employee()
        print(f"✓ Method works: {can_convert}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 3. Check required job fields
    print("\n3. Checking job posting data...")
    job = app.job
    print(f"  Job: {job.title}")
    print(f"  Department: {job.department}")
    print(f"  Job Title: {job.job_title}")
    print(f"  Salary Min: {job.salary_min}")
    print(f"  Salary Max: {job.salary_max}")
    
    # 4. Test conversion logic (dry run)
    print("\n4. Testing conversion logic (dry run)...")
    try:
        # Simulate employee creation
        test_employee = Employee()
        test_employee.name = app.full_name
        test_employee.email = app.email
        test_employee.phone = app.phone
        test_employee.birthday = app.date_of_birth
        test_employee.gender = app.gender if app.gender is not None else 0
        test_employee.address = app.address or ''
        test_employee.education_level = app.education_level if app.education_level is not None else 3
        test_employee.major = app.major or ''
        test_employee.school = app.school or ''
        
        print("✓ Basic fields populated")
        
        # Required fields
        test_employee.place_of_birth = ''
        test_employee.place_of_origin = ''
        test_employee.place_of_residence = app.address or ''
        test_employee.identification = ''
        test_employee.nationality = 'Việt Nam'
        test_employee.nation = 'Kinh'
        test_employee.religion = ''
        test_employee.marital_status = 0
        
        print("✓ Required fields set")
        
        # Job fields
        if job.job_title:
            test_employee.job_title = job.job_title
            print(f"✓ Job title assigned: {job.job_title}")
        test_employee.job_position = job.title
        test_employee.department = job.department
        test_employee.salary = app.expected_salary or job.salary_min or 10000000
        
        print(f"✓ Job fields assigned:")
        print(f"  Position: {test_employee.job_position}")
        print(f"  Department: {test_employee.department}")
        print(f"  Salary: {test_employee.salary:,.0f} VNĐ")
        
        # Employee code
        from app.HodViews import generate_employee_code
        test_code = generate_employee_code()
        print(f"✓ Generated employee code: {test_code}")
        
        print("\n✅ All conversion logic checks passed!")
        print("\nReady to convert via UI or:")
        print(f"  URL: http://127.0.0.1:8000/recruitment/applications/{app.id}/")
        print(f"  Click 'Chuyển thành nhân viên' button")
        
    except Exception as e:
        print(f"\n✗ Error in conversion logic: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Check Employee model fields
    print("\n5. Checking Employee model compatibility...")
    try:
        # Get all required fields
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(app_employee)")
            columns = cursor.fetchall()
            
        print(f"Employee table has {len(columns)} columns:")
        required_fields = ['name', 'email', 'phone', 'birthday', 'gender', 'department_id', 
                          'job_title_id', 'salary', 'employee_code', 'status']
        
        column_names = [col[1] for col in columns]
        for field in required_fields:
            status = "✓" if field in column_names else "✗"
            print(f"  {status} {field}")
            
    except Exception as e:
        print(f"✗ Error checking model: {e}")
    
else:
    print("\n⚠️ No accepted applications found!")
    print("Creating one for testing...")
    
    try:
        # Get first open job
        job = JobPosting.objects.filter(status='open').first()
        if job:
            from django.utils import timezone
            import uuid
            
            app_code = f"APP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            test_app = Application.objects.create(
                job=job,
                application_code=app_code,
                full_name='Test Candidate for Conversion',
                email='test.conversion@example.com',
                phone='0999999999',
                date_of_birth=timezone.now().date().replace(year=1995),
                gender=0,
                address='Hà Nội',
                current_position='Developer',
                current_company='Test Company',
                years_of_experience=3,
                education_level=3,
                school='Test University',
                major='Computer Science',
                expected_salary=25000000,
                status='accepted',
                source='website'
            )
            print(f"✓ Created test application: {test_app.application_code}")
            print(f"  URL: http://127.0.0.1:8000/recruitment/applications/{test_app.id}/")
        else:
            print("✗ No open jobs available to create test application")
    except Exception as e:
        print(f"✗ Error creating test application: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
