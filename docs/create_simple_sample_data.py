"""
Tạo dữ liệu mẫu đơn giản cho hệ thống HRM
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User, Group
from app.models import (
    Department, Employee, JobTitle, Contract, LeaveRequest, LeaveType,
    Payroll, SalaryComponent
)

print("=" * 70)
print("  TẠO DỮ LIỆU MẪU ĐƠN GIẢN")
print("=" * 70)

# Xóa dữ liệu cũ (trừ superuser)
print("\n🗑️  Xóa dữ liệu cũ...")
Employee.objects.all().delete()
Department.objects.all().delete()
JobTitle.objects.all().delete()
Contract.objects.all().delete()
LeaveRequest.objects.all().delete()
LeaveType.objects.all().delete()
Payroll.objects.all().delete()
SalaryComponent.objects.all().delete()
print("✅ Đã xóa dữ liệu cũ!")

# 1. Tạo Groups
print("\n📁 Tạo groups...")
hr_group, _ = Group.objects.get_or_create(name='HR')
manager_group, _ = Group.objects.get_or_create(name='Manager')
employee_group, _ = Group.objects.get_or_create(name='Employee')
print(f"✅ Tạo {Group.objects.count()} groups")

# 2. Tạo Departments
print("\n🏢 Tạo phòng ban...")
departments_data = [
    {'name': 'Ban Giám Đốc', 'description': 'Ban lãnh đạo công ty'},
    {'name': 'Phòng Nhân Sự', 'description': 'Quản lý nhân sự'},
    {'name': 'Phòng Kế Toán', 'description': 'Quản lý tài chính'},
    {'name': 'Phòng IT', 'description': 'Công nghệ thông tin'},
    {'name': 'Phòng Marketing', 'description': 'Marketing và truyền thông'},
]

departments = []
for dept_data in departments_data:
    dept = Department.objects.create(
        name=dept_data['name'],
        description=dept_data['description'],
        date_establishment=date(2020, 1, 1)
    )
    departments.append(dept)
    print(f"  ✓ {dept.name}")

# 3. Tạo Job Titles
print("\n💼 Tạo chức danh...")
job_titles_data = [
    {'name': 'Giám Đốc', 'description': 'Giám đốc công ty', 'salary_coefficient': 5.0},
    {'name': 'Phó Giám Đốc', 'description': 'Phó giám đốc', 'salary_coefficient': 4.0},
    {'name': 'Trưởng Phòng', 'description': 'Trưởng phòng ban', 'salary_coefficient': 3.0},
    {'name': 'Phó Phòng', 'description': 'Phó phòng ban', 'salary_coefficient': 2.5},
    {'name': 'Nhân Viên Chính', 'description': 'Nhân viên chính thức', 'salary_coefficient': 2.0},
    {'name': 'Nhân Viên', 'description': 'Nhân viên', 'salary_coefficient': 1.5},
]

job_titles = []
for jt_data in job_titles_data:
    jt = JobTitle.objects.create(**jt_data)
    job_titles.append(jt)
    print(f"  ✓ {jt.name}")

# 4. Tạo Employees
print("\n👥 Tạo nhân viên...")
employees_data = [
    # Ban Giám Đốc
    {'name': 'Nguyễn Văn An', 'dept': 'Ban Giám Đốc', 'job_title': 'Giám Đốc', 'salary': 50000000},
    {'name': 'Trần Thị Bình', 'dept': 'Ban Giám Đốc', 'job_title': 'Phó Giám Đốc', 'salary': 40000000},
    
    # Phòng Nhân Sự
    {'name': 'Lê Văn Cường', 'dept': 'Phòng Nhân Sự', 'job_title': 'Trưởng Phòng', 'salary': 25000000},
    {'name': 'Phạm Thị Dung', 'dept': 'Phòng Nhân Sự', 'job_title': 'Nhân Viên Chính', 'salary': 15000000},
    {'name': 'Hoàng Văn Em', 'dept': 'Phòng Nhân Sự', 'job_title': 'Nhân Viên', 'salary': 12000000},
    
    # Phòng Kế Toán
    {'name': 'Huỳnh Thị Giang', 'dept': 'Phòng Kế Toán', 'job_title': 'Trưởng Phòng', 'salary': 25000000},
    {'name': 'Phan Văn Hùng', 'dept': 'Phòng Kế Toán', 'job_title': 'Nhân Viên Chính', 'salary': 15000000},
    
    # Phòng IT
    {'name': 'Vũ Thị Lan', 'dept': 'Phòng IT', 'job_title': 'Trưởng Phòng', 'salary': 30000000},
    {'name': 'Võ Văn Minh', 'dept': 'Phòng IT', 'job_title': 'Nhân Viên Chính', 'salary': 20000000},
    {'name': 'Đặng Thị Nga', 'dept': 'Phòng IT', 'job_title': 'Nhân Viên Chính', 'salary': 18000000},
    {'name': 'Bùi Văn Phúc', 'dept': 'Phòng IT', 'job_title': 'Nhân Viên', 'salary': 15000000},
    
    # Phòng Marketing
    {'name': 'Đỗ Thị Quỳnh', 'dept': 'Phòng Marketing', 'job_title': 'Trưởng Phòng', 'salary': 25000000},
    {'name': 'Hồ Văn Sơn', 'dept': 'Phòng Marketing', 'job_title': 'Nhân Viên Chính', 'salary': 16000000},
    {'name': 'Ngô Thị Trang', 'dept': 'Phòng Marketing', 'job_title': 'Nhân Viên', 'salary': 13000000},
]

employees = []
for i, emp_data in enumerate(employees_data, 1):
    # Tìm Department và JobTitle
    dept = Department.objects.get(name=emp_data['dept'])
    job_title = JobTitle.objects.get(name=emp_data['job_title'])
    
    # Tạo Employee
    emp = Employee.objects.create(
        employee_code=f"NV{2024}{i:03d}",
        name=emp_data['name'],
        gender=random.choice([0, 1]),
        birthday=date(random.randint(1980, 2000), random.randint(1, 12), random.randint(1, 28)),
        place_of_birth='TP. Hồ Chí Minh',
        place_of_origin='TP. Hồ Chí Minh',
        place_of_residence=f"{random.randint(1, 200)} Nguyễn Văn Linh, Quận 7, TP.HCM",
        identification=f"0{random.randint(10000000, 99999999)}",
        date_of_issue=date(2020, 1, 1),
        place_of_issue='CA TP.HCM',
        nationality='Việt Nam',
        nation='Kinh',
        religion='Không',
        email=f"nv{i:03d}@company.com",
        phone=f"090{random.randint(1000000, 9999999)}",
        address=f"{random.randint(1, 200)} Nguyễn Văn Linh, Quận 7, TP.HCM",
        marital_status=random.choice([0, 1]),
        job_title=job_title,
        job_position=job_title.name,
        department=dept,
        is_manager=(job_title.name in ['Giám Đốc', 'Phó Giám Đốc', 'Trưởng Phòng']),
        salary=emp_data['salary'],
        contract_start_date=date(2024, 1, 1),
        contract_duration=12,
        status=2,  # Nhân viên chính thức
        education_level=3,  # Đại học
        major='Quản trị kinh doanh',
        school='Đại học Kinh tế TP.HCM',
        certificate='',
    )
    employees.append(emp)
    print(f"  ✓ {emp.name} - {dept.name} - {job_title.name}")

print(f"✅ Tạo {len(employees)} nhân viên")

# 5. Tạo Leave Types
print("\n🏖️  Tạo loại nghỉ phép...")
leave_types_data = [
    {'name': 'Phép năm', 'code': 'AL', 'max_days_per_year': 12, 'is_paid': True},
    {'name': 'Nghỉ ốm', 'code': 'SL', 'max_days_per_year': 30, 'is_paid': True},
    {'name': 'Nghỉ không lương', 'code': 'UL', 'max_days_per_year': 365, 'is_paid': False},
]

for lt_data in leave_types_data:
    LeaveType.objects.create(**lt_data)
    print(f"  ✓ {lt_data['name']}")

# 6. Tạo Salary Components
print("\n💰 Tạo các khoản lương...")
salary_components_data = [
    {
        'code': 'BASE', 
        'name': 'Lương cơ bản', 
        'component_type': 'allowance', 
        'calculation_method': 'fixed',
        'default_amount': 0,
        'is_mandatory': True
    },
    {
        'code': 'LUNCH', 
        'name': 'Phụ cấp ăn trưa', 
        'component_type': 'allowance', 
        'calculation_method': 'fixed',
        'default_amount': 1000000,
        'is_mandatory': True
    },
    {
        'code': 'TRANS', 
        'name': 'Phụ cấp xăng xe', 
        'component_type': 'allowance', 
        'calculation_method': 'fixed',
        'default_amount': 500000,
        'is_mandatory': True
    },
    {
        'code': 'SI', 
        'name': 'Bảo hiểm xã hội', 
        'component_type': 'deduction', 
        'calculation_method': 'percentage',
        'percentage': 10.5,
        'is_mandatory': True
    },
    {
        'code': 'TAX', 
        'name': 'Thuế TNCN', 
        'component_type': 'deduction', 
        'calculation_method': 'percentage',
        'percentage': 10.0,
        'is_mandatory': True
    },
]

for sc_data in salary_components_data:
    SalaryComponent.objects.create(**sc_data)
    print(f"  ✓ {sc_data['name']}")

print("\n" + "=" * 70)
print("🎉 TẠO DỮ LIỆU MẪU THÀNH CÔNG!")
print("=" * 70)
print(f"\n📊 Thống kê:")
print(f"  ✅ Phòng ban:        {Department.objects.count()}")
print(f"  ✅ Chức danh:        {JobTitle.objects.count()}")
print(f"  ✅ Nhân viên:        {Employee.objects.count()}")
print(f"  ✅ Loại nghỉ phép:   {LeaveType.objects.count()}")
print(f"  ✅ Khoản lương:      {SalaryComponent.objects.count()}")
print("\n✅ Bạn có thể chạy server và truy cập admin!")
print("   python manage.py createsuperuser  (nếu chưa có)")
print("   python manage.py runserver")
print()
