# 🚀 KẾ HOẠCH PHÁT TRIỂN HRM SYSTEM

## Cập nhật: 30/11/2025

---

# 📋 DANH SÁCH 10 YÊU CẦU CẦN PHÁT TRIỂN

| #   | Yêu cầu                                          | Độ ưu tiên  | Độ khó | Thời gian | Trạng thái |
| --- | ------------------------------------------------ | ----------- | ------ | --------- | ---------- |
| 1   | Sửa hệ thống phân quyền                          | 🔴 CRITICAL | Medium | 0.5 ngày  | ✅ DONE    |
| 2   | Hoàn thiện Performance Appraisal                 | 🔴 CRITICAL | High   | 1-2 ngày  | ✅ DONE    |
| 3   | Thêm tạo tài khoản nhân viên vào sidebar         | 🟢 EASY     | Low    | 0.5 giờ   | ✅ DONE    |
| 4   | Module Khen thưởng - Kỷ luật                     | 🟠 HIGH     | Medium | 1-2 ngày  | ✅ DONE    |
| 5   | Sửa Chấm công Portal                             | 🟠 HIGH     | Medium | 0.5 ngày  | ✅ DONE    |
| 6   | Loại bỏ Portal khỏi /management, thêm nút chuyển | 🟢 EASY     | Low    | 0.5 giờ   | ✅ DONE    |
| 7   | Sắp xếp lại Sidebar theo chuẩn HRM               | 🟡 MEDIUM   | Low    | 0.5 ngày  | ✅ DONE    |
| 8   | Thiết kế lại Dashboard với Charts                | 🟠 HIGH     | Medium | 1-2 ngày  | ✅ DONE    |
| 9   | Tích hợp Email Notifications                     | 🟡 MEDIUM   | Medium | 1 ngày    | ✅ DONE    |
| 10  | Thêm phần Settings                               | 🟡 MEDIUM   | Medium | 1 ngày    | ✅ DONE    |

---

# 📝 CHI TIẾT TỪNG YÊU CẦU

---

## 1️⃣ SỬA HỆ THỐNG PHÂN QUYỀN ✅ HOÀN THÀNH

**Mức độ ưu tiên:** 🔴 CRITICAL  
**Thời gian ước tính:** 0.5 ngày
**Trạng thái:** ✅ ĐÃ HOÀN THÀNH (30/11/2025)

### 📌 Yêu cầu

- HR: Có quyền truy cập đầy đủ vào `/management`
- Manager: Chỉ được truy cập `/portal`, KHÔNG được vào `/management`
- Nhân viên thường: Chỉ được truy cập `/portal`

### 🔧 Giải pháp kỹ thuật

#### A. Cập nhật Middleware/Decorator

**File cần sửa:** `app/decorators.py`

```python
# Thêm decorator mới
def hr_only(view_func):
    """
    Chỉ cho phép HR truy cập.
    HR được xác định bởi: thuộc phòng 'HR' hoặc có quyền 'app.hr_staff'
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        employee = get_user_employee(request.user)

        if not employee:
            messages.error(request, 'Không tìm thấy thông tin nhân viên.')
            return redirect('login')

        # Kiểm tra có phải HR không
        is_hr = (
            employee.department and
            employee.department.name.lower() in ['hr', 'nhân sự', 'human resources']
        ) or request.user.has_perm('app.hr_staff')

        if not is_hr:
            messages.error(request, 'Bạn không có quyền truy cập khu vực này.')
            return redirect('portal_dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper
```

#### B. Cập nhật tất cả views trong `/management`

**File cần sửa:** `app/management_views.py`

Thay đổi từ `@require_hr_or_manager` thành `@require_hr` cho các trang management.

#### C. Tạo Middleware chặn Manager

**File mới:** `app/middleware.py`

```python
class ManagementAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Kiểm tra nếu URL bắt đầu bằng /management/ hoặc các URL quản lý khác
        management_patterns = [
            '/department', '/job_title', '/add_employee', '/employee_list',
            '/payroll', '/attendance/add', '/attendance/manage',
            '/leave/manage', '/leave/types', '/expense/manage',
            '/expense/categories', '/contracts', '/recruitment',
            '/salary-rules', '/reward', '/discipline', '/appraisal/hr',
            '/appraisal/periods', '/ai/'
        ]

        if any(request.path.startswith(p) for p in management_patterns):
            employee = get_user_employee(request.user)
            if employee and not is_hr_staff(employee):
                messages.error(request, 'Bạn không có quyền truy cập.')
                return redirect('portal_dashboard')

        return self.get_response(request)
```

