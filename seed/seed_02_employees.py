"""
Seed 02: Employees
Run: python manage.py shell < seed/seed_02_employees.py
Requires: seed_01_departments.py
"""
from seed.base import *
from app.models import Department, JobTitle, Employee

print_header("SEED 02: Employees")

# Check dependencies
if JobTitle.objects.count() == 0:
    print("❌ Lỗi: Chưa có chức danh. Chạy seed_01_departments.py trước!")
    exit(1)

if Department.objects.count() == 0:
    print("❌ Lỗi: Chưa có phòng ban. Chạy seed_01_departments.py trước!")
    exit(1)

# Get existing data
job_titles = {jt.name: jt for jt in JobTitle.objects.all()}
departments = {d.name: d for d in Department.objects.all()}

# Clear employees
print("Xóa nhân viên cũ...")
Employee.objects.all().delete()

# Major by department
NGANH_HOC = {
    "Phòng Công nghệ thông tin": ["Công nghệ thông tin", "Khoa học máy tính", "Kỹ thuật phần mềm", "An toàn thông tin"],
    "Phòng Kế toán - Tài chính": ["Kế toán", "Tài chính ngân hàng", "Kiểm toán", "Quản trị tài chính"],
    "Phòng Nhân sự": ["Quản trị nhân lực", "Quản trị kinh doanh", "Tâm lý học", "Luật"],
    "Phòng Kinh doanh": ["Quản trị kinh doanh", "Marketing", "Kinh tế", "Thương mại quốc tế"],
    "Phòng Marketing": ["Marketing", "Truyền thông", "Quan hệ công chúng", "Thiết kế đồ họa"],
    "Phòng Hành chính": ["Quản trị văn phòng", "Quản trị kinh doanh", "Hành chính học"],
    "Phòng Chăm sóc khách hàng": ["Quản trị kinh doanh", "Marketing", "Truyền thông"],
    "Ban Giám đốc": ["Quản trị kinh doanh", "Kinh tế", "Tài chính"],
}

# Employee definitions
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

print("\nTạo nhân viên...")
used_names = set()
used_phones = set()
used_cccd = set()
count = 0

for emp_data in employees_data:
    # Generate unique name
    full_name = generate_random_name(emp_data["gender"], used_names)
    
    # Birthday based on role
    if emp_data["is_manager"] or emp_data["job"] in ["Giám đốc", "Phó Giám đốc"]:
        birth_year = random.randint(1970, 1985)
    elif emp_data["job"] == "Thực tập sinh":
        birth_year = random.randint(1998, 2002)
    else:
        birth_year = random.randint(1985, 1998)
    
    birthday = date(birth_year, random.randint(1, 12), random.randint(1, 28))
    place_of_birth = random.choice(TINH_THANH)
    
    # CCCD & Phone
    cccd = generate_cccd(used_cccd)
    phone = generate_phone(used_phones)
    
    # Email
    email_name = remove_vietnamese_accents(full_name).replace(" ", ".")
    email = f"{email_name}@company.com"
    
    # Contract dates
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
    
    # Contract duration
    if emp_data["status"] == 0:
        contract_duration = 3
    elif emp_data["status"] == 1:
        contract_duration = 2
    else:
        contract_duration = random.choice([12, 24, 36])
    
    # School & major
    dept_name = emp_data["dept"]
    school = random.choice(TRUONG_DAI_HOC)
    major = random.choice(NGANH_HOC.get(dept_name, ["Quản trị kinh doanh"]))
    
    # Address
    streets = ['Nguyễn Trãi', 'Lê Văn Lương', 'Trần Duy Hưng', 'Phạm Hùng', 'Láng Hạ', 'Kim Mã', 'Hoàng Quốc Việt', 'Cầu Giấy']
    address = f"Số {random.randint(1, 200)}, Đường {random.choice(streets)}, {random.choice(['Hà Nội', 'TP. Hồ Chí Minh'])}"
    
    Employee.objects.create(
        employee_code=emp_data["code"],
        name=full_name,
        gender=emp_data["gender"],
        birthday=birthday,
        place_of_birth=place_of_birth,
        place_of_origin=random.choice(TINH_THANH),
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
    count += 1

print_success(f"Đã tạo {count} nhân viên")

print_header("HOÀN TẤT SEED 02")
print(f"- Tổng nhân viên: {Employee.objects.count()}")
print(f"- Theo phòng ban:")
for dept in Department.objects.all():
    emp_count = Employee.objects.filter(department=dept).count()
    print(f"  + {dept.name}: {emp_count} người")
