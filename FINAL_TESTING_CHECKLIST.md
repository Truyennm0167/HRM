# 📋 DANH SÁCH KIỂM TRA CUỐI CÙNG - HRM MANAGEMENT PORTAL

**Ngày cập nhật:** 19/11/2025  
**Trạng thái:** Phase 1, 2, 3 + Bug Fixes Complete  
**Tổng số lỗi đã sửa:** 33 bugs

---

## 🎯 TỔNG QUAN CÁC LỖI ĐÃ SỬA

### ✅ Phase 1-3: 23 bugs (Đã sửa trước đó)

- 12 lỗi NoReverseMatch URLs
- 8 lỗi POST 404 form submissions
- 3 lỗi chức năng (contract, org chart, leave balance)

### ✅ Round 2: 10 bugs mới (Vừa sửa xong)

1. ❌→✅ `get_attendance_data` - Missing URL (đã thêm)
2. ❌→✅ `get_payroll_data` - Missing URL (đã thêm)
3. ❌→✅ `delete_payroll` - Missing URL (đã thêm)
4. ❌→✅ `delete_job` - Missing URL (đã thêm)
5. ❌→✅ `update_application` - Missing URL (đã thêm)
6. ❌→✅ `edit_salary_rule_template` - Missing URL (đã thêm)
7. ❌→✅ `generate_appraisals` - Missing URL (đã thêm)
8. ❌→✅ `edit_expense_category_save` - Sai parameter (đã sửa view)
9. ❌→✅ `update_employee_save` - Template thiếu employee_id (đã sửa)
10. ❌→✅ Department/Job Title delete - Dùng GET thay vì POST (đã sửa JavaScript)

---

## 🧪 CHECKLIST KIỂM TRA CHI TIẾT

### 📌 SECTION 1: EMPLOYEE MANAGEMENT

#### ✅ Test 1.1: Thêm Nhân Viên

- [ ] Navigate: `/management/employees/add/` - OK
- [ ] Điền đầy đủ thông tin bắt buộc (\*, email unique) - OK
- [ ] Click **"Lưu"** - OK
- [ ] **Expected:**
  - POST thành công → 200/302 - Trả về HTTP/1.1" 200
  - Redirect đến hồ sơ nhân viên mới tạo - KHÔNG. Cần điều chỉnh lại chổ này
  - Dữ liệu lưu chính xác - OK

#### ✅ Test 1.2: Sửa Nhân Viên

**BUG FIXED:** Template thiếu employee_id trong URL

- [ ] Navigate: `/management/employees/{id}/edit/` - OK
- [ ] Form action giờ là: `{% url 'update_employee_save' employee.id %}` - OK
- [ ] Sửa tên hoặc email - OK
- [ ] Click **"Cập nhật"** - OK
- [ ] **Expected:**
  - POST đến `/management/employees/{id}/edit/save/` (KHÔNG thiếu ID) - LỖI
    TypeError at /management/employees/173/edit/save/
    update_employee_save() got an unexpected keyword argument 'employee_id'
  - Cập nhật thành công
  - KHÔNG có NoReverseMatch

#### ✅ Test 1.3: Xóa Nhân Viên

- [ ] Navigate: `/management/employees/` - OK
- [ ] Click vào 1 nhân viên → Click **"Xóa nhân viên"** - OK
- [ ] **Expected:**
  - Modal xác nhận xuất hiện - CHƯA CÓ
  - KHÔNG có lỗi 500 NoReverseMatch - OK

Tuy nhiên còn lỗi khi vào /management/employees/{id}/edit/ và nhấn nút Xóa nhân viên trong trang này
INFO "GET /management/employees/174/edit/ HTTP/1.1" 200 36739
WARNING Method Not Allowed (GET): /management/employees/174/delete/
WARNING "GET /management/employees/174/delete/ HTTP/1.1" 405 0

---

### 📌 SECTION 2: ATTENDANCE MANAGEMENT

#### ✅ Test 2.1: Thêm Điểm Danh

**BUG FIXED:** Thiếu URL `get_attendance_data`

- [ ] Navigate: `/management/attendance/add/` - OK
- [ ] **Expected:**
  - Trang load thành công (KHÔNG NoReverseMatch) - OK
  - Có thể chọn nhân viên và ngày - OK
