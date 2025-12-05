"""
Script tạo DỮ LIỆU ĐẦY ĐỦ cho TẤT CẢ tính năng hệ thống HRM
Bao gồm: Nhân viên, Chấm công, Lương, Nghỉ phép, Chi phí, Đánh giá, Khen thưởng, Kỷ luật, Tuyển dụng
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
from app.models import (
    Department, Employee, JobTitle,
    Reward, Discipline, Evaluation, Attendance, Payroll,
    LeaveType, LeaveBalance, LeaveRequest,
    ExpenseCategory, Expense,
    JobPosting, Application
)

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def clear_all_data():
    """Xóa TẤT CẢ dữ liệu cũ"""
    print_header("XÓA DỮ LIỆU CŨ")
    
    # Xóa theo thứ tự để tránh lỗi foreign key
    Application.objects.all().delete()
    print_success("Đã xóa hồ sơ ứng tuyển")
    
    JobPosting.objects.all().delete()
    print_success("Đã xóa tin tuyển dụng")
    
    Expense.objects.all().delete()
    print_success("Đã xóa đơn hoàn tiền")
    
    ExpenseCategory.objects.all().delete()
    print_success("Đã xóa danh mục chi phí")
    
    LeaveRequest.objects.all().delete()
    print_success("Đã xóa đơn xin nghỉ phép")
    
    LeaveBalance.objects.all().delete()
    print_success("Đã xóa số dư phép")
    
    LeaveType.objects.all().delete()
    print_success("Đã xóa loại nghỉ phép")
    
    Payroll.objects.all().delete()
    print_success("Đã xóa bảng lương")
    
    Attendance.objects.all().delete()
    print_success("Đã xóa chấm công")
    
    Evaluation.objects.all().delete()
    print_success("Đã xóa đánh giá")
    
    Discipline.objects.all().delete()
    print_success("Đã xóa kỷ luật")
    
    Reward.objects.all().delete()
    print_success("Đã xóa khen thưởng")
    
    Employee.objects.all().delete()
    print_success("Đã xóa nhân viên")
    
    JobTitle.objects.all().delete()
    print_success("Đã xóa chức vụ")
    
    Department.objects.all().delete()
    print_success("Đã xóa phòng ban")
    
    # Xóa users (giữ lại superuser)
    User.objects.filter(is_superuser=False).delete()
    print_success("Đã xóa users (giữ lại superuser)")


def create_leave_types():
    """Tạo các loại nghỉ phép"""
    print_header("TẠO LOẠI NGHỈ PHÉP")
    
    leave_types_data = [
        {
            'name': 'Phép năm',
            'code': 'AL',
            'max_days_per_year': 12,
            'requires_approval': True,
            'is_paid': True,
            'description': 'Nghỉ phép năm theo quy định'
        },
        {
            'name': 'Nghỉ ốm',
            'code': 'SL',
            'max_days_per_year': 30,
            'requires_approval': True,
            'is_paid': True,
            'description': 'Nghỉ ốm có giấy bác sĩ'
        },
        {
            'name': 'Nghỉ thai sản',
            'code': 'ML',
            'max_days_per_year': 180,
            'requires_approval': True,
            'is_paid': True,
            'description': 'Nghỉ thai sản (6 tháng)'
        },
        {
            'name': 'Nghỉ cưới',
            'code': 'WL',
            'max_days_per_year': 3,
            'requires_approval': True,
            'is_paid': True,
            'description': 'Nghỉ cưới (3 ngày)'
        },
        {
            'name': 'Nghỉ tang',
            'code': 'BL',
            'max_days_per_year': 5,
            'requires_approval': True,
            'is_paid': True,
            'description': 'Nghỉ tang (5 ngày)'
        },
        {
            'name': 'Nghỉ không lương',
            'code': 'UL',
            'max_days_per_year': 60,
            'requires_approval': True,
            'is_paid': False,
            'description': 'Nghỉ không hưởng lương'
        },
    ]
    
    leave_types = []
    for data in leave_types_data:
        lt = LeaveType.objects.create(**data)
        leave_types.append(lt)
        print_success(f"Tạo loại phép: {lt.name} ({lt.code}) - {lt.max_days_per_year} ngày/năm")
    
    return leave_types


def create_expense_categories():
    """Tạo danh mục chi phí"""
    print_header("TẠO DANH MỤC CHI PHÍ")
    
    categories_data = [
        {'name': 'Đi lại', 'code': 'TRAVEL', 'description': 'Chi phí đi lại công tác'},
        {'name': 'Ăn uống', 'code': 'MEAL', 'description': 'Chi phí ăn uống khách hàng'},
        {'name': 'Khách sạn', 'code': 'HOTEL', 'description': 'Chi phí lưu trú'},
        {'name': 'Văn phòng phẩm', 'code': 'OFFICE', 'description': 'Mua sắm văn phòng phẩm'},
        {'name': 'Đào tạo', 'code': 'TRAINING', 'description': 'Chi phí đào tạo, học tập'},
        {'name': 'Điện thoại', 'code': 'PHONE', 'description': 'Cước điện thoại'},
        {'name': 'Internet', 'code': 'NET', 'description': 'Cước internet'},
        {'name': 'Khác', 'code': 'OTHER', 'description': 'Chi phí khác'},
    ]
    
    categories = []
    for data in categories_data:
        cat = ExpenseCategory.objects.create(**data)
        categories.append(cat)
        print_success(f"Tạo danh mục: {cat.name} ({cat.code})")
    
    return categories


def create_attendance_data(employees, months=3):
    """Tạo dữ liệu chấm công cho 3 tháng gần nhất"""
    print_header(f"TẠO DỮ LIỆU CHẤM CÔNG ({months} THÁNG)")
    
    today = datetime.now().date()
    start_date = today - timedelta(days=months * 30)
    
    attendance_count = 0
    
    for employee in employees:
        current_date = start_date
        
        while current_date <= today:
            # Chỉ tạo cho ngày làm việc (T2-T6)
            if current_date.weekday() < 5:
                # 95% có làm việc, 3% nghỉ phép, 2% nghỉ không phép
                rand = random.random()
                
                if rand < 0.95:
                    status = 'Có làm việc'
                    working_hours = random.choice([8, 8.5, 9, 10])  # Làm thêm giờ đôi khi
                elif rand < 0.98:
                    status = 'Nghỉ phép'
                    working_hours = 0
                else:
                    status = 'Nghỉ không phép'
                    working_hours = 0
                
                Attendance.objects.create(
                    employee=employee,
                    date=datetime.combine(current_date, datetime.min.time()),
                    status=status,
                    working_hours=working_hours,
                    notes=''
                )
                attendance_count += 1
            
            current_date += timedelta(days=1)
    
    print_success(f"Đã tạo {attendance_count} bản ghi chấm công cho {len(employees)} nhân viên")


def create_leave_balances(employees, leave_types, year=2025):
    """Tạo số dư phép cho nhân viên"""
    print_header(f"TẠO SỐ DƯ PHÉP NĂM {year}")
    
    balance_count = 0
    
    for employee in employees:
        for leave_type in leave_types:
            # Phân bổ ngẫu nhiên số ngày đã dùng
            total_days = leave_type.max_days_per_year
            used_days = random.uniform(0, total_days * 0.6)  # Đã dùng 0-60%
            
            LeaveBalance.objects.create(
                employee=employee,
                leave_type=leave_type,
                year=year,
                total_days=total_days,
                used_days=used_days,
                remaining_days=total_days - used_days
            )
            balance_count += 1
    
    print_success(f"Đã tạo {balance_count} bản ghi số dư phép")


def create_leave_requests(employees, leave_types, count=30):
    """Tạo đơn xin nghỉ phép"""
    print_header(f"TẠO ĐƠN XIN NGHỈ PHÉP ({count} ĐƠN)")
    
    statuses = ['pending', 'approved', 'rejected', 'cancelled']
    reasons = [
        'Nghỉ việc riêng',
        'Về quê',
        'Khám bệnh',
        'Con ốm',
        'Đi du lịch',
        'Tham gia đám cưới',
        'Chuyện gia đình',
        'Nghỉ ngơi',
    ]
    
    # Lấy danh sách manager để duyệt đơn
    managers = Employee.objects.filter(is_manager=True)
    
    for i in range(count):
        employee = random.choice(employees)
        leave_type = random.choice(leave_types)
        
        # Random ngày trong 3 tháng vừa qua hoặc tương lai
        days_offset = random.randint(-60, 30)
        start_date = datetime.now().date() + timedelta(days=days_offset)
        total_days = random.choice([1, 2, 3, 5])
        end_date = start_date + timedelta(days=total_days - 1)
        
        status = random.choice(statuses)
        
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            reason=random.choice(reasons),
            status=status
        )
        
        # Nếu đã duyệt/từ chối thì thêm thông tin
        if status in ['approved', 'rejected']:
            leave_request.approved_by = random.choice(managers)
            leave_request.approved_at = datetime.now() - timedelta(days=random.randint(1, 10))
            if status == 'rejected':
                leave_request.rejection_reason = 'Không đủ số dư phép' if random.random() < 0.5 else 'Công việc bận'
            leave_request.save()
    
    print_success(f"Đã tạo {count} đơn xin nghỉ phép")


def create_expenses(employees, categories, count=40):
    """Tạo đơn hoàn tiền chi phí"""
    print_header(f"TẠO ĐƠN HOÀN TIỀN CHI PHÍ ({count} ĐƠN)")
    
    statuses = ['pending', 'approved', 'rejected', 'paid']
    descriptions = {
        'TRAVEL': ['Taxi đi gặp khách', 'Xăng xe công tác', 'Vé máy bay đi Hà Nội', 'Grab đi meeting'],
        'MEAL': ['Ăn trưa với khách hàng', 'Tiệc chiêu đãi đối tác', 'Cà phê bàn công việc'],
        'HOTEL': ['Khách sạn 2 đêm Đà Nẵng', 'Nhà nghỉ công tác Cần Thơ'],
        'OFFICE': ['Mua bút, giấy A4', 'Mua bảng flipchart', 'Mực in'],
        'TRAINING': ['Khóa học Excel nâng cao', 'Workshop về Marketing', 'Sách chuyên môn'],
        'PHONE': ['Cước điện thoại tháng 10', 'Sim data 4G'],
        'NET': ['Internet công ty', 'Wifi cá nhân'],
        'OTHER': ['Sửa chữa máy tính', 'Mua kệ sách', 'Đồ dùng văn phòng'],
    }
    
    managers = Employee.objects.filter(is_manager=True)
    accountants = Employee.objects.filter(department__name='Phòng Kế Toán')
    
    for i in range(count):
        employee = random.choice(employees)
        category = random.choice(categories)
        
        amount = Decimal(random.randint(10, 500)) * 10000  # 100k - 5tr
        date = datetime.now().date() - timedelta(days=random.randint(1, 90))
        description = random.choice(descriptions.get(category.code, ['Chi phí khác']))
        status = random.choice(statuses)
        
        expense = Expense.objects.create(
            employee=employee,
            category=category,
            amount=amount,
            date=date,
            description=description,
            status=status
        )
        
        # Nếu đã duyệt hoặc từ chối
        if status in ['approved', 'rejected', 'paid']:
            expense.approved_by = random.choice(managers)
            expense.approved_at = datetime.now() - timedelta(days=random.randint(1, 30))
            if status == 'rejected':
                expense.rejection_reason = random.choice([
                    'Không đủ hóa đơn chứng từ',
                    'Vượt quá định mức',
                    'Chi phí không hợp lý'
                ])
            expense.save()
        
        # Nếu đã thanh toán
        if status == 'paid' and accountants:
            expense.paid_by = random.choice(accountants)
            expense.paid_at = datetime.now() - timedelta(days=random.randint(1, 15))
            expense.payment_method = random.choice(['cash', 'bank_transfer'])
            expense.payment_reference = f"TXN{random.randint(100000, 999999)}"
            expense.save()
    
    print_success(f"Đã tạo {count} đơn hoàn tiền")


def create_payrolls(employees, months=3):
    """Tạo bảng lương cho 3 tháng gần nhất"""
    print_header(f"TẠO BẢNG LƯƠNG ({months} THÁNG)")
    
    today = datetime.now()
    payroll_count = 0
    
    for i in range(months):
        month = (today.month - i - 1) % 12 + 1
        year = today.year if month <= today.month else today.year - 1
        
        for employee in employees:
            # Tính toán dữ liệu lương
            base_salary = employee.salary
            salary_coefficient = employee.job_title.salary_coefficient if employee.job_title else 1.0
            standard_working_days = 22
            hourly_rate = base_salary / (standard_working_days * 8)
            
            # Lấy tổng giờ làm từ attendance
            start_of_month = datetime(year, month, 1)
            if month == 12:
                end_of_month = datetime(year + 1, 1, 1)
            else:
                end_of_month = datetime(year, month + 1, 1)
            
            total_hours = Attendance.objects.filter(
                employee=employee,
                date__gte=start_of_month,
                date__lt=end_of_month,
                status='Có làm việc'
            ).aggregate(total=django.db.models.Sum('working_hours'))['total'] or 0
            
            # Random bonus và penalty
            bonus = random.choice([0, 0, 0, 500000, 1000000, 2000000])
            penalty = random.choice([0, 0, 0, 0, 100000, 200000])
            
            total_salary = hourly_rate * total_hours + bonus - penalty
            
            Payroll.objects.create(
                employee=employee,
                month=month,
                year=year,
                base_salary=base_salary,
                salary_coefficient=salary_coefficient,
                standard_working_days=standard_working_days,
                hourly_rate=hourly_rate,
                total_working_hours=total_hours,
                bonus=bonus,
                penalty=penalty,
                total_salary=total_salary,
                status=random.choice(['pending', 'confirmed']),
                notes=''
            )
            payroll_count += 1
    
    print_success(f"Đã tạo {payroll_count} bảng lương")


def create_evaluations(employees, count=50):
    """Tạo đánh giá hiệu suất"""
    print_header(f"TẠO ĐÁNH GIÁ HIỆU SUẤT ({count} BẢN)")
    
    periods = ['Tháng 9/2024', 'Tháng 10/2024', 'Tháng 11/2024', 'Q3/2024', 'Q4/2024']
    comments = [
        'Hoàn thành tốt công việc được giao',
        'Tích cực, nhiệt tình, có tinh thần trách nhiệm cao',
        'Cần cải thiện kỹ năng giao tiếp',
        'Làm việc chăm chỉ, đáng tin cậy',
        'Xuất sắc trong dự án vừa qua',
        'Cần chủ động hơn trong công việc',
        'Có tinh thần học hỏi tốt',
        'Kỹ năng chuyên môn tốt, cần phát triển soft skill',
    ]
    
    for i in range(count):
        employee = random.choice(employees)
        score = random.uniform(6.0, 10.0)
        
        Evaluation.objects.create(
            employee=employee,
            period=random.choice(periods),
            score=round(score, 1),
            comment=random.choice(comments)
        )
    
    print_success(f"Đã tạo {count} đánh giá")


def create_rewards(employees, count=15):
    """Tạo khen thưởng"""
    print_header(f"TẠO KHEN THƯỞNG ({count} LẦN)")
    
    descriptions = [
        'Hoàn thành xuất sắc dự án X',
        'Nhân viên của tháng',
        'Đóng góp ý tưởng sáng tạo',
        'Hỗ trợ tích cực team',
        'Đạt KPI vượt mức',
        'Giải pháp tiết kiệm chi phí',
    ]
    
    for i in range(count):
        Reward.objects.create(
            number=1000 + i,
            description=random.choice(descriptions),
            date=datetime.now() - timedelta(days=random.randint(1, 180)),
            amount=random.choice([500000, 1000000, 2000000, 3000000, 5000000]),
            cash_payment=random.choice([True, False]),
            employee=random.choice(employees)
        )
    
    print_success(f"Đã tạo {count} khen thưởng")


def create_disciplines(employees, count=8):
    """Tạo kỷ luật"""
    print_header(f"TẠO KỶ LUẬT ({count} LẦN)")
    
    descriptions = [
        'Đi muộn nhiều lần',
        'Không hoàn thành deadline',
        'Vi phạm quy định công ty',
        'Thái độ làm việc không tốt',
        'Nghỉ không phép',
    ]
    
    for i in range(count):
        Discipline.objects.create(
            number=2000 + i,
            description=random.choice(descriptions),
            date=datetime.now() - timedelta(days=random.randint(1, 180)),
            amount=random.choice([200000, 500000, 1000000]),
            employee=random.choice(employees)
        )
    
    print_success(f"Đã tạo {count} kỷ luật")


def create_job_postings(count=5):
    """Tạo tin tuyển dụng"""
    print_header(f"TẠO TIN TUYỂN DỤNG ({count} VỊ TRÍ)")
    
    jobs_data = [
        {
            'title': 'Lập trình viên PHP/Laravel',
            'code': 'JOB001',
            'department_name': 'Phòng IT',
            'employment_type': 'fulltime',
            'experience_level': 'mid',
            'number_of_positions': 2,
            'location': 'TP. Hồ Chí Minh',
            'salary_min': 15000000,
            'salary_max': 25000000,
            'salary_negotiable': False,
            'description': 'Phát triển và bảo trì hệ thống web của công ty sử dụng PHP/Laravel framework.',
            'requirements': '- 2+ năm kinh nghiệm PHP/Laravel\n- Biết MySQL, Git\n- Có tinh thần làm việc nhóm\n- Có khả năng làm việc độc lập',
            'responsibilities': '- Phát triển các tính năng mới\n- Bảo trì hệ thống hiện tại\n- Tối ưu performance\n- Code review',
            'benefits': '- Lương tháng 13\n- Bảo hiểm đầy đủ\n- Review lương 6 tháng/lần\n- Team building hàng quý',
            'contact_person': 'Phòng Nhân Sự',
            'contact_email': 'hr@company.vn',
            'contact_phone': '0901234567',
        },
        {
            'title': 'Nhân viên Marketing',
            'code': 'JOB002',
            'department_name': 'Phòng Marketing',
            'employment_type': 'fulltime',
            'experience_level': 'junior',
            'number_of_positions': 1,
            'location': 'TP. Hồ Chí Minh',
            'salary_min': 10000000,
            'salary_max': 15000000,
            'salary_negotiable': False,
            'description': 'Thực hiện các chiến dịch marketing online/offline để quảng bá sản phẩm dịch vụ.',
            'requirements': '- Tốt nghiệp Đại học chuyên ngành Marketing\n- Biết sử dụng Facebook Ads, Google Ads\n- Có kinh nghiệm làm content',
            'responsibilities': '- Lên kế hoạch marketing\n- Quản lý fanpage, website\n- Chạy quảng cáo\n- Phân tích hiệu quả chiến dịch',
            'benefits': '- Môi trường trẻ trung, năng động\n- Đào tạo kỹ năng\n- Thưởng KPI hàng tháng',
            'contact_person': 'Phòng Nhân Sự',
            'contact_email': 'hr@company.vn',
            'contact_phone': '0901234567',
        },
        {
            'title': 'Kế toán tổng hợp',
            'code': 'JOB003',
            'department_name': 'Phòng Kế Toán',
            'employment_type': 'fulltime',
            'experience_level': 'mid',
            'number_of_positions': 1,
            'location': 'TP. Hồ Chí Minh',
            'salary_min': 12000000,
            'salary_max': 18000000,
            'salary_negotiable': False,
            'description': 'Quản lý sổ sách kế toán, báo cáo tài chính, thuế cho công ty.',
            'requirements': '- Tốt nghiệp Đại học Kế toán\n- 2+ năm kinh nghiệm\n- Thành thạo Excel, phần mềm kế toán MISA/FAST',
            'responsibilities': '- Hạch toán chứng từ\n- Lập báo cáo tài chính\n- Quyết toán thuế\n- Đối chiếu công nợ',
            'benefits': '- Lương thưởng cạnh tranh\n- Môi trường ổn định\n- Tăng lương định kỳ',
            'contact_person': 'Phòng Nhân Sự',
            'contact_email': 'hr@company.vn',
            'contact_phone': '0901234567',
        },
        {
            'title': 'Nhân viên Nhân sự',
            'code': 'JOB004',
            'department_name': 'Phòng Nhân Sự',
            'employment_type': 'fulltime',
            'experience_level': 'entry',
            'number_of_positions': 1,
            'location': 'TP. Hồ Chí Minh',
            'salary_min': 8000000,
            'salary_max': 12000000,
            'salary_negotiable': False,
            'description': 'Hỗ trợ tuyển dụng, quản lý hồ sơ nhân viên và các công việc HR khác.',
            'requirements': '- Tốt nghiệp Đại học chuyên ngành Quản trị nhân sự\n- Chăm chỉ, cẩn thận\n- Kỹ năng giao tiếp tốt',
            'responsibilities': '- Đăng tin tuyển dụng\n- Sàng lọc hồ sơ\n- Quản lý dữ liệu nhân sự\n- Hỗ trợ công tác đào tạo',
            'benefits': '- Được đào tạo bài bản\n- Cơ hội thăng tiến\n- Môi trường trẻ, năng động',
            'contact_person': 'Phòng Nhân Sự',
            'contact_email': 'hr@company.vn',
            'contact_phone': '0901234567',
        },
        {
            'title': 'Thực tập sinh IT',
            'code': 'JOB005',
            'department_name': 'Phòng IT',
            'employment_type': 'internship',
            'experience_level': 'entry',
            'number_of_positions': 3,
            'location': 'TP. Hồ Chí Minh',
            'salary_min': 3000000,
            'salary_max': 5000000,
            'salary_negotiable': False,
            'description': 'Học tập và hỗ trợ team phát triển sản phẩm web/mobile.',
            'requirements': '- Sinh viên năm 3, 4 hoặc mới tốt nghiệp\n- Có kiến thức về lập trình web\n- Biết HTML, CSS, JavaScript cơ bản',
            'responsibilities': '- Học hỏi từ senior\n- Làm các task nhỏ\n- Viết tài liệu kỹ thuật\n- Testing',
            'benefits': '- Được mentor bởi senior\n- Cơ hội trở thành nhân viên chính thức\n- Môi trường học hỏi tốt',
            'contact_person': 'Phòng Nhân Sự',
            'contact_email': 'hr@company.vn',
            'contact_phone': '0901234567',
        },
    ]
    
    job_postings = []
    
    for job_data in jobs_data:
        dept_name = job_data.pop('department_name')
        department = Department.objects.filter(name=dept_name).first()
        
        # Random deadline (1-3 tháng)
        deadline = datetime.now().date() + timedelta(days=random.randint(30, 90))
        start_date = deadline + timedelta(days=random.randint(7, 30))
        
        # Lấy người tạo (HR hoặc Manager)
        hr_staff = Employee.objects.filter(department__name='Phòng Nhân Sự').first()
        
        job = JobPosting.objects.create(
            department=department,
            deadline=deadline,
            start_date=start_date,
            status=random.choice(['open', 'open', 'draft']),
            created_by=hr_staff,
            **job_data
        )
        job_postings.append(job)
        print_success(f"Tạo tin tuyển dụng: {job.title}")
    
    return job_postings


def create_applications(job_postings, count=20):
    """Tạo hồ sơ ứng tuyển"""
    print_header(f"TẠO HỒ SƠ ỨNG TUYỂN ({count} HỒ SƠ)")
    
    first_names = ['An', 'Bình', 'Châu', 'Dũng', 'Giang', 'Hà', 'Khoa', 'Linh', 'Mai', 'Nam', 'Phúc', 'Quân', 'Trang', 'Uyên', 'Vinh']
    last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ']
    
    statuses = ['new', 'screening', 'phone_interview', 'interview', 'test', 'offer', 'rejected']
    sources = ['website', 'referral', 'linkedin', 'facebook', 'vietnamworks']
    
    # Lấy HR để assign
    hr_staff = Employee.objects.filter(department__name='Phòng Nhân Sự').first()
    
    for i in range(count):
        job = random.choice(job_postings)
        
        full_name = f"{random.choice(last_names)} {random.choice(first_names)}"
        email = f"{full_name.lower().replace(' ', '')}{random.randint(100, 999)}@gmail.com"
        phone = f"09{random.randint(10000000, 99999999)}"
        
        status = random.choice(statuses)
        
        Application.objects.create(
            job=job,
            application_code=f"APP{datetime.now().year}{str(i+1).zfill(4)}",
            full_name=full_name,
            email=email,
            phone=phone,
            date_of_birth=datetime.now().date() - timedelta(days=random.randint(8000, 12000)),
            gender=random.choice([0, 1]),
            current_position=random.choice(['Sinh viên', 'Nhân viên', 'Trưởng nhóm', 'Freelancer', 'Không có']),
            current_company=random.choice(['', 'FPT', 'Viettel', 'VNPT', 'Tập đoàn X', 'Công ty Y']),
            years_of_experience=random.randint(0, 8),
            education_level=random.choice([2, 3, 4]),  # Cao đẳng, Đại học, Thạc sĩ
            school=random.choice(['ĐH Bách Khoa', 'ĐH Kinh Tế', 'ĐH KHTN', 'ĐH Công Nghệ']),
            major=random.choice(['Công nghệ thông tin', 'Marketing', 'Kế toán', 'Quản trị nhân sự']),
            cover_letter=f'Kính gửi ban tuyển dụng,\n\nTôi rất quan tâm đến vị trí {job.title}.\nTôi tin rằng với kinh nghiệm và kỹ năng của mình, tôi có thể đóng góp tích cực cho công ty.\n\nTrân trọng,\n{full_name}',
            expected_salary=random.randint(8, 30) * 1000000,
            status=status,
            source=random.choice(sources),
            rating=random.choice([None, None, 3, 4, 5]),
            assigned_to=hr_staff,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60))
        )
    
    print_success(f"Đã tạo {count} hồ sơ ứng tuyển")


def main():
    """Main function"""
    print_header("TẠO DỮ LIỆU ĐẦY ĐỦ CHO HỆ THỐNG HRM")
    
    confirm = input("\n⚠️  Script sẽ XÓA TẤT CẢ dữ liệu và tạo mới. Tiếp tục? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Đã hủy!")
        return 1
    
    try:
        # Import script tạo nhân viên cũ
        import create_sample_data_simple
        
        # Xóa dữ liệu cũ
        clear_all_data()
        
        # Tạo dữ liệu cơ bản (Department, JobTitle, Employee, User)
        print_header("TẠO DỮ LIỆU CƠ BẢN")
        print("Sử dụng script create_sample_data_simple.py...\n")
        
        departments = create_sample_data_simple.create_departments()
        job_titles = create_sample_data_simple.create_job_titles()
        employees = create_sample_data_simple.create_employees(departments, job_titles)
        
        # Tạo dữ liệu mở rộng
        leave_types = create_leave_types()
        expense_categories = create_expense_categories()
        
        # Tạo dữ liệu cho các tính năng
        create_attendance_data(employees, months=3)
        create_leave_balances(employees, leave_types, year=2025)
        create_leave_requests(employees, leave_types, count=30)
        create_expenses(employees, expense_categories, count=40)
        create_payrolls(employees, months=3)
        create_evaluations(employees, count=50)
        create_rewards(employees, count=15)
        create_disciplines(employees, count=8)
        
        # Tạo dữ liệu tuyển dụng
        job_postings = create_job_postings(count=5)
        create_applications(job_postings, count=20)
        
        # Thống kê
        print_header("THỐNG KÊ TỔNG HỢP")
        print_success(f"📊 Phòng ban: {Department.objects.count()}")
        print_success(f"📊 Chức vụ: {JobTitle.objects.count()}")
        print_success(f"👥 Nhân viên: {Employee.objects.count()}")
        print_success(f"📅 Chấm công: {Attendance.objects.count()}")
        print_success(f"💰 Bảng lương: {Payroll.objects.count()}")
        print_success(f"🏖️  Loại nghỉ phép: {LeaveType.objects.count()}")
        print_success(f"📝 Đơn nghỉ phép: {LeaveRequest.objects.count()}")
        print_success(f"💳 Đơn hoàn tiền: {Expense.objects.count()}")
        print_success(f"⭐ Đánh giá: {Evaluation.objects.count()}")
        print_success(f"🏆 Khen thưởng: {Reward.objects.count()}")
        print_success(f"⚠️  Kỷ luật: {Discipline.objects.count()}")
        print_success(f"📢 Tin tuyển dụng: {JobPosting.objects.count()}")
        print_success(f"📄 Hồ sơ ứng tuyển: {Application.objects.count()}")
        
        print_header("HOÀN TẤT")
        print("🎉 Đã tạo dữ liệu đầy đủ cho TẤT CẢ tính năng!")
        print("\n💡 Chạy server: python manage.py runserver")
        print("   Truy cập: http://localhost:8000/\n")
        
        return 0
        
    except Exception as e:
        print_error(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
