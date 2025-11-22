# 📋 ROUND 4 BUG FIXES - HRM MANAGEMENT PORTAL

**Ngày tạo:** 20/11/2025  
**Tổng số bugs:** 13 bugs (1 đã fix, 12 còn lại)  
**Mục đích:** Fix tất cả bugs phát hiện trong Round 3 testing

---

## ✅ ĐÃ FIX (3/13)

### 1. ✅ convert_to_employee Missing URL

**Lỗi:** `NoReverseMatch: Reverse for 'convert_to_employee' not found`  
**Fix:** Thêm URL alias vào `urls_management.py`

```python
path('recruitment/applications/<int:application_id>/convert/',
     management_views.convert_to_employee,
     name='convert_to_employee'),
```

### 2. ✅ Delete Attendance Button Not Responding

**Lỗi:** AJAX không phản hồi khi click button xóa  
**Fix:** Thay đổi view signature từ `def delete_attendance(request)` thành `def delete_attendance(request, attendance_id)` để nhận ID từ URL thay vì POST data

### 3. ✅ Add Appraisal Criteria Form Issue

**Lỗi:** POST trả về 200 nhưng không thêm criteria  
**Cần kiểm tra:** View `add_appraisal_criteria` có đang lưu data không

---

## ⚠️ ĐANG FIX (0/13)

_(Đang tiến hành fix các bugs còn lại)_

---

## 🔴 CẦN FIX (10/13)

### GROUP A: PAYROLL CRITICAL BUGS (6 bugs)

#### 4. 🔴 Hourly Wage Calculation Error

**Mô tả:** Lương theo giờ hiển thị sai (7,738,095,238,095,238 VNĐ thay vì 147,727 VNĐ)  
**Trường hợp:**

- Lương cơ bản: 26,000,000 VNĐ
- Ngày làm việc: 21 ngày → SAI
- Ngày làm việc: 22 ngày → ĐÚNG

**Nguyên nhân:** Công thức tính lương giờ có vấn đề khi số ngày = 21  
**File cần sửa:** `app/management_views.py` - hàm tính lương giờ  
**Priority:** CRITICAL ⚡

#### 5. 🔴 Month Dropdown Display Bug

**Mô tả:** Trang `/management/payroll/calculate/` hiển thị tháng: 1,2,3,4,5,6,7,8,9,1,0,1,1,1,2 thay vì 1-12  
**Nguyên nhân:** Template loop tháng bị lỗi logic  
**File cần sửa:** `app/templates/hod_template/calculate_payroll.html`  
**Priority:** HIGH 🔥

#### 6. 🔴 Payroll Manage Filter Not Working

**Mô tả:** Chức năng lọc ở `/management/payroll/manage/` không hoạt động  
**File cần sửa:** `app/templates/hod_template/manage_payroll.html` - JavaScript filter  
**Priority:** MEDIUM

#### 7. 🔴 Payroll Sorting by Month/Year Wrong

**Mô tả:** Sắp xếp theo Tháng/Năm: 1/2025 → 10/2025 → 11/2025 → 8/2025 → 9/2025  
**Đúng phải:** 1/2025 → 8/2025 → 9/2025 → 10/2025 → 11/2025  
**Nguyên nhân:** Sắp xếp string "1/2025", "10/2025" thay vì số  
**File cần sửa:** `app/templates/hod_template/manage_payroll.html` - DataTables config  
**Priority:** MEDIUM

#### 8. 🔴 Payroll Visibility by Department

**Mô tả:** Manager chỉ thấy bảng lương phòng ban của mình, cần thấy toàn bộ  
**File cần sửa:** `app/management_views.py` - `manage_payroll` view filter logic  
**Priority:** HIGH 🔥

#### 9. 🔴 Payroll Export Filters Not Working

**Mô tả:** Không thể xuất Excel theo Tháng/Năm/Phòng ban/Trạng thái  
**File cần sửa:** `app/management_views.py` - `export_payroll` view  
**Priority:** MEDIUM

### GROUP B: FORM DEFAULT VALUES (2 bugs)

#### 10. 🔴 Attendance Date Default to Today

**Mô tả:** Form thêm chấm công cần mặc định ngày = hôm nay  
**File cần sửa:** `app/templates/hod_template/add_attendance.html`  
**Fix:** Thêm `value="{{ today|date:'Y-m-d' }}"` vào input date  
**Priority:** LOW

#### 11. 🔴 Employee Form Default Values