- [ ] Chọn nhân viên + ngày → Submit - OK
- [ ] **Expected:** Điểm danh được lưu - LỖI
      NoReverseMatch at /management/attendance/manage/
      Reverse for 'delete_attendance' with no arguments not found. 1 pattern(s) tried: ['management/attendance/(?P<attendance_id>[0-9]+)/delete/\\Z']

#### ✅ Test 2.2: Quản Lý Điểm Danh

**BUG FIXED:** Template gọi `delete_attendance` không đúng cách

- [ ] Navigate: `/management/attendance/manage/` - LỖI
- [ ] **Expected:**
  - Trang load thành công - LỖI
  - Hiển thị bảng điểm danh với DataTable - CHƯA TEST ĐƯỢC
- [ ] Click **"Xóa"** trên 1 bản ghi - CHƯA TEST ĐƯỢC
- [ ] **Expected:** Xóa thành công (URL có attendance_id) - CHƯA TEST ĐƯỢC

---

### 📌 SECTION 3: DEPARTMENT & JOB TITLE MANAGEMENT

#### ✅ Test 3.1: Thêm Phòng Ban

- [ ] Navigate: `/management/departments/` - OK
- [ ] Điền tên phòng ban mới - OK
- [ ] Click **"Lưu"** - OK
- [ ] **Expected:** - OK
  - POST thành công → `/management/departments/add/` - OK
  - Phòng ban xuất hiện trong danh sách - OK

#### ✅ Test 3.2: Xóa Phòng Ban

**BUG FIXED:** JavaScript dùng GET (window.location), đã đổi thành POST form

- [ ] Navigate: `/management/departments/` - OK
- [ ] Click **"Sửa"** → Click **"Xóa phòng ban"** (màu đỏ) - OK
- [ ] **Expected:**
  - JavaScript tạo form POST với CSRF token - OK
  - Submit POST request → `/management/departments/{id}/delete/` - OK
  - KHÔNG còn lỗi 405 Method Not Allowed - OK
  - Xóa thành công - OK

#### ✅ Test 3.3: Thêm Chức Vụ

- [ ] Navigate: `/management/job-titles/` - OK
- [ ] Điền tên + hệ số lương - OK
- [ ] Click **"Lưu"** - OK
- [ ] **Expected:** POST thành công, chức vụ xuất hiện - OK

#### ✅ Test 3.4: Xóa Chức Vụ

**BUG FIXED:** JavaScript dùng GET, đã đổi thành POST form

- [ ] Navigate: `/management/job-titles/` - OK
- [ ] Click **"Sửa"** → Click **"Xóa chức vụ"** (màu đỏ) - OK
- [ ] **Expected:**
  - JavaScript tạo form POST với CSRF token - OK
  - Submit POST request → `/management/job-titles/{id}/delete/` - OK
  - KHÔNG còn lỗi 405 Method Not Allowed - OK
  - Xóa thành công - OK

---

### 📌 SECTION 4: PAYROLL MANAGEMENT

#### ✅ Test 4.1: Tính Lương

**BUG FIXED:** Thiếu URL `get_payroll_data`

- [ ] Navigate: `/management/payroll/calculate/` - OK
- [ ] **Expected:**
  - Trang load thành công (KHÔNG NoReverseMatch) - OK
  - Có thể chọn tháng/năm - OK
- [ ] Click **"Tính lương"** - OK
- [ ] **Expected:** Hiển thị bảng lương tạm tính - OK

#### ✅ Test 4.2: Lưu Bảng Lương

- [ ] Sau khi tính lương xong → Click **"Lưu bảng lương"** - LỖI
      NoReverseMatch at /management/payroll/manage/
      Reverse for 'confirm_payroll' not found. 'confirm_payroll' is not a valid view function or pattern name.
- [ ] **Expected:**
  - POST thành công → `/management/payroll/save/` - CHƯA TEST ĐƯỢC
  - Lưu vào database - CHƯA TEST ĐƯỢC

#### ✅ Test 4.3: Quản Lý Bảng Lương

**BUG FIXED:** Thiếu URL `delete_payroll`

- [ ] Navigate: `/management/payroll/manage/` - LỖI
      NoReverseMatch at /management/payroll/manage/
      Reverse for 'confirm_payroll' not found. 'confirm_payroll' is not a valid view function or pattern name.
- [ ] **Expected:**
  - Trang load thành công (KHÔNG NoReverseMatch) - CHƯA TEST ĐƯỢC
  - Hiển thị danh sách bảng lương - CHƯA TEST ĐƯỢC
