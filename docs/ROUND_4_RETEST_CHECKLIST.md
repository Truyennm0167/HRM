# 🔄 ROUND 4 RE-TEST CHECKLIST

**Ngày tạo:** 21/11/2025  
**Phiên bản:** 4.1 (After Fixes)  
**Trạng thái:** Ready for Re-Testing

---

## 📊 TÓM TẮT CÁC FIX ĐÃ THỰC HIỆN

### ✅ Đã fix 6 vấn đề từ lần test trước:

1. ✅ **Delete Attendance Button** - Removed duplicate route
2. ✅ **Payroll Visibility for Manager** - Fixed permission logic
3. ✅ **Export with Filters** - Added GET parameter passing
4. ✅ **Edit Payroll Form** - Added data pre-population
5. ✅ **Add Appraisal Criteria** - Added validation error display
6. ✅ **Month Dropdown in Filters** - Fixed broken loop

---

## 🧪 DANH SÁCH TEST CASES CẦN RETEST

### 🔴 PRIORITY 1: CÁC LỖI ĐÃ FIX (6 tests)

---

### TEST A: Delete Attendance Button ✅ **[RETEST REQUIRED]**

**Vấn đề cũ:** Nút Xóa không phản hồi

**Fix đã thực hiện:**

- File: `app/urls_management.py` line 42
- **Removed:** Duplicate route `path('attendance/delete/', ...)` không có parameter
- **Kept:** Route `path('attendance/<int:attendance_id>/delete/', ...)` với parameter
- **Impact:** AJAX call giờ match đúng route

**Các bước test:**

1. **Login** với quyền quản lý attendance
2. **Navigate:** `http://127.0.0.1:8000/management/attendance/manage/`
3. **Click nút "Xóa"** trên bất kỳ attendance record nào
4. **Confirm** trong popup

**Expected Result:**

```
✅ Popup confirmation hiện
✅ Record bị xóa khỏi table
✅ Page reload hoặc table refresh
✅ Database không còn record đó
```

**Actual Result:**

```
[ ] PASS - Xóa thành công
[X] FAIL - Lỗi: Nút xóa không phản hồi - trên màn hình Console cũng không trả về bất cứ thứ gì
```

**Console Check:**

- Open DevTools → Network tab
- Should see: `POST /management/attendance/{id}/delete/` → Status 200
- Should NOT see: 404 errors

---

### TEST B: Payroll Visibility for Manager ✅ **[RETEST REQUIRED]**

**Vấn đề cũ:** User hangpt (quyền Manager/Superuser) chỉ xem được bảng lương của mình

**Fix đã thực hiện:**

- File: `app/management_views.py` line 917-945
- **Before:** Checked employee email first → Always tried to get user_employee
- **After:** Check role first → Only get user_employee for regular employees

```python
is_hr = request.user.groups.filter(name='HR').exists()
is_manager = request.user.groups.filter(name='Manager').exists() or request.user.is_superuser

if not is_hr and not is_manager:
    # Only regular employees filtered
    user_employee = Employee.objects.get(email=request.user.email)
    payrolls = payrolls.filter(employee=user_employee)
# HR and Managers see ALL payrolls (no filtering)
```

**Các bước test:**

**Test Case 1: Login as Manager/Superuser (hangpt)**

1. **Login:** Username `hangpt` (Manager/Superuser)
2. **Navigate:** `/management/payroll/manage/`
3. **Count visible records**
4. **Check departments:** Should see payrolls from ALL departments

**Test Case 2: Login as Regular Employee**

1. **Login:** Regular employee account (không phải HR, Manager)
2. **Navigate:** `/management/payroll/manage/`
3. **Check:** Should only see OWN payroll records

**Expected Result:**

```
✅ hangpt (Manager/Superuser): Sees ALL payrolls
✅ HR users: See ALL payrolls
✅ Regular employees: See only OWN payroll
✅ No exceptions or errors
```

**Verification:**

```sql
-- Check total payrolls in system
SELECT COUNT(*) as total FROM app_payroll;

-- What hangpt should see
SELECT COUNT(*) as visible
FROM app_payroll p
JOIN app_employee e ON p.employee_id = e.id
JOIN app_department d ON e.department_id = d.id;
-- visible should equal total
```

**Actual Result:**

