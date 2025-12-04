"""
Seed 11: User Accounts and Permissions
Run: python seed/seed_11_users_permissions.py (từ thư mục gốc)
Requires: seed_02_employees.py
"""
import os
import sys

# Thêm thư mục gốc vào path - sử dụng getcwd thay vì __file__
BASE_DIR = os.getcwd()
# Nếu đang chạy từ run_all.py, BASE_DIR đã đúng
if 'seed' in BASE_DIR:
    BASE_DIR = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Setup Django - check if already setup
if 'django' not in sys.modules or not hasattr(sys.modules.get('django'), 'apps'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
    import django
    django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Employee

print("="*60)
print(" SEED 11: User Accounts & Permissions")
print("="*60)

# ============================================================================
# 1. TẠO GROUPS (NHÓM QUYỀN)
# ============================================================================
print("\n1. Tạo nhóm quyền...")

# Xóa groups cũ
Group.objects.all().delete()

groups_data = {
    'Admin': 'Quản trị hệ thống - Full quyền',
    'HR': 'Phòng Nhân sự - Quản lý nhân viên, tuyển dụng, đánh giá',
    'Manager': 'Quản lý - Xem và đánh giá nhân viên trong phòng',
    'Accountant': 'Kế toán - Quản lý lương, chi phí',
    'Employee': 'Nhân viên - Quyền cơ bản',
}

groups = {}
for name, desc in groups_data.items():
    group, _ = Group.objects.get_or_create(name=name)
    groups[name] = group
    print(f"   ✓ Tạo group: {name}")

print(f"✓ Đã tạo {len(groups)} nhóm quyền")

# ============================================================================
# 2. PHÂN QUYỀN CHO GROUPS
# ============================================================================
print("\n2. Phân quyền cho các nhóm...")

# Get all permissions
all_permissions = Permission.objects.all()

# Admin - Full quyền
groups['Admin'].permissions.set(all_permissions)
print("   ✓ Admin: Full quyền")

# HR permissions
hr_permissions = Permission.objects.filter(
    codename__in=[
        # Employee
        'add_employee', 'change_employee', 'delete_employee', 'view_employee',
        'view_all_employees', 'view_employee_salary', 'manage_employee_contracts',
        # Leave
        'add_leavetype', 'change_leavetype', 'view_leavetype',
        'add_leavebalance', 'change_leavebalance', 'view_leavebalance',
        'add_leaverequest', 'change_leaverequest', 'view_leaverequest', 'approve_leave_request',
        # Attendance
        'add_attendance', 'change_attendance', 'view_attendance',
        # Reward/Discipline
        'add_reward', 'change_reward', 'view_reward',
        'add_discipline', 'change_discipline', 'view_discipline',
        # Evaluation/Appraisal
        'add_evaluation', 'change_evaluation', 'view_evaluation',
        'add_appraisal', 'change_appraisal', 'view_appraisal',
        'add_appraisalperiod', 'change_appraisalperiod', 'view_appraisalperiod',
        # Recruitment
        'add_jobposting', 'change_jobposting', 'view_jobposting',
        'add_application', 'change_application', 'view_application',
        # Contract
        'add_contract', 'change_contract', 'view_contract',
        # Documents
        'add_document', 'change_document', 'view_document',
        'add_announcement', 'change_announcement', 'view_announcement',
        # Department/JobTitle
        'add_department', 'change_department', 'view_department',
        'add_jobtitle', 'change_jobtitle', 'view_jobtitle',
    ]
)
groups['HR'].permissions.set(hr_permissions)
print(f"   ✓ HR: {hr_permissions.count()} quyền")

# Manager permissions
manager_permissions = Permission.objects.filter(
    codename__in=[
        'view_employee', 'view_team_employees',
        'view_leaverequest', 'approve_leave_request', 'view_team_leave_requests',
        'view_attendance',
        'view_evaluation', 'add_evaluation', 'change_evaluation',
        'view_appraisal', 'change_appraisal',
        'view_expense', 'approve_expense',
        'view_reward', 'view_discipline',
        'view_announcement', 'view_document',
    ]
)
groups['Manager'].permissions.set(manager_permissions)
print(f"   ✓ Manager: {manager_permissions.count()} quyền")

# Accountant permissions
accountant_permissions = Permission.objects.filter(
    codename__in=[
        'view_employee', 'view_employee_salary',
        'add_payroll', 'change_payroll', 'view_payroll',
        'view_attendance',
        'view_expense', 'approve_expense', 'pay_expense',
        'view_reward', 'view_discipline',
        'view_contract',
        'view_announcement', 'view_document',
    ]
)
groups['Accountant'].permissions.set(accountant_permissions)
print(f"   ✓ Accountant: {accountant_permissions.count()} quyền")

# Employee permissions (basic)
employee_permissions = Permission.objects.filter(
    codename__in=[
        'view_leaverequest', 'add_leaverequest',
        'view_leavebalance',
        'view_expense', 'add_expense',
        'view_attendance',
        'view_appraisal',
        'view_announcement', 'view_document',
    ]
)
groups['Employee'].permissions.set(employee_permissions)
print(f"   ✓ Employee: {employee_permissions.count()} quyền")

# ============================================================================
# 3. TẠO SUPERUSER
# ============================================================================
print("\n3. Tạo Superuser...")

if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@company.com',
        password='admin123',
        first_name='System',
        last_name='Admin'
    )
    print("   ✓ Tạo superuser: admin / admin123")
