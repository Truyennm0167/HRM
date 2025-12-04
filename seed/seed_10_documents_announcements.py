"""
Seed 10: Documents and Announcements
Run: python manage.py shell < seed/seed_10_documents_announcements.py
Requires: seed_02_employees.py
"""
from seed.base import *
from app.models import Employee, Department, DocumentCategory, Document, Announcement

print_header("SEED 10: Documents & Announcements")

# Check dependencies
if Employee.objects.count() == 0:
    print("❌ Lỗi: Chưa có nhân viên. Chạy seed_02_employees.py trước!")
    exit(1)

# Clear data
print("Xóa dữ liệu cũ...")
Announcement.objects.all().delete()
Document.objects.all().delete()
DocumentCategory.objects.all().delete()

hr_manager = Employee.objects.filter(employee_code="HR001").first()

# ============================================================================
# 1. TẠO DANH MỤC TÀI LIỆU
# ============================================================================
print("\n1. Tạo danh mục tài liệu...")

categories_data = [
    {"name": "Chính sách công ty", "description": "Các chính sách, quy định của công ty", "icon": "fa-gavel", "color": "primary", "order": 1},
    {"name": "Biểu mẫu", "description": "Các mẫu đơn, biểu mẫu sử dụng nội bộ", "icon": "fa-file-alt", "color": "success", "order": 2},
    {"name": "Hướng dẫn", "description": "Tài liệu hướng dẫn sử dụng, quy trình", "icon": "fa-book", "color": "info", "order": 3},
    {"name": "Đào tạo", "description": "Tài liệu đào tạo, học tập", "icon": "fa-graduation-cap", "color": "warning", "order": 4},
    {"name": "Pháp lý", "description": "Văn bản pháp lý, hợp đồng mẫu", "icon": "fa-balance-scale", "color": "danger", "order": 5},
]

categories = {}
for cat in categories_data:
    categories[cat["name"]] = DocumentCategory.objects.create(**cat)

print_success(f"Đã tạo {len(categories)} danh mục tài liệu")

# ============================================================================
# 2. TẠO TÀI LIỆU
# ============================================================================
print("\n2. Tạo tài liệu...")

documents_data = [
    {"title": "Nội quy lao động 2025", "cat": "Chính sách công ty", "desc": "Nội quy lao động áp dụng từ 01/01/2025", "type": "pdf", "size": 1024000},
    {"title": "Quy chế lương thưởng", "cat": "Chính sách công ty", "desc": "Quy chế lương thưởng và phúc lợi", "type": "pdf", "size": 2048000},
    {"title": "Chính sách nghỉ phép", "cat": "Chính sách công ty", "desc": "Quy định về các loại nghỉ phép", "type": "pdf", "size": 512000},
    {"title": "Quy trình đánh giá nhân viên", "cat": "Chính sách công ty", "desc": "Quy trình đánh giá hiệu suất định kỳ", "type": "pdf", "size": 768000},
    {"title": "Đơn xin nghỉ phép", "cat": "Biểu mẫu", "desc": "Mẫu đơn xin nghỉ phép các loại", "type": "docx", "size": 45000},
    {"title": "Đơn đề nghị thanh toán", "cat": "Biểu mẫu", "desc": "Mẫu đơn đề nghị hoàn tiền chi phí", "type": "docx", "size": 38000},
    {"title": "Biên bản bàn giao công việc", "cat": "Biểu mẫu", "desc": "Mẫu biên bản bàn giao khi thôi việc", "type": "docx", "size": 52000},
    {"title": "Mẫu báo cáo công việc tuần", "cat": "Biểu mẫu", "desc": "Template báo cáo công việc hàng tuần", "type": "xlsx", "size": 35000},
    {"title": "Hướng dẫn sử dụng HRM", "cat": "Hướng dẫn", "desc": "Hướng dẫn sử dụng hệ thống quản lý nhân sự", "type": "pdf", "size": 5120000},
    {"title": "Quy trình onboarding", "cat": "Hướng dẫn", "desc": "Quy trình tiếp nhận nhân viên mới", "type": "pdf", "size": 1536000},
    {"title": "Quy trình đào tạo nội bộ", "cat": "Đào tạo", "desc": "Quy trình tổ chức đào tạo nội bộ", "type": "pdf", "size": 896000},
    {"title": "Tài liệu văn hóa doanh nghiệp", "cat": "Đào tạo", "desc": "Giới thiệu văn hóa và giá trị công ty", "type": "pptx", "size": 15360000},
    {"title": "Luật Lao động 2019", "cat": "Pháp lý", "desc": "Bộ Luật Lao động số 45/2019/QH14", "type": "pdf", "size": 3072000},
    {"title": "Mẫu hợp đồng lao động", "cat": "Pháp lý", "desc": "Mẫu HĐLĐ các loại theo quy định", "type": "docx", "size": 128000},
]

