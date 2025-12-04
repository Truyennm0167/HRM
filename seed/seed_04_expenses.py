"""
Seed 04: Expense Categories and Expense Claims
Run: python manage.py shell < seed/seed_04_expenses.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import Employee, ExpenseCategory, Expense

print_header("SEED 04: Expense Management")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
Expense.objects.all().delete()
ExpenseCategory.objects.all().delete()

# ============================================================================
# 1. TẠO DANH MỤC CHI PHÍ
# ============================================================================
print("\n1. Tạo danh mục chi phí...")
categories_data = [
    {"name": "Đi lại", "code": "TRAVEL", "description": "Chi phí xăng xe, taxi, grab, vé máy bay..."},
    {"name": "Ăn uống", "code": "FOOD", "description": "Chi phí tiếp khách, ăn trưa công tác..."},
    {"name": "Khách sạn", "code": "HOTEL", "description": "Chi phí lưu trú khi đi công tác"},
    {"name": "Văn phòng phẩm", "code": "OFFICE", "description": "Chi phí mua VPP, thiết bị văn phòng"},
    {"name": "Đào tạo", "code": "TRAINING", "description": "Chi phí học tập, thi chứng chỉ, khóa học"},
    {"name": "Khác", "code": "OTHER", "description": "Các chi phí khác"},
]

categories = {}
for cat in categories_data:
    categories[cat["code"]] = ExpenseCategory.objects.create(**cat)
print_success(f"Đã tạo {len(categories)} danh mục chi phí")

# ============================================================================
# 2. TẠO YÊU CẦU HOÀN TIỀN
# ============================================================================
print("\n2. Tạo yêu cầu hoàn tiền...")
hr_manager = Employee.objects.filter(employee_code="HR001").first()
expense_count = 0

descriptions_by_category = {
    "TRAVEL": [
        "Chi phí taxi đi gặp khách hàng",
        "Vé máy bay công tác Đà Nẵng",
        "Tiền xăng xe tháng {}",
        "Chi phí grab đi họp",
        "Phí gửi xe tháng {}"
    ],
    "FOOD": [
        "Tiếp khách hàng ABC Corp",
        "Ăn trưa với đối tác",
        "Chi phí ăn uống công tác",
        "Tiếp khách dự án XYZ",
        "Team lunch tháng {}"
    ],
    "HOTEL": [
        "Khách sạn công tác TP.HCM",
        "Lưu trú công tác Đà Nẵng",
        "Khách sạn đi triển khai dự án",
    ],
    "OFFICE": [
        "Mua văn phòng phẩm",
        "Mực in, giấy A4",
        "Thiết bị văn phòng",
        "Bàn phím, chuột máy tính"
    ],
    "TRAINING": [
        "Học phí khóa AWS",
        "Thi chứng chỉ PMP",
        "Khóa học tiếng Anh",
        "Học Python nâng cao"
    ],
    "OTHER": [
        "Chi phí phát sinh dự án",
        "Quà tặng khách hàng",
        "Chi phí sự kiện công ty"
    ]
}

amounts_by_category = {
    "TRAVEL": [50000, 100000, 200000, 500000, 1000000, 3000000, 5000000],
    "FOOD": [200000, 300000, 500000, 800000, 1000000, 2000000],
    "HOTEL": [500000, 800000, 1200000, 1500000, 2000000],
    "OFFICE": [100000, 200000, 300000, 500000],
    "TRAINING": [500000, 1000000, 2000000, 5000000, 10000000],
    "OTHER": [100000, 200000, 500000, 1000000]
}

for emp in Employee.objects.filter(status=2):
    # Mỗi nhân viên 0-5 yêu cầu
    for _ in range(random.randint(0, 5)):
        cat_code = random.choice(list(categories.keys()))
        cat = categories[cat_code]
        
        desc_template = random.choice(descriptions_by_category[cat_code])
        month = random.randint(1, 11)
        description = desc_template.format(month) if "{}" in desc_template else desc_template
        
        amount = random.choice(amounts_by_category[cat_code])
        status = random.choice(["approved", "approved", "pending", "paid", "rejected"])
        
        Expense.objects.create(
            employee=emp,
            category=cat,
            amount=Decimal(amount),
            date=date(2025, month, random.randint(1, 28)),
            description=description,
            status=status,
            approved_by=hr_manager if status in ["approved", "paid", "rejected"] else None,
            approved_at=timezone.now() - timedelta(days=random.randint(1, 30)) if status in ["approved", "paid", "rejected"] else None,
            rejection_reason="Không có hóa đơn/chứng từ hợp lệ" if status == "rejected" else ""
        )
        expense_count += 1

print_success(f"Đã tạo {expense_count} yêu cầu hoàn tiền")

print_header("HOÀN TẤT SEED 04")
print(f"- Danh mục chi phí: {ExpenseCategory.objects.count()}")
print(f"- Yêu cầu hoàn tiền: {Expense.objects.count()}")
print(f"  + Chờ duyệt: {Expense.objects.filter(status='pending').count()}")
print(f"  + Đã duyệt: {Expense.objects.filter(status='approved').count()}")
print(f"  + Đã thanh toán: {Expense.objects.filter(status='paid').count()}")
print(f"  + Từ chối: {Expense.objects.filter(status='rejected').count()}")

# Tổng tiền theo trạng thái
from django.db.models import Sum
for status in ['pending', 'approved', 'paid']:
    total = Expense.objects.filter(status=status).aggregate(total=Sum('amount'))['total'] or 0
    print(f"  + Tổng tiền {status}: {total:,.0f} VNĐ")