#### D. Cập nhật settings.py

```python
MIDDLEWARE = [
    ...
    'app.middleware.ManagementAccessMiddleware',
]
```

### ✅ Checklist

- [x] Tạo `app/middleware.py` - Đã có sẵn trong `app/middleware/portal_redirect.py`
- [x] Cập nhật `app/decorators.py` - thêm decorator `hr_only`
- [x] Cập nhật `app/permissions.py` - thêm `is_hr_user`, `is_hr_department`, `user_can_access_management`
- [x] Middleware đã có trong settings.py
- [x] Test với các role: HR, Manager, Employee

### 📋 Thay đổi đã thực hiện:

**1. `app/permissions.py`:**

- Thêm `is_hr_department(employee)` - kiểm tra nhân viên thuộc phòng HR
- Thêm `is_hr_user(user)` - kiểm tra user có phải HR (superuser/group HR/phòng HR)
- Cập nhật `user_can_access_management(user)` - CHỈ cho phép HR và superuser

**2. `app/decorators.py`:**

- Thêm `hr_only` decorator
- Cập nhật `is_hr_staff()` để kiểm tra cả phòng ban HR
- Thêm helper `_is_hr_department()` và `_get_employee_from_user()`

**3. `app/middleware/portal_redirect.py`:**

- Cập nhật `ManagementAccessMiddleware` với danh sách URLs đầy đủ
- Cập nhật `PortalRedirectMiddleware` để HR mặc định vào Management

---

## 2️⃣ HOÀN THIỆN PERFORMANCE APPRAISAL ✅ HOÀN THÀNH

**Mức độ ưu tiên:** 🔴 CRITICAL  
**Thời gian ước tính:** 1-2 ngày
**Trạng thái:** ✅ ĐÃ HOÀN THÀNH (30/11/2025)

### 📌 Yêu cầu chi tiết

#### A. Manager đánh giá team trong Portal

- Tạo view `portal_manager_appraisals` để hiển thị danh sách nhân viên cần đánh giá
- Tạo view `portal_manager_review` để manager đánh giá nhân viên

#### B. Thêm trường "Góp ý cho công ty"

- Thêm field `company_feedback` vào model `Appraisal`
- Cập nhật form self-assessment

#### C. Sửa tên hiển thị tiêu chí

- Vietnamese mapping cho category labels trong template

### 🔧 Giải pháp kỹ thuật

#### A. Cập nhật Model

**File:** `app/models.py`

```python
class Appraisal(models.Model):
    # ... existing fields ...

    # Thêm field mới
    company_feedback = models.TextField(
        blank=True,
        help_text="Góp ý của nhân viên cho công ty"
    )
```

#### B. Tạo Views Portal cho Manager

**File:** `app/portal_views.py`

```python
@login_required
@require_manager_permission
def portal_manager_appraisals(request):
    """
    Danh sách nhân viên cần manager đánh giá (trong Portal)
    """
    employee = get_user_employee(request.user)

    # Lấy tất cả appraisals của team mà manager quản lý
    appraisals = Appraisal.objects.filter(
        manager=employee,
        status='pending_manager'
    ).select_related('employee', 'period')

    return render(request, 'portal/appraisals/manager_list.html', {
        'appraisals': appraisals
    })


@login_required
@require_manager_permission
def portal_manager_review(request, appraisal_id):
    """
    Form cho manager đánh giá nhân viên
    """
    employee = get_user_employee(request.user)
    appraisal = get_object_or_404(
        Appraisal,
        pk=appraisal_id,
        manager=employee,
        status='pending_manager'
    )

    if request.method == 'POST':
        # Xử lý form submit
        # Cập nhật manager scores
        # Chuyển status sang 'pending_hr'
        pass

    return render(request, 'portal/appraisals/manager_review.html', {
        'appraisal': appraisal,
        'scores': appraisal.scores.all()
    })
```

#### C. Cập nhật URL

**File:** `hrm/urls.py`

```python
# Portal Appraisal URLs
path('portal/appraisals/team/', portal_views.portal_manager_appraisals, name='portal_manager_appraisals'),
path('portal/appraisals/review/<int:appraisal_id>/', portal_views.portal_manager_review, name='portal_manager_review'),
```

#### D. Tạo Templates

**Template 1:** `app/templates/portal/appraisals/manager_list.html`

