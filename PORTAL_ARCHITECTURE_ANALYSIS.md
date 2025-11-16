# Phân Tích Kiến Trúc Hệ Thống HRM - Portal Separation

## 📊 TÌNH TRẠNG HIỆN TẠI

### 1. Cấu Trúc URL (hrm/urls.py)

**Đặc điểm:**

- Tất cả URLs đều nằm chung trong một file
- Không có phân tách rõ ràng giữa admin và employee portal
- Đã có một số URLs "portal" nhưng chỉ là 4 trang: dashboard, profile, payrolls, attendance

**URLs Hiện Tại:**

#### A. Authentication (app/urls.py)

```
/login/ → auth_views.LoginView
/logout/ → auth_views.LogoutView
```

#### B. Employee Portal (Đã có - 4 trang)

```
/portal/dashboard/ → employee_dashboard
/portal/profile/ → employee_profile
/portal/profile/edit/ → edit_employee_profile
/portal/payrolls/ → my_payrolls
/portal/attendance/ → my_attendance
```

#### C. Admin Management (Tất cả còn lại - 100+ URLs)

```
# Core HR Management
/ → admin_home
/add_employee → add_employee
/employee_list → employee_list
/employee/<id>/ → employee_detail_view
/department/ → department_page
/job_title → job_title

# Attendance Management
/attendance/add/ → add_attendance
/attendance/manage/ → manage_attendance
/attendance/edit/<id>/ → edit_attendance

# Payroll Management
/payroll/calculate/ → calculate_payroll
/payroll/manage/ → manage_payroll
/payroll/edit/<id>/ → edit_payroll

# Leave Management
/leave/types/ → manage_leave_types
/leave/request/ → request_leave
/leave/history/ → leave_history
/leave/manage/ → manage_leave_requests
/leave/approve/<id>/ → approve_leave_request

# Expense Management
/expense/categories/ → manage_expense_categories
/expense/create/ → create_expense
/expense/history/ → expense_history
/expense/manage/ → manage_expenses
/expense/approve/<id>/ → approve_expense

# Contract Management
/contracts/ → manage_contracts
/contracts/create/ → create_contract
/contracts/<id>/ → contract_detail

# Recruitment (Public + Admin)
/careers/ → careers_list (PUBLIC)
/careers/<id>/ → careers_detail (PUBLIC)
/careers/<id>/apply/ → careers_apply (PUBLIC)
/recruitment/jobs/ → list_jobs_admin (ADMIN)
/recruitment/applications/ → applications_kanban (ADMIN)

# Advanced Features
/org-chart/ → org_chart
/salary-rules/ → salary management
/appraisal/ → performance appraisal
/ai/ → AI recruitment
```

### 2. Views Structure (app/HodViews.py)

**Đặc điểm:**

- Một file duy nhất chứa TẤT CẢ views (4037 lines!)
- Sử dụng decorators: `@login_required`, `@hr_required`, `@manager_or_hr_required`
- Đã có custom decorators trong `app/decorators.py`

**Phân Loại Views:**

#### A. Employee Self-Service (5 views - đã có)

```python
@login_required
def employee_dashboard(request)
def employee_profile(request)
def edit_employee_profile(request)
def my_payrolls(request)
def my_attendance(request)
```

#### B. HR Management (cần @hr_required)

```python
@login_required
@hr_required
def add_employee(request)
def manage_leave_types(request)
def manage_expense_categories(request)
# ... nhiều views khác
```

#### C. Mixed (Employee + Manager)

```python
@login_required
def request_leave(request)  # Employee có thể tạo
def create_expense(request)  # Employee có thể tạo

@login_required
def manage_leave_requests(request)  # Manager duyệt
def manage_expenses(request)  # Manager duyệt
```

#### D. Public (No login required)

```python
def careers_list(request)  # Trang tuyển dụng công khai
def careers_detail(request, job_id)
def careers_apply(request, job_id)
```

### 3. Templates Structure

**Đặc điểm:**

- Base template: `hod_template/base_template.html` (tên cũ, có chữ "HOD" = Head of Department)
- Sidebar: `hod_template/sidebar_template.html` - menu admin đầy đủ
- Hiện có 5 templates portal riêng:
  - `employee_dashboard.html`
  - `employee_profile.html`
  - `edit_employee_profile.html`
  - `my_payrolls.html`
  - `my_attendance.html`

**Template Hierarchy:**