```
[X] PASS - Manager sees all records
[ ] FAIL - Manager only sees: _____ records
```

---

### TEST C: Export Payroll with Filters ✅ **[RETEST REQUIRED]**

**Vấn đề cũ:** Khi tải xuống luôn là tất cả bảng lương (không apply filters)

**Fix đã thực hiện:**

**1. Frontend Fix** - `app/templates/hod_template/manage_payroll.html`

```javascript
$("#export").click(function () {
  var month = $("#month").val();
  var year = $("#year").val();
  var department = $("#department").val();
  var status = $("#status").val();

  // Build URL with query parameters
  var url = "{% url 'export_payroll' %}";
  var params = [];
  if (month) params.push("month=" + month);
  if (year) params.push("year=" + year);
  if (department) params.push("department=" + department);
  if (status) params.push("status=" + status);

  if (params.length > 0) {
    url += "?" + params.join("&");
  }

  window.location.href = url;
});
```

**2. Backend Fix** - `app/management_views.py` line 1037-1075

```python
# Changed from:
payrolls = payrolls.filter(employee__department_id=department)

# To:
payrolls = payrolls.filter(employee__department__name=department)
# Because frontend sends department NAME, not ID
```

**Các bước test:**

**Test Case 1: Filter by Month & Year**

1. Navigate: `/management/payroll/manage/`
2. Select: Tháng = 10, Năm = 2025
3. Click "Xuất Excel"
4. Open Excel file
5. Verify: All rows have "10/2025" in Tháng/Năm column

**Test Case 2: Filter by Department**

1. Navigate: `/management/payroll/manage/`
2. Select: Phòng Ban = "Nhân sự"
3. Click "Xuất Excel"
4. Open Excel file
5. Verify: All rows have "Nhân sự" in Phòng Ban column

**Test Case 3: Multiple Filters**

1. Select: Tháng=11, Năm=2025, Phòng Ban="Giám đốc"
2. Click "Xuất Excel"
3. Verify: Rows match ALL three filters

**Expected Result:**

```
✅ URL shows query params: ?month=10&year=2025&department=Nhân%20sự
✅ Excel contains only filtered records
✅ Record count matches what's visible in table after filter
✅ Empty Excel if no matching records
```

**Actual Result:**

```
[ ] PASS - Filter works correctly
[X] FAIL - Chức năng Lọc chưa hoạt động đúng
Hiện tại tôi không thể lọc theo tháng và trạng thái
Khi tôi lọc theo tháng thì vẫn hiển thị tất cả record
Khi tôi lọc theo Trạng thái Chưa xác nhận hoặc Đã xác nhận thì không hiển thị record nào


Hiện tại thì tôi xuất Excel cho phòng ban thì hoạt động tốt rồi, nhưng tôi cần bạn đặt tên file theo Bộ lọc luôn.
```

---

### TEST D: Edit Payroll Form Data ✅ **[RETEST REQUIRED]**

**Vấn đề cũ:** Tất cả field đều không show được khi edit

**Fix đã thực hiện:**

- File: `app/templates/hod_template/calculate_payroll.html` lines 150-175
- **Added:** JavaScript to pre-populate form when `edit_mode=True`

```javascript
// If edit mode, populate form with existing payroll data
{% if edit_mode and payroll %}
$("#employee").val({{ payroll.employee.id }});
$("#month").val({{ payroll.month }});
$("#year").val({{ payroll.year }});
// ... populate all fields
{% endif %}
```

**Các bước test:**

1. **Login as HR:** `admin` / `admin123`
2. **Navigate:** `/management/payroll/manage/`
3. **Click "Cập nhật"** trên một payroll record (status = "Chưa xác nhận")
4. **Check form fields:**

| Field                | Should Show       | Pass/Fail |
| -------------------- | ----------------- | --------- |
| Nhân viên (dropdown) | Selected employee | [ ]       |
| Tháng (dropdown)     | Selected month    | [ ]       |
| Năm (dropdown)       | Selected year     | [ ]       |
| Lương cơ bản         | e.g. 26,000,000   | [ ]       |
| Hệ số lương          | e.g. 4.5          | [ ]       |
| Lương theo giờ       | e.g. 696,429      | [ ]       |
| Tổng giờ             | e.g. 168          | [ ]       |
| Thưởng               | e.g. 2,000,000    | [ ]       |
| Phạt                 | e.g. 500,000      | [ ]       |
| Tổng lương           | Calculated total  | [ ]       |
| Ghi chú              | Existing notes    | [ ]       |