doc_count = 0
for doc in documents_data:
    Document.objects.create(
        title=doc["title"],
        description=doc["desc"],
        category=categories[doc["cat"]],
        file=f"documents/2025/01/{doc['title'].replace(' ', '_').lower()}.{doc['type']}",
        file_size=doc["size"],
        file_type=doc["type"],
        visibility="all",
        uploaded_by=hr_manager,
        version="1.0"
    )
    doc_count += 1

print_success(f"Đã tạo {doc_count} tài liệu")

# ============================================================================
# 3. TẠO THÔNG BÁO
# ============================================================================
print("\n3. Tạo thông báo...")

announcements_data = [
    {
        "title": "Lịch nghỉ Tết Nguyên Đán 2026",
        "content": """Kính gửi toàn thể CBNV,

Công ty thông báo lịch nghỉ Tết Nguyên Đán năm 2026 như sau:

📅 Thời gian nghỉ: Từ ngày 26/01/2026 (27 tháng Chạp) đến hết ngày 02/02/2026 (mùng 5 Tết)
📅 Ngày đi làm lại: 03/02/2026 (mùng 6 Tết)

Lưu ý:
- Các phòng ban bố trí hoàn thành công việc trước kỳ nghỉ
- Bàn giao công việc cho người phụ trách trong thời gian nghỉ
- Đảm bảo an toàn tài sản công ty

Chúc toàn thể CBNV và gia đình năm mới An Khang Thịnh Vượng!

Trân trọng,
Ban Giám đốc""",
        "category": "holiday",
        "priority": "high",
        "is_pinned": True,
        "publish_at": timezone.now() - timedelta(days=5)
    },
    {
        "title": "Thông báo Team Building Q4/2025",
        "content": """Kính gửi toàn thể CBNV,

Công ty tổ chức chương trình Team Building Q4/2025 với thông tin như sau:

🎯 Chủ đề: "Đoàn kết - Sáng tạo - Vươn xa"
📅 Thời gian: 20-21/12/2025 (Thứ 7 - Chủ nhật)
📍 Địa điểm: Resort ABC, Sơn Tây, Hà Nội

Chương trình:
- Team building games
- Gala dinner & vinh danh
- Các hoạt động ngoài trời

Đề nghị các phòng ban đăng ký danh sách tham gia trước ngày 10/12/2025.

Trân trọng,
Phòng Nhân sự""",
        "category": "event",
        "priority": "normal",
        "is_pinned": True,
        "publish_at": timezone.now() - timedelta(days=10)
    },
    {
        "title": "Cập nhật chính sách bảo hiểm 2025",
        "content": """Kính gửi toàn thể CBNV,

Phòng Nhân sự thông báo cập nhật chính sách bảo hiểm năm 2025:

1. Bảo hiểm sức khỏe:
   - Nâng hạn mức khám ngoại trú lên 15 triệu/năm
   - Bổ sung quyền lợi nha khoa 5 triệu/năm
   - Mở rộng danh sách bệnh viện liên kết

2. Bảo hiểm tai nạn:
   - Tăng quyền lợi tử vong/thương tật lên 500 triệu

3. Quyền lợi người thân:
   - CBNV có thể đăng ký bảo hiểm cho người thân với giá ưu đãi

Chi tiết xem trong file đính kèm. Mọi thắc mắc liên hệ Phòng Nhân sự.

Trân trọng,
Phòng Nhân sự""",
        "category": "policy",
        "priority": "normal",
        "is_pinned": False,
        "publish_at": timezone.now() - timedelta(days=30)
    },
    {
        "title": "Khai giảng khóa đào tạo Leadership",
        "content": """Kính gửi các Trưởng/Phó phòng,

Công ty tổ chức khóa đào tạo "Leadership Excellence" dành cho cấp quản lý:

📚 Nội dung:
- Kỹ năng lãnh đạo hiệu quả
- Quản lý đội nhóm và động lực
- Ra quyết định và giải quyết vấn đề
- Giao tiếp và phản hồi

👨‍🏫 Giảng viên: Chuyên gia từ Học viện Quản lý ABC
📅 Thời gian: 4 buổi (Thứ 7 hàng tuần, bắt đầu 14/12/2025)
📍 Địa điểm: Phòng họp tầng 10

Đăng ký tại: training@company.com

Trân trọng,
Phòng Nhân sự""",
        "category": "training",
        "priority": "normal",
        "is_pinned": False,
        "publish_at": timezone.now() - timedelta(days=7)
    },
    {
        "title": "Vinh danh nhân viên xuất sắc Q3/2025",
        "content": """Kính gửi toàn thể CBNV,

Ban Giám đốc trân trọng công bố danh sách nhân viên xuất sắc Q3/2025:

🏆 Nhân viên xuất sắc:
1. Nguyễn Văn A - Phòng IT - Hoàn thành xuất sắc dự án ERP
2. Trần Thị B - Phòng Kinh doanh - Vượt 150% chỉ tiêu
3. Lê Văn C - Phòng CSKH - Đạt 98% hài lòng KH

🎖️ Phòng ban xuất sắc: Phòng Công nghệ thông tin

Chúc mừng các cá nhân và tập thể được vinh danh!

Trân trọng,
Ban Giám đốc""",
        "category": "reward",
        "priority": "high",
        "is_pinned": False,
        "publish_at": timezone.now() - timedelta(days=15)
    },
    {
        "title": "Thông báo bảo trì hệ thống",
        "content": """Kính gửi toàn thể CBNV,

Phòng IT thông báo lịch bảo trì hệ thống:

🔧 Thời gian: 22:00 ngày 15/12/2025 đến 06:00 ngày 16/12/2025
⚠️ Ảnh hưởng: 
- Hệ thống HRM không truy cập được
- Email nội bộ tạm ngưng

Đề nghị CBNV lưu ý để chủ động trong công việc.

Trân trọng,
Phòng IT""",
        "category": "general",
        "priority": "normal",
        "is_pinned": False,
        "publish_at": timezone.now() - timedelta(days=2)
    },
]

announcement_count = 0
for ann in announcements_data:
    Announcement.objects.create(
        title=ann["title"],
        content=ann["content"],
        category=ann["category"],
        priority=ann["priority"],
        target_all=True,
        is_pinned=ann["is_pinned"],
        publish_at=ann["publish_at"],
        created_by=hr_manager
    )
    announcement_count += 1

print_success(f"Đã tạo {announcement_count} thông báo")

print_header("HOÀN TẤT SEED 10")
print(f"- Danh mục tài liệu: {DocumentCategory.objects.count()}")
print(f"- Tài liệu: {Document.objects.count()}")
for cat in DocumentCategory.objects.all():
    count = Document.objects.filter(category=cat).count()
    print(f"  + {cat.name}: {count}")
print(f"- Thông báo: {Announcement.objects.count()}")
print(f"  + Ghim: {Announcement.objects.filter(is_pinned=True).count()}")
print(f"  + Ưu tiên cao: {Announcement.objects.filter(priority='high').count()}")