- Hiển thị danh sách nhân viên cần đánh giá
- Link đến trang review

**Template 2:** `app/templates/portal/appraisals/manager_review.html`

- Form đánh giá với các tiêu chí
- Input điểm và nhận xét

#### E. Vietnamese Labels cho Categories

**File:** Template hoặc templatetags

```python
# Trong template
{% load appraisal_tags %}

CATEGORY_LABELS = {
    'performance': 'Hiệu suất công việc',
    'behavior': 'Hành vi & Thái độ',
    'skill': 'Kỹ năng chuyên môn',
    'leadership': 'Năng lực lãnh đạo',
    'development': 'Phát triển bản thân',
}
```

### ✅ Checklist

- [x] Thêm field `company_feedback` vào model Appraisal
- [x] Chạy migration
- [x] Tạo view `portal_manager_appraisals`
- [x] Tạo view `portal_manager_review`
- [x] Cập nhật URLs
- [x] Tạo template `manager_list.html`
- [x] Tạo template `manager_review.html`
- [x] Cập nhật sidebar Portal để thêm menu "Đánh giá team"
- [x] Sửa Vietnamese labels cho categories
- [x] Cập nhật self-assessment form để thêm "Góp ý công ty"

### 📋 Thay đổi đã thực hiện:

**1. `app/models.py`:**

- Thêm field `company_feedback` vào model Appraisal

**2. `app/portal_views.py`:**

- Thêm CATEGORY_LABELS dictionary cho Vietnamese labels
- Thêm view `manager_appraisals` - danh sách nhân viên cần đánh giá
- Thêm view `manager_review` - form đánh giá nhân viên
- Thêm view `manager_appraisal_detail` - xem chi tiết đánh giá
- Cập nhật `self_assessment` để lưu company_feedback và sử dụng Vietnamese labels

**3. `app/urls_portal.py`:**

- Thêm 3 URLs mới cho Manager Appraisal

**4. `app/templates/portal/appraisal/`:**

- Tạo `manager_list.html` - danh sách team cần đánh giá
- Tạo `manager_review.html` - form đánh giá
- Tạo `manager_detail.html` - xem chi tiết
- Cập nhật `self_assessment.html` để thêm "Góp ý công ty"

**5. `app/templates/portal/portal_base.html`:**

- Thêm menu "Đánh giá team" cho Manager

---

## 3️⃣ THÊM TẠO TÀI KHOẢN NHÂN VIÊN VÀO SIDEBAR ✅ HOÀN THÀNH

**Mức độ ưu tiên:** 🟢 EASY  
**Thời gian ước tính:** 0.5 giờ

### 📌 Yêu cầu

Thêm menu item "Tạo tài khoản nhân viên" vào sidebar management

### 🔧 Giải pháp

**File:** `app/templates/hod_template/sidebar_template.html`

Thêm vào trong menu "Nhân viên":

```html
<li class="nav-item">
  <a
    href="{% url 'register_employee_account' %}"
    class="nav-link {% if '/accounts/register' in request.path %}active{% endif %}"
  >
    <i class="nav-icon fas fa-user-cog"></i>
    <p>Tạo tài khoản</p>
  </a>
</li>
```

### ✅ Checklist

- [ ] Xác nhận URL `register_employee_account` tồn tại
- [ ] Thêm menu item vào sidebar
- [ ] Test hiển thị

---

## 4️⃣ MODULE KHEN THƯỞNG - KỶ LUẬT

**Mức độ ưu tiên:** 🟠 HIGH  
**Thời gian ước tính:** 1-2 ngày

### 📌 Yêu cầu

Hoàn thiện module Khen thưởng - Kỷ luật đã có sẵn models (Reward, Discipline)

### 🔧 Giải pháp kỹ thuật

#### A. Models (Đã có sẵn)

```python
class Reward(models.Model):
    number = models.IntegerField(unique=True)
    description = models.TextField()
    date = models.DateTimeField()
    amount = models.FloatField()
    cash_payment = models.BooleanField()
    employee = models.ForeignKey(Employee, ...)

class Discipline(models.Model):
    number = models.IntegerField(unique=True)
    description = models.TextField()
    date = models.DateTimeField()
    amount = models.FloatField()
    employee = models.ForeignKey(Employee, ...)
```

#### B. Cần tạo Views

**File:** `app/management_views.py` hoặc tạo `app/reward_views.py`

