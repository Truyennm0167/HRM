"""
Seed 01: Job Titles and Departments
Run: python manage.py shell < seed/seed_01_departments.py
"""
from seed.base import *
from app.models import Department, JobTitle

print_header("SEED 01: Job Titles & Departments")

# Clear existing data
print("Xóa dữ liệu cũ...")
JobTitle.objects.all().delete()
Department.objects.all().delete()

# ============================================================================
# 1. TẠO CHỨC DANH (Job Titles)
# ============================================================================
print("\n1. Tạo chức danh...")
job_titles_data = [
    {"name": "Giám đốc", "salary_coefficient": 8.0, "description": "Điều hành toàn bộ công ty"},
    {"name": "Phó Giám đốc", "salary_coefficient": 7.0, "description": "Hỗ trợ Giám đốc điều hành"},
    {"name": "Trưởng phòng", "salary_coefficient": 5.5, "description": "Quản lý phòng ban"},
    {"name": "Phó phòng", "salary_coefficient": 4.5, "description": "Hỗ trợ Trưởng phòng"},
    {"name": "Chuyên viên cao cấp", "salary_coefficient": 4.0, "description": "Chuyên viên có kinh nghiệm"},
    {"name": "Chuyên viên", "salary_coefficient": 3.0, "description": "Nhân viên chính thức"},
    {"name": "Nhân viên", "salary_coefficient": 2.5, "description": "Nhân viên văn phòng"},
    {"name": "Thực tập sinh", "salary_coefficient": 1.5, "description": "Đang trong thời gian thực tập"},
]

for jt in job_titles_data:
    JobTitle.objects.create(**jt)
print_success(f"Đã tạo {len(job_titles_data)} chức danh")

# ============================================================================
# 2. TẠO PHÒNG BAN (Departments)
# ============================================================================
print("\n2. Tạo phòng ban...")
departments_data = [
    {"name": "Ban Giám đốc", "description": "Điều hành công ty", "date_establishment": date(2015, 1, 1)},
    {"name": "Phòng Nhân sự", "description": "Quản lý nhân sự, tuyển dụng, đào tạo", "date_establishment": date(2015, 1, 15)},
    {"name": "Phòng Kế toán - Tài chính", "description": "Quản lý tài chính, kế toán", "date_establishment": date(2015, 1, 15)},
    {"name": "Phòng Công nghệ thông tin", "description": "Phát triển và quản trị hệ thống IT", "date_establishment": date(2016, 3, 1)},
    {"name": "Phòng Kinh doanh", "description": "Bán hàng và phát triển thị trường", "date_establishment": date(2015, 2, 1)},
    {"name": "Phòng Marketing", "description": "Marketing và truyền thông", "date_establishment": date(2017, 6, 1)},
    {"name": "Phòng Hành chính", "description": "Quản lý hành chính, văn phòng", "date_establishment": date(2015, 1, 15)},
    {"name": "Phòng Chăm sóc khách hàng", "description": "Hỗ trợ và chăm sóc khách hàng", "date_establishment": date(2018, 1, 1)},
]

for dept in departments_data:
    Department.objects.create(**dept)
print_success(f"Đã tạo {len(departments_data)} phòng ban")

print_header("HOÀN TẤT SEED 01")
print(f"- Chức danh: {JobTitle.objects.count()}")
print(f"- Phòng ban: {Department.objects.count()}")
