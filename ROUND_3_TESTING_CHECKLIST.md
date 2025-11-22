# 📋 ROUND 3 TESTING CHECKLIST - HRM MANAGEMENT PORTAL

**Ngày tạo:** 20/11/2025  
**Trạng thái:** 7 Bugs Fixed (Round 3)  
**Mục đích:** Kiểm tra lại các lỗi vừa được fix trong Round 3

---

## 🎯 TỔNG QUAN ROUND 3

### ✅ Đã sửa 7 lỗi mới phát hiện:

1. ✅ **update_employee_save TypeError** - View không nhận employee_id từ URL
2. ✅ **Delete Employee 405 Error** - Button dùng GET thay vì POST
3. ✅ **manage_attendance NoReverseMatch** - Template gọi delete_attendance sai cách
4. ✅ **confirm_payroll Missing URL** - Thiếu URL alias
5. ✅ **add_application_note Missing URL** - Thiếu URL alias
6. ✅ **delete_template_item Missing URL** - Thiếu URL alias
7. ✅ **add_appraisal_criteria Missing URL** - Thiếu URL alias

---

## 🧪 CHECKLIST CHI TIẾT - 7 TEST CASES

### 📌 TEST 1: Sửa Nhân Viên (update_employee_save)

**Bug đã fix:** TypeError - view không nhận employee_id từ URL parameter

**Thay đổi:**

```python
# TRƯỚC (management_views.py line 505):
def update_employee_save(request):
    employee_id = request.POST.get("employee_id")

# SAU:
def update_employee_save(request, employee_id):
    # Nhận employee_id từ URL parameter
```

**Test Steps:**

- [ ] 1. Navigate: `/management/employees/{id}/edit/` - OK
- [ ] 2. Form action: `{% url 'update_employee_save' employee.id %}` - OK
- [ ] 3. Sửa tên hoặc email - OK
- [ ] 4. Click **"Cập nhật"** - OK

**Expected Result:**

- ✅ POST thành công → `/management/employees/{id}/edit/save/` - OK
- ✅ KHÔNG có lỗi `TypeError: update_employee_save() got an unexpected keyword argument 'employee_id'` - OK
- ✅ Cập nhật dữ liệu thành công - OK
- ✅ Hiển thị message success - OK

**Verify:**

```bash
# Check server log:
INFO "POST /management/employees/173/edit/save/ HTTP/1.1" 302
```

---

### 📌 TEST 2: Xóa Nhân Viên từ trang Edit (Delete Employee Button)

**Bug đã fix:** 405 Method Not Allowed - Button dùng GET thay vì POST

**Thay đổi:**

```html
<!-- TRƯỚC (update_employee_template.html): -->
<a href="{% url 'delete_employee' employee.id %}" class="btn btn-danger">Xóa</a>

<!-- SAU: -->
<button
  type="button"
  class="btn btn-danger"
  onclick="deleteEmployee({{ employee.id }})"
>
  Xóa
</button>

<script>
  function deleteEmployee(employeeId) {
    if (confirm("Bạn có chắc chắn muốn xóa nhân viên này?")) {
      // Tạo POST form dynamically
      const form = document.createElement("form");
      form.method = "POST";
      form.action = "/management/employees/" + employeeId + "/delete/";
      // Add CSRF token
      form.submit();
    }
  }
</script>
```

**Test Steps:**

- [ ] 1. Navigate: `/management/employees/{id}/edit/` - OK
- [ ] 2. Click button **"Xóa"** (màu đỏ, bên phải) - OK
- [ ] 3. Confirm trong alert dialog - OK

**Expected Result:**

- ✅ KHÔNG có lỗi `405 Method Not Allowed (GET)` - OK
- ✅ POST request → `/management/employees/{id}/delete/` - OK
- ✅ Xóa thành công - OK
- ✅ Redirect về danh sách nhân viên - OK

**Verify:**

```bash
# Check server log:
INFO "POST /management/employees/174/delete/ HTTP/1.1" 302
# NOT:
WARNING "GET /management/employees/174/delete/ HTTP/1.1" 405
```

---

### 📌 TEST 3: Xóa Bảng Chấm Công (manage_attendance)

**Bug đã fix:** NoReverseMatch - Template gọi `{% url 'delete_attendance' %}` không có argument

**Thay đổi:**

