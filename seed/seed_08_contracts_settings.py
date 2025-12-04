"""
Seed 08: Contracts and System Settings
Run: python manage.py shell < seed/seed_08_contracts_settings.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import Employee, Department, JobTitle, Contract, SystemSettings

print_header("SEED 08: Contracts & System Settings")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear contracts
print("Xóa hợp đồng cũ...")
Contract.objects.all().delete()

# ============================================================================
# 1. TẠO HỢP ĐỒNG LAO ĐỘNG
# ============================================================================
print("\n1. Tạo hợp đồng lao động...")
contract_count = 0
hr_manager = Employee.objects.filter(employee_code="HR001").first()

for emp in Employee.objects.all():
    # Xác định loại hợp đồng
    if emp.status == 0:  # Thực tập
        contract_type = "probation"
        duration_months = 3
    elif emp.status == 1:  # Thử việc
        contract_type = "probation"
        duration_months = 2
    elif emp.is_manager or (emp.job_title and emp.job_title.salary_coefficient >= 5.0):
        contract_type = "indefinite"
        duration_months = None
    else:
        contract_type = random.choice(["fixed_term", "fixed_term", "indefinite"])
        duration_months = random.choice([12, 24, 36]) if contract_type == "fixed_term" else None
    
    # Ngày bắt đầu
    start_date = emp.contract_start_date
    end_date = start_date + timedelta(days=duration_months * 30) if duration_months else None
    
    Contract.objects.create(
        employee=emp,
        contract_type=contract_type,
        start_date=start_date,
        end_date=end_date,
        signed_date=start_date - timedelta(days=random.randint(1, 7)),
        base_salary=Decimal(emp.salary),
        job_title=emp.job_title,
        department=emp.department,
        work_location="Tòa nhà ABC, 123 Nguyễn Trãi, Thanh Xuân, Hà Nội",
        working_hours="08:00-12:00, 13:00-17:00",
        status="active" if emp.status in [1, 2] else "draft",
        terms="""ĐIỀU KHOẢN HỢP ĐỒNG LAO ĐỘNG

1. Thời gian làm việc: 8 giờ/ngày, 5 ngày/tuần (Thứ 2 - Thứ 6)
2. Địa điểm làm việc: Tòa nhà ABC, 123 Nguyễn Trãi, Thanh Xuân, Hà Nội
3. Quyền lợi:
   - Lương tháng 13
   - BHXH, BHYT, BHTN theo quy định
   - Nghỉ phép năm: 12 ngày/năm
   - Đào tạo nâng cao chuyên môn
4. Nghĩa vụ:
   - Tuân thủ nội quy công ty
   - Hoàn thành công việc được giao
   - Bảo mật thông tin công ty
""",
        created_by=hr_manager
    )
    contract_count += 1

print_success(f"Đã tạo {contract_count} hợp đồng")

# ============================================================================
# 2. CẬP NHẬT SYSTEM SETTINGS
# ============================================================================
print("\n2. Cập nhật System Settings...")

settings = SystemSettings.get_settings()
settings.company_name = "Công ty TNHH Công nghệ ABC"
settings.company_address = "Tầng 10, Tòa nhà ABC, 123 Nguyễn Trãi, Thanh Xuân, Hà Nội"
settings.company_phone = "024-3456-7890"
settings.company_email = "contact@abctech.com.vn"
settings.company_website = "https://www.abctech.com.vn"
settings.company_tax_code = "0123456789"

# Work settings
settings.standard_working_days = 22
settings.standard_working_hours = Decimal("8.00")
settings.work_start_time = "08:00"
settings.work_end_time = "17:00"
settings.lunch_break_start = "12:00"
settings.lunch_break_end = "13:00"

# Insurance rates (2025)
settings.social_insurance_rate = Decimal("8.00")
settings.health_insurance_rate = Decimal("1.50")
settings.unemployment_insurance_rate = Decimal("1.00")
settings.employer_social_insurance_rate = Decimal("17.50")
settings.employer_health_insurance_rate = Decimal("3.00")
settings.employer_unemployment_insurance_rate = Decimal("1.00")

# Tax settings
settings.tax_rate = Decimal("10.00")
settings.tax_deduction_personal = Decimal("11000000")
settings.tax_deduction_dependent = Decimal("4400000")
settings.minimum_wage = Decimal("4960000")
settings.social_insurance_max_salary = Decimal("46800000")

# Notification settings
settings.notify_leave_approved = True
settings.notify_expense_approved = True
settings.notify_contract_expiring = True
settings.contract_expiring_days = 30
settings.notify_appraisal_reminder = True
settings.notify_welcome_email = True

# System settings
settings.date_format = "d/m/Y"
settings.currency_symbol = "VNĐ"
settings.pagination_size = 20

settings.save()
print_success("Đã cập nhật System Settings")

print_header("HOÀN TẤT SEED 08")
print(f"- Hợp đồng: {Contract.objects.count()}")
print(f"  + Thử việc: {Contract.objects.filter(contract_type='probation').count()}")
print(f"  + Xác định thời hạn: {Contract.objects.filter(contract_type='fixed_term').count()}")
print(f"  + Không xác định thời hạn: {Contract.objects.filter(contract_type='indefinite').count()}")
print(f"  + Đang hiệu lực: {Contract.objects.filter(status='active').count()}")
print(f"- System Settings: Đã cấu hình")
print(f"  + Công ty: {settings.company_name}")
print(f"  + BHXH NLĐ: {settings.social_insurance_rate}%")
print(f"  + BHYT NLĐ: {settings.health_insurance_rate}%")
print(f"  + BHTN NLĐ: {settings.unemployment_insurance_rate}%")
