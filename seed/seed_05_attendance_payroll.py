"""
Seed 05: Attendance and Payroll
Run: python manage.py shell < seed/seed_05_attendance_payroll.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import Employee, Attendance, Payroll

print_header("SEED 05: Attendance & Payroll")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
Payroll.objects.all().delete()
Attendance.objects.all().delete()

# ============================================================================
# 1. TẠO CHẤM CÔNG
# ============================================================================
print("\n1. Tạo dữ liệu chấm công...")
attendance_count = 0

# Tạo chấm công cho 3 tháng: 9, 10, 11
for month in [9, 10, 11]:
    print(f"   Tạo chấm công tháng {month}...")
    for day in range(1, 29):
        try:
            current_date = date(2025, month, day)
        except ValueError:
            continue
        
        # Bỏ qua thứ 7, CN
        if current_date.weekday() >= 5:
            continue
        
        for emp in Employee.objects.exclude(status=3):  # Không tính đã nghỉ việc
            # 90% đi làm, 5% nghỉ phép, 5% nghỉ không phép
            rand = random.random()
            if rand < 0.90:
                status = "Có làm việc"
                working_hours = random.choice([8.0, 8.0, 8.0, 8.5, 7.5, 9.0, 9.5])
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

print_success(f"Đã tạo {attendance_count} bản ghi chấm công")

# ============================================================================
# 2. TẠO BẢNG LƯƠNG
# ============================================================================
print("\n2. Tạo bảng lương...")
payroll_count = 0

for month in [9, 10, 11]:
    print(f"   Tạo bảng lương tháng {month}...")
    for emp in Employee.objects.exclude(status=3):
        # Tính số giờ làm việc
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
        bonus = random.choice([0, 0, 0, 0, 500000, 1000000, 2000000, 3000000])
        penalty = random.choice([0, 0, 0, 0, 0, 200000, 500000])
        
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

print_success(f"Đã tạo {payroll_count} bảng lương")

print_header("HOÀN TẤT SEED 05")
print(f"- Chấm công: {Attendance.objects.count()}")
print(f"  + Có làm việc: {Attendance.objects.filter(status='Có làm việc').count()}")
print(f"  + Nghỉ phép: {Attendance.objects.filter(status='Nghỉ phép').count()}")
print(f"  + Nghỉ không phép: {Attendance.objects.filter(status='Nghỉ không phép').count()}")
print(f"- Bảng lương: {Payroll.objects.count()}")
print(f"  + Đã xác nhận: {Payroll.objects.filter(status='confirmed').count()}")
print(f"  + Chờ xác nhận: {Payroll.objects.filter(status='pending').count()}")

# Tổng lương theo tháng
from django.db.models import Sum
for month in [9, 10, 11]:
    total = Payroll.objects.filter(month=month, year=2025).aggregate(total=Sum('total_salary'))['total'] or 0
    print(f"  + Tổng lương tháng {month}: {total:,.0f} VNĐ")