```javascript
// TRƯỚC (manage_attendance.html):
url: "{% url 'delete_attendance' %}",
data: {
    id: id,
    ...
}

// SAU:
url: "/management/attendance/" + id + "/delete/",
data: {
    csrfmiddlewaretoken: "{{ csrf_token }}"
}
```

**Test Steps:**

- [ ] 1. Navigate: `/management/attendance/manage/` - OK
- [ ] 2. Trang phải load thành công (KHÔNG NoReverseMatch) - OK
- [ ] 3. Click button **"Xóa"** trên 1 bản ghi attendance - KHÔNG PHẢN HỒI
- [ ] 4. Confirm trong alert - KHÔNG PHẢN HỒI

**Expected Result:**

- ✅ Trang load thành công - OK
- ✅ KHÔNG có lỗi `NoReverseMatch: Reverse for 'delete_attendance' with no arguments not found` - OK
- ✅ AJAX POST thành công → `/management/attendance/{id}/delete/' - KHÔNG PHẢN HỒI
- ✅ Xóa thành công và reload trang - KHÔNG PHẢN HỒI

**Verify:**

```bash
# Check server log:
INFO "GET /management/attendance/manage/ HTTP/1.1" 200
INFO "POST /management/attendance/123/delete/ HTTP/1.1" 200
```

---

### 📌 TEST 4: Lưu Bảng Lương (confirm_payroll)

**Bug đã fix:** NoReverseMatch - Thiếu URL alias `confirm_payroll`

**Thay đổi:**

```python
# urls_management.py - Thêm vào backward compatibility section:
path('payroll/confirm/', management_views.confirm_payroll, name='confirm_payroll'),
```

**Test Steps:**

- [ ] 1. Navigate: `/management/payroll/calculate/` - OK
- [ ] 2. Chọn tháng/năm → Click **"Tính lương"** - OK
- [ ] 3. Sau khi hiển thị bảng lương → Click **"Lưu bảng lương"** - OK
- [ ] 4. Navigate: `/management/payroll/manage/` - OK

**Expected Result:**

- ✅ Trang calculate load thành công - OK
- ✅ Trang manage load thành công - OK
- ✅ KHÔNG có lỗi `NoReverseMatch: Reverse for 'confirm_payroll' not found` - OK
- ✅ Có thể click "Lưu bảng lương" và lưu thành công - OK

**Verify:**

```bash
# Check server log:
INFO "GET /management/payroll/calculate/ HTTP/1.1" 200
INFO "GET /management/payroll/manage/ HTTP/1.1" 200
# NO:
ERROR NoReverseMatch at /management/payroll/manage/
```

---

### 📌 TEST 5: Xem Chi Tiết Ứng Viên (add_application_note)

**Bug đã fix:** NoReverseMatch - Thiếu URL alias `add_application_note`

**Thay đổi:**

```python
# urls_management.py - Thêm vào backward compatibility section:
path('recruitment/applications/<int:application_id>/note/',
     management_views.add_application_note,
     name='add_application_note'),
```

**Test Steps:**

- [ ] 1. Navigate: `/management/recruitment/applications/` - OK
- [ ] 2. Click vào 1 ứng viên để xem chi tiết - LỖI
     NoReverseMatch at /management/recruitment/applications/21/
     Reverse for 'convert_to_employee' not found. 'convert_to_employee' is not a valid view function or pattern name.
- [ ] 3. Trang chi tiết phải load thành công - LỖI

**Expected Result:**

- ✅ Trang chi tiết load thành công
- ✅ KHÔNG có lỗi `NoReverseMatch: Reverse for 'add_application_note' not found`
- ✅ Có thể thêm ghi chú cho ứng viên

**Verify:**

```bash
# Check server log:
INFO "GET /management/recruitment/applications/21/ HTTP/1.1" 200
# NO:
ERROR NoReverseMatch at /management/recruitment/applications/21/
```

---

### 📌 TEST 6: Sửa Mẫu Quy Tắc Lương (delete_template_item)

**Bug đã fix:** NoReverseMatch - Thiếu URL alias `delete_template_item`

**Thay đổi:**

```python
# urls_management.py - Thêm vào backward compatibility section:
path('salary-rules/template-item/<int:item_id>/delete/',
     management_views.delete_template_item,
     name='delete_template_item'),
