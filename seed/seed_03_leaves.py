"""
Seed 03: Leave Types, Balances, Requests
Run: python manage.py shell < seed/seed_03_leaves.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import Employee, LeaveType, LeaveBalance, LeaveRequest

print_header("SEED 03: Leave Management")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
LeaveRequest.objects.all().delete()
LeaveBalance.objects.all().delete()
LeaveType.objects.all().delete()

# ============================================================================
# 1. TẠO LOẠI NGHỈ PHÉP
# ============================================================================
print("\n1. Tạo loại nghỉ phép...")
leave_types_data = [
    {"name": "Phép năm", "code": "AL", "description": "Nghỉ phép năm theo quy định", "max_days_per_year": 12, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ ốm", "code": "SL", "description": "Nghỉ ốm có giấy bác sĩ", "max_days_per_year": 30, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ cưới (bản thân)", "code": "WL", "description": "Nghỉ khi kết hôn", "max_days_per_year": 3, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ tang", "code": "FL", "description": "Nghỉ tang lễ người thân", "max_days_per_year": 3, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ thai sản", "code": "ML", "description": "Nghỉ thai sản theo luật", "max_days_per_year": 180, "requires_approval": True, "is_paid": True},
    {"name": "Nghỉ không lương", "code": "UL", "description": "Nghỉ không hưởng lương", "max_days_per_year": 30, "requires_approval": True, "is_paid": False},
]

leave_types = {}
for lt in leave_types_data:
    leave_types[lt["code"]] = LeaveType.objects.create(**lt)
print_success(f"Đã tạo {len(leave_types)} loại nghỉ phép")

# ============================================================================
# 2. TẠO SỐ DƯ NGÀY PHÉP
# ============================================================================
print("\n2. Tạo số dư ngày phép...")
balance_count = 0
for emp in Employee.objects.filter(status=2):  # Chỉ nhân viên chính thức
    for code, lt in leave_types.items():
        if code == "ML" and emp.gender == 0:  # Nam không có thai sản
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
        balance_count += 1
print_success(f"Đã tạo {balance_count} bản ghi số dư ngày phép")

# ============================================================================
# 3. TẠO ĐƠN XIN NGHỈ PHÉP
# ============================================================================
print("\n3. Tạo đơn xin nghỉ phép...")
hr_manager = Employee.objects.filter(employee_code="HR001").first()
request_count = 0

reasons = [
    "Về quê thăm gia đình",
    "Bị cảm, cần nghỉ ngơi",
    "Có việc gia đình cần giải quyết",
    "Đi khám sức khỏe định kỳ",
    "Đưa con đi học",
    "Có lịch hẹn bác sĩ",
    "Đi du lịch cùng gia đình",
    "Tham gia sự kiện gia đình"
]

for emp in Employee.objects.filter(status=2):
    # Mỗi nhân viên 0-3 đơn
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
            reason=random.choice(reasons),
            status=status,
            approved_by=hr_manager if status in ["approved", "rejected"] else None,
            approved_at=timezone.now() - timedelta(days=random.randint(1, 30)) if status in ["approved", "rejected"] else None,
            rejection_reason="Không đủ số ngày phép còn lại" if status == "rejected" else ""
        )
        request_count += 1

print_success(f"Đã tạo {request_count} đơn xin nghỉ phép")

print_header("HOÀN TẤT SEED 03")
print(f"- Loại nghỉ phép: {LeaveType.objects.count()}")
print(f"- Số dư ngày phép: {LeaveBalance.objects.count()}")
print(f"- Đơn xin nghỉ: {LeaveRequest.objects.count()}")
print(f"  + Đã duyệt: {LeaveRequest.objects.filter(status='approved').count()}")
print(f"  + Chờ duyệt: {LeaveRequest.objects.filter(status='pending').count()}")
print(f"  + Từ chối: {LeaveRequest.objects.filter(status='rejected').count()}")
