# 🚀 NEXT STEPS - ROUND 4 REMAINING WORK

**Ngày tạo:** 20/11/2025  
**Trạng thái hiện tại:** 10/13 bugs fixed (77%)  
**Công việc còn lại:** 3 items

---

## 📊 TỔNG QUAN CÔNG VIỆC CÒN LẠI

### ⚠️ BUG #7: Payroll Filter Functionality

- **Priority:** HIGH
- **Estimated Time:** 2 hours
- **Complexity:** Medium
- **Files to modify:** 1 file (manage_payroll.html)

### ⚠️ BUG #8: Payroll Sorting by Month/Year

- **Priority:** HIGH
- **Estimated Time:** 1.5 hours
- **Complexity:** Medium
- **Files to modify:** 1 file (manage_payroll.html)

### 🆕 FEATURE #13: User Management Page

- **Priority:** MEDIUM
- **Estimated Time:** 6-8 hours
- **Complexity:** High
- **Files to create:** 3-4 new files
- **Files to modify:** 1 file (urls_management.py)

---

## 🔧 CHI TIẾT TỪNG CÔNG VIỆC

---

## ⚠️ BUG #7: Fix Payroll Filter Functionality

### 📋 MÔ TẢ VẤN ĐỀ

**Hiện trạng:**

- Filter controls (month, year, department, status) đã có trong UI
- Backend đã hỗ trợ filter (export_payroll đã có GET parameters)
- **Nhưng:** Click button "Lọc" không filter DataTable

**Expected behavior:**

- User chọn filters → Click "Lọc" → DataTable chỉ hiển thị matching records

---

### 🎯 GIẢI PHÁP

**File cần sửa:** `app/templates/hod_template/manage_payroll.html`

**Approach 1: Server-side filtering (Recommended)**

Modify form to submit và reload page với query parameters:

```html
<!-- Current form (around line 20) -->
<form method="GET" action="{% url 'manage_payroll' %}" class="form-inline">
    <div class="form-group mr-2">
        <label>Tháng:</label>
        <select name="month" class="form-control">
            <option value="">Tất cả</option>
            <option value="1" {% if request.GET.month == '1' %}selected{% endif %}>1</option>
            <option value="2" {% if request.GET.month == '2' %}selected{% endif %}>2</option>
            <!-- ... thêm options 3-12 ... -->
            <option value="12" {% if request.GET.month == '12' %}selected{% endif %}>12</option>
        </select>
    </div>

    <div class="form-group mr-2">
        <label>Năm:</label>
        <select name="year" class="form-control">
            <option value="">Tất cả</option>
            <option value="2024" {% if request.GET.year == '2024' %}selected{% endif %}>2024</option>
            <option value="2025" {% if request.GET.year == '2025' %}selected{% endif %}>2025</option>
            <option value="2026" {% if request.GET.year == '2026' %}selected{% endif %}>2026</option>
        </select>
    </div>

    <div class="form-group mr-2">
        <label>Phòng ban:</label>
        <select name="department" class="form-control">
            <option value="">Tất cả</option>
            {% for dept in departments %}
            <option value="{{ dept.id }}"
                    {% if request.GET.department == dept.id|stringformat:'s' %}selected{% endif %}>
                {{ dept.name }}
            </option>
            {% endfor %}
        </select>
    </div>

    <div class="form-group mr-2">
        <label>Trạng thái:</label>
        <select name="status" class="form-control">
            <option value="">Tất cả</option>
            <option value="Đang xử lý" {% if request.GET.status == 'Đang xử lý' %}selected{% endif %}>Đang xử lý</option>
            <option value="Đã duyệt" {% if request.GET.status == 'Đã duyệt' %}selected{% endif %}>Đã duyệt</option>
            <option value="Đã thanh toán" {% if request.GET.status == 'Đã thanh toán' %}selected{% endif %}>Đã thanh toán</option>
        </select>
    </div>

    <button type="submit" class="btn btn-primary">
        <i class="fas fa-filter"></i> Lọc
    </button>

    <a href="{% url 'manage_payroll' %}" class="btn btn-secondary ml-2">
        <i class="fas fa-times"></i> Xóa lọc
    </a>
</form>
```

