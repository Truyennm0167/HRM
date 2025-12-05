"""
Tạo dữ liệu mẫu tiếng Việt cho hệ thống HRM
Bao gồm: Nhân viên, Phòng ban, Hợp đồng, Nghỉ phép, Lương, Tuyển dụng, Đánh giá
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User, Group
from app.models import (
    Department, Employee, JobTitle, Contract, LeaveRequest,
    Payroll, SalaryComponent, Appraisal, Application, JobPosting
)

# ==================== DATA GENERATORS ====================

# Họ phổ biến ở Việt Nam
VIETNAMESE_SURNAMES = [
    'Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ',
    'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý', 'Trịnh', 'Đinh',
    'Lâm', 'Mai', 'Đào', 'Hà', 'Tôn', 'Tạ', 'Chu', 'La'
]

# Tên đệm nam
MALE_MIDDLE_NAMES = [
    'Văn', 'Đức', 'Quốc', 'Hữu', 'Minh', 'Công', 'Bá', 'Duy',
    'Tuấn', 'Anh', 'Thành', 'Hoàng', 'Quang', 'Xuân', 'Thanh'
]

# Tên đệm nữ
FEMALE_MIDDLE_NAMES = [
    'Thị', 'Thu', 'Hồng', 'Kim', 'Thanh', 'Lan', 'Phương', 'Thúy',
    'Hương', 'Mai', 'Linh', 'Ngọc', 'Diệu', 'Bích', 'Thảo'
]

# Tên nam
MALE_FIRST_NAMES = [
    'Hùng', 'Dũng', 'Nam', 'Khang', 'Phong', 'Tuấn', 'Long', 'Hải',
    'Minh', 'Quân', 'Đạt', 'Thắng', 'Hiếu', 'Trí', 'Kiên', 'Hưng',
    'Cường', 'Vinh', 'Bình', 'Tài', 'Sơn', 'Tùng', 'Khoa', 'Phúc',
    'Đức', 'An', 'Bảo', 'Khánh', 'Hoàng', 'Nhân', 'Thiện', 'Toàn'
]

# Tên nữ
FEMALE_FIRST_NAMES = [
    'Hằng', 'Linh', 'Hương', 'Nhung', 'Hà', 'Chi', 'Trang', 'Thảo',
    'My', 'Vy', 'Huyền', 'Ngân', 'Anh', 'Phương', 'Lan', 'Mai',
    'Hoa', 'Dung', 'Yến', 'Thủy', 'Tú', 'Diệu', 'Ngọc', 'Bích',
    'Thuỳ', 'Trinh', 'Quỳnh', 'Châu', 'Loan', 'Oanh', 'Vân', 'Hiền'
]

# Email domains
EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'company.vn']

# Địa chỉ Việt Nam
VIETNAM_ADDRESSES = [
    'Số 15, Đường Nguyễn Trãi, Phường Bến Thành, Quận 1, TP.HCM',
    'Số 23, Đường Lê Lợi, Phường Bến Nghé, Quận 1, TP.HCM',
    'Số 45, Đường Võ Văn Tần, Phường 6, Quận 3, TP.HCM',
    'Số 78, Đường Cách Mạng Tháng 8, Phường 6, Quận Tân Bình, TP.HCM',
    'Số 12, Đường Lý Thường Kiệt, Phường 7, Quận 10, TP.HCM',
    'Số 34, Đường Phan Đăng Lưu, Phường 3, Quận Bình Thạnh, TP.HCM',
    'Số 56, Đường Xo Viết Nghệ Tĩnh, Phường Tân Thành, Quận Tân Phú, TP.HCM',
    'Số 89, Đường Hoàng Văn Thụ, Phường 4, Quận Phú Nhuận, TP.HCM',
    'Số 102, Đường Hai Bà Trưng, Phường Đa Kao, Quận 1, TP.HCM',
    'Số 67, Đường Trần Hưng Đạo, Phường Nguyễn Cư Trinh, Quận 1, TP.HCM',
    'Số 123, Đường Nguyễn Đình Chiểu, Phường 2, Quận 3, TP.HCM',
    'Số 45, Đường Điện Biên Phủ, Phường Đa Kao, Quận 1, TP.HCM',
    'Số 78, Đường Nguyễn Huệ, Phường Bến Nghé, Quận 1, TP.HCM',
    'Số 234, Đường Nam Kỳ Khởi Nghĩa, Phường 7, Quận 3, TP.HCM',
    'Số 156, Đường Pasteur, Phường 6, Quận 3, TP.HCM',
]

def generate_vietnamese_name(gender='male'):
    """Tạo tên người Việt Nam ngẫu nhiên"""
    surname = random.choice(VIETNAMESE_SURNAMES)
    
    if gender == 'male':
        middle = random.choice(MALE_MIDDLE_NAMES)
        first = random.choice(MALE_FIRST_NAMES)
    else:
        middle = random.choice(FEMALE_MIDDLE_NAMES)
        first = random.choice(FEMALE_FIRST_NAMES)
    
    return surname, middle, first

def generate_email(surname, first_name):
    """Tạo email từ tên"""
    # Convert Vietnamese to ASCII
    import unicodedata
    
    def remove_accents(text):
        nfd = unicodedata.normalize('NFD', text)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    surname_ascii = remove_accents(surname).lower()
    first_ascii = remove_accents(first_name).lower()
    
    domain = random.choice(EMAIL_DOMAINS)
    number = random.randint(1, 999)
    
    patterns = [
        f"{first_ascii}{surname_ascii}{number}@{domain}",
        f"{surname_ascii}{first_ascii}@{domain}",
        f"{first_ascii}.{surname_ascii}@{domain}",
        f"{surname_ascii}.{first_ascii}{number}@{domain}",
    ]
    
    return random.choice(patterns)

def generate_phone():
    """Tạo số điện thoại Việt Nam"""
    prefixes = ['090', '091', '093', '094', '097', '098', '086', '096', '070', '079', '077', '076', '078']
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefix}{number}"

def generate_employee_code(index):
    """Tạo mã nhân viên"""
    return f"NV{datetime.now().year}{index:04d}"

# ==================== PRINT HELPERS ====================

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_success(text):
    print(f"✅ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_error(text):
    print(f"❌ {text}")

# ==================== DATA CREATION ====================

def clear_existing_data():
    """Xóa dữ liệu cũ"""
    print_header("XÓA DỮ LIỆU CŨ")
    
    models_to_clear = [
        (Appraisal, 'Đánh giá'),
        (Application, 'Ứng tuyển'),
        (JobPosting, 'Công việc tuyển dụng'),
        (Payroll, 'Bảng lương'),
        (SalaryComponent, 'Thành phần lương'),
        (LeaveRequest, 'Đơn nghỉ phép'),
        (Contract, 'Hợp đồng'),
        (Employee, 'Nhân viên'),
        (JobTitle, 'Chức vụ'),
        (Department, 'Phòng ban'),
    ]
    
    for model, name in models_to_clear:
        count = model.objects.count()
        if count > 0:
            model.objects.all().delete()
            print_success(f"Đã xóa {count} {name}")
    
    # Keep superuser, delete other users
    User.objects.filter(is_superuser=False).delete()
    print_success("Đã xóa người dùng (giữ lại superuser)")

def create_groups():
    """Tạo nhóm quyền"""
    print_header("TẠO NHÓM QUYỀN")
    
    groups_data = [
        ('HR', 'Nhân sự - Quản lý toàn bộ hệ thống'),
        ('Manager', 'Quản lý - Quản lý phòng ban'),
        ('Employee', 'Nhân viên - Người dùng thông thường'),
    ]
    
    for group_name, description in groups_data:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print_success(f"Tạo nhóm: {group_name} - {description}")

def create_departments():
    """Tạo phòng ban"""
    print_header("TẠO PHÒNG BAN")
    
    departments_data = [
        {
            'name': 'Ban Giám Đốc',
            
            'description': 'Ban lãnh đạo công ty, hoạch định chiến lược và điều hành tổng thể',
            'date_establishment': datetime.now().date() - timedelta(days=1825),  # 5 năm trước
        },
        {
            'name': 'Phòng Nhân Sự',
            
            'description': 'Quản lý nguồn nhân lực, tuyển dụng, đào tạo và phát triển nhân viên',
            'date_establishment': datetime.now().date() - timedelta(days=1460),  # 4 năm trước
        },
        {
            'name': 'Phòng Kế Toán',
            
            'description': 'Quản lý tài chính, kế toán và ngân sách công ty',
            'date_establishment': datetime.now().date() - timedelta(days=1460),
        },
        {
            'name': 'Phòng Công Nghệ Thông Tin',
            
            'description': 'Phát triển và bảo trì hệ thống công nghệ thông tin',
            'date_establishment': datetime.now().date() - timedelta(days=1095),  # 3 năm trước
        },
        {
            'name': 'Phòng Marketing',
            
            'description': 'Xây dựng thương hiệu, quảng bá sản phẩm và dịch vụ',
            'date_establishment': datetime.now().date() - timedelta(days=1095),
        },
        {
            'name': 'Phòng Kinh Doanh',
            
            'description': 'Phát triển thị trường, chăm sóc khách hàng và bán hàng',
            'date_establishment': datetime.now().date() - timedelta(days=1095),
        },
        {
            'name': 'Phòng Hành Chính',
            
            'description': 'Quản lý hành chính, văn phòng và tài sản công ty',
            'date_establishment': datetime.now().date() - timedelta(days=730),  # 2 năm trước
        },
        {
            'name': 'Phòng Sản Xuất',
            
            'description': 'Quản lý và điều hành hoạt động sản xuất',
            'date_establishment': datetime.now().date() - timedelta(days=1095),
        },
    ]
    
    departments = []
    for dept_data in departments_data:
        dept = Department.objects.create(**dept_data)
        departments.append(dept)
        print_success(f"Tạo phòng ban: {dept.name} ")
    
    return departments

def create_positions():
    """Tạo chức vụ"""
    print_header("TẠO CHỨC VỤ")
    
    positions_data = [
        {'name': 'Tổng Giám Đốc', 'salary_coefficient': 5.0, 'description': 'Lãnh đạo cao nhất công ty'},
        {'name': 'Phó Giám Đốc', 'salary_coefficient': 4.5, 'description': 'Phó lãnh đạo công ty'},
        {'name': 'Trưởng Phòng', 'salary_coefficient': 3.5, 'description': 'Quản lý phòng ban'},
        {'name': 'Phó Phòng', 'salary_coefficient': 3.0, 'description': 'Phó quản lý phòng ban'},
        {'name': 'Trưởng Nhóm', 'salary_coefficient': 2.5, 'description': 'Quản lý nhóm'},
        {'name': 'Nhân Viên Chính', 'salary_coefficient': 2.0, 'description': 'Nhân viên chính thức'},
        {'name': 'Nhân Viên', 'salary_coefficient': 1.5, 'description': 'Nhân viên thường'},
        {'name': 'Thực Tập Sinh', 'salary_coefficient': 1.0, 'description': 'Sinh viên thực tập'},
    ]
    
    positions = []
    for pos_data in positions_data:
        pos = JobTitle.objects.create(**pos_data)
        positions.append(pos)
        print_success(f"Tạo chức vụ: {pos.name}")
    
    return positions

def create_employees(departments, positions):
    """Tạo nhân viên"""
    print_header("TẠO NHÂN VIÊN")
    
    # Tổng số nhân viên mỗi phòng
    employee_distribution = {
        'Ban Giám Đốc': 3,
        'Phòng Nhân Sự': 6,
        'Phòng Kế Toán': 5,
        'Phòng Công Nghệ Thông Tin': 12,
        'Phòng Marketing': 8,
        'Phòng Kinh Doanh': 10,
        'Phòng Hành Chính': 5,
        'Phòng Sản Xuất': 15,
    }
    
    # Chức vụ theo phòng
    position_by_dept = {
        'Ban Giám Đốc': ['Tổng Giám Đốc', 'Phó Giám Đốc', 'Nhân Viên Chính'],
        'Phòng Nhân Sự': ['Trưởng Phòng', 'Phó Phòng', 'Nhân Viên Chính', 'Nhân Viên', 'Thực Tập Sinh'],
        'Phòng Kế Toán': ['Trưởng Phòng', 'Nhân Viên Chính', 'Nhân Viên'],
        'Phòng Công Nghệ Thông Tin': ['Trưởng Phòng', 'Phó Phòng', 'Trưởng Nhóm', 'Nhân Viên Chính', 'Nhân Viên', 'Thực Tập Sinh'],
        'Phòng Marketing': ['Trưởng Phòng', 'Trưởng Nhóm', 'Nhân Viên Chính', 'Nhán Viên'],
        'Phòng Kinh Doanh': ['Trưởng Phòng', 'Phó Phòng', 'Nhân Viên Chính', 'Nhân Viên'],
        'Phòng Hành Chính': ['Trưởng Phòng', 'Nhân Viên Chính', 'Nhân Viên'],
        'Phòng Sản Xuất': ['Trưởng Phòng', 'Phó Phòng', 'Trưởng Nhóm', 'Nhân Viên Chính', 'Nhân Viên'],
    }
    
    employees = []
    used_usernames = set()
    employee_index = 1
    
    for dept in departments:
        num_employees = employee_distribution.get(dept.name, 5)
        position_names = position_by_dept.get(dept.name, ['Nhân Viên'])
        
        for i in range(num_employees):
            # Tạo tên
            gender = random.choice(['male', 'female'])
            surname, middle, first_name = generate_vietnamese_name(gender)
            full_name = f"{surname} {middle} {first_name}"
            
            # Tạo username duy nhất
            import unicodedata
            def remove_accents(text):
                nfd = unicodedata.normalize('NFD', text)
                return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
            
            base_username = remove_accents(f"{first_name}{surname}").lower().replace(' ', '')
            username = base_username
            counter = 1
            while username in used_usernames:
                username = f"{base_username}{counter}"
                counter += 1
            used_usernames.add(username)
            
            # Tạo email
            email = generate_email(surname, first_name)
            
            # Tạo User
            user = User.objects.create_user(
                username=username,
                email=email,
                password='123456',  # Default password
                first_name=f"{surname} {middle}",
                last_name=first_name,
            )
            
            # Assign group
            if i == 0:  # Trưởng phòng
                user.groups.add(Group.objects.get(name='Manager'))
            else:
                user.groups.add(Group.objects.get(name='Employee'))
            
            # Chọn chức vụ
            if i < len(position_names):
                position_name = position_names[i]
            else:
                position_name = random.choice(['Nhân Viên', 'Nhân Viên Chính'])
            
            job_title = JobTitle.objects.get(name=position_name)
            
            # Tạo thông tin nhân viên
            birthday = datetime.now().date() - timedelta(days=random.randint(8000, 15000))  # 22-41 tuổi
            hire_date = datetime.now().date() - timedelta(days=random.randint(30, 1825))  # 1 tháng - 5 năm
            
            employee = Employee.objects.create(
                user=user,
                employee_code=generate_employee_code(employee_index),
                first_name=surname,
                middle_name=middle,
                last_name=first_name,
                birthday=birthday,
                gender=gender,
                email=email,
                phone_number=generate_phone(),
                address=random.choice(VIETNAM_ADDRESSES),
                department=dept,
                job_title=job_title,
                hire_date=hire_date,
                salary=Decimal(random.randint(8, 50)) * Decimal(1000000),  # 8-50 triệu
                is_manager=(i == 0),  # Người đầu tiên là manager
                major=random.choice(['Kinh tế', 'Công nghệ thông tin', 'Quản trị', 'Marketing', 'Kế toán', 'Kỹ thuật']),
                school=random.choice(['ĐH Bách Khoa', 'ĐH Kinh Tế', 'ĐH Khoa Học Tự Nhiên', 'ĐH FPT', 'ĐH Ngoại Thương']),
            )
            
            employees.append(employee)
            employee_index += 1
            
            print_success(f"Tạo nhân viên: {full_name} - {dept.name} - {job_title.name}")
    
    return employees

def create_contracts(employees):
    """Tạo hợp đồng"""
    print_header("TẠO HỢP ĐỒNG")
    
    contract_types = [
        ('Thử việc', 2),  # 2 tháng
        ('Xác định thời hạn', 12),  # 1 năm
        ('Xác định thời hạn', 24),  # 2 năm
        ('Không xác định thời hạn', 0),  # Vô thời hạn
    ]
    
    contracts = []
    
    for employee in employees:
        # Nhân viên thực tập: hợp đồng thử việc
        if employee.JobTitle.name == 'Thực Tập Sinh':
            contract_type, duration_months = contract_types[0]
        # Nhân viên mới: hợp đồng 1 năm
        elif (datetime.now().date() - employee.hire_date).days < 365:
            contract_type, duration_months = random.choice(contract_types[:2])
        # Nhân viên lâu năm: hợp đồng vô thời hạn
        elif (datetime.now().date() - employee.hire_date).days > 730:
            contract_type, duration_months = contract_types[3]
        # Nhân viên khác: ngẫu nhiên
        else:
            contract_type, duration_months = random.choice(contract_types[1:3])
        
        start_date = employee.hire_date
        
        if duration_months > 0:
            end_date = start_date + timedelta(days=duration_months * 30)
        else:
            end_date = start_date + timedelta(days=36500)  # 100 năm (vô thời hạn)
        
        contract = Contract.objects.create(
            employee=employee,
            contract_type=contract_type,
            start_date=start_date,
            end_date=end_date,
            salary=employee.salary,
            signed_date=start_date,
            status='active' if end_date > datetime.now().date() else 'expired',
        )
        
        contracts.append(contract)
        print_success(f"Tạo hợp đồng: {employee.first_name} {employee.last_name} - {contract_type}")
    
    return contracts

def create_leave_requests(employees):
    """Tạo đơn nghỉ phép"""
    print_header("TẠO ĐƠN NGHỈ PHÉP")
    
    leave_types = [
        'Nghỉ phép năm',
        'Nghỉ ốm',
        'Nghỉ việc riêng',
        'Nghỉ không lương',
    ]
    
    leave_reasons = {
        'Nghỉ phép năm': [
            'Về quê thăm gia đình',
            'Đi du lịch nghỉ dưỡng',
            'Tham dự đám cưới người thân',
            'Giải quyết việc cá nhân',
        ],
        'Nghỉ ốm': [
            'Bị cảm sốt, cần nghỉ ngơi',
            'Đau dạ dày, cần điều trị',
            'Khám bệnh định kỳ',
            'Theo dõi sức khỏe tại bệnh viện',
        ],
        'Nghỉ việc riêng': [
            'Đưa con đi khám bác sĩ',
            'Lo hậu sự người thân',
            'Giải quyết giấy tờ cá nhân',
            'Tham gia sự kiện gia đình',
        ],
        'Nghỉ không lương': [
            'Đi công tác riêng dài ngày',
            'Chăm sóc người nhà ốm',
            'Giải quyết việc cá nhân quan trọng',
        ],
    }
    
    statuses = ['pending', 'approved', 'rejected']
    
    leave_requests = []
    
    # Mỗi nhân viên có 2-5 đơn nghỉ phép trong năm
    for employee in employees:
        num_requests = random.randint(2, 5)
        
        for i in range(num_requests):
            leave_type = random.choice(leave_types)
            
            # Ngày bắt đầu trong khoảng 1 năm qua
            days_ago = random.randint(1, 365)
            start_date = datetime.now().date() - timedelta(days=days_ago)
            
            # Số ngày nghỉ
            duration = random.randint(1, 5)
            end_date = start_date + timedelta(days=duration - 1)
            
            # Trạng thái: đơn cũ thì approved/rejected, đơn mới thì pending
            if days_ago > 30:
                status = random.choice(['approved', 'rejected'])
            elif days_ago > 7:
                status = random.choice(['approved', 'approved', 'approved', 'rejected'])  # 75% approved
            else:
                status = 'pending'
            
            # Người duyệt (nếu không pending)
            approved_by = None
            if status != 'pending' and employee.department:
                # Tìm manager của phòng ban
                manager = Employee.objects.filter(
                    department=employee.department,
                    is_manager=True
                ).first()
                if manager:
                    approved_by = manager.user
            
            leave_request = LeaveRequest.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=random.choice(leave_reasons[leave_type]),
                status=status,
                approved_by=approved_by,
                applied_date=start_date - timedelta(days=random.randint(1, 7)),
            )
            
            leave_requests.append(leave_request)
    
    print_success(f"Đã tạo {len(leave_requests)} đơn nghỉ phép")
    return leave_requests

def create_salary_components():
    """Tạo các thành phần lương"""
    print_header("TẠO THÀNH PHẦN LƯƠNG")
    
    components_data = [
        # Khoản thu nhập
        {'name': 'Lương cơ bản', 'type': 'allowance', 'is_fixed': True, 'is_taxable': True},
        {'name': 'Phụ cấp ăn trưa', 'type': 'allowance', 'is_fixed': True, 'is_taxable': False},
        {'name': 'Phụ cấp xăng xe', 'type': 'allowance', 'is_fixed': True, 'is_taxable': False},
        {'name': 'Phụ cấp điện thoại', 'type': 'allowance', 'is_fixed': True, 'is_taxable': False},
        {'name': 'Thưởng hiệu suất', 'type': 'bonus', 'is_fixed': False, 'is_taxable': True},
        {'name': 'Thưởng dự án', 'type': 'bonus', 'is_fixed': False, 'is_taxable': True},
        {'name': 'Làm thêm giờ', 'type': 'overtime', 'is_fixed': False, 'is_taxable': True},
        
        # Khoản khấu trừ
        {'name': 'Bảo hiểm xã hội', 'type': 'deduction', 'is_fixed': True, 'is_taxable': False},
        {'name': 'Bảo hiểm y tế', 'type': 'deduction', 'is_fixed': True, 'is_taxable': False},
        {'name': 'Bảo hiểm thất nghiệp', 'type': 'deduction', 'is_fixed': True, 'is_taxable': False},
        {'name': 'Thuế thu nhập cá nhân', 'type': 'deduction', 'is_fixed': False, 'is_taxable': False},
        {'name': 'Tạm ứng', 'type': 'deduction', 'is_fixed': False, 'is_taxable': False},
    ]
    
    components = []
    for comp_data in components_data:
        comp = SalaryComponent.objects.create(**comp_data)
        components.append(comp)
        print_success(f"Tạo thành phần lương: {comp.name} ({comp.type})")
    
    return components

def create_payrolls(employees, salary_components):
    """Tạo bảng lương"""
    print_header("TẠO BẢNG LƯƠNG")
    
    # Tạo bảng lương cho 3 tháng gần nhất
    current_date = datetime.now().date()
    
    payrolls = []
    
    for month_offset in range(3):
        # Tính tháng
        month_date = current_date - timedelta(days=30 * month_offset)
        month = month_date.month
        year = month_date.year
        
        print_info(f"Tạo bảng lương tháng {month}/{year}")
        
        for employee in employees:
            # Bỏ qua nhân viên mới tuyển (chưa đủ 1 tháng)
            if employee.hire_date > month_date:
                continue
            
            # Lương cơ bản
            base_salary = employee.salary
            
            # Phụ cấp cố định
            allowances = Decimal('0')
            allowances += Decimal('730000')  # Phụ cấp ăn trưa (730k/tháng)
            allowances += Decimal('500000')  # Phụ cấp xăng xe
            
            if employee.JobTitle.level in ['Quản lý', 'Cấp cao']:
                allowances += Decimal('300000')  # Phụ cấp điện thoại
            
            # Thưởng (ngẫu nhiên)
            bonus = Decimal('0')
            if random.random() > 0.5:  # 50% có thưởng
                bonus = base_salary * Decimal(random.uniform(0.1, 0.3))
            
            # Làm thêm giờ (ngẫu nhiên)
            overtime = Decimal('0')
            if random.random() > 0.7:  # 30% làm OT
                overtime_hours = random.randint(5, 20)
                hourly_rate = base_salary / Decimal('176')  # 22 ngày * 8h
                overtime = hourly_rate * Decimal(overtime_hours) * Decimal('1.5')
            
            # Tổng thu nhập
            gross_salary = base_salary + allowances + bonus + overtime
            
            # Bảo hiểm (8% + 1.5% + 1% = 10.5% lương cơ bản)
            insurance = base_salary * Decimal('0.105')
            
            # Thuế TNCN (đơn giản hóa: 10% trên thu nhập chịu thuế sau khi trừ bảo hiểm và giảm trừ)
            taxable_income = gross_salary - insurance - Decimal('11000000')  # Giảm trừ gia cảnh
            if taxable_income > 0:
                # Bậc thuế đơn giản
                if taxable_income <= Decimal('5000000'):
                    tax = taxable_income * Decimal('0.05')
                elif taxable_income <= Decimal('10000000'):
                    tax = Decimal('250000') + (taxable_income - Decimal('5000000')) * Decimal('0.10')
                elif taxable_income <= Decimal('18000000'):
                    tax = Decimal('750000') + (taxable_income - Decimal('10000000')) * Decimal('0.15')
                else:
                    tax = Decimal('1950000') + (taxable_income - Decimal('18000000')) * Decimal('0.20')
            else:
                tax = Decimal('0')
            
            # Tạm ứng (ngẫu nhiên)
            advance = Decimal('0')
            if random.random() > 0.9:  # 10% có tạm ứng
                advance = Decimal(random.randint(1, 5)) * Decimal('1000000')
            
            # Tổng khấu trừ
            total_deductions = insurance + tax + advance
            
            # Thực lĩnh
            net_salary = gross_salary - total_deductions
            
            payroll = Payroll.objects.create(
                employee=employee,
                month=month,
                year=year,
                base_salary=base_salary,
                allowances=allowances,
                bonus=bonus,
                overtime=overtime,
                gross_salary=gross_salary,
                insurance=insurance,
                tax=tax,
                other_deductions=advance,
                total_deductions=total_deductions,
                net_salary=net_salary,
                payment_date=datetime(year, month, 25).date(),  # Trả lương ngày 25
                status='paid' if month_offset > 0 else 'pending',
            )
            
            payrolls.append(payroll)
        
        print_success(f"Đã tạo {len([p for p in payrolls if p.month == month and p.year == year])} bảng lương tháng {month}/{year}")
    
    return payrolls

def create_jobs():
    """Tạo tin tuyển dụng"""
    print_header("TẠO TIN TUYỂN DỤNG")
    
    jobs_data = [
        {
            'title': 'Lập Trình Viên Backend Python/Django',
            'department': 'Phòng Công Nghệ Thông Tin',
            'description': '''
Mô tả công việc:
- Phát triển và bảo trì hệ thống backend sử dụng Python/Django
- Thiết kế và tối ưu database
- Viết API RESTful cho mobile và web
- Tham gia code review và mentoring junior
- Làm việc với team để phát triển tính năng mới

Yêu cầu:
- Tốt nghiệp Đại học chuyên ngành IT
- Có ít nhất 2 năm kinh nghiệm Python/Django
- Thành thạo PostgreSQL/MySQL
- Hiểu biết về Git, Docker
- Có khả năng làm việc nhóm tốt

Quyền lợi:
- Lương: 15-25 triệu (thỏa thuận theo năng lực)
- Thưởng dự án, thưởng tháng 13
- Bảo hiểm đầy đủ theo luật
- Môi trường làm việc chuyên nghiệp
- Cơ hội thăng tiến rõ ràng
            ''',
            'requirements': 'Tốt nghiệp Đại học IT, 2+ năm kinh nghiệm Python/Django',
            'benefits': 'Lương 15-25 triệu, thưởng dự án, bảo hiểm đầy đủ',
            'location': 'TP. Hồ Chí Minh',
            'salary_range': '15-25 triệu',
            'employment_type': 'full_time',
            'experience_required': '2-3 years',
            'vacancies': 2,
        },
        {
            'title': 'Nhân Viên Marketing Digital',
            'department': 'Phòng Marketing',
            'description': '''
Mô tả công việc:
- Xây dựng và triển khai chiến dịch marketing online
- Quản lý fanpage, website, kênh social media
- Viết content, thiết kế hình ảnh quảng cáo
- Phân tích số liệu, đo lường hiệu quả campaign
- Nghiên cứu xu hướng thị trường

Yêu cầu:
- Tốt nghiệp Đại học Marketing/Truyền thông
- 1-2 năm kinh nghiệm Marketing Digital
- Thành thạo Facebook Ads, Google Ads
- Kỹ năng viết content tốt
- Sáng tạo, nhiệt huyết với công việc

Quyền lợi:
- Lương: 10-15 triệu
- Thưởng KPI hàng tháng
- Môi trường trẻ trung, năng động
- Đào tạo kỹ năng chuyên môn
            ''',
            'requirements': 'Tốt nghiệp ĐH Marketing, 1-2 năm kinh nghiệm Digital Marketing',
            'benefits': 'Lương 10-15 triệu, thưởng KPI, đào tạo',
            'location': 'TP. Hồ Chí Minh',
            'salary_range': '10-15 triệu',
            'employment_type': 'full_time',
            'experience_required': '1-2 years',
            'vacancies': 1,
        },
        {
            'title': 'Kế Toán Tổng Hợp',
            'department': 'Phòng Kế Toán',
            'description': '''
Mô tả công việc:
- Hạch toán các nghiệp vụ kế toán tổng hợp
- Kiểm tra chứng từ, theo dõi công nợ
- Lập báo cáo tài chính định kỳ
- Quyết toán thuế, làm việc với cơ quan thuế
- Kiểm kê tài sản

Yêu cầu:
- Tốt nghiệp Đại học Kế toán
- Có ít nhất 2 năm kinh nghiệm kế toán tổng hợp
- Thành thạo Excel, phần mềm kế toán
- Có chứng chỉ hành nghề kế toán (ưu tiên)
- Cẩn thận, trung thực

Quyền lợi:
- Lương: 12-18 triệu
- Thưởng cuối năm
- Bảo hiểm đầy đủ
- Làm việc giờ hành chính
            ''',
            'requirements': 'Tốt nghiệp ĐH Kế toán, 2+ năm kinh nghiệm',
            'benefits': 'Lương 12-18 triệu, thưởng cuối năm',
            'location': 'TP. Hồ Chí Minh',
            'salary_range': '12-18 triệu',
            'employment_type': 'full_time',
            'experience_required': '2-3 years',
            'vacancies': 1,
        },
        {
            'title': 'Nhân Viên Kinh Doanh B2B',
            'department': 'Phòng Kinh Doanh',
            'description': '''
Mô tả công việc:
- Tìm kiếm và phát triển khách hàng doanh nghiệp
- Tư vấn giải pháp, chốt hợp đồng
- Chăm sóc và duy trì mối quan hệ khách hàng
- Lập báo cáo bán hàng định kỳ
- Phối hợp với các phòng ban khác để phục vụ khách hàng

Yêu cầu:
- Tốt nghiệp Đại học (ưu tiên Kinh tế, Quản trị)
- Có kinh nghiệm bán hàng B2B là lợi thế
- Kỹ năng giao tiếp, thuyết phục tốt
- Chịu được áp lực công việc
- Ham học hỏi, nhiệt tình

Quyền lợi:
- Lương cơ bản: 8-12 triệu
- Hoa hồng không giới hạn (10-15% doanh số)
- Thưởng đạt target
- Đào tạo kỹ năng bán hàng
            ''',
            'requirements': 'Tốt nghiệp ĐH, kinh nghiệm bán hàng B2B',
            'benefits': 'Lương 8-12 triệu + hoa hồng 10-15%',
            'location': 'TP. Hồ Chí Minh',
            'salary_range': '8-12 triệu + Hoa hồng',
            'employment_type': 'full_time',
            'experience_required': '0-1 year',
            'vacancies': 3,
        },
        {
            'title': 'Thực Tập Sinh Nhân Sự',
            'department': 'Phòng Nhân Sự',
            'description': '''
Mô tả công việc:
- Hỗ trợ công tác tuyển dụng (đăng tin, sàng lọc CV)
- Hỗ trợ công tác đào tạo nhân viên
- Cập nhật hồ sơ nhân sự
- Tham gia tổ chức các hoạt động nội bộ
- Các công việc khác theo yêu cầu

Yêu cầu:
- Sinh viên năm 3, năm 4 ngành Quản trị nhân lực
- Có thể làm full-time ít nhất 3 tháng
- Thành thạo tin học văn phòng
- Có trách nhiệm, chủ động
- Ham học hỏi, nhiệt tình

Quyền lợi:
- Trợ cấp: 3-4 triệu/tháng
- Được đào tạo kỹ năng chuyên môn
- Môi trường làm việc chuyên nghiệp
- Cơ hội trở thành nhân viên chính thức
            ''',
            'requirements': 'Sinh viên năm 3-4 Quản trị nhân lực',
            'benefits': 'Trợ cấp 3-4 triệu, đào tạo, cơ hội chính thức hóa',
            'location': 'TP. Hồ Chí Minh',
            'salary_range': '3-4 triệu',
            'employment_type': 'internship',
            'experience_required': 'No experience',
            'vacancies': 2,
        },
    ]
    
    jobs = []
    for job_data in jobs_data:
        dept_name = job_data.pop('department')
        department = Department.objects.get(name=dept_name)
        
        # Tạo deadline 30-90 ngày sau
        application_deadline = datetime.now().date() + timedelta(days=random.randint(30, 90))
        posted_date = datetime.now().date() - timedelta(days=random.randint(1, 15))
        
        JobPosting = JobPosting.objects.create(
            department=department,
            posted_date=posted_date,
            application_deadline=application_deadline,
            status='open',
            **job_data
        )
        
        jobs.append(JobPosting)
        print_success(f"Tạo tin tuyển dụng: {JobPosting.title}")
    
    return jobs

def create_applications(jobs, count=30):
    """Tạo đơn ứng tuyển"""
    print_header("TẠO ĐƠN ỨNG TUYỂN")
    
    applications = []
    
    for i in range(count):
        JobPosting = random.choice(jobs)
        
        # Tạo ứng viên
        gender = random.choice(['male', 'female'])
        surname, middle, first_name = generate_vietnamese_name(gender)
        full_name = f"{surname} {middle} {first_name}"
        
        email = generate_email(surname, first_name)
        phone = generate_phone()
        
        # Ngày ứng tuyển
        days_ago = random.randint(1, 30)
        application_date = datetime.now().date() - timedelta(days=days_ago)
        
        # Trạng thái
        if days_ago > 20:
            status = random.choice(['approved', 'rejected'])
        elif days_ago > 10:
            status = random.choice(['interviewed', 'approved', 'rejected'])
        else:
            status = random.choice(['pending', 'reviewed'])
        
        # CV path (giả lập)
        cv_path = f"cvs/{surname}_{first_name}_CV.pdf"
        
        application = Application.objects.create(
            JobPosting=JobPosting,
            applicant_name=full_name,
            email=email,
            phone=phone,
            cv_file=cv_path,
            application_date=application_date,
            status=status,
            cover_letter=f"Kính gửi Ban Tuyển Dụng,\n\nTôi là {full_name}, tôi rất quan tâm đến vị trí {JobPosting.title} tại công ty. Với kinh nghiệm và kỹ năng của mình, tôi tin rằng tôi sẽ đóng góp tích cực cho công ty.\n\nRất mong được hợp tác với Quý công ty.\n\nTrân trọng,\n{full_name}",
        )
        
        applications.append(application)
    
    print_success(f"Đã tạo {len(applications)} đơn ứng tuyển")
    return applications

def create_appraisals(employees):
    """Tạo đánh giá nhân viên"""
    print_header("TẠO ĐÁNH GIÁ NHÂN VIÊN")
    
    appraisals = []
    
    # Đánh giá 6 tháng và cuối năm
    review_periods = [
        (6, 2024),  # Tháng 6/2024
        (12, 2024),  # Tháng 12/2024
    ]
    
    for employee in employees:
        # Bỏ qua nhân viên mới (chưa đủ 6 tháng)
        if (datetime.now().date() - employee.hire_date).days < 180:
            continue
        
        for month, year in review_periods:
            review_date = datetime(year, month, 30).date()
            
            # Tìm manager để review
            reviewer = None
            if employee.department:
                reviewer = Employee.objects.filter(
                    department=employee.department,
                    is_manager=True
                ).exclude(id=employee.id).first()
            
            if not reviewer:
                continue
            
            # Điểm số ngẫu nhiên (1-5)
            performance_score = round(random.uniform(3.0, 5.0), 1)
            attitude_score = round(random.uniform(3.0, 5.0), 1)
            teamwork_score = round(random.uniform(3.0, 5.0), 1)
            
            # Comments
            if performance_score >= 4.5:
                performance_comment = "Xuất sắc, vượt kỳ vọng. Hoàn thành công việc đúng hạn với chất lượng cao."
            elif performance_score >= 3.5:
                performance_comment = "Tốt, đáp ứng yêu cầu công việc. Cần cải thiện một số kỹ năng chuyên môn."
            else:
                performance_comment = "Cần cố gắng hơn. Một số công việc chưa đạt yêu cầu."
            
            if attitude_score >= 4.5:
                attitude_comment = "Thái độ làm việc tích cực, nhiệt tình. Luôn sẵn sàng hỗ trợ đồng nghiệp."
            elif attitude_score >= 3.5:
                attitude_comment = "Thái độ tốt, chủ động trong công việc."
            else:
                attitude_comment = "Cần cải thiện thái độ làm việc và tinh thần trách nhiệm."
            
            # Mục tiêu cho kỳ tiếp theo
            goals = [
                "Nâng cao kỹ năng chuyên môn",
                "Cải thiện hiệu suất làm việc",
                "Học thêm công nghệ mới",
                "Tăng cường làm việc nhóm",
            ]
            
            appraisal = Appraisal.objects.create(
                employee=employee,
                reviewer=reviewer.user,
                review_period_start=datetime(year, month - 6 if month > 6 else year - 1, 1).date(),
                review_period_end=review_date,
                performance_score=performance_score,
                attitude_score=attitude_score,
                teamwork_score=teamwork_score,
                comments=f"{performance_comment}\n\n{attitude_comment}",
                goals_next_period="\n".join(f"- {goal}" for goal in random.sample(goals, 2)),
                status='completed',
            )
            
            appraisals.append(appraisal)
    
    print_success(f"Đã tạo {len(appraisals)} đánh giá nhân viên")
    return appraisals

# ==================== MAIN ====================

def main():
    """Hàm chính"""
    print_header("TẠO DỮ LIỆU MẪU TIẾNG VIỆT CHO HỆ THỐNG HRM")
    
    print("⚠️  CẢNH BÁO: Script này sẽ XÓA TẤT CẢ dữ liệu hiện có!")
    print("   Chỉ chạy script này khi bạn muốn tạo lại dữ liệu từ đầu.")
    
    confirm = input("\n✋ Bạn có chắc chắn muốn tiếp tục? (yes/no): ")
    if confirm.lower() != 'yes':
        print_error("Đã hủy bỏ!")
        return
    
    try:
        # 1. Xóa dữ liệu cũ
        clear_existing_data()
        
        # 2. Tạo nhóm quyền
        create_groups()
        
        # 3. Tạo phòng ban
        departments = create_departments()
        
        # 4. Tạo chức vụ
        positions = create_positions()
        
        # 5. Tạo nhân viên
        employees = create_employees(departments, positions)
        
        # 6. Tạo hợp đồng
        contracts = create_contracts(employees)
        
        # 7. Tạo đơn nghỉ phép
        leave_requests = create_leave_requests(employees)
        
        # 8. Tạo thành phần lương
        salary_components = create_salary_components()
        
        # 9. Tạo bảng lương
        payrolls = create_payrolls(employees, salary_components)
        
        # 10. Tạo tin tuyển dụng
        jobs = create_jobs()
        
        # 11. Tạo đơn ứng tuyển
        applications = create_applications(jobs)
        
        # 12. Tạo đánh giá
        appraisals = create_appraisals(employees)
        
        # Tổng kết
        print_header("HOÀN THÀNH TẠO DỮ LIỆU MẪU")
        print(f"✅ Phòng ban:           {len(departments)}")
        print(f"✅ Chức vụ:            {len(positions)}")
        print(f"✅ Nhân viên:          {len(employees)}")
        print(f"✅ Hợp đồng:           {len(contracts)}")
        print(f"✅ Đơn nghỉ phép:      {len(leave_requests)}")
        print(f"✅ Thành phần lương:   {len(salary_components)}")
        print(f"✅ Bảng lương:         {len(payrolls)}")
        print(f"✅ Tin tuyển dụng:     {len(jobs)}")
        print(f"✅ Đơn ứng tuyển:      {len(applications)}")
        print(f"✅ Đánh giá:           {len(appraisals)}")
        
        print("\n" + "=" * 70)
        print("💡 THÔNG TIN ĐĂNG NHẬP")
        print("=" * 70)
        print("\n📌 Tất cả tài khoản có mật khẩu mặc định: 123456")
        print("\nMột số tài khoản mẫu:")
        
        # Hiển thị một số tài khoản
        sample_employees = Employee.objects.select_related('user', 'department', 'JobTitle')[:5]
        for emp in sample_employees:
            print(f"\n  👤 {emp.first_name} {emp.middle_name} {emp.last_name}")
            print(f"     Username: {emp.user.username}")
            print(f"     Email: {emp.email}")
            print(f"     Phòng ban: {emp.department.name if emp.department else 'N/A'}")
            print(f"     Chức vụ: {emp.JobTitle.name if emp.JobTitle else 'N/A'}")
        
        print("\n" + "=" * 70)
        print("🚀 Bây giờ bạn có thể chạy server và đăng nhập!")
        print("   python manage.py runserver")
        print("=" * 70)
        
    except Exception as e:
        print_error(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
