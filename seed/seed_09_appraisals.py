"""
Seed 09: Appraisal Periods, Criteria, and Appraisals
Run: python manage.py shell < seed/seed_09_appraisals.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import (
    Employee, Department, 
    AppraisalPeriod, AppraisalCriteria, Appraisal, AppraisalScore
)

print_header("SEED 09: Performance Appraisals")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
AppraisalScore.objects.all().delete()
Appraisal.objects.all().delete()
AppraisalCriteria.objects.all().delete()
AppraisalPeriod.objects.all().delete()

hr_manager = Employee.objects.filter(employee_code="HR001").first()

# ============================================================================
# 1. TẠO KỲ ĐÁNH GIÁ
# ============================================================================
print("\n1. Tạo kỳ đánh giá...")

periods_data = [
    {
        "name": "Đánh giá giữa năm 2025",
        "description": "Đánh giá hiệu suất làm việc 6 tháng đầu năm 2025",
        "start_date": date(2025, 6, 1),
        "end_date": date(2025, 6, 30),
        "self_deadline": date(2025, 6, 15),
        "manager_deadline": date(2025, 6, 25),
        "status": "closed"
    },
    {
        "name": "Đánh giá cuối năm 2025",
        "description": "Đánh giá hiệu suất làm việc toàn năm 2025",
        "start_date": date(2025, 12, 1),
        "end_date": date(2025, 12, 31),
        "self_deadline": date(2025, 12, 15),
        "manager_deadline": date(2025, 12, 25),
        "status": "active"
    },
]

periods = {}
for p in periods_data:
    period = AppraisalPeriod.objects.create(
        name=p["name"],
        description=p["description"],
        start_date=p["start_date"],
        end_date=p["end_date"],
        self_assessment_deadline=p["self_deadline"],
        manager_review_deadline=p["manager_deadline"],
        status=p["status"],
        created_by=hr_manager
    )
    periods[p["name"]] = period

print_success(f"Đã tạo {len(periods)} kỳ đánh giá")

# ============================================================================
# 2. TẠO TIÊU CHÍ ĐÁNH GIÁ
# ============================================================================
print("\n2. Tạo tiêu chí đánh giá...")

criteria_data = [
    # Hiệu suất công việc (50%)
    {"name": "Hoàn thành công việc", "desc": "Hoàn thành công việc được giao đúng thời hạn và chất lượng", "category": "performance", "weight": 20, "order": 1},
    {"name": "Chất lượng công việc", "desc": "Mức độ chính xác và chuyên nghiệp trong công việc", "category": "performance", "weight": 15, "order": 2},
    {"name": "Năng suất làm việc", "desc": "Khối lượng công việc hoàn thành so với kỳ vọng", "category": "performance", "weight": 15, "order": 3},
    
    # Hành vi & Thái độ (20%)
    {"name": "Tinh thần trách nhiệm", "desc": "Ý thức trách nhiệm với công việc và đồng nghiệp", "category": "behavior", "weight": 10, "order": 4},
    {"name": "Kỷ luật lao động", "desc": "Tuân thủ nội quy, quy định công ty", "category": "behavior", "weight": 10, "order": 5},
    
    # Kỹ năng (20%)
    {"name": "Kỹ năng chuyên môn", "desc": "Kiến thức và kỹ năng trong lĩnh vực chuyên môn", "category": "skill", "weight": 10, "order": 6},
    {"name": "Kỹ năng làm việc nhóm", "desc": "Khả năng phối hợp và hỗ trợ đồng nghiệp", "category": "skill", "weight": 10, "order": 7},
    
    # Phát triển (10%)
    {"name": "Học hỏi & Phát triển", "desc": "Chủ động học hỏi, nâng cao năng lực bản thân", "category": "development", "weight": 10, "order": 8},
]

criteria_count = 0
for period in periods.values():
    for c in criteria_data:
        AppraisalCriteria.objects.create(
            period=period,
            name=c["name"],
            description=c["desc"],
            category=c["category"],
            weight=Decimal(c["weight"]),
            max_score=5,
            order=c["order"]
        )
        criteria_count += 1

print_success(f"Đã tạo {criteria_count} tiêu chí đánh giá")

# ============================================================================
# 3. TẠO ĐÁNH GIÁ NHÂN VIÊN
# ============================================================================
print("\n3. Tạo đánh giá nhân viên...")

# Get managers by department
managers = {}
for emp in Employee.objects.filter(is_manager=True):
    if emp.department:
        managers[emp.department.id] = emp

appraisal_count = 0
score_count = 0

rating_map = {
    (4.5, 5.0): "outstanding",
    (4.0, 4.5): "exceeds",
    (3.0, 4.0): "meets",
    (2.0, 3.0): "needs_improvement",
    (0, 2.0): "unsatisfactory"
}

for period in periods.values():
    for emp in Employee.objects.filter(status=2):  # Nhân viên chính thức
        # Get manager
        manager = managers.get(emp.department_id) if emp.department else hr_manager
        if manager == emp:  # Manager không tự đánh giá mình
            manager = hr_manager
        
        # Determine status based on period
        if period.status == "closed":
            status = "completed"
        else:
            status = random.choice(["pending_self", "pending_manager", "pending_hr"])
        
        # Generate scores based on job title
        if emp.is_manager:
            base_score = random.uniform(4.0, 5.0)
        elif emp.job_title and emp.job_title.salary_coefficient >= 4.0:
            base_score = random.uniform(3.5, 5.0)
        else:
            base_score = random.uniform(3.0, 4.5)
        
        appraisal = Appraisal.objects.create(
            period=period,
            employee=emp,
            manager=manager,
            status=status,
            self_assessment_date=timezone.now() - timedelta(days=random.randint(5, 15)) if status != "pending_self" else None,
            manager_review_date=timezone.now() - timedelta(days=random.randint(1, 5)) if status in ["pending_hr", "completed"] else None,
            final_review_date=timezone.now() if status == "completed" else None,
            self_overall_score=Decimal(str(round(base_score, 2))) if status != "pending_self" else None,
            self_comments="Tôi đã hoàn thành tốt các công việc được giao trong kỳ đánh giá này.",
            self_achievements="- Hoàn thành 100% KPI\n- Hỗ trợ đồng nghiệp tốt\n- Tham gia các dự án quan trọng",
            self_challenges="- Áp lực công việc cao\n- Cần cải thiện kỹ năng giao tiếp",
            self_development_plan="- Học thêm kỹ năng mới\n- Tham gia các khóa đào tạo",
            manager_overall_score=Decimal(str(round(base_score * 0.95, 2))) if status in ["pending_hr", "completed"] else None,
            manager_comments="Nhân viên hoàn thành tốt công việc, có tinh thần trách nhiệm cao.",
            manager_strengths="- Chuyên môn tốt\n- Làm việc nhóm hiệu quả",
            manager_weaknesses="- Cần chủ động hơn\n- Cải thiện time management",
            manager_recommendations="Đề xuất tăng lương theo hiệu suất" if base_score >= 4.0 else "",
            final_score=Decimal(str(round(base_score * 0.97, 2))) if status == "completed" else None,
            hr_comments="Đã xem xét và phê duyệt đánh giá." if status == "completed" else "",
            promotion_recommended=base_score >= 4.5 and status == "completed"
        )
        
        # Determine overall rating
        if status == "completed":
            for (low, high), rating in rating_map.items():
                if low <= base_score < high:
                    appraisal.overall_rating = rating
                    break
            appraisal.save()
        
        appraisal_count += 1
        
        # Create scores for each criterion
        for criteria in period.criteria.all():
            # Add some variation to scores
            variation = random.uniform(-0.5, 0.5)
            self_score = min(5, max(1, round(base_score + variation)))
            manager_score = min(5, max(1, round(base_score + variation * 0.8)))
            
            AppraisalScore.objects.create(
                appraisal=appraisal,
                criteria=criteria,
                self_score=self_score if status != "pending_self" else None,
                self_comment=f"Tự đánh giá {criteria.name}",
                manager_score=manager_score if status in ["pending_hr", "completed"] else None,
                manager_comment=f"Đánh giá của quản lý về {criteria.name}",
                final_score=manager_score if status == "completed" else None
            )
            score_count += 1

print_success(f"Đã tạo {appraisal_count} đánh giá nhân viên")
print_success(f"Đã tạo {score_count} điểm đánh giá chi tiết")

print_header("HOÀN TẤT SEED 09")
print(f"- Kỳ đánh giá: {AppraisalPeriod.objects.count()}")
print(f"  + Đang diễn ra: {AppraisalPeriod.objects.filter(status='active').count()}")
print(f"  + Đã kết thúc: {AppraisalPeriod.objects.filter(status='closed').count()}")
print(f"- Tiêu chí đánh giá: {AppraisalCriteria.objects.count()}")
print(f"- Đánh giá nhân viên: {Appraisal.objects.count()}")
print(f"  + Chờ tự đánh giá: {Appraisal.objects.filter(status='pending_self').count()}")
print(f"  + Chờ quản lý: {Appraisal.objects.filter(status='pending_manager').count()}")
print(f"  + Chờ HR: {Appraisal.objects.filter(status='pending_hr').count()}")
print(f"  + Hoàn thành: {Appraisal.objects.filter(status='completed').count()}")
print(f"- Điểm đánh giá chi tiết: {AppraisalScore.objects.count()}")