```
app/templates/
├── login.html
├── home.html
├── hod_template/
│   ├── base_template.html  ← Base cho ADMIN
│   ├── sidebar_template.html  ← Sidebar đầy đủ cho ADMIN
│   ├── home_content.html
│   ├── employee_*.html  ← 5 trang portal hiện tại
│   ├── add_*.html
│   ├── manage_*.html
│   └── ... (70+ admin templates)
├── public/
│   ├── careers_*.html  ← Trang tuyển dụng công khai
└── emails/
```

### 4. Permission System

**Decorators hiện có (app/decorators.py):**

```python
@hr_required  # Chỉ HR staff
@manager_or_hr_required  # Manager hoặc HR
@check_employee_access  # Kiểm tra quyền truy cập employee
@check_salary_access  # Kiểm tra quyền xem lương
@check_appraisal_access  # Kiểm tra quyền đánh giá
@group_required  # Kiểm tra nhóm quyền
```

**Permission Fields trong Employee Model:**

```python
is_manager = models.BooleanField(default=False)
# User model:
is_staff = models.BooleanField(default=False)  # Manager/HR
is_superuser = models.BooleanField(default=False)  # Director
```

### 5. Authentication Flow

**Login Redirect:**

- File: `app/urls.py`
- Login view: `auth_views.LoginView` → template: `login.html`
- Logout: `auth_views.LogoutView` → next_page: `/login/`
- **CHƯA CÓ logic redirect sau login** → mặc định đến `/` (admin_home)

---

## 🎯 YÊU CẦU MỚI

### Mục Tiêu

1. **Tách rời 2 Portal:**

   - **Employee Portal** (`/portal/`) - Self-service cho nhân viên
   - **Admin Portal** (`/management/`) - Quản lý cho HR/Manager

2. **Login Redirect:**

   - Tất cả user sau login → `/portal/` (mặc định)
   - Staff/Manager có nút chuyển sang `/management/`
   - Superuser có thể chọn portal hoặc admin

3. **Permission-based Feature Hiding:**
   - Ẩn các tính năng user không có quyền
   - Dynamic menu dựa trên permissions
   - View-level và template-level permission checks

---

## 📋 PHÂN TÍCH CHI TIẾT

### I. EMPLOYEE PORTAL (`/portal/`)

**Người dùng:** TẤT CẢ nhân viên (bao gồm cả Manager/HR)

**Tính năng cần có:**

#### 1. Dashboard (`/portal/dashboard/`)

✅ **Đã có** - `employee_dashboard`

- Thông tin cá nhân
- Thông báo
- Quick actions
- Lịch làm việc

#### 2. Leave Management (`/portal/leaves/`)

⚠️ **Cần tạo mới** (hiện có `/leave/request/` và `/leave/history/` trong admin)

- Xem số dư phép
- Tạo đơn nghỉ phép
- Lịch sử đơn
- Hủy đơn (nếu pending)

#### 3. Payroll View (`/portal/payroll/`)

✅ **Đã có** - `my_payrolls` ở `/portal/payrolls/`

- Cần thêm: Download payslip PDF

#### 4. Attendance (`/portal/attendance/`)

✅ **Đã có** - `my_attendance` ở `/portal/attendance/`

- Cần thêm: Calendar view, statistics

#### 5. Expense Management (`/portal/expenses/`)

⚠️ **Cần tạo mới** (hiện có `/expense/create/` và `/expense/history/` trong admin)

- Tạo đơn hoàn tiền
- Upload hóa đơn
- Theo dõi trạng thái
- Lịch sử

#### 6. Profile (`/portal/profile/`)

✅ **Đã có** - `employee_profile` và `edit_employee_profile`

#### 7. Documents & Announcements (`/portal/documents/`)

❌ **Cần tạo mới hoàn toàn**

- Tài liệu công ty
- Thông báo

#### 8. Manager Features (nếu is_manager = True)

❌ **Cần tạo mới** - `/portal/approvals/`

- Duyệt đơn nghỉ phép của team
- Duyệt chi phí của team
- Xem báo cáo team

---

### II. ADMIN PORTAL (`/management/`)

**Người dùng:** Chỉ Staff (is_staff=True) và Superuser

**Tính năng:**

#### A. HR Management (is_staff hoặc is_superuser)

```
/management/ → admin_home
/management/employees/ → employee_list
/management/employees/add/ → add_employee
/management/employees/<id>/ → employee_detail
/management/departments/ → department_page
/management/job-titles/ → job_title
/management/org-chart/ → org_chart
```

#### B. Attendance Management (Manager hoặc HR)