**Modify backend view** (`app/management_views.py` line ~913):

```python
@login_required
def manage_payroll(request):
    """Manage payroll with filtering support"""

    # Get filters from GET parameters
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')
    department_filter = request.GET.get('department')
    status_filter = request.GET.get('status')

    # Base queryset
    payrolls = Payroll.objects.select_related(
        'employee',
        'employee__department',
        'employee__job_title'
    ).all()

    # Apply filters
    if month_filter:
        payrolls = payrolls.filter(month=month_filter)

    if year_filter:
        payrolls = payrolls.filter(year=year_filter)

    if department_filter:
        payrolls = payrolls.filter(employee__department_id=department_filter)

    if status_filter:
        payrolls = payrolls.filter(status=status_filter)

    # Permission filtering
    is_hr = request.user.groups.filter(name='HR').exists()
    is_manager = request.user.groups.filter(name='Manager').exists()

    if not is_hr and not is_manager:
        try:
            user_employee = Employee.objects.get(admin=request.user)
            payrolls = payrolls.filter(employee=user_employee)
        except Employee.DoesNotExist:
            payrolls = Payroll.objects.none()

    # Get departments for dropdown
    departments = Department.objects.all()

    context = {
        "payrolls": payrolls,
        "departments": departments,
        "is_hr": is_hr,
        "is_manager": is_manager,
    }

    return render(request, "hod_template/manage_payroll.html", context)
```

**Approach 2: Client-side filtering (Alternative)**

Add JavaScript to filter DataTable:

```javascript
<script>
$(document).ready(function() {
    var table = $('#payroll-table').DataTable();

    $('#filter-btn').on('click', function() {
        var month = $('#month-filter').val();
        var year = $('#year-filter').val();
        var dept = $('#dept-filter').val();
        var status = $('#status-filter').val();

        // Combine month/year filter
        var monthYear = '';
        if (month && year) {
            monthYear = month + '/' + year;
        } else if (month) {
            monthYear = month + '/';
        } else if (year) {
            monthYear = '/' + year;
        }

        // Apply filters to columns
        table.column(1).search(monthYear)      // Month/Year column
             .column(4).search(dept)            // Department column
             .column(6).search(status)          // Status column
             .draw();
    });

    $('#clear-filter-btn').on('click', function() {
        $('#month-filter').val('');
        $('#year-filter').val('');
        $('#dept-filter').val('');
        $('#status-filter').val('');
        table.search('').columns().search('').draw();
    });
});
</script>
```

---

### ✅ TESTING CHECKLIST

**After implementing fix:**

- [ ] Select month only → Table filters
- [ ] Select year only → Table filters
- [ ] Select department only → Table filters
- [ ] Select status only → Table filters
- [ ] Select multiple filters → Table shows intersection
- [ ] Click "Xóa lọc" → Shows all records
- [ ] Export button respects filters (already implemented)

---

### 📦 FILES TO MODIFY

1. `app/templates/hod_template/manage_payroll.html`

   - Add filter form with GET method
   - Add selected state for dropdowns
   - Add clear filter button

2. `app/management_views.py` (line ~913)
   - Modify `manage_payroll` view to accept GET parameters
   - Apply filters to queryset
   - Pass departments to template

---

### ⏱️ ESTIMATED TIME: 2 hours

**Breakdown:**

- Code modification: 1 hour
- Testing: 30 minutes
- Bug fixes: 30 minutes

---

## ⚠️ BUG #8: Fix Payroll Sorting by Month/Year

### 📋 MÔ TẢ VẤN ĐỀ

**Hiện trạng:**

- Payroll table có column "Tháng/Năm" với format: "1/2025", "10/2025"
- DataTables sort theo string → Sai thứ tự: 1, 10, 11, 2, 3, 4...
- **Expected:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

**Example of wrong sorting:**

```
Current (string sort):
1/2025
10/2025
11/2025
12/2025
2/2025
3/2025

Expected (numeric sort):
1/2025
2/2025
3/2025
...
10/2025
11/2025
12/2025
```

---

### 🎯 GIẢI PHÁP