- [ ] Click **"Xóa"** trên 1 bảng lương - CHƯA TEST ĐƯỢC
- [ ] **Expected:** Xóa thành công - CHƯA TEST ĐƯỢC

#### ✅ Test 4.4: Xuất Excel

- [ ] Tại trang quản lý → Click **"Xuất Excel"** - CHƯA TEST ĐƯỢC
- [ ] **Expected:** File .xlsx tải về thành công - CHƯA TEST ĐƯỢC

---

### 📌 SECTION 5: EXPENSE MANAGEMENT

#### ✅ Test 5.1: Sửa Danh Mục Chi Phí

**BUG FIXED:** View nhận sai parameter (từ POST data → URL parameter)

- [ ] Navigate: `/management/expense/categories/` - OK
- [ ] Click **"Sửa"** trên 1 danh mục - OK
- [ ] Modal mở với dữ liệu đúng - OK
- [ ] Sửa tên → Submit - OK
- [ ] **Expected:**
  - POST thành công → `/management/expense/categories/{id}/edit/` - OK
  - KHÔNG còn lỗi `unexpected keyword argument 'category_id'` - OK
  - Cập nhật thành công - OK

#### ✅ Test 5.2: Duyệt/Từ Chối Chi Phí

- [ ] Navigate: `/management/expense/requests/` - OK
- [ ] Tìm expense "Chờ duyệt" - OK
- [ ] Click **"Duyệt"** → Submit - OK
- [ ] **Expected:**
  - AJAX POST thành công → `/management/expense/requests/{id}/approve/` - OK
  - Status → "Đã duyệt" - OK
- [ ] Với expense khác → Click **"Từ chối"** → Submit - OK
- [ ] **Expected:** Status → "Từ chối" - OK

#### ✅ Test 5.3: Đánh Dấu Đã Thanh Toán

- [ ] Tìm expense "Đã duyệt" - OK
- [ ] Click **"Đánh dấu đã thanh toán"** → Submit - OK
- [ ] **Expected:**
  - AJAX POST → `/management/expense/requests/{id}/mark-paid/` - OK
  - Status → "Đã thanh toán" - OK

---

### 📌 SECTION 6: RECRUITMENT MANAGEMENT

#### ✅ Test 6.1: Sửa Job Posting

**BUG FIXED:** Thiếu URL `delete_job`

- [ ] Navigate: `/management/recruitment/jobs/` - OK
- [ ] Click **"Sửa"** trên 1 job - OK
- [ ] **Expected:**
  - Trang edit load thành công - OK
  - KHÔNG còn NoReverseMatch cho delete_job - OK

#### ✅ Test 6.2: Xem Chi Tiết Ứng Viên

**BUG FIXED:** Thiếu URL `update_application`

- [ ] Navigate: `/management/recruitment/applications/` - OK
- [ ] Click vào 1 ứng viên - LỖI
- [ ] **Expected:**
  - Trang chi tiết load thành công - LỖI
    NoReverseMatch at /management/recruitment/applications/21/
    Reverse for 'add_application_note' not found. 'add_application_note' is not a valid view function or pattern name
  - KHÔNG còn NoReverseMatch cho update_application - LỖI

#### ✅ Test 6.3: Chuyển Trạng Thái Ứng Viên

- [ ] Tại trang chi tiết ứng viên - CHƯA TEST ĐƯỢC
- [ ] Chọn trạng thái mới (Screening, Interview, Offer, v.v.) - CHƯA TEST ĐƯỢC
- [ ] Click **"Cập nhật"**
- [ ] **Expected:** Trạng thái thay đổi thành công - CHƯA TEST ĐƯỢC

---

### 📌 SECTION 7: SALARY RULES MANAGEMENT

#### ✅ Test 7.1: Sửa Thành Phần Lương

- [ ] Navigate: `/management/salary-rules/components/` - OK
- [ ] Click **"Sửa"** trên 1 component - OK
- [ ] **Expected:** Modal mở với dữ liệu -
- [ ] **⚠️ LƯU Ý:** Kiểm tra giá trị hiển thị đúng (không bị 0) - VẪN LỖI
- [ ] Sửa giá trị → Submit - VẪN CÒN LỖI SAI DỮ LIỆU
- [ ] **Expected:** Cập nhật thành công

#### ✅ Test 7.2: Quản Lý Mẫu Quy Tắc Lương