```

**Test Steps:**

- [ ] 1. Navigate: `/management/salary-rules/templates/` - OK
- [ ] 2. Click **"Sửa"** trên 1 mẫu template - OK
- [ ] 3. Trang edit phải load thành công - OK

**Expected Result:**

- ✅ Trang edit load thành công
- ✅ KHÔNG có lỗi `NoReverseMatch: Reverse for 'delete_template_item' not found`
- ✅ URL: `/management/salary-rules/templates/{id}/edit/`

**Verify:**

```bash
# Check server log:
INFO "GET /management/salary-rules/templates/2/edit/ HTTP/1.1" 200
# NO:
ERROR NoReverseMatch at /management/salary-rules/templates/2/edit/
```

---

### 📌 TEST 7: Xem Chi Tiết Kỳ Đánh Giá (add_appraisal_criteria)

**Bug đã fix:** NoReverseMatch - Thiếu URL alias `add_appraisal_criteria`

**Thay đổi:**

```python
# urls_management.py - Thêm vào backward compatibility section:
path('appraisal/periods/<int:period_id>/add-criteria/',
     management_views.add_appraisal_criteria,
     name='add_appraisal_criteria'),
```

**Test Steps:**

- [ ] 1. Navigate: `/management/appraisal/periods/` - OK
- [ ] 2. Click vào 1 kỳ đánh giá để xem chi tiết - OK
- [ ] 3. Trang chi tiết phải load thành công - OK

**Expected Result:**

- ✅ Trang chi tiết load thành công
- ✅ KHÔNG có lỗi `NoReverseMatch: Reverse for 'add_appraisal_criteria' not found`
- ✅ Có thể thêm tiêu chí đánh giá - LỖI

**Verify:**

```bash
# Check server log:
INFO "GET /management/appraisal/periods/1/ HTTP/1.1" 200
# NO:
ERROR NoReverseMatch at /management/appraisal/periods/1/
```

---

BUG MỚI:

1. Không thể thêm tiêu chí đánh giá, trong khi kết quả trả về là: INFO "POST /management/appraisal/periods/1/add-criteria/ HTTP/1.1" 200 36328

2. Khi đã tính lương rồi nhưng khi bấm Cập nhật thì form không hiển thị thông tin lương đã tính trước đó

3. Xem chi tiết bảng lương thì lương theo giờ ở 1 số bảng lương đang bị sai.
   Trường hợp tính sai:

- Lương cơ bản: 26,000,000 VNĐ
- Số ngày làm việc chuẩn: 21 ngày
- Lương theo giờ: 7,738,095,238,095,238 VNĐ

Trường hợp tính đúng:

- Lương cơ bản: 26,000,000 VNĐ
- Số ngày làm việc chuẩn: 22 ngày
- Lương theo giờ: 147,727 VNĐ

4. Ở trang Tính lương management/payroll/calculate/ thì đang hiển thị tháng bị sai. Không thể chọn được tháng 10,11,12. Đang hiển thị như sau: 1,2,3,4,5,6,7,8,9,1,0,1,1,1,2.

5. Không dùng được chức năng lọc ở quản lý bảng lương /management/payroll/manage/

6. Hiển thị bản ghi ở trang /management/payroll/manage/ cần chỉnh lại. Mặc định sẽ sắp xếp theo STT. Và theo tôi thấy sắp xếp theo Tháng/Năm đang bị sai. Khi tôi chọn sắp xêp theo Tháng/Năm thì kết quả là 1/2025 -> 10/2025 -> 11/2025 -> 8/2025 -> 9/2025. Nếu đúng sẽ là 1/2025 -> 8/2025 -> 9/2025 -> 10/2025 -> 11/2025.

7. Không hiển thị đầy đủ tất cả bảng lương của toàn bộ nhân sự. Hiện tại tôi đang đăng nhập bằng tài khoản hangpt (Giám đốc) thì chỉ xem được nhân sự của phòng ban Giám đốc thôi. Trong khi tôi xuất excel bảng lương tổng thì thấy được toàn bộ nhân sự.

8. Ở trang Quản lý Bảng lương tôi không thể xuất theo Tháng / Năm / Phòng ban / Trạng thái được.

9. Thêm bảng chấm công -> Cần để mặc định Ngày chấm công là ngày hiện tại

10. Cần thêm dữ liệu mặc định ở trang thêm mới nhân viên là:

- Nơi cấp: CỤC TRƯỞNG CỤC CẢNH SÁT QUẢN LÝ HÀNH CHÍNH VỀ TRẬT TỰ XÃ HỘI
- Quốc tịch: Việt Nam
- Dân tộc: Kinh
- Tôn giáo: Không

## 🔧 KIỂM TRA KỸ THUẬT

### Console Check (F12)

**Mở Developer Tools trong quá trình test:**

✅ **KHÔNG được có:**

- ❌ `NoReverseMatch`
- ❌ `405 Method Not Allowed`
- ❌ `TypeError`
- ❌ `404 Not Found`

### Server Log Check

**Quan sát terminal `python manage.py runserver`:**

✅ **Phải có:**

```
INFO "POST /management/employees/173/edit/save/ HTTP/1.1" 302
INFO "POST /management/employees/174/delete/ HTTP/1.1" 302
INFO "GET /management/attendance/manage/ HTTP/1.1" 200
INFO "POST /management/attendance/123/delete/ HTTP/1.1" 200
INFO "GET /management/payroll/manage/ HTTP/1.1" 200
INFO "GET /management/recruitment/applications/21/ HTTP/1.1" 200
INFO "GET /management/salary-rules/templates/2/edit/ HTTP/1.1" 200
INFO "GET /management/appraisal/periods/1/ HTTP/1.1" 200
```

❌ **KHÔNG được có:**

```
WARNING "GET /management/employees/174/delete/ HTTP/1.1" 405
ERROR NoReverseMatch at /management/attendance/manage/
ERROR TypeError: update_employee_save() got an unexpected keyword argument
```

---

## 📊 BÁO CÁO KẾT QUẢ

### 🎯 Success Criteria

**Round 3 hoàn thành khi:**

- [ ] 7/7 test cases PASS
- [ ] 0 lỗi NoReverseMatch
- [ ] 0 lỗi 405 Method Not Allowed
- [ ] 0 lỗi TypeError
- [ ] Tất cả trang load thành công

### 📋 Test Result Template

```
## ROUND 3 TEST RESULTS - [Ngày test]

