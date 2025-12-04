"""
Seed 07: Recruitment - Job Postings and Applications
Run: python manage.py shell < seed/seed_07_recruitment.py
Requires: seed_01_departments.py, seed_02_employees.py
"""
from seed.base import *
from app.models import Department, Employee, JobTitle, JobPosting, Application

print_header("SEED 07: Recruitment")

# Check dependencies
if Department.objects.count() == 0:
    print("❌ Lỗi: Chưa có phòng ban. Chạy seed_01_departments.py trước!")
    exit(1)

if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
Application.objects.all().delete()
JobPosting.objects.all().delete()

# Get data
departments = {d.name: d for d in Department.objects.all()}
hr_manager = Employee.objects.filter(employee_code="HR001").first()

# ============================================================================
# 1. TẠO TIN TUYỂN DỤNG
# ============================================================================
print("\n1. Tạo tin tuyển dụng...")

job_postings_data = [
    {
        "title": "Senior Software Engineer",
        "code": "JOB-2025-001",
        "dept": "Phòng Công nghệ thông tin",
        "desc": """Phát triển và duy trì các ứng dụng web sử dụng Python/Django và React.
        
Công việc chính:
- Thiết kế và phát triển tính năng mới
- Code review và mentor cho junior developers
- Tối ưu hiệu suất hệ thống
- Viết unit tests và documentation""",
        "req": """- Tối thiểu 5 năm kinh nghiệm lập trình
- Thành thạo Python, Django Framework
- Kinh nghiệm với React/Vue.js
- Có kinh nghiệm với AWS/Azure
- Tiếng Anh đọc hiểu tốt tài liệu kỹ thuật
- Có kinh nghiệm làm việc Agile/Scrum""",
        "salary_min": 30000000,
        "salary_max": 50000000,
        "positions": 2,
        "exp": "senior",
        "status": "open"
    },
    {
        "title": "Business Analyst",
        "code": "JOB-2025-002",
        "dept": "Phòng Kinh doanh",
        "desc": """Phân tích yêu cầu kinh doanh và đề xuất giải pháp công nghệ.
        
Công việc chính:
- Thu thập và phân tích yêu cầu từ stakeholders
- Viết tài liệu BRD, SRS
- Làm cầu nối giữa business và IT
- Hỗ trợ UAT và deployment""",
        "req": """- 3+ năm kinh nghiệm BA trong lĩnh vực IT
- Kỹ năng phân tích và tư duy logic tốt
- Có kinh nghiệm viết tài liệu nghiệp vụ
- Giao tiếp tốt với nhiều đối tượng
- Ưu tiên có kinh nghiệm ERP/CRM""",
        "salary_min": 20000000,
        "salary_max": 35000000,
        "positions": 1,
        "exp": "mid",
        "status": "open"
    },
    {
        "title": "HR Executive",
        "code": "JOB-2025-003",
        "dept": "Phòng Nhân sự",
        "desc": """Thực hiện các công việc nhân sự tổng hợp.
        
Công việc chính:
- Quản lý hồ sơ nhân viên
- Thực hiện quy trình onboarding/offboarding
- Hỗ trợ công tác tuyển dụng
- Quản lý chấm công, nghỉ phép""",
        "req": """- 2+ năm kinh nghiệm HR
- Am hiểu Luật Lao động và các quy định BHXH
- Kỹ năng giao tiếp và xử lý tình huống tốt
- Thành thạo MS Office
- Tốt nghiệp Đại học chuyên ngành Quản trị nhân lực""",
        "salary_min": 12000000,
        "salary_max": 18000000,
        "positions": 1,
        "exp": "junior",
        "status": "open"
    },
    {
        "title": "Junior Developer",
        "code": "JOB-2025-004",
        "dept": "Phòng Công nghệ thông tin",
        "desc": """Hỗ trợ phát triển và bảo trì ứng dụng web.
        
Công việc chính:
- Phát triển tính năng theo yêu cầu
- Fix bugs và maintenance
- Viết unit tests
- Học hỏi từ senior developers""",
        "req": """- Fresh graduate hoặc dưới 1 năm kinh nghiệm
- Biết Python hoặc JavaScript cơ bản
- Hiểu biết về HTML/CSS
- Ham học hỏi, chịu khó
- Có khả năng làm việc nhóm""",
        "salary_min": 10000000,
        "salary_max": 15000000,
        "positions": 3,
        "exp": "entry",
        "status": "open"
    },
    {
        "title": "Marketing Specialist",
        "code": "JOB-2025-005",
        "dept": "Phòng Marketing",
        "desc": """Thực hiện các chiến dịch marketing digital.
        
Công việc chính:
- Lên kế hoạch và thực hiện chiến dịch digital marketing
- Quản lý các kênh social media
- Chạy quảng cáo Facebook, Google Ads
- Phân tích hiệu quả chiến dịch""",
        "req": """- 2+ năm kinh nghiệm Digital Marketing
- Có kinh nghiệm chạy Facebook Ads, Google Ads
- Sáng tạo, có khả năng viết content
- Biết sử dụng các công cụ analytics
- Ưu tiên có portfolio""",
        "salary_min": 15000000,
        "salary_max": 25000000,
        "positions": 1,
        "exp": "junior",
        "status": "closed"
    },
    {
        "title": "Accountant",
        "code": "JOB-2025-006",
        "dept": "Phòng Kế toán - Tài chính",
        "desc": """Thực hiện công việc kế toán tổng hợp.
        
Công việc chính:
- Xử lý các nghiệp vụ kế toán hàng ngày
- Lập báo cáo tài chính
- Kê khai thuế
- Đối chiếu công nợ""",
        "req": """- 2+ năm kinh nghiệm kế toán
- Tốt nghiệp Đại học chuyên ngành Kế toán/Tài chính
- Thành thạo Excel, phần mềm kế toán
- Am hiểu luật thuế, chế độ kế toán
- Có chứng chỉ kế toán trưởng là lợi thế""",
        "salary_min": 12000000,
        "salary_max": 20000000,
        "positions": 1,
        "exp": "junior",
        "status": "open"
    },
]

