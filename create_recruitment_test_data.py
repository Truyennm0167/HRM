"""
Script to create sample data for Recruitment Workflow testing
Run: python manage.py shell < create_recruitment_test_data.py
"""

from django.utils import timezone
from datetime import timedelta
from app.models import JobPosting, Application, Department, JobTitle, Employee
import uuid

print("=" * 60)
print("CREATING RECRUITMENT TEST DATA")
print("=" * 60)

# Get or create departments
print("\n1. Checking departments...")
departments = Department.objects.all()
if not departments.exists():
    print("No departments found! Please create departments first.")
else:
    print(f"Found {departments.count()} departments")

# Get or create job titles
print("\n2. Checking job titles...")
job_titles = JobTitle.objects.all()
if not job_titles.exists():
    print("No job titles found! Please create job titles first.")
else:
    print(f"Found {job_titles.count()} job titles")

# Get an employee for created_by
print("\n3. Getting employee for created_by...")
try:
    creator = Employee.objects.filter(is_manager=True).first()
    if not creator:
        creator = Employee.objects.first()
    print(f"Using employee: {creator.name if creator else 'None'}")
except:
    creator = None
    print("No employees found!")

# Create sample job postings
print("\n4. Creating sample job postings...")
if departments.exists() and creator:
    dept = departments.first()
    job_title = job_titles.first() if job_titles.exists() else None
    
    # Job 1: Open position
    job1, created = JobPosting.objects.get_or_create(
        code='JOB2025001',
        defaults={
            'title': 'Senior Python Developer',
            'department': dept,
            'job_title': job_title,
            'description': 'Chúng tôi đang tìm kiếm Senior Python Developer có kinh nghiệm phát triển ứng dụng web với Django, Flask.',
            'requirements': '- 3+ năm kinh nghiệm Python\n- Thành thạo Django/Flask\n- Kinh nghiệm REST API\n- Có kinh nghiệm với PostgreSQL/MySQL',
            'responsibilities': '- Phát triển và maintain các dự án Python\n- Code review\n- Mentoring junior developers\n- Tham gia thiết kế kiến trúc hệ thống',
            'benefits': '- Lương competitive\n- Thưởng theo dự án\n- Bảo hiểm đầy đủ\n- Du lịch hàng năm',
            'employment_type': 'fulltime',
            'experience_level': 'senior',
            'number_of_positions': 2,
            'location': 'Hà Nội',
            'salary_min': 25000000,
            'salary_max': 35000000,
            'deadline': timezone.now().date() + timedelta(days=30),
            'start_date': timezone.now().date() + timedelta(days=45),
            'status': 'open',
            'contact_person': 'HR Department',
            'contact_email': 'hr@company.com',
            'contact_phone': '0123456789',
            'created_by': creator,
        }
    )
    if created:
        print(f"✓ Created: {job1.code} - {job1.title}")
    else:
        print(f"Already exists: {job1.code}")
    
    # Job 2: Another open position
    job2, created = JobPosting.objects.get_or_create(
        code='JOB2025002',
        defaults={
            'title': 'Frontend Developer (ReactJS)',
            'department': dept,
            'job_title': job_title,
            'description': 'Tìm kiếm Frontend Developer có kỹ năng tốt về ReactJS để join team phát triển sản phẩm.',
            'requirements': '- 2+ năm kinh nghiệm ReactJS\n- Thành thạo HTML/CSS/JavaScript\n- Kinh nghiệm với Redux, React Hooks\n- Biết TypeScript là lợi thế',
            'responsibilities': '- Phát triển giao diện web với ReactJS\n- Tối ưu performance\n- Làm việc với backend team\n- Maintain existing codebase',
            'benefits': '- Lương hấp dẫn\n- Làm việc với công nghệ mới\n- Team trẻ, năng động\n- Cơ hội thăng tiến',
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
    
    # Create sample applications
    print("\n5. Creating sample applications...")
    
    # Application 1: New
    app1_code = f"APP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    app1, created = Application.objects.get_or_create(
        email='nguyen.van.a@gmail.com',
        job=job1,
        defaults={
            'application_code': app1_code,
            'full_name': 'Nguyễn Văn A',
            'phone': '0987654321',
            'date_of_birth': timezone.now().date() - timedelta(days=365*28),
            'gender': 0,
            'address': 'Hà Nội',
            'current_position': 'Python Developer',
            'current_company': 'Tech Company ABC',
            'years_of_experience': 4,
            'education_level': 3,
            'school': 'Đại học Bách Khoa Hà Nội',
            'major': 'Công nghệ thông tin',
            'cover_letter': 'Tôi có 4 năm kinh nghiệm phát triển ứng dụng với Python và Django. Mong muốn được làm việc tại công ty để phát triển kỹ năng.',
            'expected_salary': 30000000,
            'available_start_date': timezone.now().date() + timedelta(days=30),
            'status': 'new',
            'source': 'website',
        }
    )
    if created:
        print(f"✓ Created application: {app1.application_code} - {app1.full_name}")
    else:
        print(f"Already exists: {app1.application_code}")
    
    # Application 2: Screening
    app2_code = f"APP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    app2, created = Application.objects.get_or_create(
        email='tran.thi.b@gmail.com',
        job=job1,
        defaults={
            'application_code': app2_code,
            'full_name': 'Trần Thị B',
            'phone': '0912345678',
            'date_of_birth': timezone.now().date() - timedelta(days=365*26),
            'gender': 1,
            'address': 'Hà Nội',
            'current_position': 'Software Engineer',
            'current_company': 'XYZ Technology',
            'years_of_experience': 3,
            'education_level': 3,
            'school': 'Đại học Công nghệ',
            'major': 'Khoa học máy tính',
            'cover_letter': 'Tôi là Software Engineer với 3 năm kinh nghiệm. Đam mê với Python và muốn phát triển sự nghiệp.',
            'expected_salary': 28000000,
            'available_start_date': timezone.now().date() + timedelta(days=20),
            'status': 'screening',
            'source': 'linkedin',
            'rating': 4,
        }
    )
    if created:
        print(f"✓ Created application: {app2.application_code} - {app2.full_name}")
    else:
        print(f"Already exists: {app2.application_code}")
    
    # Application 3: Interview
    app3_code = f"APP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    app3, created = Application.objects.get_or_create(
        email='le.van.c@gmail.com',
        job=job2,
        defaults={
            'application_code': app3_code,
            'full_name': 'Lê Văn C',
            'phone': '0976543210',
            'date_of_birth': timezone.now().date() - timedelta(days=365*25),
            'gender': 0,
            'address': 'Hà Nội',
            'current_position': 'Frontend Developer',
            'current_company': 'Digital Agency',
            'years_of_experience': 2,
            'education_level': 3,
            'school': 'Đại học FPT',
            'major': 'Kỹ thuật phần mềm',
            'cover_letter': 'Frontend Developer với 2 năm kinh nghiệm ReactJS. Thích thú với UI/UX và công nghệ mới.',
            'expected_salary': 20000000,
            'available_start_date': timezone.now().date() + timedelta(days=15),
            'status': 'interview',
            'source': 'referral',
            'rating': 5,
            'interview_date': timezone.now() + timedelta(days=3),
            'interview_location': 'Phòng họp A2, Tầng 3',
        }
    )
    if created:
        print(f"✓ Created application: {app3.application_code} - {app3.full_name}")
    else:
        print(f"Already exists: {app3.application_code}")
    
    print("\n" + "=" * 60)
    print("✓ TEST DATA CREATION COMPLETED!")
    print("=" * 60)
    print("\nSummary:")
    print(f"- Job Postings: {JobPosting.objects.count()}")
    print(f"- Applications: {Application.objects.count()}")
    print("\nYou can now test the Recruitment Workflow!")
    print("- Public page: http://127.0.0.1:8000/careers/")
    print("- Admin page: http://127.0.0.1:8000/recruitment/jobs/")
    print("- Kanban: http://127.0.0.1:8000/recruitment/applications/")
    
else:
    print("\n✗ Cannot create test data. Please ensure:")
    print("  1. At least one Department exists")
    print("  2. At least one Employee exists")