5. **Test editing:**
   - Change "Thưởng" from 2,000,000 to 3,000,000
   - Click "Lưu Bảng Lương"
   - Verify saved correctly

**Expected Result:**

```
✅ All fields populated with existing data
✅ Employee/Month/Year dropdowns pre-selected
✅ Can edit values
✅ Changes save correctly
```

**Actual Result:**

```
[X] PASS - All fields show data - Nhưng hiện tại tôi không thể Xem chi tiết các bảng lương đã xác nhận được.
INFO "GET /management/payroll/manage/ HTTP/1.1" 200 112200
INFO "GET /management/payroll/158/ HTTP/1.1" 302 0


Tôi cần bạn chỉnh sửa thêm khi hiển thị số tiền thì cần thêm dấu phân cách đơn vị vào
[ ] FAIL - Fields không show: _______________________
```

---

### TEST E: Add Appraisal Criteria ✅ **[RETEST REQUIRED]**

**Vấn đề cũ:** Không thể thêm tiêu chí đánh giá

**Fix đã thực hiện:**

- File: `app/management_views.py` line 3693-3721
- **Added:** Detailed validation error messages

```python
if form.is_valid():
    # Save logic
else:
    # Show specific field errors
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f'{field}: {error}')
    logger.warning(f"Form validation failed: {form.errors}")
```

**Các bước test:**

1. **Login as HR:** `admin` / `admin123`
2. **Navigate:** `/management/appraisal/periods/`
3. **Click vào một appraisal period**
4. **Click "Thêm tiêu chí"**
5. **Fill form với data hợp lệ:**
   - Tên tiêu chí: "Kỹ năng giao tiếp"
   - Mô tả: "Đánh giá khả năng giao tiếp"
   - Danh mục: "Hành vi" (behavior)
   - Trọng số: 15
   - Điểm tối đa: 5
6. **Submit form**

**Expected Result:**

```
✅ Form submits successfully
✅ Success message: "Đã thêm tiêu chí: Kỹ năng giao tiếp"
✅ Redirects to period detail page
✅ New criteria appears in list
✅ Database has new record
```

**If form validation fails:**

```
✅ Error messages show specific field issues
✅ Example: "weight: Ensure this value is less than or equal to 100"
```

**Verification:**

```sql
SELECT
    name,
    description,
    category,
    weight,
    max_score
FROM app_appraisalcriteria
WHERE period_id = {period_id}
ORDER BY id DESC
LIMIT 1;

-- Should show: "Kỹ năng giao tiếp", "behavior", 15, 5
```

**Actual Result:**

```
[ ] PASS - Criteria added successfully
[X] FAIL -

Lỗi Khi xem 1 Kỳ đánh giá đang diễn ra:
NoReverseMatch at /management/appraisal/periods/2/
Reverse for 'appraisal_detail' not found. 'appraisal_detail' is not a valid view function or pattern name.


Có thể truy cập vào để xem 1 kỳ đánh giá nháp và khi thêm tiêu chí đánh giá mới thì hiện vẫn không thêm được, trong khi tôi đã nhập đầy đủ trường dữ liệu
INFO "GET /management/appraisal/periods/1/add-criteria/ HTTP/1.1" 200 35660
WARNING Form validation failed: <ul class="errorlist"><li>order<ul class="errorlist"><li>This field is required.</li></ul></li></ul>
INFO "POST /management/appraisal/periods/1/add-criteria/ HTTP/1.1" 200 36290
[ ] Form validation errors: _______________________
```

---

### TEST F: Month Dropdown in Filters ✅ **[RETEST REQUIRED]**

**Vấn đề cũ:** (Nếu có vấn đề tương tự trong manage_payroll.html)

**Fix đã thực hiện:**

- File: `app/templates/hod_template/manage_payroll.html` lines 18-34
- **Before:** `{% for i in "123456789101112"|make_list %}` → Showed 1,2,3,4,5,6,7,8,9,1,0,1,1,1,2
- **After:** Explicit options 1-12

**Các bước test:**