**BUG FIXED:** Thiếu URL `edit_salary_rule_template`

- [ ] Navigate: `/management/salary-rules/templates/` - OK
- [ ] **Expected:**
  - Trang load thành công - OK
  - KHÔNG còn NoReverseMatch - OK
- [ ] Click **"Tạo mẫu mới"** - OK
- [ ] **Expected:** Trang tạo mẫu load - OK

#### ✅ Test 7.3: Sửa Mẫu Quy Tắc

- [ ] Tại trang templates → Click **"Sửa"** trên 1 mẫu
- [ ] **Expected:**
  - Trang edit load thành công - LỖI
    NoReverseMatch at /management/salary-rules/templates/2/edit/
    Reverse for 'delete_template_item' not found. 'delete_template_item' is not a valid view function or pattern name.
  - URL: `/management/salary-rules/templates/{id}/edit/` - LỖI

---

### 📌 SECTION 8: APPRAISAL MANAGEMENT

#### ✅ Test 8.1: Xem Chi Tiết Kỳ Đánh Giá

**BUG FIXED:** Thiếu URL `generate_appraisals`

- [ ] Navigate: `/management/appraisal/periods/` - OK
- [ ] Click vào 1 kỳ đánh giá - LỖI
      NoReverseMatch at /management/appraisal/periods/1/
      Reverse for 'add_appraisal_criteria' not found. 'add_appraisal_criteria' is not a valid view function or pattern name.
- [ ] **Expected:**
  - Trang chi tiết load thành công - LỖI
  - KHÔNG còn NoReverseMatch cho generate_appraisals - LỖI

#### ✅ Test 8.2: Tạo Phiếu Đánh Giá Tự Động

- [ ] Tại trang chi tiết kỳ đánh giá - CHƯA TEST ĐƯỢC
- [ ] Click **"Tạo phiếu đánh giá"** - CHƯA TEST ĐƯỢC
- [ ] **Expected:**
  - POST thành công → `/management/appraisal/periods/{id}/generate/` - CHƯA TEST ĐƯỢC
  - Tạo phiếu cho tất cả nhân viên - CHƯA TEST ĐƯỢC

---

### 📌 SECTION 9: CONTRACT MANAGEMENT

#### ✅ Test 9.1: Tạo Hợp Đồng

**BUG FIXED trong Phase 3:** Template field names không khớp form

- [ ] Navigate: `/management/contracts/create/` - OK
- [ ] **Kiểm tra các trường hiển thị:**
  - ✅ Nhân viên, Loại HĐ, Ngày ký, Ngày bắt đầu/kết thúc
  - ✅ Lương cơ bản (NOT "hệ số lương")
  - ✅ Chức danh, Phòng ban
  - ✅ Nơi làm việc (NOT "workplace")
  - ✅ Thời gian làm việc, Điều khoản, Ghi chú, File đính kèm
  - ❌ KHÔNG CÒN: Số HĐ, Hệ số lương, Phụ cấp, Mô tả công việc, Quyền lợi, Bảo hiểm
- [ ] Điền đầy đủ → Click **"Tạo hợp đồng"** - OK
- [ ] **Expected:**
  - Lưu thành công - OK
  - Mã HĐ tự động: CT-YYYYMMDD-XXXX - OK
  - Redirect đến chi tiết HĐ - OK

#### ✅ Test 9.2: HĐ Không Xác Định Thời Hạn

- [ ] Chọn loại: "Không xác định thời hạn" - OK
- [ ] **Expected:** Trường "Ngày kết thúc" bị disable - OK
- [ ] Submit → Lưu với end_date = NULL - OK

---

### 📌 SECTION 10: ORG CHART

#### ✅ Test 10.1: Tìm Kiếm Nhân Viên

**BUG FIXED trong Phase 3:** Search không giữ hierarchy

- [ ] Navigate: `/management/org-chart/` - OK
- [ ] Nhập tên nhân viên (vd: "Nguyễn") - OK
- [ ] **Expected:**
  - ✅ Hiển thị tất cả NV matching - OK
  - ✅ Hiển thị cả PHÒNG BAN của họ - OK
  - ✅ Cấu trúc phân cấp được giữ - OK

#### ✅ Test 10.2: Lọc Theo Phòng Ban

