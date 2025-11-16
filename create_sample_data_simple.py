"""
Script tạo dữ liệu mẫu tiếng Việt cho hệ thống HRM
Đơn giản, chính xác với models hiện tại
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Fix UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Department, Employee, JobTitle

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

# Dữ liệu tiếng Việt
VIETNAMESE_SURNAMES = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng']
MALE_NAMES = ['Văn Hùng', 'Đức Dũng', 'Minh Khang', 'Quốc Tuấn', 'Hoàng Long', 'Anh Minh']
FEMALE_NAMES = ['Thị Hằng', 'Thu Linh', 'Hồng Hương', 'Mai Nhung', 'Thanh Hà', 'Ngọc Chi']
VIETNAM_ADDRESSES = [
    '123 Nguyễn Văn Linh, Quận 7, TP.HCM',
    '456 Lê Văn Việt, Quận 9, TP.HCM',
    '789 Võ Văn Ngân, Thủ Đức, TP.HCM',
    '321 Điện Biên Phủ, Quận 3, TP.HCM',
    '654 Lý Thường Kiệt, Quận 10, TP.HCM'
]

def clear_data():
    """Xóa dữ liệu cũ"""
    print_header("XÓA DỮ LIỆU CŨ")
    
    Employee.objects.all().delete()
    print_success("Đã xóa tất cả nhân viên")
    
    JobTitle.objects.all().delete()
    print_success("Đã xóa tất cả chức vụ")
    
    Department.objects.all().delete()
    print_success("Đã xóa tất cả phòng ban")
    
    # Xóa users trừ superuser
    User.objects.filter(is_superuser=False).delete()
    print_success("Đã xóa users (giữ lại superuser)")

def create_departments():
    """Tạo phòng ban"""
    print_header("TẠO PHÒNG BAN")
    
    departments_data = [
        {
            'name': 'Ban Giám Đốc',
            'description': 'Ban lãnh đạo công ty',
            'date_establishment': datetime.now().date() - timedelta(days=1825),
        },
        {
            'name': 'Phòng Nhân Sự',
            'description': 'Quản lý nguồn nhân lực',
            'date_establishment': datetime.now().date() - timedelta(days=1460),
        },
        {
            'name': 'Phòng Kế Toán',
            'description': 'Quản lý tài chính và kế toán',
            'date_establishment': datetime.now().date() - timedelta(days=1460),
        },
        {
            'name': 'Phòng IT',
            'description': 'Công nghệ thông tin',
            'date_establishment': datetime.now().date() - timedelta(days=1095),
        },
        {
            'name': 'Phòng Marketing',
            'description': 'Marketing và truyền thông',
            'date_establishment': datetime.now().date() - timedelta(days=1095),
        },
    ]
    
    departments = []
    for data in departments_data:
        dept = Department.objects.create(**data)
        departments.append(dept)
        print_success(f"Tạo phòng ban: {dept.name}")
    
    return departments

def create_job_titles():
    """Tạo chức vụ"""
    print_header("TẠO CHỨC VỤ")
    
    titles_data = [
        {'name': 'Giám Đốc', 'salary_coefficient': 5.0, 'description': 'Giám đốc công ty'},
        {'name': 'Phó Giám Đốc', 'salary_coefficient': 4.5, 'description': 'Phó giám đốc'},
        {'name': 'Trưởng Phòng', 'salary_coefficient': 3.5, 'description': 'Trưởng phòng ban'},
        {'name': 'Nhân Viên', 'salary_coefficient': 2.0, 'description': 'Nhân viên'},
    ]
    
    titles = []
    for data in titles_data:
        title = JobTitle.objects.create(**data)
        titles.append(title)
        print_success(f"Tạo chức vụ: {title.name}")
    
    return titles

def generate_employee_code(index):
    """Tạo mã nhân viên NV2024001"""
    year = datetime.now().year
    return f"NV{year}{index:03d}"

def generate_phone():
    """Tạo số điện thoại Việt Nam"""
    prefixes = ['090', '091', '093', '094', '096', '097', '098']
    return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(7)])

def remove_vietnamese_accents(text):
    """
    Chuyển chữ tiếng Việt có dấu thành không dấu
    Ví dụ: "Nguyễn" -> "nguyen", "Truyền" -> "truyen"
    """
    # Bảng chuyển đổi từ có dấu sang không dấu
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }
    
    result = text.lower()
    for viet, eng in vietnamese_map.items():
        result = result.replace(viet, eng)
    
    return result

def generate_email_username(surname, middle_name, first_name):
    """
    Tạo email và username theo quy tắc:
    Tên + Chữ cái đầu Họ + Chữ cái đầu Tên lót
    
    Ví dụ:
    - Nguyễn Minh Truyền -> truyennm
    - Trần Thị Hồng Khang -> khangtth
    """
    # Chuyển tất cả về không dấu và lowercase
    surname_no_accent = remove_vietnamese_accents(surname)
    middle_no_accent = remove_vietnamese_accents(middle_name) if middle_name else ''
    first_no_accent = remove_vietnamese_accents(first_name)
    
    # Lấy chữ cái đầu
    surname_initial = surname_no_accent[0] if surname_no_accent else ''
    middle_initial = middle_no_accent[0] if middle_no_accent else ''
    
    # Tạo username: tên + chữ cái đầu họ + chữ cái đầu tên lót
    username = f"{first_no_accent}{surname_initial}{middle_initial}"
    
    return username

def create_employees(departments, job_titles):
    """Tạo nhân viên mẫu"""
    print_header("TẠO NHÂN VIÊN")
    
    employees = []
    employee_index = 1
    
    # Track used usernames to avoid duplicates
    used_usernames = set()
    
    # Phân bổ nhân viên theo phòng ban và chức vụ
    distribution = [
        ('Ban Giám Đốc', 'Giám Đốc', 1),
        ('Ban Giám Đốc', 'Phó Giám Đốc', 1),
        ('Phòng Nhân Sự', 'Trưởng Phòng', 1),
        ('Phòng Nhân Sự', 'Nhân Viên', 3),
        ('Phòng Kế Toán', 'Trưởng Phòng', 1),
        ('Phòng Kế Toán', 'Nhân Viên', 3),
        ('Phòng IT', 'Trưởng Phòng', 1),
        ('Phòng IT', 'Nhân Viên', 4),
        ('Phòng Marketing', 'Trưởng Phòng', 1),
        ('Phòng Marketing', 'Nhân Viên', 3),
    ]
    
    for dept_name, title_name, count in distribution:
        dept = Department.objects.get(name=dept_name)
        job_title = JobTitle.objects.get(name=title_name)
        
        for i in range(count):
            # Tạo tên người Việt
            surname = random.choice(VIETNAMESE_SURNAMES)
            gender = random.choice([0, 1])  # 0=Nam, 1=Nữ
            
            if gender == 0:
                given_name = random.choice(MALE_NAMES)
            else:
                given_name = random.choice(FEMALE_NAMES)
            
            # Tách tên lót và tên
            # MALE_NAMES và FEMALE_NAMES có format: "Tên lót Tên"
            # Ví dụ: "Văn Hùng" -> middle="Văn", first="Hùng"
            name_parts = given_name.split()
            if len(name_parts) >= 2:
                middle_name = name_parts[0]
                first_name = name_parts[1]
            else:
                middle_name = ''
                first_name = name_parts[0]
            
            full_name = f"{surname} {given_name}"
            
            # Tạo email và username theo quy tắc mới
            # Ví dụ: Nguyễn Minh Truyền -> truyennm
            base_username = generate_email_username(surname, middle_name, first_name)
            
            # Xử lý trùng lặp username
            username = base_username
            counter = 1
            while username in used_usernames or User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            used_usernames.add(username)
            email = f"{username}@company.vn"
            
            # Xác định quyền dựa vào chức vụ
            is_staff = False
            is_superuser = False
            
            if title_name == 'Giám Đốc':
                is_staff = True
                is_superuser = True  # Giám đốc có full quyền
            elif title_name in ['Phó Giám Đốc', 'Trưởng Phòng']:
                is_staff = True  # Có quyền truy cập admin
            elif dept_name == 'Phòng Nhân Sự':
                is_staff = True  # Nhân viên HR có quyền truy cập admin
            
            # Tạo user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='123456',
                first_name=given_name,
                last_name=surname,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            
            # Tạo employee
            birthday = datetime.now().date() - timedelta(days=random.randint(8000, 15000))
            hire_date = datetime.now().date() - timedelta(days=random.randint(30, 1095))
            issue_date = birthday + timedelta(days=6570)  # 18 tuổi
            
            employee = Employee.objects.create(
                employee_code=generate_employee_code(employee_index),
                name=full_name,
                gender=gender,
                birthday=birthday,
                place_of_birth='TP. Hồ Chí Minh',
                place_of_origin='TP. Hồ Chí Minh',
                place_of_residence=random.choice(VIETNAM_ADDRESSES),
                identification=f"{random.randint(100000000, 999999999)}",
                date_of_issue=issue_date,
                place_of_issue='Công an TP. Hồ Chí Minh',
                nationality='Việt Nam',
                nation='Kinh',
                religion='Không',
                email=email,
                phone=generate_phone(),
                address=random.choice(VIETNAM_ADDRESSES),
                marital_status=random.choice([0, 1]),  # 0=Độc thân, 1=Đã kết hôn
                job_title=job_title,
                job_position=title_name,
                department=dept,
                is_manager=(title_name in ['Giám Đốc', 'Phó Giám Đốc', 'Trưởng Phòng']),
                salary=random.randint(10, 50) * 1000000.0,  # 10-50 triệu
                contract_start_date=hire_date,
                contract_duration=12.0,  # 12 tháng
                status=2,  # Nhân viên chính thức
                education_level=3,  # Đại học
                major=random.choice(['Kinh tế', 'Công nghệ thông tin', 'Quản trị', 'Marketing', 'Kế toán']),
                school=random.choice(['ĐH Bách Khoa', 'ĐH Kinh Tế', 'ĐH Khoa Học Tự Nhiên']),
                certificate='',
            )
            
            employees.append(employee)
            employee_index += 1
            
            print_success(f"Tạo nhân viên: {full_name} - {dept.name} - {job_title.name}")
    
    return employees

def main():
    """Main function"""
    print_header("TẠO DỮ LIỆU MẪU TIẾNG VIỆT CHO HỆ THỐNG HRM")
    
    confirm = input("\n⚠️  Script sẽ XÓA TẤT CẢ dữ liệu hiện có. Tiếp tục? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Đã hủy!")
        return
    
    try:
        # Xóa dữ liệu cũ
        clear_data()
        
        # Tạo dữ liệu mới
        departments = create_departments()
        job_titles = create_job_titles()
        employees = create_employees(departments, job_titles)
        
        # Thống kê
        print_header("THỐNG KÊ")
        print_success(f"Tổng số phòng ban: {len(departments)}")
        print_success(f"Tổng số chức vụ: {len(job_titles)}")
        print_success(f"Tổng số nhân viên: {len(employees)}")
        
        # Hiển thị các tài khoản quản trị
        print("\n📋 TÀI KHOẢN QUẢN TRỊ:")
        
        # Giám đốc (superuser)
        gd_users = User.objects.filter(is_superuser=True).exclude(username='admin')
        if gd_users.exists():
            print("\n   🔑 GIÁM ĐỐC (Full quyền):")
            for u in gd_users:
                emp = Employee.objects.filter(email=u.email).first()
                dept_name = emp.department.name if emp and emp.department else "N/A"
                print(f"      • {u.username:15} | {u.last_name} {u.first_name:20} | {dept_name}")
        
        # Phó GĐ và Trưởng phòng (không phải HR)
        manager_users = User.objects.filter(is_staff=True, is_superuser=False)
        non_hr_managers = []
        hr_staff = []
        
        for u in manager_users:
            emp = Employee.objects.filter(email=u.email).first()
            if emp:
                if emp.department and emp.department.name == 'Phòng Nhân Sự':
                    hr_staff.append((u, emp))
                else:
                    non_hr_managers.append((u, emp))
        
        if non_hr_managers:
            print("\n   👔 PHÓ GIÁM ĐỐC / TRƯỞNG PHÒNG:")
            for u, emp in non_hr_managers:
                dept_name = emp.department.name if emp.department else "N/A"
                print(f"      • {u.username:15} | {u.last_name} {u.first_name:20} | {dept_name}")
        
        if hr_staff:
            print("\n   💼 PHÒNG NHÂN SỰ (Quyền quản lý nhân viên):")
            for u, emp in hr_staff:
                job_title = emp.job_title.name if emp.job_title else "N/A"
                print(f"      • {u.username:15} | {u.last_name} {u.first_name:20} | {job_title}")
        
        print_header("HOÀN TẤT")
        print("🎉 Tạo dữ liệu mẫu thành công!")
        print("\n📝 Thông tin đăng nhập:")
        print("   - Username: Theo tên nhân viên (VD: truyennm, khangtth)")
        print("   - Password: 123456")
        print("\n💡 Quy tắc username: Tên + Chữ cái đầu Họ + Chữ cái đầu Tên lót")
        print("   VD: Nguyễn Minh Truyền -> truyennm")
        print("       Trần Thị Hồng Khang -> khangtth")
        print("\n💡 Phân quyền:")
        print("   - Giám Đốc: Full quyền (is_superuser=True)")
        print("   - Phó GĐ/Trưởng Phòng: Quyền staff (is_staff=True)")
        print("   - Nhân viên HR: Quyền staff (is_staff=True)")
        print("   - Nhân viên khác: Không có quyền admin")
        print("\n💡 Chạy server: python manage.py runserver")
        print("   Truy cập: http://localhost:8000/admin/\n")
        
    except Exception as e:
        print_error(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