job_postings = {}
for jp in job_postings_data:
    posting = JobPosting.objects.create(
        title=jp["title"],
        code=jp["code"],
        department=departments[jp["dept"]],
        description=jp["desc"],
        requirements=jp["req"],
        responsibilities="- Thực hiện công việc được giao đúng tiến độ\n- Báo cáo tiến độ định kỳ\n- Phối hợp với các bộ phận liên quan\n- Tuân thủ quy trình và quy định công ty",
        benefits="- Lương tháng 13, thưởng theo hiệu quả\n- Bảo hiểm đầy đủ theo quy định\n- Du lịch, team building hàng quý\n- Đào tạo nâng cao chuyên môn\n- Môi trường làm việc chuyên nghiệp",
        employment_type="fulltime",
        experience_level=jp["exp"],
        number_of_positions=jp["positions"],
        location="Tòa nhà ABC, 123 Nguyễn Trãi, Thanh Xuân, Hà Nội",
        salary_min=jp["salary_min"],
        salary_max=jp["salary_max"],
        deadline=date(2025, 12, 31) if jp["status"] == "open" else date(2025, 10, 31),
        status=jp["status"],
        contact_person="Phòng Nhân sự",
        contact_email="hr@company.com",
        contact_phone="024-3456-7890",
        created_by=hr_manager
    )
    job_postings[jp["code"]] = posting

print_success(f"Đã tạo {len(job_postings)} tin tuyển dụng")

# ============================================================================
# 2. TẠO ĐƠN ỨNG TUYỂN
# ============================================================================
print("\n2. Tạo đơn ứng tuyển...")