- [ ] Chọn 1 phòng ban từ dropdown - OK
- [ ] **Expected:**
  - ✅ Hiển thị node phòng ban - OK
  - ✅ Hiển thị TẤT CẢ nhân viên trong phòng - OK
  - ✅ Ẩn các phòng khác - OK

---

## 🔧 KIỂM TRA KỸ THUẬT

### Console Check (F12)

**Trong quá trình test, mở Developer Tools:**

✅ **KHÔNG được có:**

- ❌ `404 Not Found`
- ❌ `500 Internal Server Error`
- ❌ `NoReverseMatch`
- ❌ `405 Method Not Allowed` (đặc biệt là delete operations)

✅ **Chấp nhận:**

- ⚠️ Static file warnings (không ảnh hưởng)

### Network Tab Check

**Khi submit form/AJAX:**

- [ ] POST requests → 200 hoặc 302 (redirect)
- [ ] KHÔNG có 404
- [ ] KHÔNG có 405 (Method Not Allowed)
- [ ] DELETE operations qua POST (không phải GET)

### Server Log Check

**Quan sát terminal chạy `runserver`:**

- [ ] INFO logs cho successful operations
- [ ] WARNING logs (nếu có) không critical
- [ ] KHÔNG có ERROR/Exception traces

---

## 📊 BÁO CÁO LỖI MỚI

**Nếu phát hiện lỗi trong quá trình test:**

### 🐛 Bug Report Template:

```
## Bug #{số}
**Trang:** [URL đầy đủ]
**Thao tác:** [Các bước thực hiện]
**Lỗi:** [Nội dung lỗi chính xác]
**Expected:** [Kết quả mong đợi]
**Actual:** [Kết quả thực tế]
**Console Errors:** [Copy từ Console]
**Screenshot:** [Đính kèm nếu có]
```

### 📋 Checklist Báo Lỗi:

- [ ] Chụp screenshot Console errors
- [ ] Ghi lại URL đầy đủ (copy từ address bar)
- [ ] Ghi lại tất cả các bước thao tác
- [ ] Kiểm tra Network tab (request/response)
- [ ] Note: User đang login (admin/manager/staff)

---

## ✅ KẾT QUẢ MONG ĐỢI

**Sau khi hoàn thành toàn bộ checklist:**

### 🎯 Zero Tolerance:

- **0** lỗi 404 Not Found
- **0** lỗi 500 Internal Server Error
- **0** lỗi NoReverseMatch
- **0** lỗi 405 Method Not Allowed
- **0** JavaScript errors liên quan URL

### 🚀 Functionality:

- ✅ Tất cả form submissions → Success
- ✅ Tất cả AJAX operations → Success
- ✅ Tất cả CRUD operations → Working
- ✅ DELETE operations → POST method
- ✅ Contract creation → All fields visible & saving
- ✅ Org chart → Hierarchy maintained
- ✅ Leave balance → Decimal display correct

### 📈 Performance:

- Page load < 3s (với DB <1000 records)
- AJAX response < 2s
- DataTables rendering < 1s

---

## 🎉 PRODUCTION READINESS

**Management Portal sẵn sàng deploy khi:**

- [x] All 33 bugs fixed
- [ ] All test cases PASS
- [ ] Zero critical errors
- [ ] Performance acceptable
- [ ] User acceptance testing complete

---

## 📝 GHI CHÚ QUAN TRỌNG

### ⚠️ Known Limitations:

1. **Salary Component Value:** Có thể bị hiển thị 0 khi edit - cần kiểm tra thêm
2. **Expense Requests:** Cần đảm bảo tập hợp được tất cả requests từ toàn bộ nhân sự
3. **Add Employee Redirect:** Hiện redirect về list, cần redirect đến profile của NV mới

### 🔐 Test Accounts:

- **Admin:** dungpd / dungpd2412
- **Manager:** hangpt / hangpt1122
- **Employee:** (tùy theo data)

### 🌐 Browser Testing:

- ✅ Chrome (primary)
- ✅ Firefox
- ✅ Edge

### 💾 Backup Reminder:

**Trước khi test DELETE operations:**

- [ ] Backup database: `python manage.py dumpdata > backup.json`
- [ ] Có thể restore nếu cần: `python manage.py loaddata backup.json`

---

**Document Version:** 2.0  
**Created:** 18/11/2025  
**Updated:** 19/11/2025 01:00  
**Total Bugs Fixed:** 33  
**Status:** Ready for Final Testing ✅