```python
# CRUD cho Reward
def reward_list(request):
    """Danh sách khen thưởng"""

def reward_create(request):
    """Tạo khen thưởng mới"""

def reward_edit(request, pk):
    """Sửa khen thưởng"""

def reward_delete(request, pk):
    """Xóa khen thưởng"""

# CRUD cho Discipline
def discipline_list(request):
    """Danh sách kỷ luật"""

def discipline_create(request):
    """Tạo kỷ luật mới"""

def discipline_edit(request, pk):
    """Sửa kỷ luật"""

def discipline_delete(request, pk):
    """Xóa kỷ luật"""
```

#### C. URLs

```python
# Reward URLs
path('rewards/', views.reward_list, name='reward_list'),
path('rewards/create/', views.reward_create, name='reward_create'),
path('rewards/<int:pk>/edit/', views.reward_edit, name='reward_edit'),
path('rewards/<int:pk>/delete/', views.reward_delete, name='reward_delete'),

# Discipline URLs
path('disciplines/', views.discipline_list, name='discipline_list'),
path('disciplines/create/', views.discipline_create, name='discipline_create'),
path('disciplines/<int:pk>/edit/', views.discipline_edit, name='discipline_edit'),
path('disciplines/<int:pk>/delete/', views.discipline_delete, name='discipline_delete'),
```

#### D. Templates

- `hod_template/rewards/list.html`
- `hod_template/rewards/form.html`
- `hod_template/disciplines/list.html`
- `hod_template/disciplines/form.html`

#### E. Cập nhật Sidebar

```html
<li class="nav-item">
  <a href="{% url 'reward_list' %}" class="nav-link">
    <i class="nav-icon fas fa-trophy"></i>
    <p>Khen thưởng</p>
  </a>
</li>
<li class="nav-item">
  <a href="{% url 'discipline_list' %}" class="nav-link">
    <i class="nav-icon fas fa-gavel"></i>
    <p>Kỷ luật</p>
  </a>
</li>
```

### ✅ Checklist

- [ ] Tạo RewardForm, DisciplineForm
- [ ] Tạo views CRUD cho Reward
- [ ] Tạo views CRUD cho Discipline
- [ ] Cập nhật URLs
- [ ] Tạo templates
- [ ] Cập nhật sidebar với URLs đúng
- [ ] Tích hợp với Payroll (trừ/cộng lương)

---

## 5️⃣ SỬA CHẤM CÔNG PORTAL

**Mức độ ưu tiên:** 🟠 HIGH  
**Thời gian ước tính:** 0.5 ngày

### 📌 Yêu cầu

Sửa tính năng Chấm công trong Portal để hoạt động đúng

### 🔧 Cần kiểm tra

- [ ] View `my_attendance` có trả về data đúng không
- [ ] Template có hiển thị đúng không
- [ ] Check-in/Check-out có hoạt động không
- [ ] Xem lịch sử chấm công

### ✅ Checklist

- [ ] Debug view `my_attendance` trong `portal_views.py`
- [ ] Kiểm tra template `portal/attendance/my_attendance.html`
- [ ] Test chức năng check-in/out
- [ ] Sửa lỗi nếu có

---

## 6️⃣ LOẠI BỎ PORTAL KHỎI /MANAGEMENT, THÊM NÚT CHUYỂN

**Mức độ ưu tiên:** 🟢 EASY  
**Thời gian ước tính:** 0.5 giờ

### 📌 Yêu cầu

- Xóa menu "Portal Nhân Viên" khỏi sidebar management
- Thêm nút "Chuyển sang Portal" ở header hoặc góc màn hình

### 🔧 Giải pháp

#### A. Xóa menu Portal từ Sidebar

**File:** `app/templates/hod_template/sidebar_template.html`

Xóa block sau:

```html
<!-- Self-Service Portal -->
<li
  class="nav-item has-treeview {% if '/portal' in request.path %}menu-open{% endif %}"
>
  ...
</li>
```

#### B. Thêm nút chuyển Portal vào Header/Navbar

**File:** `app/templates/hod_template/navbar_template.html` hoặc `base_template.html`

```html
<!-- Thêm vào góc phải navbar -->
<li class="nav-item">
  <a
    href="{% url 'portal_dashboard' %}"
    class="nav-link"
    title="Chuyển sang Portal Nhân viên"
  >
    <i class="fas fa-exchange-alt"></i>
    <span class="d-none d-md-inline-block ml-1">Portal NV</span>
  </a>
</li>
```

### ✅ Checklist

