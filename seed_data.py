"""
Script tạo dữ liệu mẫu cho hệ thống HRM
Chạy: python manage.py shell < seed_data.py
Hoặc: python manage.py runscript seed_data (nếu cài django-extensions)
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.utils import timezone
from app.models import (
    Department, JobTitle, Employee, Reward, Discipline, 
    Attendance, Payroll, Evaluation,
    LeaveType, LeaveBalance, LeaveRequest,
    ExpenseCategory, Expense,
    JobPosting, Application
)

# Xóa dữ liệu cũ (tùy chọn)
print("Đang xóa dữ liệu cũ...")
Application.objects.all().delete()
JobPosting.objects.all().delete()
Expense.objects.all().delete()
ExpenseCategory.objects.all().delete()
LeaveRequest.objects.all().delete()
LeaveBalance.objects.all().delete()
LeaveType.objects.all().delete()
Payroll.objects.all().delete()
Evaluation.objects.all().delete()
Attendance.objects.all().delete()
Discipline.objects.all().delete()
Reward.objects.all().delete()
Employee.objects.all().delete()
Department.objects.all().delete()
JobTitle.objects.all().delete()
print("✓ Đã xóa dữ liệu cũ")

# ============================================================================
# 1. TẠO CHỨC DANH (Job Titles)
# ============================================================================
print("\n1. Tạo chức danh...")
job_titles_data = [
    {"name": "Giám đốc", "salary_coefficient": 8.0, "description": "Điều hành toàn bộ công ty"},
    {"name": "Phó Giám đốc", "salary_coefficient": 7.0, "description": "Hỗ trợ Giám đốc điều hành"},
    {"name": "Trưởng phòng", "salary_coefficient": 5.5, "description": "Quản lý phòng ban"},
    {"name": "Phó phòng", "salary_coefficient": 4.5, "description": "Hỗ trợ Trưởng phòng"},
    {"name": "Chuyên viên cao cấp", "salary_coefficient": 4.0, "description": "Chuyên viên có kinh nghiệm"},
    {"name": "Chuyên viên", "salary_coefficient": 3.0, "description": "Nhân viên chính thức"},
    {"name": "Nhân viên", "salary_coefficient": 2.5, "description": "Nhân viên văn phòng"},
    {"name": "Thực tập sinh", "salary_coefficient": 1.5, "description": "Đang trong thời gian thực tập"},
]

job_titles = {}
for jt in job_titles_data:
    job_titles[jt["name"]] = JobTitle.objects.create(**jt)
print(f"✓ Đã tạo {len(job_titles)} chức danh")

# ============================================================================
# 2. TẠO PHÒNG BAN (Departments)
# ============================================================================
print("\n2. Tạo phòng ban...")
departments_data = [
    {"name": "Ban Giám đốc", "description": "Điều hành công ty", "date_establishment": date(2015, 1, 1)},
    {"name": "Phòng Nhân sự", "description": "Quản lý nhân sự, tuyển dụng, đào tạo", "date_establishment": date(2015, 1, 15)},
    {"name": "Phòng Kế toán - Tài chính", "description": "Quản lý tài chính, kế toán", "date_establishment": date(2015, 1, 15)},
    {"name": "Phòng Công nghệ thông tin", "description": "Phát triển và quản trị hệ thống IT", "date_establishment": date(2016, 3, 1)},
    {"name": "Phòng Kinh doanh", "description": "Bán hàng và phát triển thị trường", "date_establishment": date(2015, 2, 1)},
    {"name": "Phòng Marketing", "description": "Marketing và truyền thông", "date_establishment": date(2017, 6, 1)},
    {"name": "Phòng Hành chính", "description": "Quản lý hành chính, văn phòng", "date_establishment": date(2015, 1, 15)},
    {"name": "Phòng Chăm sóc khách hàng", "description": "Hỗ trợ và chăm sóc khách hàng", "date_establishment": date(2018, 1, 1)},
]

departments = {}
for dept in departments_data:
    departments[dept["name"]] = Department.objects.create(**dept)
print(f"✓ Đã tạo {len(departments)} phòng ban")

# ============================================================================
# 3. TẠO NHÂN VIÊN (Employees)
# ============================================================================
print("\n3. Tạo nhân viên...")

# Họ và tên Việt Nam thực tế
ho_list = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", 
           "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Lương", "Mai", "Trịnh"]
dem_list = ["Văn", "Thị", "Hoàng", "Hữu", "Minh", "Quốc", "Đức", "Thanh", "Xuân", "Ngọc", 
            "Kim", "Anh", "Thành", "Phương", "Bảo", "Quang", "Hải", "Tuấn", "Công", "Mạnh"]
ten_nam = ["Hùng", "Dũng", "Mạnh", "Cường", "Tuấn", "Đức", "Thắng", "Quân", "Bình", "Phong",
           "Long", "Khang", "Kiệt", "Vinh", "Tùng", "Nam", "Trung", "Hải", "Sơn", "Đạt"]
ten_nu = ["Hương", "Lan", "Hoa", "Thảo", "Linh", "Hạnh", "Ngọc", "Mai", "Trang", "Yến",
          "Nhung", "Chi", "Vy", "Trinh", "Oanh", "Hà", "Như", "Phương", "Thùy", "Diệu"]

tinh_thanh = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", 
              "Nghệ An", "Thanh Hóa", "Bình Dương", "Đồng Nai", "Quảng Ninh",
              "Bắc Ninh", "Thái Nguyên", "Nam Định", "Hải Dương", "Vĩnh Phúc"]

truong_dai_hoc = ["Đại học Bách khoa Hà Nội", "Đại học Kinh tế Quốc dân", 
                 "Đại học Ngoại thương", "Đại học FPT", "Đại học Công nghệ - ĐHQGHN",
                 "Đại học Kinh tế TP.HCM", "Đại học Bách khoa TP.HCM",
                 "Học viện Ngân hàng", "Đại học Thương mại", "Đại học Công nghiệp Hà Nội"]

nganh_hoc = {
    "Phòng Công nghệ thông tin": ["Công nghệ thông tin", "Khoa học máy tính", "Kỹ thuật phần mềm", "An toàn thông tin"],
    "Phòng Kế toán - Tài chính": ["Kế toán", "Tài chính ngân hàng", "Kiểm toán", "Quản trị tài chính"],
    "Phòng Nhân sự": ["Quản trị nhân lực", "Quản trị kinh doanh", "Tâm lý học", "Luật"],
    "Phòng Kinh doanh": ["Quản trị kinh doanh", "Marketing", "Kinh tế", "Thương mại quốc tế"],
    "Phòng Marketing": ["Marketing", "Truyền thông", "Quan hệ công chúng", "Thiết kế đồ họa"],
    "Phòng Hành chính": ["Quản trị văn phòng", "Quản trị kinh doanh", "Hành chính học"],
    "Phòng Chăm sóc khách hàng": ["Quản trị kinh doanh", "Marketing", "Truyền thông"],
    "Ban Giám đốc": ["Quản trị kinh doanh", "Kinh tế", "Tài chính"],
}

employees_data = [
    # Ban Giám đốc
    {"code": "GD001", "dept": "Ban Giám đốc", "job": "Giám đốc", "is_manager": True, "gender": 0, "salary": 80000000, "status": 2, "edu": 4},
    {"code": "PGD001", "dept": "Ban Giám đốc", "job": "Phó Giám đốc", "is_manager": True, "gender": 0, "salary": 60000000, "status": 2, "edu": 4},
    
    # Phòng Nhân sự
    {"code": "HR001", "dept": "Phòng Nhân sự", "job": "Trưởng phòng", "is_manager": True, "gender": 1, "salary": 35000000, "status": 2, "edu": 3},
    {"code": "HR002", "dept": "Phòng Nhân sự", "job": "Chuyên viên cao cấp", "is_manager": False, "gender": 1, "salary": 22000000, "status": 2, "edu": 3},
    {"code": "HR003", "dept": "Phòng Nhân sự", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 15000000, "status": 2, "edu": 3},
    {"code": "HR004", "dept": "Phòng Nhân sự", "job": "Nhân viên", "is_manager": False, "gender": 1, "salary": 12000000, "status": 1, "edu": 3},
    
    # Phòng Kế toán - Tài chính
    {"code": "FIN001", "dept": "Phòng Kế toán - Tài chính", "job": "Trưởng phòng", "is_manager": True, "gender": 1, "salary": 38000000, "status": 2, "edu": 4},
    {"code": "FIN002", "dept": "Phòng Kế toán - Tài chính", "job": "Phó phòng", "is_manager": False, "gender": 1, "salary": 28000000, "status": 2, "edu": 3},
    {"code": "FIN003", "dept": "Phòng Kế toán - Tài chính", "job": "Chuyên viên cao cấp", "is_manager": False, "gender": 1, "salary": 20000000, "status": 2, "edu": 3},
    {"code": "FIN004", "dept": "Phòng Kế toán - Tài chính", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 16000000, "status": 2, "edu": 3},
    {"code": "FIN005", "dept": "Phòng Kế toán - Tài chính", "job": "Nhân viên", "is_manager": False, "gender": 1, "salary": 13000000, "status": 2, "edu": 3},
    
    # Phòng Công nghệ thông tin
    {"code": "IT001", "dept": "Phòng Công nghệ thông tin", "job": "Trưởng phòng", "is_manager": True, "gender": 0, "salary": 45000000, "status": 2, "edu": 4},
    {"code": "IT002", "dept": "Phòng Công nghệ thông tin", "job": "Phó phòng", "is_manager": False, "gender": 0, "salary": 35000000, "status": 2, "edu": 3},
    {"code": "IT003", "dept": "Phòng Công nghệ thông tin", "job": "Chuyên viên cao cấp", "is_manager": False, "gender": 0, "salary": 30000000, "status": 2, "edu": 3},
    {"code": "IT004", "dept": "Phòng Công nghệ thông tin", "job": "Chuyên viên cao cấp", "is_manager": False, "gender": 0, "salary": 28000000, "status": 2, "edu": 3},
    {"code": "IT005", "dept": "Phòng Công nghệ thông tin", "job": "Chuyên viên", "is_manager": False, "gender": 0, "salary": 22000000, "status": 2, "edu": 3},
    {"code": "IT006", "dept": "Phòng Công nghệ thông tin", "job": "Chuyên viên", "is_manager": False, "gender": 0, "salary": 20000000, "status": 2, "edu": 3},
    {"code": "IT007", "dept": "Phòng Công nghệ thông tin", "job": "Nhân viên", "is_manager": False, "gender": 0, "salary": 15000000, "status": 1, "edu": 3},
    {"code": "IT008", "dept": "Phòng Công nghệ thông tin", "job": "Thực tập sinh", "is_manager": False, "gender": 0, "salary": 5000000, "status": 0, "edu": 3},
    
    # Phòng Kinh doanh
    {"code": "SALE001", "dept": "Phòng Kinh doanh", "job": "Trưởng phòng", "is_manager": True, "gender": 0, "salary": 40000000, "status": 2, "edu": 3},
    {"code": "SALE002", "dept": "Phòng Kinh doanh", "job": "Phó phòng", "is_manager": False, "gender": 0, "salary": 30000000, "status": 2, "edu": 3},
    {"code": "SALE003", "dept": "Phòng Kinh doanh", "job": "Chuyên viên cao cấp", "is_manager": False, "gender": 0, "salary": 25000000, "status": 2, "edu": 3},
    {"code": "SALE004", "dept": "Phòng Kinh doanh", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 18000000, "status": 2, "edu": 3},
    {"code": "SALE005", "dept": "Phòng Kinh doanh", "job": "Chuyên viên", "is_manager": False, "gender": 0, "salary": 16000000, "status": 2, "edu": 3},
    {"code": "SALE006", "dept": "Phòng Kinh doanh", "job": "Nhân viên", "is_manager": False, "gender": 1, "salary": 14000000, "status": 2, "edu": 3},
    {"code": "SALE007", "dept": "Phòng Kinh doanh", "job": "Nhân viên", "is_manager": False, "gender": 0, "salary": 12000000, "status": 1, "edu": 3},
    
    # Phòng Marketing
    {"code": "MKT001", "dept": "Phòng Marketing", "job": "Trưởng phòng", "is_manager": True, "gender": 1, "salary": 35000000, "status": 2, "edu": 3},
    {"code": "MKT002", "dept": "Phòng Marketing", "job": "Chuyên viên cao cấp", "is_manager": False, "gender": 1, "salary": 22000000, "status": 2, "edu": 3},
    {"code": "MKT003", "dept": "Phòng Marketing", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 16000000, "status": 2, "edu": 3},
    {"code": "MKT004", "dept": "Phòng Marketing", "job": "Nhân viên", "is_manager": False, "gender": 0, "salary": 13000000, "status": 2, "edu": 3},
    
    # Phòng Hành chính
    {"code": "ADM001", "dept": "Phòng Hành chính", "job": "Trưởng phòng", "is_manager": True, "gender": 1, "salary": 28000000, "status": 2, "edu": 3},
    {"code": "ADM002", "dept": "Phòng Hành chính", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 14000000, "status": 2, "edu": 3},
    {"code": "ADM003", "dept": "Phòng Hành chính", "job": "Nhân viên", "is_manager": False, "gender": 1, "salary": 11000000, "status": 2, "edu": 2},
    
    # Phòng Chăm sóc khách hàng
    {"code": "CS001", "dept": "Phòng Chăm sóc khách hàng", "job": "Trưởng phòng", "is_manager": True, "gender": 1, "salary": 30000000, "status": 2, "edu": 3},
    {"code": "CS002", "dept": "Phòng Chăm sóc khách hàng", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 15000000, "status": 2, "edu": 3},
    {"code": "CS003", "dept": "Phòng Chăm sóc khách hàng", "job": "Chuyên viên", "is_manager": False, "gender": 1, "salary": 14000000, "status": 2, "edu": 3},
    {"code": "CS004", "dept": "Phòng Chăm sóc khách hàng", "job": "Nhân viên", "is_manager": False, "gender": 0, "salary": 12000000, "status": 2, "edu": 3},
    {"code": "CS005", "dept": "Phòng Chăm sóc khách hàng", "job": "Nhân viên", "is_manager": False, "gender": 1, "salary": 11000000, "status": 1, "edu": 2},
]

employees = {}
used_names = set()
used_phones = set()
used_cccd = set()

for i, emp_data in enumerate(employees_data):
    # Tạo tên ngẫu nhiên không trùng
    while True:
        ho = random.choice(ho_list)
        dem = random.choice(dem_list)
        gender = emp_data["gender"]
        ten = random.choice(ten_nam if gender == 0 else ten_nu)
        full_name = f"{ho} {dem} {ten}"
        if full_name not in used_names:
            used_names.add(full_name)
            break
    
    # Tạo ngày sinh (25-55 tuổi, manager thường lớn tuổi hơn)
    if emp_data["is_manager"] or emp_data["job"] in ["Giám đốc", "Phó Giám đốc"]:
        birth_year = random.randint(1970, 1985)
    elif emp_data["job"] == "Thực tập sinh":
        birth_year = random.randint(1998, 2002)
    else:
        birth_year = random.randint(1985, 1998)
    
    birthday = date(birth_year, random.randint(1, 12), random.randint(1, 28))
    
    # Nơi sinh và quê quán
    place_of_birth = random.choice(tinh_thanh)
    place_of_origin = random.choice(tinh_thanh)
    
    # CCCD
    while True:
        cccd = f"0{random.randint(10, 99)}{random.randint(100000000, 999999999)}"
        if cccd not in used_cccd:
            used_cccd.add(cccd)
            break
    
    # Số điện thoại
    while True:
        phone = f"0{random.choice(['9', '8', '7', '3', '5'])}{random.randint(10000000, 99999999)}"
        if phone not in used_phones:
            used_phones.add(phone)
            break
    
    # Email
    email_name = full_name.lower().replace(" ", ".").replace("ă", "a").replace("â", "a").replace("đ", "d").replace("ê", "e").replace("ô", "o").replace("ơ", "o").replace("ư", "u").replace("á", "a").replace("à", "a").replace("ả", "a").replace("ã", "a").replace("ạ", "a").replace("é", "e").replace("è", "e").replace("ẻ", "e").replace("ẽ", "e").replace("ẹ", "e").replace("í", "i").replace("ì", "i").replace("ỉ", "i").replace("ĩ", "i").replace("ị", "i").replace("ó", "o").replace("ò", "o").replace("ỏ", "o").replace("õ", "o").replace("ọ", "o").replace("ú", "u").replace("ù", "u").replace("ủ", "u").replace("ũ", "u").replace("ụ", "u").replace("ý", "y").replace("ỳ", "y").replace("ỷ", "y").replace("ỹ", "y").replace("ỵ", "y").replace("ắ", "a").replace("ằ", "a").replace("ẳ", "a").replace("ẵ", "a").replace("ặ", "a").replace("ấ", "a").replace("ầ", "a").replace("ẩ", "a").replace("ẫ", "a").replace("ậ", "a").replace("ế", "e").replace("ề", "e").replace("ể", "e").replace("ễ", "e").replace("ệ", "e").replace("ố", "o").replace("ồ", "o").replace("ổ", "o").replace("ỗ", "o").replace("ộ", "o").replace("ớ", "o").replace("ờ", "o").replace("ở", "o").replace("ỡ", "o").replace("ợ", "o").replace("ứ", "u").replace("ừ", "u").replace("ử", "u").replace("ữ", "u").replace("ự", "u")
    email = f"{email_name}@company.com"
    
    # Ngày bắt đầu hợp đồng
    if emp_data["job"] in ["Giám đốc", "Phó Giám đốc"]:
        contract_start = date(2015, random.randint(1, 3), random.randint(1, 28))
    elif emp_data["is_manager"]:
        contract_start = date(random.randint(2016, 2020), random.randint(1, 12), random.randint(1, 28))
    elif emp_data["status"] == 0:  # Thực tập
        contract_start = date(2025, random.randint(9, 11), random.randint(1, 28))
    elif emp_data["status"] == 1:  # Thử việc
        contract_start = date(2025, random.randint(10, 11), random.randint(1, 28))
    else:
        contract_start = date(random.randint(2019, 2024), random.randint(1, 12), random.randint(1, 28))
    
    # Thời hạn hợp đồng
    if emp_data["status"] == 0:  # Thực tập
        contract_duration = 3
    elif emp_data["status"] == 1:  # Thử việc
        contract_duration = 2
    else:
        contract_duration = random.choice([12, 24, 36])
    
    # Trường và ngành học
    dept_name = emp_data["dept"]
    school = random.choice(truong_dai_hoc)
    major = random.choice(nganh_hoc.get(dept_name, ["Quản trị kinh doanh"]))
    
    # Địa chỉ
    address = f"Số {random.randint(1, 200)}, Đường {random.choice(['Nguyễn Trãi', 'Lê Văn Lương', 'Trần Duy Hưng', 'Phạm Hùng', 'Láng Hạ', 'Kim Mã', 'Hoàng Quốc Việt', 'Cầu Giấy'])}, {random.choice(['Hà Nội', 'TP. Hồ Chí Minh'])}"
    
    employee = Employee.objects.create(
        employee_code=emp_data["code"],
        name=full_name,
        gender=emp_data["gender"],
        birthday=birthday,
        place_of_birth=place_of_birth,
        place_of_origin=place_of_origin,
        place_of_residence=place_of_birth,
        identification=cccd,
        date_of_issue=date(2020, random.randint(1, 12), random.randint(1, 28)),
        place_of_issue="Cục Cảnh sát QLHC về TTXH",
        nationality="Việt Nam",
        nation="Kinh",
        religion="Không",
        email=email,
        phone=phone,
        address=address,
        marital_status=random.choice([0, 1]) if birth_year < 1995 else 0,
        job_title=job_titles[emp_data["job"]],
        job_position=emp_data["job"],
        department=departments[emp_data["dept"]],
        is_manager=emp_data["is_manager"],
        salary=emp_data["salary"],
        contract_start_date=contract_start,
        contract_duration=contract_duration,
        status=emp_data["status"],
        education_level=emp_data["edu"],
        major=major,
        school=school,
        certificate="TOEIC 700, Tin học văn phòng" if random.random() > 0.5 else ""
    )
    employees[emp_data["code"]] = employee

print(f"✓ Đã tạo {len(employees)} nhân viên")

# ============================================================================
# 4. TẠO LOẠI NGHỈ PHÉP (Leave Types)
# ============================================================================
print("\n4. Tạo loại nghỉ phép...")
leave_types_data = [
    {"name": "Phép năm", "code": "AL", "max_days_per_year": 12, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ ốm", "code": "SL", "max_days_per_year": 30, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ cưới (bản thân)", "code": "WL", "max_days_per_year": 3, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ tang", "code": "FL", "max_days_per_year": 3, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ thai sản", "code": "ML", "max_days_per_year": 180, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ không lương", "code": "UL", "max_days_per_year": 30, "requires_approval": True, "is_paid": False},
]

leave_types = {}
for lt in leave_types_data:
    leave_types[lt["code"]] = LeaveType.objects.create(**lt)
print(f"✓ Đã tạo {len(leave_types)} loại nghỉ phép")

# ============================================================================
# 5. TẠO SỐ DƯ NGÀY PHÉP (Leave Balance)
# ============================================================================
print("\n5. Tạo số dư ngày phép...")
leave_balance_count = 0
for emp_code, emp in employees.items():
    if emp.status in [2]:  # Chỉ nhân viên chính thức
        for lt_code, lt in leave_types.items():
            if lt_code == "ML" and emp.gender == 0:  # Nam không có thai sản
                continue
            used = random.randint(0, min(5, lt.max_days_per_year))
            LeaveBalance.objects.create(
                employee=emp,
                leave_type=lt,
                year=2025,
                total_days=lt.max_days_per_year,
                used_days=used,
                remaining_days=lt.max_days_per_year - used
            )
            leave_balance_count += 1
print(f"✓ Đã tạo {leave_balance_count} bản ghi số dư ngày phép")

# ============================================================================
# 6. TẠO ĐƠN XIN NGHỈ PHÉP (Leave Requests)
# ============================================================================
print("\n6. Tạo đơn xin nghỉ phép...")
leave_request_count = 0
hr_manager = employees.get("HR001")

for emp_code, emp in employees.items():
    if emp.status not in [2]:  # Chỉ nhân viên chính thức
        continue
    # Mỗi nhân viên có 0-3 đơn nghỉ phép
    for _ in range(random.randint(0, 3)):
        lt = random.choice([leave_types["AL"], leave_types["SL"]])
        start_date = date(2025, random.randint(1, 11), random.randint(1, 28))
        total_days = random.randint(1, 3)
        end_date = start_date + timedelta(days=total_days - 1)
        status = random.choice(["approved", "approved", "approved", "pending", "rejected"])
        
        LeaveRequest.objects.create(
            employee=emp,
            leave_type=lt,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=random.choice([
                "Về quê thăm gia đình",
                "Bị cảm, cần nghỉ ngơi",
                "Có việc gia đình cần giải quyết",
                "Đi khám sức khỏe định kỳ",
                "Đưa con đi học",
                "Có lịch hẹn bác sĩ"
            ]),
            status=status,
            approved_by=hr_manager if status in ["approved", "rejected"] else None,
            approved_at=timezone.now() - timedelta(days=random.randint(1, 30)) if status in ["approved", "rejected"] else None,
            rejection_reason="Không đủ số ngày phép" if status == "rejected" else ""
        )
        leave_request_count += 1
print(f"✓ Đã tạo {leave_request_count} đơn xin nghỉ phép")

# ============================================================================
# 7. TẠO DANH MỤC CHI PHÍ (Expense Categories)
# ============================================================================
print("\n7. Tạo danh mục chi phí...")
expense_categories_data = [
    {"name": "Đi lại", "code": "TRAVEL", "description": "Chi phí xăng xe, taxi, grab..."},
    {"name": "Ăn uống", "code": "FOOD", "description": "Chi phí tiếp khách, ăn trưa công tác..."},
    {"name": "Khách sạn", "code": "HOTEL", "description": "Chi phí lưu trú công tác"},
    {"name": "Văn phòng phẩm", "code": "OFFICE", "description": "Chi phí mua VPP"},
    {"name": "Đào tạo", "code": "TRAINING", "description": "Chi phí học tập, khóa học"},
    {"name": "Khác", "code": "OTHER", "description": "Chi phí khác"},
]

expense_categories = {}
for cat in expense_categories_data:
    expense_categories[cat["code"]] = ExpenseCategory.objects.create(**cat)
print(f"✓ Đã tạo {len(expense_categories)} danh mục chi phí")

# ============================================================================
# 8. TẠO YÊU CẦU HOÀN TIỀN (Expenses)
# ============================================================================
print("\n8. Tạo yêu cầu hoàn tiền...")
expense_count = 0
for emp_code, emp in employees.items():
    if emp.status not in [2]:
        continue
    # Mỗi nhân viên có 0-5 yêu cầu hoàn tiền
    for _ in range(random.randint(0, 5)):
        cat = random.choice(list(expense_categories.values()))
        amount = random.choice([50000, 100000, 150000, 200000, 300000, 500000, 1000000, 2000000])
        status = random.choice(["approved", "approved", "pending", "paid", "rejected"])
        
        Expense.objects.create(
            employee=emp,
            category=cat,
            amount=Decimal(amount),
            date=date(2025, random.randint(1, 11), random.randint(1, 28)),
            description=random.choice([
                f"Chi phí {cat.name.lower()} cho dự án ABC",
                f"Tiền {cat.name.lower()} tháng {random.randint(1, 11)}",
                f"Thanh toán {cat.name.lower()} công tác Đà Nẵng",
                f"{cat.name} cho cuộc họp khách hàng",
            ]),
            status=status,
            approved_by=hr_manager if status in ["approved", "paid", "rejected"] else None,
            approved_at=timezone.now() - timedelta(days=random.randint(1, 30)) if status in ["approved", "paid", "rejected"] else None
        )
        expense_count += 1
print(f"✓ Đã tạo {expense_count} yêu cầu hoàn tiền")

# ============================================================================
# 9. TẠO CHẤM CÔNG (Attendance)
# ============================================================================
print("\n9. Tạo dữ liệu chấm công...")
attendance_count = 0

# Tạo chấm công cho 3 tháng gần nhất
for month in [9, 10, 11]:
    for day in range(1, 29):
        try:
            current_date = date(2025, month, day)
        except ValueError:
            continue
        
        # Bỏ qua thứ 7, CN
        if current_date.weekday() >= 5:
            continue
        
        for emp_code, emp in employees.items():
            if emp.status == 3:  # Đã nghỉ việc
                continue
            
            # 90% đi làm, 5% nghỉ phép, 5% nghỉ không phép
            rand = random.random()
            if rand < 0.90:
                status = "Có làm việc"
                working_hours = random.choice([8.0, 8.0, 8.0, 8.5, 7.5, 9.0])
            elif rand < 0.95:
                status = "Nghỉ phép"
                working_hours = 0
            else:
                status = "Nghỉ không phép"
                working_hours = 0
            
            Attendance.objects.create(
                employee=emp,
                date=timezone.make_aware(datetime.combine(current_date, datetime.min.time())),
                status=status,
                working_hours=working_hours,
                notes="" if status == "Có làm việc" else random.choice(["", "Đã báo trước", "Việc gia đình"])
            )
            attendance_count += 1

print(f"✓ Đã tạo {attendance_count} bản ghi chấm công")

# ============================================================================
# 10. TẠO KHEN THƯỞNG (Rewards)
# ============================================================================
print("\n10. Tạo khen thưởng...")
rewards_data = [
    {"emp": "IT001", "desc": "Hoàn thành xuất sắc dự án ERP", "amount": 10000000},
    {"emp": "SALE001", "desc": "Vượt 150% chỉ tiêu doanh số Q3/2025", "amount": 15000000},
    {"emp": "IT003", "desc": "Phát hiện và khắc phục lỗi bảo mật nghiêm trọng", "amount": 5000000},
    {"emp": "HR001", "desc": "Tổ chức thành công team building 2025", "amount": 3000000},
    {"emp": "FIN001", "desc": "Tối ưu quy trình kế toán, tiết kiệm 20% thời gian", "amount": 8000000},
    {"emp": "MKT001", "desc": "Chiến dịch marketing tăng 200% traffic", "amount": 7000000},
    {"emp": "IT004", "desc": "Hoàn thành khóa đào tạo AWS với chứng chỉ", "amount": 2000000},
    {"emp": "SALE003", "desc": "Ký hợp đồng lớn với khách hàng ABC Corp", "amount": 12000000},
    {"emp": "CS001", "desc": "Đạt 98% độ hài lòng khách hàng", "amount": 5000000},
    {"emp": "IT002", "desc": "Mentor xuất sắc cho team IT", "amount": 3000000},
]

reward_count = 0
for i, r in enumerate(rewards_data, 1):
    if r["emp"] in employees:
        Reward.objects.create(
            number=i,
            description=r["desc"],
            date=timezone.now() - timedelta(days=random.randint(1, 300)),
            amount=r["amount"],
            cash_payment=True,
            employee=employees[r["emp"]]
        )
        reward_count += 1
print(f"✓ Đã tạo {reward_count} khen thưởng")

# ============================================================================
# 11. TẠO KỶ LUẬT (Disciplines)
# ============================================================================
print("\n11. Tạo kỷ luật...")
disciplines_data = [
    {"emp": "SALE007", "desc": "Đi làm muộn quá 5 lần trong tháng", "amount": 500000},
    {"emp": "IT008", "desc": "Không tuân thủ quy trình bảo mật", "amount": 1000000},
    {"emp": "CS005", "desc": "Phản hồi khách hàng không đúng quy trình", "amount": 300000},
]

discipline_count = 0
for i, d in enumerate(disciplines_data, 1):
    if d["emp"] in employees:
        Discipline.objects.create(
            number=i,
            description=d["desc"],
            date=timezone.now() - timedelta(days=random.randint(1, 180)),
            amount=d["amount"],
            employee=employees[d["emp"]]
        )
        discipline_count += 1
print(f"✓ Đã tạo {discipline_count} kỷ luật")

# ============================================================================
# 12. TẠO ĐÁNH GIÁ (Evaluations)
# ============================================================================
print("\n12. Tạo đánh giá nhân viên...")
evaluation_count = 0
periods = ["Q1/2025", "Q2/2025", "Q3/2025"]

for emp_code, emp in employees.items():
    if emp.status not in [2]:  # Chỉ nhân viên chính thức
        continue
    
    for period in periods:
        score = round(random.uniform(3.0, 5.0), 1)
        comments = {
            5.0: "Xuất sắc, vượt mọi kỳ vọng",
            4.5: "Rất tốt, hoàn thành vượt mức",
            4.0: "Tốt, hoàn thành tốt công việc",
            3.5: "Khá, cần cải thiện một số điểm",
            3.0: "Trung bình, cần nỗ lực hơn"
        }
        comment = comments.get(score, "Hoàn thành công việc được giao")
        
        Evaluation.objects.create(
            employee=emp,
            period=period,
            score=score,
            comment=comment
        )
        evaluation_count += 1
print(f"✓ Đã tạo {evaluation_count} đánh giá")

# ============================================================================
# 13. TẠO BẢNG LƯƠNG (Payroll)
# ============================================================================
print("\n13. Tạo bảng lương...")
payroll_count = 0

for month in [9, 10, 11]:
    for emp_code, emp in employees.items():
        if emp.status == 3:  # Đã nghỉ việc
            continue
        
        # Tính số giờ làm việc trong tháng
        attendances = Attendance.objects.filter(
            employee=emp,
            date__month=month,
            date__year=2025,
            status="Có làm việc"
        )
        total_hours = sum(a.working_hours for a in attendances)
        
        # Tính lương
        base_salary = emp.salary
        salary_coefficient = emp.job_title.salary_coefficient if emp.job_title else 1.0
        standard_days = 22
        hourly_rate = base_salary / (standard_days * 8)
        
        # Thưởng/phạt ngẫu nhiên
        bonus = random.choice([0, 0, 0, 500000, 1000000, 2000000])
        penalty = random.choice([0, 0, 0, 0, 200000, 500000])
        
        total_salary = (hourly_rate * total_hours) + bonus - penalty
        
        Payroll.objects.create(
            employee=emp,
            month=month,
            year=2025,
            base_salary=base_salary,
            salary_coefficient=salary_coefficient,
            standard_working_days=standard_days,
            hourly_rate=hourly_rate,
            total_working_hours=total_hours,
            bonus=bonus,
            penalty=penalty,
            total_salary=total_salary,
            status="confirmed" if month < 11 else "pending",
            notes=""
        )
        payroll_count += 1
print(f"✓ Đã tạo {payroll_count} bảng lương")

# ============================================================================
# 14. TẠO TIN TUYỂN DỤNG (Job Postings)
# ============================================================================
print("\n14. Tạo tin tuyển dụng...")
job_postings_data = [
    {
        "title": "Senior Software Engineer",
        "code": "JOB-2025-001",
        "dept": "Phòng Công nghệ thông tin",
        "desc": "Phát triển và duy trì các ứng dụng web sử dụng Python/Django và React",
        "req": "- Tối thiểu 5 năm kinh nghiệm lập trình\n- Thành thạo Python, Django, React\n- Có kinh nghiệm với AWS/Azure\n- Tiếng Anh giao tiếp tốt",
        "salary_min": 30000000,
        "salary_max": 50000000,
        "positions": 2,
        "exp": "senior",
        "status": "open"
    },
    {
        "title": "Business Analyst",
        "code": "JOB-2025-002",
        "dept": "Phòng Kinh doanh",
        "desc": "Phân tích yêu cầu kinh doanh và đề xuất giải pháp công nghệ",
        "req": "- 3+ năm kinh nghiệm BA\n- Kỹ năng phân tích tốt\n- Có kinh nghiệm viết document\n- Giao tiếp tốt",
        "salary_min": 20000000,
        "salary_max": 35000000,
        "positions": 1,
        "exp": "mid",
        "status": "open"
    },
    {
        "title": "HR Executive",
        "code": "JOB-2025-003",
        "dept": "Phòng Nhân sự",
        "desc": "Thực hiện các công việc nhân sự tổng hợp",
        "req": "- 2+ năm kinh nghiệm HR\n- Am hiểu luật lao động\n- Kỹ năng giao tiếp tốt\n- Thành thạo MS Office",
        "salary_min": 12000000,
        "salary_max": 18000000,
        "positions": 1,
        "exp": "junior",
        "status": "open"
    },
    {
        "title": "Junior Developer",
        "code": "JOB-2025-004",
        "dept": "Phòng Công nghệ thông tin",
        "desc": "Hỗ trợ phát triển ứng dụng web",
        "req": "- Fresh graduate hoặc 1 năm kinh nghiệm\n- Biết Python hoặc JavaScript\n- Ham học hỏi\n- Có thể làm việc nhóm",
        "salary_min": 10000000,
        "salary_max": 15000000,
        "positions": 3,
        "exp": "entry",
        "status": "open"
    },
    {
        "title": "Marketing Specialist",
        "code": "JOB-2025-005",
        "dept": "Phòng Marketing",
        "desc": "Thực hiện các chiến dịch marketing digital",
        "req": "- 2+ năm kinh nghiệm Digital Marketing\n- Có kinh nghiệm chạy Ads\n- Sáng tạo\n- Biết sử dụng các công cụ analytics",
        "salary_min": 15000000,
        "salary_max": 25000000,
        "positions": 1,
        "exp": "junior",
        "status": "closed"
    },
]

hr_manager = employees.get("HR001")
job_postings = {}

for jp in job_postings_data:
    posting = JobPosting.objects.create(
        title=jp["title"],
        code=jp["code"],
        department=departments[jp["dept"]],
        description=jp["desc"],
        requirements=jp["req"],
        responsibilities="- Thực hiện công việc được giao\n- Báo cáo tiến độ\n- Phối hợp với các bộ phận liên quan",
        benefits="- Lương tháng 13\n- Bảo hiểm đầy đủ\n- Team building hàng quý\n- Đào tạo nâng cao",
        employment_type="fulltime",
        experience_level=jp["exp"],
        number_of_positions=jp["positions"],
        location="Hà Nội",
        salary_min=jp["salary_min"],
        salary_max=jp["salary_max"],
        deadline=date(2025, 12, 31) if jp["status"] == "open" else date(2025, 10, 31),
        status=jp["status"],
        contact_person="Phòng Nhân sự",
        contact_email="hr@company.com",
        contact_phone="0243456789",
        created_by=hr_manager
    )
    job_postings[jp["code"]] = posting
print(f"✓ Đã tạo {len(job_postings)} tin tuyển dụng")

# ============================================================================
# 15. TẠO ĐƠN ỨNG TUYỂN (Applications)
# ============================================================================
print("\n15. Tạo đơn ứng tuyển...")

applicants_data = [
    # Ứng viên cho Senior Software Engineer
    {"job": "JOB-2025-001", "name": "Trần Minh Quân", "email": "quan.tm@gmail.com", "phone": "0912345678", "exp": 6, "status": "interview", "rating": 4},
    {"job": "JOB-2025-001", "name": "Lê Hoàng Nam", "email": "nam.lh@gmail.com", "phone": "0923456789", "exp": 5, "status": "screening", "rating": 3},
    {"job": "JOB-2025-001", "name": "Nguyễn Đức Anh", "email": "anh.nd@gmail.com", "phone": "0934567890", "exp": 7, "status": "offer", "rating": 5},
    {"job": "JOB-2025-001", "name": "Phạm Văn Hải", "email": "hai.pv@gmail.com", "phone": "0945678901", "exp": 4, "status": "rejected", "rating": 2},
    
    # Ứng viên cho Business Analyst
    {"job": "JOB-2025-002", "name": "Vũ Thị Hương", "email": "huong.vt@gmail.com", "phone": "0956789012", "exp": 4, "status": "interview", "rating": 4},
    {"job": "JOB-2025-002", "name": "Hoàng Minh Tuấn", "email": "tuan.hm@gmail.com", "phone": "0967890123", "exp": 3, "status": "new", "rating": None},
    
    # Ứng viên cho HR Executive
    {"job": "JOB-2025-003", "name": "Ngô Thị Lan", "email": "lan.nt@gmail.com", "phone": "0978901234", "exp": 2, "status": "phone_interview", "rating": 3},
    {"job": "JOB-2025-003", "name": "Đặng Văn Bình", "email": "binh.dv@gmail.com", "phone": "0989012345", "exp": 3, "status": "accepted", "rating": 5},
    
    # Ứng viên cho Junior Developer
    {"job": "JOB-2025-004", "name": "Bùi Quang Huy", "email": "huy.bq@gmail.com", "phone": "0990123456", "exp": 0, "status": "test", "rating": 4},
    {"job": "JOB-2025-004", "name": "Mai Thị Ngọc", "email": "ngoc.mt@gmail.com", "phone": "0901234567", "exp": 1, "status": "new", "rating": None},
    {"job": "JOB-2025-004", "name": "Trịnh Văn Long", "email": "long.tv@gmail.com", "phone": "0812345678", "exp": 0, "status": "screening", "rating": 3},
    {"job": "JOB-2025-004", "name": "Lý Thị Mai", "email": "mai.lt@gmail.com", "phone": "0823456789", "exp": 1, "status": "interview", "rating": 4},
    
    # Ứng viên cho Marketing (đã đóng)
    {"job": "JOB-2025-005", "name": "Đinh Văn Khoa", "email": "khoa.dv@gmail.com", "phone": "0834567890", "exp": 3, "status": "accepted", "rating": 5},
]

application_count = 0
for i, app in enumerate(applicants_data, 1):
    if app["job"] not in job_postings:
        continue
    
    Application.objects.create(
        job=job_postings[app["job"]],
        application_code=f"APP-2025-{i:04d}",
        full_name=app["name"],
        email=app["email"],
        phone=app["phone"],
        date_of_birth=date(random.randint(1990, 2000), random.randint(1, 12), random.randint(1, 28)),
        gender=random.choice([0, 1]),
        address=f"Số {random.randint(1, 100)}, {random.choice(tinh_thanh)}",
        years_of_experience=app["exp"],
        education_level=3,
        school=random.choice(truong_dai_hoc),
        major=random.choice(["Công nghệ thông tin", "Quản trị kinh doanh", "Marketing", "Nhân sự"]),
        resume="resumes/cv_sample.pdf",
        cover_letter="Tôi rất mong muốn được làm việc tại công ty...",
        expected_salary=random.randint(15, 40) * 1000000,
        status=app["status"],
        source=random.choice(["website", "linkedin", "referral", "vietnamworks"]),
        rating=app["rating"],
        assigned_to=hr_manager
    )
    application_count += 1

print(f"✓ Đã tạo {application_count} đơn ứng tuyển")

# ============================================================================
# HOÀN TẤT
# ============================================================================
print("\n" + "="*60)
print("✅ HOÀN TẤT TẠO DỮ LIỆU MẪU")
print("="*60)
print(f"""
Tổng kết:
- Chức danh: {len(job_titles)}
- Phòng ban: {len(departments)}
- Nhân viên: {len(employees)}
- Loại nghỉ phép: {len(leave_types)}
- Số dư ngày phép: {leave_balance_count}
- Đơn xin nghỉ: {leave_request_count}
- Danh mục chi phí: {len(expense_categories)}
- Yêu cầu hoàn tiền: {expense_count}
- Chấm công: {attendance_count}
- Khen thưởng: {reward_count}
- Kỷ luật: {discipline_count}
- Đánh giá: {evaluation_count}
- Bảng lương: {payroll_count}
- Tin tuyển dụng: {len(job_postings)}
- Đơn ứng tuyển: {application_count}
""")