```
/management/attendance/add/ → add_attendance
/management/attendance/manage/ → manage_attendance
```

#### C. Payroll Management (HR only)

```
/management/payroll/calculate/ → calculate_payroll
/management/payroll/manage/ → manage_payroll
/management/salary-rules/ → salary management
```

#### D. Leave Management (Manager hoặc HR)

```
/management/leave/types/ → manage_leave_types
/management/leave/requests/ → manage_leave_requests
```

#### E. Expense Management (Manager hoặc HR)

```
/management/expense/categories/ → manage_expense_categories
/management/expense/requests/ → manage_expenses
```

#### F. Contract Management (HR only)

```
/management/contracts/ → manage_contracts
```

#### G. Recruitment (HR only)

```
/management/recruitment/jobs/ → list_jobs_admin
/management/recruitment/applications/ → applications_kanban
```

#### H. Appraisal (HR/Manager)

```
/management/appraisal/periods/ → appraisal_periods
/management/appraisal/hr/ → hr_appraisals
```

#### I. AI Recruitment (HR only)

```
/management/ai/resumes/ → resume_list
/management/ai/job-descriptions/ → job_description_list
```

---

### III. PUBLIC (No login)

```
/careers/ → careers_list
/careers/<id>/ → careers_detail
/careers/<id>/apply/ → careers_apply
```

---

## 🏗️ KIẾN TRÚC MỚI ĐỀ XUẤT

### 1. URL Structure

```
# Authentication
/login/
/logout/

# PUBLIC - Recruitment
/careers/
/careers/<id>/
/careers/<id>/apply/

# EMPLOYEE PORTAL (ALL users after login)
/portal/
/portal/dashboard/
/portal/leaves/
/portal/leaves/create/
/portal/leaves/<id>/
/portal/payroll/
/portal/payroll/<id>/download/
/portal/attendance/
/portal/expenses/
/portal/expenses/create/
/portal/expenses/<id>/
/portal/profile/
/portal/profile/edit/
/portal/documents/
/portal/announcements/
/portal/appraisal/my/  # Employee appraisal

# PORTAL - Manager Features (if is_manager=True)
/portal/approvals/
/portal/team/leaves/
/portal/team/expenses/
/portal/team/reports/

# ADMIN PORTAL (is_staff or is_superuser)
/management/
/management/employees/
/management/departments/
/management/attendance/
/management/payroll/
/management/leave/
/management/expense/
/management/contracts/
/management/recruitment/
/management/appraisal/
/management/salary-rules/
/management/ai/
/management/org-chart/
```

### 2. File Structure

```python
# URLs
hrm/urls.py  # Main routing
app/urls.py  # Authentication
app/urls_portal.py  # NEW - Employee portal
app/urls_management.py  # NEW - Admin management
app/urls_public.py  # NEW - Public pages

# Views
app/views.py  # Authentication, Public
app/portal_views.py  # NEW - Employee portal
app/management_views.py  # Rename từ HodViews.py

# Templates
app/templates/
├── base.html  # Common base
├── login.html
├── portal/  # NEW FOLDER
│   ├── portal_base.html
│   ├── dashboard.html
│   ├── leaves/
│   ├── payroll/
│   ├── attendance/
│   ├── expenses/
│   ├── profile/
│   └── documents/
├── management/  # RENAME từ hod_template
│   ├── management_base.html
│   ├── sidebar.html
│   ├── employees/
│   ├── attendance/
│   ├── payroll/
│   └── ...
└── public/
    └── careers/

# Middleware
app/middleware/
├── __init__.py
├── portal_redirect.py  # NEW - Auto redirect after login
```

### 3. Permission Logic

```python
# app/permissions.py (NEW)

def user_can_access_management(user):
    """Kiểm tra quyền truy cập Admin Portal"""
    return user.is_staff or user.is_superuser

def user_can_manage_employees(user):
    """Chỉ HR"""
    return user.is_staff or user.is_superuser

def user_can_approve_leaves(user):
    """Manager hoặc HR"""
    try:
        employee = user.employee
        return employee.is_manager or user.is_staff
    except:
        return False

def user_can_manage_payroll(user):
    """Chỉ HR"""
    return user.is_staff or user.is_superuser

# Template tags
@register.filter
def can_access_management(user):
    return user_can_access_management(user)
```

---

## 📝 CÁC FILE CẦN TẠO/SỬA

### TẠO MỚI:

1. ✅ `app/urls_portal.py` - Portal URLs
2. ✅ `app/urls_management.py` - Management URLs
3. ✅ `app/urls_public.py` - Public URLs
4. ✅ `app/portal_views.py` - Portal views
5. ✅ `app/middleware/portal_redirect.py` - Login redirect
6. ✅ `app/permissions.py` - Permission helpers
7. ✅ `app/templatetags/permission_tags.py` - Template filters
8. ✅ `app/templates/portal/` - Portal templates folder
9. ✅ `app/templates/portal/portal_base.html` - Portal base template

### SỬA ĐỔI:

1. ✅ `hrm/urls.py` - Include new URL files
2. ✅ `hrm/settings.py` - Add middleware, LOGIN_REDIRECT_URL
3. ✅ `app/HodViews.py` → Rename to `app/management_views.py`
4. ✅ `app/templates/hod_template/` → Rename to `app/templates/management/`
5. ✅ `app/templates/hod_template/base_template.html` → `management/management_base.html`

### DI CHUYỂN:

1. ✅ Move 5 portal views từ `HodViews.py` sang `portal_views.py`:

   - employee_dashboard
   - employee_profile
   - edit_employee_profile
   - my_payrolls
   - my_attendance

2. ✅ Move 3 public views từ `views.py` sang `public_views.py`:
   - careers_list
   - careers_detail
   - careers_apply

---

## 🎨 UI/UX Changes

### Employee Portal Design:

- **Navbar**: Logo, User dropdown, Notifications
- **Sidebar**: Minimal menu (Dashboard, Leave, Payroll, Attendance, Expenses, Profile)
- **Color Scheme**: Lighter, friendlier (blue/green)
- **Footer**: Simple company info

### Admin Portal Design:

- **Navbar**: Logo, Portal Switch Button, User dropdown
- **Sidebar**: Full menu với categories
- **Color Scheme**: Professional (dark blue/gray)
- **Footer**: Admin info, version

---

## ⚠️ RỦIRO & GIẢI PHÁP

### 1. Breaking Changes

**Rủi ro:** URLs cũ sẽ bị thay đổi
**Giải pháp:**

- Giữ URLs cũ với redirect
- Hoặc thông báo deprecation

### 2. Performance

**Rủi ro:** Permission checks ở mỗi view
**Giải pháp:**

- Cache permissions
- Use middleware efficiently

### 3. Testing

**Rủi ro:** Khối lượng test lớn
**Giải pháp:**

- Test từng module riêng
- Automated permission tests

---

## 📊 THỐNG KÊ

- **Tổng URLs hiện tại:** ~120 URLs
- **Cần di chuyển sang Portal:** ~10 URLs (đã có 5)
- **Cần di chuyển sang Management:** ~100 URLs
- **Cần tạo mới:** ~15 URLs (Portal features mới)
- **Templates hiện tại:** ~70 files
- **Cần tạo template mới:** ~10 files
- **Views hiện tại:** 1 file (4037 lines)
- **Views sau refactor:** 3 files (portal, management, public)

---

## ✅ TODO SUMMARY

### PHASE 1 - Analysis & Design (3 tasks)

- [x] **Todo 1:** Phân tích cấu trúc hiện tại ← DONE (file này)
- [ ] **Todo 2:** Thiết kế kiến trúc Portal (xem section "KIẾN TRÚC MỚI")
- [ ] **Todo 3:** Tạo middleware phân quyền

### PHASE 2 - Employee Portal (7 tasks)

- [ ] **Todo 4:** Dashboard
- [ ] **Todo 5:** Leave Management
- [ ] **Todo 6:** Payroll View
- [ ] **Todo 7:** Attendance
- [ ] **Todo 8:** Expense Management
- [ ] **Todo 9:** Profile
- [ ] **Todo 10:** Documents & Announcements

### PHASE 3 - Admin Portal (2 tasks)

- [ ] **Todo 11:** Admin Layout
- [ ] **Todo 12:** Permission System

### PHASE 4 - Integration (2 tasks)

- [ ] **Todo 13:** Login Flow
- [ ] **Todo 14:** Manager Portal Features

### PHASE 5 - QA (1 task)

- [ ] **Todo 15:** Testing & Bug Fixes

---

**Kết luận:** Hệ thống hiện tại đã có nền tảng tốt với decorators và một số portal views. Công việc chính là:

1. Tái cấu trúc URLs và views thành 3 modules: Portal, Management, Public
2. Tạo middleware redirect sau login
3. Xây dựng thêm ~10 portal views mới
4. Thiết kế permission system động
5. Testing toàn diện