- [ ] Xóa menu Portal từ sidebar_template.html
- [ ] Thêm nút chuyển vào navbar
- [ ] Kiểm tra responsive
- [ ] Test link hoạt động

---

## 7️⃣ SẮP XẾP LẠI SIDEBAR THEO CHUẨN HRM

**Mức độ ưu tiên:** 🟡 MEDIUM  
**Thời gian ước tính:** 0.5 ngày

### 📌 Yêu cầu

Sắp xếp sidebar theo thứ tự chuẩn ngành HRM

### 🔧 Cấu trúc đề xuất

```
📊 TỔNG QUAN (Dashboard)
│
├── 👥 QUẢN LÝ NHÂN SỰ
│   ├── Phòng ban
│   ├── Chức vụ
│   ├── Danh sách nhân viên
│   ├── Thêm nhân viên
│   ├── Tạo tài khoản
│   └── Biểu đồ tổ chức
│
├── 📄 HỢP ĐỒNG
│   ├── Danh sách hợp đồng
│   └── Tạo hợp đồng
│
├── ⏰ CHẤM CÔNG & NGHỈ PHÉP
│   ├── Thêm bảng chấm công
│   ├── Quản lý chấm công
│   ├── Duyệt đơn nghỉ phép
│   └── Loại nghỉ phép
│
├── 💰 LƯƠNG & THU NHẬP
│   ├── Tính lương
│   ├── Bảng lương
│   ├── Thành phần lương
│   ├── Mẫu quy tắc
│   └── Lịch sử tính lương
│
├── 💵 CHI PHÍ
│   ├── Duyệt chi phí
│   └── Danh mục chi phí
│
├── ⭐ HIỆU SUẤT & ĐÁNH GIÁ
│   ├── Quản lý đánh giá (HR)
│   ├── Kỳ đánh giá
│   ├── Khen thưởng
│   └── Kỷ luật
│
├── 👔 TUYỂN DỤNG
│   ├── Tin tuyển dụng
│   ├── Tạo tin mới
│   ├── Kanban ứng tuyển
│   └── Trang công khai
│
├── 🤖 AI RECRUITMENT
│   ├── Tạo Job Description
│   ├── Quản lý JD
│   ├── Upload CV
│   └── Quản lý CV
│
└── ⚙️ CÀI ĐẶT (Mới)
    ├── Thông tin công ty
    ├── Email settings
    └── Cấu hình hệ thống
```

### ✅ Checklist

- [ ] Backup sidebar_template.html hiện tại
- [ ] Viết lại cấu trúc sidebar theo thứ tự mới
- [ ] Gộp các menu liên quan (Nghỉ phép + Chấm công)
- [ ] Test tất cả links
- [ ] Kiểm tra active state của menu items

---

## 8️⃣ THIẾT KẾ LẠI DASHBOARD VỚI CHARTS ✅ HOÀN THÀNH

**Mức độ ưu tiên:** 🟠 HIGH  
**Thời gian ước tính:** 1-2 ngày
**Trạng thái:** ✅ ĐÃ HOÀN THÀNH (01/12/2025)

### 📌 Yêu cầu

Thay đổi Dashboard từ hiển thị danh sách nhân viên sang các biểu đồ thống kê

### 🔧 Các biểu đồ đề xuất

#### A. Row 1: Summary Cards (Giữ nguyên, cải tiến)

- Tổng nhân viên
- Phòng ban
- Tổng lương tháng này
- Nhân viên đang làm việc (realtime)

#### B. Row 2: Charts Row

**Chart 1:** Biểu đồ tròn - Nhân viên theo Phòng ban

```javascript
// Pie chart - Employees by Department
```

**Chart 2:** Biểu đồ cột - Lương trung bình theo Phòng ban

```javascript
// Bar chart - Average salary by Department
```

#### C. Row 3: Trends

**Chart 3:** Line chart - Trend tuyển dụng 6 tháng gần đây
**Chart 4:** Doughnut chart - Trạng thái nhân viên (Onboarding, Thử việc, Chính thức, Nghỉ việc)

#### D. Row 4: Recent Activities

- Nhân viên mới (5 gần nhất)
- Đánh giá chờ xử lý
- Đơn nghỉ chờ duyệt
- Hợp đồng sắp hết hạn

### 🔧 Kỹ thuật

**Library:** Chart.js (đã có trong project)

**File cần sửa:**

- `app/views.py` (hoặc `management_views.py`) - Thêm data cho charts
- `app/templates/hod_template/home_content.html` - Thêm charts