applicants_data = [
    # Ứng viên cho Senior Software Engineer
    {"job": "JOB-2025-001", "name": "Trần Minh Quân", "email": "quan.tm@gmail.com", "phone": "0912345678", "exp": 6, "status": "interview", "rating": 4, "gender": 0},
    {"job": "JOB-2025-001", "name": "Lê Hoàng Nam", "email": "nam.lh@gmail.com", "phone": "0923456789", "exp": 5, "status": "screening", "rating": 3, "gender": 0},
    {"job": "JOB-2025-001", "name": "Nguyễn Đức Anh", "email": "anh.nd@gmail.com", "phone": "0934567890", "exp": 7, "status": "offer", "rating": 5, "gender": 0},
    {"job": "JOB-2025-001", "name": "Phạm Văn Hải", "email": "hai.pv@gmail.com", "phone": "0945678901", "exp": 4, "status": "rejected", "rating": 2, "gender": 0},
    {"job": "JOB-2025-001", "name": "Hoàng Thị Mai", "email": "mai.ht@gmail.com", "phone": "0956789012", "exp": 5, "status": "new", "rating": None, "gender": 1},
    
    # Ứng viên cho Business Analyst
    {"job": "JOB-2025-002", "name": "Vũ Thị Hương", "email": "huong.vt@gmail.com", "phone": "0967890123", "exp": 4, "status": "interview", "rating": 4, "gender": 1},
    {"job": "JOB-2025-002", "name": "Hoàng Minh Tuấn", "email": "tuan.hm@gmail.com", "phone": "0978901234", "exp": 3, "status": "new", "rating": None, "gender": 0},
    {"job": "JOB-2025-002", "name": "Nguyễn Thị Lan", "email": "lan.nt@gmail.com", "phone": "0989012345", "exp": 3, "status": "screening", "rating": 3, "gender": 1},
    
    # Ứng viên cho HR Executive
    {"job": "JOB-2025-003", "name": "Ngô Thị Hà", "email": "ha.nt@gmail.com", "phone": "0990123456", "exp": 2, "status": "phone_interview", "rating": 3, "gender": 1},
    {"job": "JOB-2025-003", "name": "Đặng Văn Bình", "email": "binh.dv@gmail.com", "phone": "0901234561", "exp": 3, "status": "accepted", "rating": 5, "gender": 0},
    {"job": "JOB-2025-003", "name": "Trần Thị Oanh", "email": "oanh.tt@gmail.com", "phone": "0812345671", "exp": 2, "status": "new", "rating": None, "gender": 1},
    
    # Ứng viên cho Junior Developer
    {"job": "JOB-2025-004", "name": "Bùi Quang Huy", "email": "huy.bq@gmail.com", "phone": "0823456782", "exp": 0, "status": "test", "rating": 4, "gender": 0},
    {"job": "JOB-2025-004", "name": "Mai Thị Ngọc", "email": "ngoc.mt@gmail.com", "phone": "0834567893", "exp": 1, "status": "new", "rating": None, "gender": 1},
    {"job": "JOB-2025-004", "name": "Trịnh Văn Long", "email": "long.tv@gmail.com", "phone": "0845678904", "exp": 0, "status": "screening", "rating": 3, "gender": 0},
    {"job": "JOB-2025-004", "name": "Lý Thị Hạnh", "email": "hanh.lt@gmail.com", "phone": "0856789015", "exp": 1, "status": "interview", "rating": 4, "gender": 1},
    {"job": "JOB-2025-004", "name": "Đinh Công Minh", "email": "minh.dc@gmail.com", "phone": "0867890126", "exp": 0, "status": "new", "rating": None, "gender": 0},
    {"job": "JOB-2025-004", "name": "Phan Thị Thảo", "email": "thao.pt@gmail.com", "phone": "0878901237", "exp": 0, "status": "rejected", "rating": 2, "gender": 1},
    
    # Ứng viên cho Marketing (đã đóng)
    {"job": "JOB-2025-005", "name": "Đinh Văn Khoa", "email": "khoa.dv@gmail.com", "phone": "0889012348", "exp": 3, "status": "accepted", "rating": 5, "gender": 0},
    {"job": "JOB-2025-005", "name": "Lê Thị Nhung", "email": "nhung.lt@gmail.com", "phone": "0890123459", "exp": 2, "status": "rejected", "rating": 3, "gender": 1},
    
    # Ứng viên cho Accountant
    {"job": "JOB-2025-006", "name": "Nguyễn Thị Tuyết", "email": "tuyet.nt@gmail.com", "phone": "0911234560", "exp": 3, "status": "interview", "rating": 4, "gender": 1},
    {"job": "JOB-2025-006", "name": "Phạm Văn Đức", "email": "duc.pv@gmail.com", "phone": "0922345671", "exp": 2, "status": "new", "rating": None, "gender": 0},
]