**File cần sửa:** `app/templates/hod_template/manage_payroll.html`

**Approach 1: Custom DataTables column type**

```javascript
<script>
// Define custom sort type for month/year
$.fn.dataTable.ext.type.order['month-year-pre'] = function(data) {
    if (!data || data === '-') return 0;

    var parts = data.split('/');
    var month = parseInt(parts[0]) || 0;
    var year = parseInt(parts[1]) || 0;

    // Convert to sortable number: year * 12 + month
    // Example: 10/2025 = 2025 * 12 + 10 = 24310
    return year * 12 + month;
};

// Apply to DataTable
$(document).ready(function() {
    $('#payroll-table').DataTable({
        columnDefs: [
            {
                targets: 1,  // Month/Year column (0-indexed, change if needed)
                type: 'month-year'
            }
        ],
        order: [[1, 'desc']]  // Default sort by month/year descending
    });
});
</script>
```

**Approach 2: Add hidden sortable column**

Modify table structure:

```html
<table id="payroll-table">
  <thead>
    <tr>
      <th>STT</th>
      <th>Tháng/Năm</th>
      <th data-orderable="false" style="display:none">Sort Key</th>
      <!-- Hidden -->
      <th>Nhân viên</th>
      <th>Chức vụ</th>
      <th>Phòng ban</th>
      <th>Lương cơ bản</th>
      <th>Tổng lương</th>
      <th>Trạng thái</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for payroll in payrolls %}
    <tr>
      <td>{{ forloop.counter }}</td>
      <td>{{ payroll.month }}/{{ payroll.year }}</td>
      <td style="display:none">
        {{ payroll.year }}{{ payroll.month|stringformat:"02d" }}
      </td>
      <!-- 202510 -->
      <td>
        {{ payroll.employee.admin.first_name }} {{
        payroll.employee.admin.last_name }}
      </td>
      <!-- ... rest of columns ... -->
    </tr>
    {% endfor %}
  </tbody>
</table>

<script>
  $(document).ready(function () {
    $("#payroll-table").DataTable({
      columnDefs: [
        { targets: 2, visible: false }, // Hide sort key column
      ],
      order: [[2, "desc"]], // Sort by hidden sort key
    });
  });
</script>
```

**Approach 3: Use data attributes**

```html
<td data-order="{{ payroll.year }}{{ payroll.month|stringformat:'02d' }}">
  {{ payroll.month }}/{{ payroll.year }}
</td>
```

DataTables automatically uses `data-order` attribute for sorting.

---

### ✅ TESTING CHECKLIST

**After implementing fix:**

- [ ] Click "Tháng/Năm" column header
- [ ] Ascending sort: 1/2025, 2/2025, 3/2025, ..., 10/2025, 11/2025, 12/2025
- [ ] Descending sort: 12/2025, 11/2025, 10/2025, ..., 3/2025, 2/2025, 1/2025
- [ ] Works with different years: 1/2024, 12/2024, 1/2025
- [ ] Other columns still sortable

---

### 📦 FILES TO MODIFY

1. `app/templates/hod_template/manage_payroll.html`
   - Add custom DataTables sort function
   - OR add hidden sort column
   - OR add data-order attributes

---

### ⏱️ ESTIMATED TIME: 1.5 hours

**Breakdown:**

- Code modification: 45 minutes
- Testing: 30 minutes
- Bug fixes: 15 minutes

---

## 🆕 FEATURE #13: User Management Page

### 📋 MÔ TẢ YÊU CẦU

**Chức năng cần có:**

1. ✅ List all users (username, email, groups, status)
2. ✅ Create new user (username, password, email, first_name, last_name)
3. ✅ Assign user to groups (HR, Manager, Staff)
4. ✅ Edit user information
5. ✅ Activate/Deactivate user
6. ✅ Delete user (soft delete - set is_active = False)
7. ✅ Permission: Only HR can access

---

### 🎯 GIẢI PHÁP CHI TIẾT

---

#### 📄 STEP 1: Create Views

**File:** `app/user_management_views.py` (NEW FILE)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password
from app.models import Employee