### Test 1: Update Employee Save
- Status: [ ] PASS / [ ] FAIL
- Note:

### Test 2: Delete Employee Button
- Status: [ ] PASS / [ ] FAIL
- Note:

### Test 3: Manage Attendance Delete
- Status: [ ] PASS / [ ] FAIL
- Note:

### Test 4: Confirm Payroll
- Status: [ ] PASS / [ ] FAIL
- Note:

### Test 5: Application Detail
- Status: [ ] PASS / [ ] FAIL
- Note:

### Test 6: Edit Salary Rule Template
- Status: [ ] PASS / [ ] FAIL
- Note:

### Test 7: Appraisal Period Detail
- Status: [ ] PASS / [ ] FAIL
- Note:

---

**Overall Result:** [ ] PASS / [ ] FAIL
**Pass Rate:** __/7 (___%)
**Critical Issues:**
**Notes:**
```

---

## 📝 NOTES

### Files Modified (Round 3):

1. **app/management_views.py** (line 505)

   - Changed: `def update_employee_save(request)`
   - To: `def update_employee_save(request, employee_id)`

2. **app/templates/hod_template/update_employee_template.html**

   - Changed delete button from `<a href>` to `<button onclick>`
   - Added `deleteEmployee()` JavaScript function with POST form

3. **app/templates/hod_template/manage_attendance.html**

   - Changed AJAX URL from `{% url 'delete_attendance' %}`
   - To: hardcoded `/management/attendance/{id}/delete/`

4. **app/urls_management.py** (Backward compatibility section)
   - Added: `path('payroll/confirm/', ..., name='confirm_payroll')`
   - Added: `path('recruitment/applications/<int:application_id>/note/', ..., name='add_application_note')`
   - Added: `path('salary-rules/template-item/<int:item_id>/delete/', ..., name='delete_template_item')`
   - Added: `path('appraisal/periods/<int:period_id>/add-criteria/', ..., name='add_appraisal_criteria')`

### Known Limitations:

1. **Salary Component Edit Issue** - Vẫn còn vấn đề hiển thị data khi edit (cần kiểm tra thêm)

### Next Steps:

1. Test tất cả 7 cases trong checklist này
2. Nếu tất cả PASS → Chạy full regression test (all 40+ bugs)
3. Nếu có FAIL → Report lại để fix tiếp

---

**Document Version:** 3.0 (Round 3)  
**Created:** 20/11/2025  
**Total Bugs Fixed This Round:** 7  
**Cumulative Bugs Fixed:** 32 (25 previous + 7 new)  
**Status:** Ready for Testing ✅