**View Example:**

```python
def admin_home(request):
    # Existing data
    employees = Employee.objects.all()
    departments = Department.objects.all()

    # New chart data
    # Nhân viên theo phòng ban
    dept_employee_count = []
    for dept in departments:
        dept_employee_count.append({
            'name': dept.name,
            'count': employees.filter(department=dept).count()
        })

    # Lương trung bình theo phòng ban
    dept_avg_salary = departments.annotate(
        avg_salary=Avg('employee__salary')
    ).values('name', 'avg_salary')

    # Nhân viên theo trạng thái
    status_count = employees.values('status').annotate(
        count=Count('id')
    )

    context = {
        'employees': employees,
        'departments': departments,
        'dept_employee_count': json.dumps(dept_employee_count),
        'dept_avg_salary': json.dumps(list(dept_avg_salary)),
        'status_count': json.dumps(list(status_count)),
    }
    return render(request, 'hod_template/home_content.html', context)
```

### ✅ Checklist

- [ ] Cập nhật view `admin_home` với data cho charts
- [ ] Thiết kế layout mới cho dashboard
- [ ] Tích hợp Chart.js charts
- [ ] Thêm Pie chart - Nhân viên theo phòng ban
- [ ] Thêm Bar chart - Lương theo phòng ban
- [ ] Thêm Line chart - Trend tuyển dụng
- [ ] Thêm Doughnut chart - Trạng thái nhân viên
- [ ] Thêm section Recent Activities
- [ ] Test responsive

---

## 9️⃣ TÍCH HỢP EMAIL NOTIFICATIONS ✅ HOÀN THÀNH

**Mức độ ưu tiên:** 🟡 MEDIUM  
**Thời gian ước tính:** 1 ngày

### 📌 Yêu cầu

Gửi email thông báo cho các sự kiện quan trọng

### 🔧 Các loại email cần gửi

1. **Nghỉ phép được duyệt/từ chối**
2. **Chi phí được duyệt/từ chối**
3. **Đánh giá sắp đến hạn**
4. **Hợp đồng sắp hết hạn**
5. **Welcome email cho nhân viên mới**

### 🔧 Giải pháp kỹ thuật

#### A. Cấu hình Email

**File:** `hrm/settings.py`

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # hoặc SMTP server khác
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'HRM System <noreply@company.com>'
```

#### B. Tạo Email Service

**File mới:** `app/email_service.py`

```python
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_leave_approved_email(leave_request):
    """Gửi email khi đơn nghỉ được duyệt"""
    subject = f'Đơn nghỉ phép đã được duyệt - {leave_request.leave_type.name}'
    html_message = render_to_string('emails/leave_approved.html', {
        'leave_request': leave_request
    })
    send_mail(
        subject,
        '',  # plain text (optional)
        None,  # from email (uses DEFAULT_FROM_EMAIL)
        [leave_request.employee.email],
        html_message=html_message,
        fail_silently=False
    )

def send_expense_approved_email(expense):
    """Gửi email khi chi phí được duyệt"""
    ...

def send_appraisal_reminder_email(employee, period):
    """Gửi nhắc nhở đánh giá"""
    ...
```

#### C. Email Templates

**Folder:** `app/templates/emails/`

- `leave_approved.html`
- `leave_rejected.html`
- `expense_approved.html`
- `expense_rejected.html`
- `appraisal_reminder.html`
- `contract_expiring.html`
- `welcome.html`

#### D. Tích hợp vào Views

```python
# Trong approve_leave_request()
from .email_service import send_leave_approved_email

def approve_leave_request(request, pk):
    ...
    leave_request.status = 'approved'
    leave_request.save()

    # Gửi email
    send_leave_approved_email(leave_request)
    ...
```

#### E. Background Task (Optional - nâng cao)

Sử dụng Celery cho async email:

```python
# app/tasks.py
from celery import shared_task

@shared_task
def send_email_async(subject, message, recipient_list):
    send_mail(subject, message, None, recipient_list)