def require_hr(view_func):
    """Decorator to require HR group membership"""
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='HR').exists():
            messages.error(request, "Bạn không có quyền truy cập trang này.")
            return redirect('admin_home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_hr
def manage_users(request):
    """List all users with their groups and status"""
    users = User.objects.all().prefetch_related('groups').order_by('-date_joined')
    groups = Group.objects.all()

    context = {
        "users": users,
        "groups": groups,
    }
    return render(request, "hod_template/manage_users.html", context)


@login_required
@require_hr
def add_user(request):
    """Create new user"""
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        groups = request.POST.getlist("groups")  # Multiple groups

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' đã tồn tại.")
            return redirect('add_user')

        if User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' đã được sử dụng.")
            return redirect('add_user')

        # Create user
        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )

            # Assign groups
            for group_id in groups:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)

            messages.success(request, f"Tạo user '{username}' thành công.")
            return redirect('manage_users')

        except Exception as e:
            messages.error(request, f"Lỗi khi tạo user: {str(e)}")
            return redirect('add_user')

    # GET request
    groups = Group.objects.all()
    context = {"groups": groups}
    return render(request, "hod_template/add_user.html", context)


@login_required
@require_hr
def edit_user(request, user_id):
    """Edit existing user"""
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.is_active = request.POST.get("is_active") == "on"

        # Update password if provided
        new_password = request.POST.get("password")
        if new_password:
            user.password = make_password(new_password)

        # Update groups
        groups = request.POST.getlist("groups")
        user.groups.clear()
        for group_id in groups:
            group = Group.objects.get(id=group_id)
            user.groups.add(group)

        try:
            user.save()
            messages.success(request, f"Cập nhật user '{user.username}' thành công.")
            return redirect('manage_users')
        except Exception as e:
            messages.error(request, f"Lỗi khi cập nhật user: {str(e)}")

    # GET request
    groups = Group.objects.all()
    user_groups = user.groups.all()

    context = {
        "user_obj": user,
        "groups": groups,
        "user_groups": user_groups,
    }
    return render(request, "hod_template/edit_user.html", context)


@login_required
@require_hr
@require_POST
def toggle_user_status(request, user_id):
    """Activate/Deactivate user"""
    user = get_object_or_404(User, id=user_id)

    # Prevent deactivating self
    if user.id == request.user.id:
        return JsonResponse({
            "status": "error",
            "message": "Bạn không thể deactivate chính mình."
        })

    user.is_active = not user.is_active
    user.save()

    status_text = "kích hoạt" if user.is_active else "vô hiệu hóa"

    return JsonResponse({
        "status": "success",
        "message": f"User '{user.username}' đã được {status_text}.",
        "is_active": user.is_active
    })


@login_required
@require_hr
@require_POST
def delete_user(request, user_id):
    """Soft delete user (set is_active = False)"""
    user = get_object_or_404(User, id=user_id)

    # Prevent deleting self
    if user.id == request.user.id:
        return JsonResponse({
            "status": "error",
            "message": "Bạn không thể xóa chính mình."
        })

    # Soft delete
    user.is_active = False
    user.save()

    return JsonResponse({
        "status": "success",
        "message": f"User '{user.username}' đã bị xóa (vô hiệu hóa)."
    })
```

---

#### 🌐 STEP 2: Create URLs

**File:** `app/urls_management.py`

Add these routes:

```python
from app import user_management_views

