"""
Create proper admin user and full test data
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Employee, Department, JobTitle, JobPosting, Application
from django.utils import timezone
from datetime import timedelta
import uuid

print("=" * 80)
print("CREATING ADMIN USER AND FULL TEST DATA")
print("=" * 80)

# 1. Create proper admin user
print("\n1. Creating admin user...")
try:
    # Check if admin user exists
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@hrm.com',
            password='admin123'
        )
        print(f"✓ Created superuser: admin / admin123")
    else:
        print(f"✓ Admin user already exists: {admin_user.username}")
    
    # Link to employee if needed
    employee = Employee.objects.filter(admin=admin_user).first()
    if not employee:
        dept = Department.objects.first()
        job_title = JobTitle.objects.first()
        employee = Employee.objects.create(
            admin=admin_user,
            name='Admin User',
            email='admin@hrm.com',
            gender=0,
            department=dept,
            job_title=job_title,
            is_manager=True,
            employee_code='EMP001'
        )
        print(f"✓ Created employee record for admin")
    else:
        print(f"✓ Employee exists: {employee.name}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# 2. Create more jobs
print("\n2. Creating additional job postings...")
try:
    dept = Department.objects.first()
    job_title = JobTitle.objects.first()
    creator = Employee.objects.filter(is_manager=True).first()
    
    # Job 2: Frontend Developer
    job2, created = JobPosting.objects.get_or_create(
        code='JOB2025002',
        defaults={
            'title': 'Frontend Developer (ReactJS)',
            'department': dept,
            'job_title': job_title,
            'description': 'Tìm kiếm Frontend Developer có kỹ năng tốt về ReactJS.',
            'requirements': '- 2+ năm kinh nghiệm ReactJS\n- Thành thạo HTML/CSS/JavaScript',
            'responsibilities': '- Phát triển giao diện web\n- Tối ưu performance',
            'benefits': '- Lương hấp dẫn\n- Team trẻ năng động',
            'employment_type': 'fulltime',
            'experience_level': 'middle',
            'number_of_positions': 3,
            'location': 'Hà Nội / Remote',
            'salary_min': 18000000,
            'salary_max': 25000000,
            'deadline': timezone.now().date() + timedelta(days=20),
            'start_date': timezone.now().date() + timedelta(days=35),
            'status': 'open',
            'contact_person': 'HR Department',
            'contact_email': 'hr@company.com',
            'contact_phone': '0123456789',
            'created_by': creator,
        }
    )
    if created:
        print(f"✓ Created: {job2.code} - {job2.title}")
    else:
        print(f"Already exists: {job2.code}")
    
    # Job 3: Backend Developer
    job3, created = JobPosting.objects.get_or_create(
        code='JOB2025003',
        defaults={
            'title': 'Backend Developer (Node.js)',
            'department': dept,
            'job_title': job_title,
            'description': 'Cần Backend Developer có kinh nghiệm Node.js.',
            'requirements': '- 2+ năm kinh nghiệm Node.js\n- Hiểu về microservices',
            'responsibilities': '- Phát triển APIs\n- Database design',
            'benefits': '- Lương competitive\n- Nhiều dự án thú vị',
            'employment_type': 'fulltime',
            'experience_level': 'middle',
            'number_of_positions': 2,
            'location': 'Hà Nội',
            'salary_min': 20000000,
            'salary_max': 30000000,
            'deadline': timezone.now().date() + timedelta(days=25),
            'start_date': timezone.now().date() + timedelta(days=40),
            'status': 'open',
            'contact_person': 'HR Department',
            'contact_email': 'hr@company.com',
            'contact_phone': '0123456789',
            'created_by': creator,
        }
    )
    if created:
        print(f"✓ Created: {job3.code} - {job3.title}")
    else:
        print(f"Already exists: {job3.code}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# 3. Create applications with various statuses
print("\n3. Creating test applications...")
try:
    jobs = JobPosting.objects.filter(status='open')[:2]
    if not jobs:
        print("✗ No jobs available")
    else:
        applications_data = [
            {
                'full_name': 'Nguyễn Văn A',
                'email': 'nguyenvana@gmail.com',
                'phone': '0987654321',
                'status': 'new',
                'rating': None,
            },
            {
                'full_name': 'Trần Thị B',
                'email': 'tranthib@gmail.com',
                'phone': '0912345678',
                'status': 'screening',
                'rating': 4,
            },
            {
                'full_name': 'Lê Văn C',
                'email': 'levanc@gmail.com',
                'phone': '0976543210',
                'status': 'interview',
                'rating': 5,
            },
            {
                'full_name': 'Phạm Thị D',
                'email': 'phamthid@gmail.com',
                'phone': '0965432109',
                'status': 'test',
                'rating': 4,
            },
            {
                'full_name': 'Hoàng Văn E',
                'email': 'hoangvane@gmail.com',
                'phone': '0954321098',
                'status': 'offer',
                'rating': 5,
            },
            {
                'full_name': 'Đỗ Thị F',
                'email': 'dothif@gmail.com',
                'phone': '0943210987',
                'status': 'accepted',
                'rating': 5,
            },
        ]
        
        for i, data in enumerate(applications_data):
            job = jobs[i % len(jobs)]
            app_code = f"APP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            app, created = Application.objects.get_or_create(
                email=data['email'],
                job=job,
                defaults={
                    'application_code': app_code,
                    'full_name': data['full_name'],
                    'phone': data['phone'],
                    'date_of_birth': timezone.now().date() - timedelta(days=365*28),
                    'gender': i % 2,
                    'address': 'Hà Nội',
                    'current_position': 'Software Engineer',
                    'current_company': f'Company {chr(65+i)}',
                    'years_of_experience': 2 + i,
                    'education_level': 3,
                    'school': 'Đại học Bách Khoa',
                    'major': 'Công nghệ thông tin',
                    'cover_letter': f'Tôi là {data["full_name"]}, mong muốn được làm việc tại công ty.',
                    'expected_salary': 20000000 + (i * 2000000),
                    'available_start_date': timezone.now().date() + timedelta(days=15),
                    'status': data['status'],
                    'source': 'website',
                    'rating': data['rating'],
                }
            )
            
            if created:
                print(f"✓ Created: {app.application_code} - {app.full_name} ({app.get_status_display()})")
                # Update job application count
                job.applications_count = job.applications_count + 1
                job.save()
            else:
                print(f"Already exists: {app.application_code}")
                
except Exception as e:
    print(f"✗ Error: {e}")

# 4. Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"👤 Users: {User.objects.count()}")
print(f"👥 Employees: {Employee.objects.count()}")
print(f"💼 Job Postings: {JobPosting.objects.count()}")
print(f"📝 Applications: {Application.objects.count()}")
print(f"\n✅ Admin Credentials: admin / admin123")
print(f"🌐 Admin URL: http://127.0.0.1:8000/admin/")
print(f"🌐 Careers URL: http://127.0.0.1:8000/careers/")
print(f"🌐 Kanban URL: http://127.0.0.1:8000/recruitment/applications/")
print("=" * 80)