1. **Navigate:** `/management/payroll/manage/`
2. **Click dropdown "Tháng"**
3. **Verify options:**
   - ✅ "Tất cả" (blank value)
   - ✅ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
   - ❌ NO weird values like "1", "0", "1", "1", "1", "2"

**Expected Result:**

```
✅ Dropdown shows: Tất cả, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
✅ 13 total options (including "Tất cả")
✅ Can select month 10, 11, 12 correctly
```

**Actual Result:**

```
[X] PASS - Dropdown correct
[ ] FAIL - Options hiển thị: _______________________
```

---

## ✅ PRIORITY 2: CÁC TEST ĐÃ PASS (Verify vẫn OK)

### Quick Verification Tests:

1. **convert_to_employee URL** → Navigate to application detail page → Should not error
2. **Hourly wage calculation** → Calculate payroll with 21 days → Should show ~696k VNĐ
3. **Month dropdown (calculate page)** → Check shows 1-12 correctly
4. **Employee form defaults** → Open add employee → 4 fields have defaults
5. **Attendance date default** → Open add attendance → Date = today

---

## 📊 TEST RESULTS SUMMARY

**Ngày test:** \***\*\_\_\_\*\***  
**Tester:** \***\*\_\_\_\*\***

### Critical Fixes (Must Pass):

| #   | Test Name              | Status              | Notes  |
| --- | ---------------------- | ------------------- | ------ |
| A   | Delete Attendance      | [ ] PASS / [ ] FAIL | **\_** |
| B   | Payroll Visibility     | [ ] PASS / [ ] FAIL | **\_** |
| C   | Export Filters         | [ ] PASS / [ ] FAIL | **\_** |
| D   | Edit Payroll Form      | [ ] PASS / [ ] FAIL | **\_** |
| E   | Add Appraisal Criteria | [ ] PASS / [ ] FAIL | **\_** |
| F   | Month Dropdown         | [ ] PASS / [ ] FAIL | **\_** |

**Pass Rate:** **\_** / 6 (\_\_\_\_%)

### Priority 1 Status:

- [ ] All 6 tests PASSED → Ready for production
- [ ] Some tests FAILED → Details below

**Failed Tests Details:**

```
Test A: _________________________________
Test B: _________________________________
Test C: _________________________________
Test D: _________________________________
Test E: _________________________________
Test F: _________________________________
```

---

## 🔍 DEBUGGING TIPS

### If Delete Attendance Still Fails:

1. Open DevTools → Network tab
2. Click delete button
3. Check request URL: Should be `/management/attendance/{id}/delete/`
4. Check response: Should be `{"status": "success"}`
5. If 404: Route mismatch, check urls_management.py

### If Payroll Visibility Still Wrong:

1. Check user's groups:

```python
# In Django shell:
from django.contrib.auth.models import User
user = User.objects.get(username='hangpt')
print(user.groups.all())  # Should include 'Manager'
print(user.is_superuser)  # Should be True or False
```

2. Check view logic matches expected behavior
3. Check if DoesNotExist exception is raised

### If Export Filters Don't Work:

1. Open DevTools → Network tab
2. Click "Xuất Excel"
3. Check URL: Should have `?month=10&year=2025&department=...`
4. Check server logs for filter parameters received
5. Verify department name vs department ID issue

### If Edit Form Empty:

1. Check edit_mode is True in context
2. Check payroll object is passed
3. Open DevTools → Console for JavaScript errors
4. Verify Django template renders correctly: View source → Search for `edit_mode`

### If Appraisal Criteria Fails:

1. Check form validation errors in messages
2. Check model field requirements:
   - name: required
   - category: must be valid choice
   - weight: 0-100
   - max_score: > 0
3. Check database constraints

---

## ✅ SIGN-OFF

**All Critical Fixes Verified:**

- [ ] YES - All 6 tests passed
- [ ] NO - See failed tests above

**Ready for Next Steps:**

- [ ] Proceed with remaining features (Filter JS, Sorting, User Management)
- [ ] Need additional fixes

**Tester Signature:** ****\*\*****\_\_\_****\*\*****  
**Date:** ****\*\*****\_\_\_****\*\*****

---

**Next Steps After This Test:**

1. If all pass → Implement remaining 3 features (Filter JS, Sorting, User Management)
2. If some fail → Developer fixes issues → Retest failed items
3. Final comprehensive test of ALL 13 items