```

### ✅ Checklist

- [x] Cấu hình SMTP trong settings.py
- [x] Tạo file `email_service.py`
- [x] Tạo email templates
- [x] Tích hợp email vào leave approval
- [x] Tích hợp email vào expense approval
- [x] Tạo management command cho appraisal reminders
- [x] Tạo management command cho contract expiring alerts
- [x] Test gửi email

### 📋 Thay đổi đã thực hiện:

**1. `app/email_service.py` (MỚI):**

- Class `EmailService` với các methods:
  - `send_leave_approved()`, `send_leave_rejected()`
  - `send_expense_approved()`, `send_expense_rejected()`
  - `send_appraisal_reminder()`, `send_appraisal_completed()`
  - `send_manager_review_reminder()`
  - `send_contract_expiring_alert()`, `send_contract_renewed()`
  - `send_welcome_email()`
  - `send_reward_notification()`, `send_discipline_notification()`

**2. Email Templates (12 files trong `app/templates/emails/`):**

- `leave_approved.html`, `leave_rejected.html`
- `expense_approved.html`, `expense_rejected.html`
- `welcome.html`
- `appraisal_reminder.html`, `appraisal_completed.html`
- `manager_review_reminder.html`
- `contract_expiring_employee.html`, `contract_renewed.html`
- `reward_notification.html`, `discipline_notification.html`

**3. `app/management_views.py` (CẬP NHẬT):**

- Thêm email notification trong:
  - `approve_leave_request()` - gửi email khi duyệt nghỉ phép
  - `reject_leave_request()` - gửi email khi từ chối nghỉ phép
  - `approve_expense()` - gửi email khi duyệt chi phí
  - `reject_expense()` - gửi email khi từ chối chi phí
  - `add_employee_save()` - gửi welcome email
  - `reward_create()` - gửi thông báo khen thưởng
  - `discipline_create()` - gửi thông báo kỷ luật

**4. Management Commands (MỚI):**

- `send_contract_alerts` - Gửi cảnh báo hợp đồng sắp hết hạn
  - Sử dụng: `python manage.py send_contract_alerts --days 30`
- `send_appraisal_reminders` - Gửi nhắc nhở đánh giá
  - Sử dụng: `python manage.py send_appraisal_reminders`
  - Option `--to-managers` để gửi cho manager

---

## 🔟 THÊM PHẦN SETTINGS ✅ HOÀN THÀNH

**Mức độ ưu tiên:** 🟡 MEDIUM  
**Thời gian ước tính:** 1 ngày
**Trạng thái:** ✅ ĐÃ HOÀN THÀNH (02/12/2025)

### 📌 Yêu cầu

Thêm trang Settings trong /management để cấu hình hệ thống

### 🔧 Các settings cần có

#### A. Thông tin công ty

- Tên công ty
- Logo
- Địa chỉ
- Số điện thoại
- Email

#### B. Cấu hình email

- SMTP Server
- Port
- Username/Password
- Test email

#### C. Cấu hình hệ thống

- Ngày làm việc tiêu chuẩn/tháng
- Giờ làm việc/ngày
- Múi giờ
- Ngôn ngữ

#### D. Cấu hình lương

- Thuế suất
- BHXH, BHYT, BHTN
- Lương tối thiểu vùng

### 🔧 Giải pháp kỹ thuật

#### A. Model Settings

**File:** `app/models.py`

```python
class SystemSettings(models.Model):
    """Singleton model for system settings"""
    # Company Info
    company_name = models.CharField(max_length=200, default='Company Name')
    company_logo = models.ImageField(upload_to='settings/', blank=True)
    company_address = models.TextField(blank=True)
    company_phone = models.CharField(max_length=20, blank=True)
    company_email = models.EmailField(blank=True)

    # Work Settings
    standard_working_days = models.IntegerField(default=22)
    standard_working_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8)
    timezone = models.CharField(max_length=50, default='Asia/Ho_Chi_Minh')

    # Salary Settings
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    social_insurance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=8)
    health_insurance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.5)
    unemployment_insurance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    # Email Settings (stored encrypted)
    email_host = models.CharField(max_length=200, blank=True)
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.CharField(max_length=200, blank=True)
    email_host_password = models.CharField(max_length=200, blank=True)  # Should be encrypted

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
```

#### B. Views

```python
@login_required
@require_hr
def settings_page(request):
    settings = SystemSettings.get_settings()

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật cài đặt thành công!')
    else:
        form = SystemSettingsForm(instance=settings)

    return render(request, 'hod_template/settings/settings.html', {
        'form': form,
        'settings': settings
    })