else:
    print("   ✓ Superuser 'admin' đã tồn tại")

# ============================================================================
# 4. TẠO USER CHO NHÂN VIÊN
# ============================================================================
print("\n4. Tạo tài khoản cho nhân viên...")

# Delete existing non-admin users
User.objects.exclude(username='admin').exclude(is_superuser=True).delete()

user_count = 0
for emp in Employee.objects.all():
    # Tạo username từ employee_code (lowercase)
    username = emp.employee_code.lower()
    
    # Tạo user
    user = User.objects.create_user(
        username=username,
        email=emp.email,
        password='123456',  # Default password
        first_name=emp.name.split()[0] if emp.name else '',
        last_name=' '.join(emp.name.split()[1:]) if emp.name and len(emp.name.split()) > 1 else ''
    )
    user.is_active = emp.status in [0, 1, 2]  # Active nếu không phải đã nghỉ việc
    user.save()
    
    # Gán group dựa trên phòng ban và chức vụ
    assigned_groups = ['Employee']  # Mọi người đều có quyền Employee
    
    # HR department
    if emp.department and 'nhân sự' in emp.department.name.lower():
        assigned_groups.append('HR')
    
    # Kế toán department
    if emp.department and ('kế toán' in emp.department.name.lower() or 'tài chính' in emp.department.name.lower()):
        assigned_groups.append('Accountant')
    
    # Manager
    if emp.is_manager:
        assigned_groups.append('Manager')
    
    # Ban Giám đốc = Admin
    if emp.department and 'giám đốc' in emp.department.name.lower():
        assigned_groups.append('Admin')
    
    # Assign groups
    for group_name in assigned_groups:
        if group_name in groups:
            user.groups.add(groups[group_name])
    
    user_count += 1
    print(f"   ✓ {username} ({emp.name}) - Groups: {', '.join(assigned_groups)}")

print(f"\n✓ Đã tạo {user_count} tài khoản người dùng")

# ============================================================================
# 5. THỐNG KÊ
# ============================================================================
print("\n" + "="*60)
print(" HOÀN TẤT SEED 11")
print("="*60)

print(f"\n📊 Thống kê:")
print(f"   - Groups: {Group.objects.count()}")
print(f"   - Users: {User.objects.count()}")
print(f"   - Superusers: {User.objects.filter(is_superuser=True).count()}")
print(f"   - Active users: {User.objects.filter(is_active=True).count()}")

print(f"\n👥 Users theo Group:")
for group in Group.objects.all():
    count = group.user_set.count()
    print(f"   - {group.name}: {count} users")

print(f"\n🔐 Thông tin đăng nhập:")
print(f"   - Admin: admin / admin123")
print(f"   - Nhân viên: [mã nhân viên viết thường] / 123456")
print(f"   - Ví dụ: hr001 / 123456, it001 / 123456, gd001 / 123456")
