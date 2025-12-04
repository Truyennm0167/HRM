"""
Seed 06: Rewards, Disciplines, Evaluations
Run: python manage.py shell < seed/seed_06_rewards_disciplines.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import Employee, Reward, Discipline, Evaluation

print_header("SEED 06: Rewards, Disciplines & Evaluations")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
Evaluation.objects.all().delete()
Discipline.objects.all().delete()
Reward.objects.all().delete()

# Get employees by code
employees = {e.employee_code: e for e in Employee.objects.all()}

# ============================================================================
# 1. TẠO KHEN THƯỞNG
# ============================================================================
print("\n1. Tạo khen thưởng...")
rewards_data = [
    {"emp": "GD001", "desc": "Lãnh đạo xuất sắc, đưa công ty đạt doanh thu kỷ lục năm 2025", "amount": 50000000},
    {"emp": "IT001", "desc": "Hoàn thành xuất sắc dự án chuyển đổi số toàn công ty", "amount": 15000000},
    {"emp": "IT003", "desc": "Phát hiện và khắc phục lỗi bảo mật nghiêm trọng hệ thống", "amount": 8000000},
    {"emp": "IT004", "desc": "Tối ưu hiệu suất hệ thống, giảm 50% thời gian xử lý", "amount": 5000000},
    {"emp": "SALE001", "desc": "Vượt 150% chỉ tiêu doanh số Q3/2025", "amount": 20000000},
    {"emp": "SALE003", "desc": "Ký kết thành công hợp đồng lớn với ABC Corporation", "amount": 12000000},
    {"emp": "SALE004", "desc": "Top sales tháng 10/2025", "amount": 5000000},
    {"emp": "HR001", "desc": "Tổ chức thành công chương trình team building 2025", "amount": 5000000},
    {"emp": "HR002", "desc": "Hoàn thành xuất sắc công tác tuyển dụng Q3", "amount": 3000000},
    {"emp": "FIN001", "desc": "Tối ưu quy trình kế toán, tiết kiệm 20% thời gian", "amount": 8000000},
    {"emp": "FIN003", "desc": "Phát hiện sai sót thuế, tránh phạt 100 triệu", "amount": 5000000},
    {"emp": "MKT001", "desc": "Chiến dịch marketing tăng 200% traffic website", "amount": 10000000},
    {"emp": "MKT002", "desc": "Video quảng cáo đạt 1 triệu views", "amount": 3000000},
    {"emp": "CS001", "desc": "Đạt 98% độ hài lòng khách hàng năm 2025", "amount": 7000000},
    {"emp": "IT002", "desc": "Mentor xuất sắc, đào tạo 3 nhân viên mới", "amount": 4000000},
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
print_success(f"Đã tạo {reward_count} khen thưởng")

# ============================================================================
# 2. TẠO KỶ LUẬT
# ============================================================================
print("\n2. Tạo kỷ luật...")
disciplines_data = [
    {"emp": "SALE007", "desc": "Đi làm muộn quá 5 lần trong tháng 10/2025", "amount": 500000},
    {"emp": "IT008", "desc": "Không tuân thủ quy trình bảo mật thông tin", "amount": 1000000},
    {"emp": "CS005", "desc": "Phản hồi khách hàng không đúng quy trình, gây khiếu nại", "amount": 500000},
    {"emp": "MKT004", "desc": "Đăng nội dung chưa được duyệt lên fanpage", "amount": 300000},
    {"emp": "HR004", "desc": "Để lộ thông tin lương nhân viên", "amount": 2000000},
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
print_success(f"Đã tạo {discipline_count} kỷ luật")

# ============================================================================
# 3. TẠO ĐÁNH GIÁ NHÂN VIÊN
# ============================================================================
print("\n3. Tạo đánh giá nhân viên...")
evaluation_count = 0
periods = ["Q1/2025", "Q2/2025", "Q3/2025"]

comments_by_score = {
    5.0: "Xuất sắc, vượt mọi kỳ vọng. Cần được xem xét thăng chức.",
    4.5: "Rất tốt, hoàn thành vượt mức. Tiếp tục phát huy.",
    4.0: "Tốt, hoàn thành tốt công việc được giao.",
    3.5: "Khá, hoàn thành công việc, cần cải thiện một số điểm.",
    3.0: "Trung bình, cần nỗ lực hơn trong công việc.",
}

for emp in Employee.objects.filter(status=2):  # Chỉ nhân viên chính thức
    for period in periods:
        # Manager và senior có điểm cao hơn
        if emp.is_manager:
            score = round(random.uniform(4.0, 5.0), 1)
        elif emp.job_title and emp.job_title.salary_coefficient >= 4.0:
            score = round(random.uniform(3.5, 5.0), 1)
        else:
            score = round(random.uniform(3.0, 5.0), 1)
        
        # Round to nearest 0.5
        score = round(score * 2) / 2
        comment = comments_by_score.get(score, "Hoàn thành công việc được giao.")
        
        Evaluation.objects.create(
            employee=emp,
            period=period,
            score=score,
            comment=comment
        )
        evaluation_count += 1

print_success(f"Đã tạo {evaluation_count} đánh giá")

print_header("HOÀN TẤT SEED 06")
print(f"- Khen thưởng: {Reward.objects.count()}")
from django.db.models import Sum
total_reward = Reward.objects.aggregate(total=Sum('amount'))['total'] or 0
print(f"  + Tổng tiền thưởng: {total_reward:,.0f} VNĐ")
print(f"- Kỷ luật: {Discipline.objects.count()}")
total_discipline = Discipline.objects.aggregate(total=Sum('amount'))['total'] or 0
print(f"  + Tổng tiền phạt: {total_discipline:,.0f} VNĐ")
print(f"- Đánh giá: {Evaluation.objects.count()}")
from django.db.models import Avg
for period in periods:
    avg_score = Evaluation.objects.filter(period=period).aggregate(avg=Avg('score'))['avg'] or 0
    print(f"  + Điểm TB {period}: {avg_score:.2f}")