```

#### C. Templates

- `hod_template/settings/settings.html` - Main settings page with tabs

### ✅ Checklist

- [x] Tạo model SystemSettings
- [x] Chạy migration
- [x] Tạo SystemSettingsForm (6 forms riêng biệt)
- [x] Tạo view settings_page
- [x] Tạo template settings.html
- [x] Thêm menu Settings vào sidebar
- [x] Thêm URL pattern
- [ ] Tích hợp settings vào payroll calculation (TODO: Future enhancement)
- [x] Test các cấu hình

### 📋 Thay đổi đã thực hiện:

**1. `app/models.py` (THÊM):**

- Model `SystemSettings` (Singleton pattern)
- 6 nhóm cài đặt:
  - Thông tin công ty (tên, logo, địa chỉ, MST...)
  - Thời gian làm việc (giờ/ngày, ngày/tháng, giờ nghỉ trưa)
  - Lương & Bảo hiểm (thuế TNCN, BHXH, BHYT, BHTN cả NLĐ và NSDLĐ)
  - Email/SMTP settings
  - Thông báo (các loại email notification)
  - Cài đặt chung (định dạng ngày, tiền tệ, phân trang)

**2. `app/forms.py` (THÊM 6 forms):**

- `CompanySettingsForm` - Thông tin công ty
- `WorkSettingsForm` - Thời gian làm việc
- `SalarySettingsForm` - Lương & Bảo hiểm
- `EmailSettingsForm` - SMTP settings
- `NotificationSettingsForm` - Cài đặt thông báo
- `GeneralSettingsForm` - Cài đặt chung

**3. `app/management_views.py` (THÊM):**

- `settings_page()` - Trang settings với 6 tabs
- `test_email_settings()` - API test gửi email

**4. `app/templates/hod_template/settings/settings.html` (MỚI):**

- Giao diện settings với 6 tabs
- Form riêng cho từng nhóm cài đặt
- Test email function

**5. `app/urls_management.py` (THÊM):**

- `/management/settings/` - Trang settings
- `/management/settings/test-email/` - API test email

**6. Sidebar (CẬP NHẬT):**

- Thêm section "CÀI ĐẶT" với link đến trang settings

---

# 📅 ROADMAP TRIỂN KHAI

## Phase 1: Foundation (Ngày 1-2)

| Task                                           | Thời gian | Priority |
| ---------------------------------------------- | --------- | -------- |
| 1. Sửa hệ thống phân quyền                     | 0.5 ngày  | 🔴       |
| 3. Thêm tạo tài khoản vào sidebar              | 0.5 giờ   | 🟢       |
| 6. Xóa Portal khỏi management, thêm nút chuyển | 0.5 giờ   | 🟢       |
| 7. Sắp xếp lại Sidebar                         | 0.5 ngày  | 🟡       |

## Phase 2: Core Features (Ngày 3-5)

| Task                                | Thời gian | Priority |
| ----------------------------------- | --------- | -------- |
| 2. Hoàn thiện Performance Appraisal | 1.5 ngày  | 🔴       |
| 5. Sửa Chấm công Portal             | 0.5 ngày  | 🟠       |
| 4. Module Khen thưởng - Kỷ luật     | 1.5 ngày  | 🟠       |

## Phase 3: Enhancement (Ngày 6-8)

| Task                    | Thời gian | Priority |
| ----------------------- | --------- | -------- |
| 8. Dashboard với Charts | 1.5 ngày  | 🟠       |
| 9. Email Notifications  | 1 ngày    | 🟡       |
| 10. Settings section    | 1 ngày    | 🟡       |

---

# 📊 TỔNG KẾT

**Tổng thời gian ước tính:** 8-10 ngày

**Độ phức tạp:**

- Easy (🟢): 3 tasks
- Medium (🟡): 3 tasks
- High (🟠): 3 tasks
- Critical (🔴): 2 tasks

**Yêu cầu kỹ thuật:**

- Django ORM
- Chart.js
- SMTP Email
- JavaScript/AJAX
- HTML/CSS (AdminLTE)

---

# ✅ PREVIOUS COMPLETED TASKS

| Task                          | Status  |
| ----------------------------- | ------- |
| Module Nghỉ phép              | ✅ DONE |
| Self-service Portal           | ✅ DONE |
| Module Chi phí                | ✅ DONE |
| Recruitment Workflow          | ✅ DONE |
| Contract Management           | ✅ DONE |
| Org Chart visualization       | ✅ DONE |
| RBAC cải tiến                 | ✅ DONE |
| Performance Appraisal (Basic) | ✅ DONE |

Performance Appraisal
Salary Rules engine
Mobile app (optional)
Phase 4: Polish (Tuần 7-8)
Unit tests (80% coverage)
Performance optimization
Security audit
Documentation