urlpatterns = [
    # ... existing routes ...

    # User Management
    path('users/', user_management_views.manage_users, name='manage_users'),
    path('users/add/', user_management_views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', user_management_views.edit_user, name='edit_user'),
    path('users/<int:user_id>/toggle-status/', user_management_views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', user_management_views.delete_user, name='delete_user'),
]
```

---

#### 🎨 STEP 3: Create Templates

**File 1:** `app/templates/hod_template/manage_users.html`

```html
{% extends 'hod_template/base_template.html' %}
{% block page_title %}Quản lý Người dùng{% endblock %}

{% block main_content %}
<section class="content">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Danh sách Người dùng</h3>
                        <div class="card-tools">
                            <a href="{% url 'add_user' %}" class="btn btn-primary btn-sm">
                                <i class="fas fa-plus"></i> Thêm User
                            </a>
                        </div>
                    </div>
                    <div class="card-body">
                        <table id="users-table" class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>STT</th>
                                    <th>Username</th>
                                    <th>Họ tên</th>
                                    <th>Email</th>
                                    <th>Nhóm quyền</th>
                                    <th>Trạng thái</th>
                                    <th>Ngày tạo</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for user in users %}
                                <tr>
                                    <td>{{ forloop.counter }}</td>
                                    <td>{{ user.username }}</td>
                                    <td>{{ user.first_name }} {{ user.last_name }}</td>
                                    <td>{{ user.email }}</td>
                                    <td>
                                        {% for group in user.groups.all %}
                                            <span class="badge badge-info">{{ group.name }}</span>
                                        {% empty %}
                                            <span class="badge badge-secondary">No groups</span>
                                        {% endfor %}
                                    </td>
                                    <td>
                                        {% if user.is_active %}
                                            <span class="badge badge-success">Active</span>
                                        {% else %}
                                            <span class="badge badge-danger">Inactive</span>
                                        {% endif %}
                                    </td>
                                    <td>{{ user.date_joined|date:"d/m/Y H:i" }}</td>
                                    <td>
                                        <a href="{% url 'edit_user' user.id %}"
                                           class="btn btn-warning btn-sm">
                                            <i class="fas fa-edit"></i>
                                        </a>

                                        <button onclick="toggleStatus({{ user.id }})"
                                                class="btn btn-info btn-sm">
                                            <i class="fas fa-power-off"></i>
                                        </button>

                                        <button onclick="deleteUser({{ user.id }})"
                                                class="btn btn-danger btn-sm"
                                                {% if user.id == request.user.id %}disabled{% endif %}>
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<script>
$(document).ready(function() {
    $('#users-table').DataTable({
        order: [[6, 'desc']]  // Sort by date joined
    });
});

function toggleStatus(userId) {
    if (confirm('Bạn có chắc muốn thay đổi trạng thái user này?')) {
        $.ajax({
            url: `/management/users/${userId}/toggle-status/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function(response) {
                if (response.status === 'success') {
                    alert(response.message);
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Lỗi khi thay đổi trạng thái user.');
            }
        });
    }
}

function deleteUser(userId) {
    if (confirm('Bạn có chắc muốn xóa user này? (User sẽ bị vô hiệu hóa)')) {
        $.ajax({
            url: `/management/users/${userId}/delete/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function(response) {
                if (response.status === 'success') {
                    alert(response.message);
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Lỗi khi xóa user.');
            }
        });
    }
}
</script>
{% endblock %}
```

**File 2:** `app/templates/hod_template/add_user.html`

```html
{% extends 'hod_template/base_template.html' %} {% block page_title %}Thêm Người
dùng{% endblock %} {% block main_content %}
<section class="content">
  <div class="container-fluid">
    <div class="row">
      <div class="col-md-8 offset-md-2">
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Thêm User Mới</h3>
          </div>
          <form method="POST" action="{% url 'add_user' %}">
            {% csrf_token %}
            <div class="card-body">
              <div class="form-group">
                <label>Username *</label>
                <input
                  type="text"
                  name="username"
                  class="form-control"
                  required
                />
              </div>

              <div class="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  class="form-control"
                  required
                />
              </div>

              <div class="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  name="password"
                  class="form-control"
                  required
                />
              </div>

              <div class="form-group">
                <label>Họ</label>
                <input type="text" name="first_name" class="form-control" />
              </div>

              <div class="form-group">
                <label>Tên</label>
                <input type="text" name="last_name" class="form-control" />
              </div>

              <div class="form-group">
                <label>Nhóm quyền</label>
                {% for group in groups %}
                <div class="form-check">
                  <input
                    type="checkbox"
                    name="groups"
                    value="{{ group.id }}"
                    class="form-check-input"
                    id="group{{ group.id }}"
                  />
                  <label class="form-check-label" for="group{{ group.id }}">
                    {{ group.name }}
                  </label>
                </div>
                {% endfor %}
              </div>
            </div>

            <div class="card-footer">
              <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i> Lưu
              </button>
              <a href="{% url 'manage_users' %}" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Quay lại
              </a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
```

**File 3:** `app/templates/hod_template/edit_user.html`

Similar to `add_user.html` but with pre-filled values:

```html
<!-- Pre-fill values with {{ user_obj.username }}, etc. -->
<!-- Check groups: {% if group in user_groups %}checked{% endif %} -->
```

---

#### 🔗 STEP 4: Add Menu Link

**File:** `app/templates/hod_template/base_template.html` (sidebar)

Add menu item:

```html
<li class="nav-item">
  <a href="{% url 'manage_users' %}" class="nav-link">
    <i class="nav-icon fas fa-users-cog"></i>
    <p>Quản lý User</p>
  </a>
</li>
```

---

### ✅ TESTING CHECKLIST

**After implementing feature:**

- [ ] Page loads without errors
- [ ] Can view all users
- [ ] Can create new user
- [ ] New user can login
- [ ] Can assign groups (HR, Manager, Staff)
- [ ] Can edit user information
- [ ] Can change password
- [ ] Can activate/deactivate user
- [ ] Cannot deactivate self
- [ ] Can soft delete user
- [ ] Cannot delete self
- [ ] Only HR can access page
- [ ] Non-HR redirected with error message

---

### 📦 FILES TO CREATE/MODIFY

**New Files:**

1. `app/user_management_views.py` (NEW)
2. `app/templates/hod_template/manage_users.html` (NEW)
3. `app/templates/hod_template/add_user.html` (NEW)
4. `app/templates/hod_template/edit_user.html` (NEW)

**Modified Files:**

1. `app/urls_management.py` (add 5 new routes)
2. `app/templates/hod_template/base_template.html` (add menu item)

---

### ⏱️ ESTIMATED TIME: 6-8 hours

**Breakdown:**

- Views creation: 2 hours
- Templates creation: 3 hours
- URLs and integration: 1 hour
- Testing: 1.5 hours
- Bug fixes: 1.5 hours

---

## 📊 SUMMARY

### Công việc còn lại:

| Item                   | Type        | Priority | Time | Complexity |
| ---------------------- | ----------- | -------- | ---- | ---------- |
| Bug #7: Filter         | Bug Fix     | HIGH     | 2h   | Medium     |
| Bug #8: Sorting        | Bug Fix     | HIGH     | 1.5h | Medium     |
| Feature #13: User Mgmt | New Feature | MEDIUM   | 6-8h | High       |

**Total estimated time:** 9.5 - 11.5 hours

---

## 🎯 RECOMMENDED APPROACH

### Option 1: Fix bugs first (Recommended)

1. Fix Bug #7 (Filter) - 2h
2. Fix Bug #8 (Sorting) - 1.5h
3. Test both fixes - 30 min
4. Implement Feature #13 - 6-8h
5. Final testing - 1h

**Total:** ~11-13 hours

### Option 2: Feature first

1. Implement Feature #13 - 6-8h
2. Fix Bug #7 - 2h
3. Fix Bug #8 - 1.5h
4. Final testing - 1h

**Total:** ~10.5-12.5 hours

---

## 📝 NOTES

**Important:**

- Bugs #7 và #8 liên quan đến cùng một file (manage_payroll.html)
- Nên fix cùng lúc để tránh conflict
- Feature #13 độc lập, có thể làm trước hoặc sau
- Sau khi hoàn thành cần test lại tất cả 13 items

**Dependencies:**

- Bug #7 depends on: Backend filter support (DONE ✅)
- Bug #8 depends on: None
- Feature #13 depends on: Django User model, Groups (available ✅)

---

## ✅ COMPLETION CRITERIA

**Round 4 hoàn thành khi:**

- [ ] 10/10 existing tests PASS
- [ ] Bug #7 fixed and tested
- [ ] Bug #8 fixed and tested
- [ ] Feature #13 implemented and tested
- [ ] 13/13 items complete
- [ ] Updated testing checklist verified
- [ ] No critical bugs found

---

**Document Version:** 1.0  
**Last Updated:** 20/11/2025  
**Status:** Planning phase - Ready to implement