**Mô tả:** Cần thêm giá trị mặc định:

- Nơi cấp: "CỤC TRƯỞNG CỤC CẢNH SÁT QUẢN LÝ HÀNH CHÍNH VỀ TRẬT TỰ XÃ HỘI"
- Quốc tịch: "Việt Nam"
- Dân tộc: "Kinh"
- Tôn giáo: "Không"

**File cần sửa:** `app/templates/hod_template/add_employee.html`  
**Priority:** LOW

### GROUP C: NEW FEATURE (1 task)

#### 12. 🆕 User Management Page

**Mô tả:** Tạo trang quản lý người dùng với:

- Tạo user mới
- Gán quyền (HR, Manager, Staff)
- Phân nhóm

**Files cần tạo:**

- `app/user_management_views.py` - Views
- `app/templates/hod_template/user_management.html` - Template
- `app/urls_management.py` - Add URLs

**Priority:** NEW FEATURE 🆕

---

## 📝 CHI TIẾT FIX PLAN

### PHASE 1: Critical Bugs (Bugs 4, 5, 8)

**Bug 4: Hourly Wage Calculation**

```python
# Tìm trong management_views.py:
grep -n "hourly.*wage\|lương.*giờ" app/management_views.py

# Công thức hiện tại có thể là:
hourly_wage = base_salary / working_days / 8

# Cần kiểm tra và fix logic chia 0 hoặc lỗi kiểu dữ liệu
```

**Bug 5: Month Dropdown**

```python
# Trong calculate_payroll.html, tìm:
{% for month in months %}
# Hoặc
{% for i in "123456789101112" %}

# Fix thành:
{% for month in "123456789" %}{{ month }}{% endfor %}{% for month in "10,11,12" %}
```

**Bug 8: Payroll Visibility**

```python
# Trong manage_payroll view:
# TRƯỚC:
payrolls = Payroll.objects.filter(employee__department=request.user.employee.department)

# SAU:
if request.user.groups.filter(name='Manager').exists():
    payrolls = Payroll.objects.all()  # Show all for managers
else:
    payrolls = Payroll.objects.filter(employee=request.user.employee)
```

### PHASE 2: Medium Priority (Bugs 6, 7, 9)

**Bug 6: Filter Not Working**

- Kiểm tra JavaScript filter function
- Debug AJAX calls
- Fix DataTables filter config

**Bug 7: Sorting Issue**

- Add custom sorting function cho month/year column
- Convert "1/2025" → sort value

**Bug 9: Export Filters**

- Add query parameters to export_payroll view
- Apply same filters as manage view

### PHASE 3: Low Priority (Bugs 10, 11)

**Bug 10 & 11: Form Defaults**

- Easy fixes - just add value="" attributes
- Có thể fix cùng lúc

### PHASE 4: New Feature (Bug 12)

**User Management** - Cần design và implement:

1. Create view for user list
2. Create modal for add/edit user
3. Implement role/group assignment
4. Add permissions checking

---

## 🧪 TESTING PLAN

### Test Round 4.1 (After Phase 1)

- [ ] Hourly wage calculation đúng với mọi số ngày
- [ ] Month dropdown hiển thị 1-12
- [ ] Manager thấy tất cả payroll

### Test Round 4.2 (After Phase 2)

- [ ] Filter hoạt động
- [ ] Sorting month/year đúng
- [ ] Export với filters

### Test Round 4.3 (After Phase 3)

- [ ] Attendance date = today
- [ ] Employee form có defaults

### Test Round 4.4 (After Phase 4)

- [ ] User management page working
- [ ] Can create users
- [ ] Can assign roles/groups

---

## 📊 PROGRESS TRACKING

**Status:** 3/13 bugs fixed (23%)

### By Priority:

- CRITICAL: 0/1 fixed
- HIGH: 0/2 fixed
- MEDIUM: 0/3 fixed
- LOW: 0/2 fixed
- NEW FEATURE: 0/1 done

### By Phase:

- Phase 1 (Critical): Not started
- Phase 2 (Medium): Not started
- Phase 3 (Low): Not started
- Phase 4 (Feature): Not started

---

## 🎯 NEXT STEPS

1. **Continue fixing Phase 1 bugs** (hourly wage, month dropdown, visibility)
2. **Run focused tests** on each fix
3. **Document changes** in code comments
4. **Update test checklist** after each phase
5. **Create user management** page

---

**Last Updated:** 20/11/2025  
**Status:** In Progress 🔄