majors_by_job = {
    "JOB-2025-001": ["Công nghệ thông tin", "Khoa học máy tính", "Kỹ thuật phần mềm"],
    "JOB-2025-002": ["Quản trị kinh doanh", "Hệ thống thông tin", "Công nghệ thông tin"],
    "JOB-2025-003": ["Quản trị nhân lực", "Quản trị kinh doanh", "Luật"],
    "JOB-2025-004": ["Công nghệ thông tin", "Khoa học máy tính", "Toán tin"],
    "JOB-2025-005": ["Marketing", "Truyền thông", "Quản trị kinh doanh"],
    "JOB-2025-006": ["Kế toán", "Tài chính ngân hàng", "Kiểm toán"],
}

application_count = 0
for i, app in enumerate(applicants_data, 1):
    if app["job"] not in job_postings:
        continue
    
    Application.objects.create(
        job=job_postings[app["job"]],
        application_code=f"APP-2025-{i:04d}",
        full_name=app["name"],
        email=app["email"],
        phone=app["phone"],
        date_of_birth=date(random.randint(1990, 2000), random.randint(1, 12), random.randint(1, 28)),
        gender=app["gender"],
        address=f"Số {random.randint(1, 100)}, {random.choice(TINH_THANH)}",
        years_of_experience=app["exp"],
        education_level=3,
        school=random.choice(TRUONG_DAI_HOC),
        major=random.choice(majors_by_job[app["job"]]),
        resume="resumes/cv_sample.pdf",
        cover_letter=f"Kính gửi Phòng Nhân sự,\n\nTôi viết thư này để ứng tuyển vào vị trí {job_postings[app['job']].title}. Với {app['exp']} năm kinh nghiệm trong lĩnh vực, tôi tin rằng mình có thể đóng góp tích cực cho công ty.\n\nTrân trọng,\n{app['name']}",
        expected_salary=random.randint(15, 45) * 1000000,
        status=app["status"],
        source=random.choice(["website", "linkedin", "referral", "vietnamworks", "facebook"]),
        rating=app["rating"],
        assigned_to=hr_manager,
        notes="Hồ sơ tốt, cần phỏng vấn thêm" if app["status"] in ["screening", "interview"] else ""
    )
    application_count += 1

print_success(f"Đã tạo {application_count} đơn ứng tuyển")

print_header("HOÀN TẤT SEED 07")
print(f"- Tin tuyển dụng: {JobPosting.objects.count()}")
print(f"  + Đang mở: {JobPosting.objects.filter(status='open').count()}")
print(f"  + Đã đóng: {JobPosting.objects.filter(status='closed').count()}")
print(f"- Đơn ứng tuyển: {Application.objects.count()}")
print(f"  + Mới: {Application.objects.filter(status='new').count()}")
print(f"  + Đang xét: {Application.objects.filter(status='screening').count()}")
print(f"  + Phỏng vấn: {Application.objects.filter(status__in=['phone_interview', 'interview']).count()}")
print(f"  + Làm test: {Application.objects.filter(status='test').count()}")
print(f"  + Offer: {Application.objects.filter(status='offer').count()}")
print(f"  + Đã nhận: {Application.objects.filter(status='accepted').count()}")
print(f"  + Từ chối: {Application.objects.filter(status='rejected').count()}")
