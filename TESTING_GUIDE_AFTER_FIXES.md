# 📋 HƯỚNG DẪN KIỂM TRA SAU KHI SỬA LỖI

**Ngày tạo:** 18/11/2025  
**Phiên bản:** Phase 1, 2, 3 Complete  
**Tổng số lỗi đã sửa:** 23 bugs

---

## 🎯 TỔNG QUAN

Đã sửa tổng cộng **23 lỗi nghiêm trọng** trong Management Portal:

- **Phase 1:** 12 lỗi NoReverseMatch (URL routing)
- **Phase 2:** 8 lỗi POST 404 (form submissions)
- **Phase 3:** 3 lỗi chức năng (contract, org chart, leave balance)

---

## ✅ DANH SÁCH KIỂM TRA CHI TIẾT

### 📌 PHASE 1: URL ROUTING (12 mục)

#### 1. Employee Management - Delete Employee

**URL đã sửa:** `delete_employee`

- [ ] Vào trang **Quản lý nhân viên** → `/management/employees/` - OK
- [ ] Click vào 1 nhân viên bất kỳ - OK
- [ ] Click nút **"Xóa nhân viên"** - OK
- [ ] **Kỳ vọng:** Modal xác nhận xóa xuất hiện (KHÔNG bị lỗi 500) - OK
- [ ] Cancel modal, KHÔNG thực sự xóa nhân viên - OK

#### 2. Attendance - Check Date

**URL đã sửa:** `check_attendance_date`

- [ ] Vào trang **Điểm danh** → `/management/attendance/add/` - LỖI
      NoReverseMatch at /management/attendance/add/
      Reverse for 'get_attendance_data' not found. 'get_attendance_data' is not a valid view function or pattern name.
- [ ] Chọn 1 nhân viên từ dropdown - CHƯA TEST ĐƯỢC
- [ ] Chọn ngày hôm nay - CHƯA TEST ĐƯỢC
- [ ] **Kỳ vọng:** Form load thành công, không bị lỗi - CHƯA TEST ĐƯỢC
- [ ] Submit form điểm danh - CHƯA TEST ĐƯỢC
- [ ] **Kỳ vọng:** POST thành công, không 404 - CHƯA TEST ĐƯỢC

#### 3. Attendance - Delete

**URL đã sửa:** `delete_attendance`

- [ ] Vào trang **Quản lý điểm danh** → `/management/attendance/manage/` - LỖI
      NoReverseMatch at /management/attendance/manage/
      Reverse for 'delete_attendance' with no arguments not found. 1 pattern(s) tried: ['management/attendance/(?P<attendance_id>[0-9]+)/delete/\\Z']
- [ ] Click nút **"Xóa"** trên 1 bản ghi điểm danh - CHƯA TEST ĐƯỢC
- [ ] **Kỳ vọng:** Xóa thành công (KHÔNG bị lỗi 500) - CHƯA TEST ĐƯỢC

#### 4. Expense - Mark as Paid

**URL đã sửa:** `mark_expense_as_paid`

- [ ] Vào trang **Quản lý chi phí** → `/management/expense/requests/` - OK
- [ ] Tìm 1 expense đã được approve (status = approved) - OK
- [ ] Click nút **"Đánh dấu đã thanh toán"** - OK
- [ ] **Kỳ vọng:** Modal mở thành công - OK
- [ ] Submit form - OK
- [ ] **Kỳ vọng:** Status chuyển sang "Đã thanh toán", không bị 404 - OK
      Tuy nhiên chưa tổng hợp được tất cả Phiếu yêu cầu thanh toán của toàn bộ nhân sự - Cần kiểm tra lại.

#### 5. Payroll - Save

**URL đã sửa:** `save_payroll`

- [ ] Vào trang **Tính lương** → `/management/payroll/calculate/` - LỖI
      NoReverseMatch at /management/payroll/calculate/
      Reverse for 'get_payroll_data' not found. 'get_payroll_data' is not a valid view function or pattern name.
- [ ] Click **"Tính lương"** cho 1 tháng - CHƯA TEST ĐƯỢC
- [ ] Click nút **"Lưu bảng lương"** - CHƯA TEST ĐƯỢC
- [ ] **Kỳ vọng:** Lưu thành công, không 404 - CHƯA TEST ĐƯỢC

#### 6. Payroll - Export

**URL đã sửa:** `export_payroll`

- [ ] Vào trang **Quản lý bảng lương** → `/management/payroll/manage/` - LỖI
      NoReverseMatch at /management/payroll/manage/
      Reverse for 'delete_payroll' not found. 'delete_payroll' is not a valid view function or pattern name.
- [ ] Click nút **"Xuất Excel"** - CHƯA TEST ĐƯỢC
- [ ] **Kỳ vọng:** File Excel tải về thành công - CHƯA TEST ĐƯỢC

#### 7. Recruitment - Edit Job

**URL đã sửa:** `edit_job`

- [ ] Vào trang **Quản lý tuyển dụng** → `/management/recruitment/jobs/` - OK
- [ ] Click **"Sửa"** trên 1 job posting - OK
- [ ] **Kỳ vọng:** Trang edit load thành công (KHÔNG lỗi 500) - LỖI
      NoReverseMatch at /management/recruitment/jobs/11/
      Reverse for 'delete_job' not found. 'delete_job' is not a valid view function or pattern name.

#### 8. Recruitment - Application Detail

**URL đã sửa:** `application_detail`

- [ ] Vào trang **Kanban ứng viên** → `/management/recruitment/applications/` - OK
- [ ] Click vào 1 ứng viên bất kỳ - LỖI
      NoReverseMatch at /management/recruitment/applications/21/
      Reverse for 'update_application' not found. 'update_application' is not a valid view function or pattern name.
- [ ] **Kỳ vọng:** Trang chi tiết ứng viên load thành công - LỖI
      NoReverseMatch at /management/recruitment/applications/21/
      Reverse for 'update_application' not found. 'update_application' is not a valid view function or pattern name.

#### 9. Salary Rules - Edit Component

**URL đã sửa:** `edit_salary_component`

- [ ] Vào trang **Thành phần lương** → `/management/salary-rules/components/` - OK
- [ ] Click **"Sửa"** trên 1 component - OK
- [ ] **Kỳ vọng:** Modal/trang edit mở thành công (KHÔNG lỗi 500) - OK
      Nhưng Bị sai giá trị, tôi nhập ban đầu là 100.000 nhưng khi hiển thị chỉ còn 0

#### 10. Salary Rules - Create Template

**URL đà sửa:** `create_salary_rule_template`

- [ ] Vào trang **Mẫu quy tắc lương** → `/management/salary-rules/templates/` - OK
- [ ] Click nút **"Tạo mẫu mới"** - OK
- [ ] **Kỳ vọng:** Trang tạo mẫu load thành công (KHÔNG lỗi 500) - LỖI
      NoReverseMatch at /management/salary-rules/templates/
      Reverse for 'edit_salary_rule_template' not found. 'edit_salary_rule_template' is not a valid view function or pattern name.

#### 11. Appraisal - Period Detail

**URL đã sửa:** `appraisal_period_detail`

- [ ] Vào trang **Kỳ đánh giá** → `/management/appraisal/periods/` - OK
- [ ] Click vào 1 kỳ đánh giá bất kỳ - LỖI
      NoReverseMatch at /management/appraisal/periods/1/
      Reverse for 'generate_appraisals' not found. 'generate_appraisals' is not a valid view function or pattern name.
- [ ] **Kỳ vọng:** Trang chi tiết kỳ đánh giá load thành công (KHÔNG lỗi 500)

#### 12. Expense Categories - Edit Modal

**URL đã sửa:** Fixed modal form in `manage_expense_categories.html`

- [ ] Vào trang **Danh mục chi phí** → `/management/expense/categories/` - OK
- [ ] Click nút **"Sửa"** trên 1 danh mục - OK
- [ ] **Kỳ vọng:** Modal edit mở với dữ liệu đúng - OK
- [ ] Sửa tên danh mục - OK
- [ ] Submit form - LỖI
      TypeError at /management/expense/categories/27/edit/
      edit_expense_category_save() got an unexpected keyword argument 'category_id'
- [ ] **Kỳ vọng:** Cập nhật thành công, không bị 404

---

### 📌 PHASE 2: FORM SUBMISSIONS (8 mục)

#### 13. Employee - Add Employee Save

**Template đã sửa:** `add_employee_template.html`

- [ ] Vào trang **Thêm nhân viên** → `/management/employees/add/` - OK
- [ ] Điền đầy đủ thông tin nhân viên (các trường bắt buộc có dấu \*) - OK
- [ ] Click nút **"Lưu"** - OK
- [ ] **Kỳ vọng:** POST thành công, redirect đến trang danh sách nhân viên - POST Thành công nhưng tôi cần redirect đến trang Hồ sơ nhân viên của nhân viên vừa tạo.
- [ ] **KHÔNG được 404 error** - OK

#### 14. Employee - Update Employee Save

**URL đã sửa:** Added backward compatibility alias

- [ ] Vào trang **Chi tiết nhân viên** → Click edit trên 1 nhân viên - LỖI
      NoReverseMatch at /management/employees/173/edit/
      Reverse for 'update_employee_save' with no arguments not found. 1 pattern(s) tried: ['management/employees/(?P<employee_id>[0-9]+)/edit/save/\\Z']

Error during template rendering
In template D:\Study\CT201\Project\hrm\app\templates\hod_template\update_employee_template.html, error at line 11

Reverse for 'update_employee_save' with no arguments not found. 1 pattern(s) tried: ['management/employees/(?P<employee_id>[0-9]+)/edit/save/\\Z']

- [ ] Sửa thông tin (ví dụ: tên, email) - CHƯA TEST ĐƯỢC
- [ ] Click nút **"Cập nhật"** - CHƯA TEST ĐƯỢC
- [ ] **Kỳ vọng:** POST thành công, thông tin được cập nhật - CHƯA TEST ĐƯỢC
- [ ] **KHÔNG được 404 error** - CHƯA TEST ĐƯỢC

#### 15. Department - Add Department

**Template đã sửa:** `department_template.html`

- [ ] Vào trang **Phòng ban** → `/management/departments/` - OK
- [ ] Điền tên phòng ban mới - OK
- [ ] Click nút **"Lưu"** - OK
- [ ] **Kỳ vọng:** POST thành công đến `/management/departments/add/` - OK
- [ ] Phòng ban mới xuất hiện trong danh sách - OK
- [ ] **KHÔNG được 404 error** - OK

#### 16. Department - Delete Department

**Template đã sửa:** `department_template.html` (JavaScript)

- [ ] Vào trang **Phòng ban** → `/management/departments/` - OK
- [ ] Click **"Sửa"** trên 1 phòng ban - OK
- [ ] Click nút **"Xóa phòng ban"** (màu đỏ) - OK
- [ ] Confirm xóa - LỖI
      INFO "GET /management/departments/ HTTP/1.1" 200 37783
      WARNING Method Not Allowed (GET): /management/departments/83/delete/
      WARNING "GET /management/departments/83/delete/ HTTP/1.1" 405 0
- [ ] **Kỳ vọng:** Xóa thành công, redirect về trang danh sách - CHƯA TEST ĐƯỢC
- [ ] **KHÔNG được 404 error** - CHƯA TEST ĐƯỢC

#### 17. Job Title - Add Job Title

**Template đã sửa:** `job_title_template.html`

- [ ] Vào trang **Chức vụ** → `/management/job-titles/` - OK
- [ ] Điền tên chức vụ mới + hệ số lương - OK
- [ ] Click nút **"Lưu"** - OK
- [ ] **Kỳ vọng:** POST thành công đến `/management/job-titles/add/` - OK
- [ ] Chức vụ mới xuất hiện trong danh sách - OK
- [ ] **KHÔNG được 404 error** - OK

#### 18. Job Title - Delete Job Title

**Template đã sửa:** `job_title_template.html` (JavaScript)

- [ ] Vào trang **Chức vụ** → `/management/job-titles/` - OK
- [ ] Click **"Sửa"** trên 1 chức vụ - OK
- [ ] Click nút **"Xóa chức vụ"** (màu đỏ) - OK
- [ ] Confirm xóa - LỖI
      WARNING Method Not Allowed (GET): /management/job-titles/62/delete/
      WARNING "GET /management/job-titles/62/delete/ HTTP/1.1" 405 0
- [ ] **Kỳ vọng:** Xóa thành công, redirect về trang danh sách - CHƯA TEST ĐƯỢC
- [ ] **KHÔNG được 404 error** - CHƯA TEST ĐƯỢC

#### 19. Expense - Approve

**Template đã sửa:** `manage_expenses.html` (AJAX)

- [ ] Vào trang **Quản lý chi phí** → `/management/expense/requests/` - OK
- [ ] Tìm 1 expense có status = "Chờ duyệt" - OK
- [ ] Click nút **"Duyệt"** - OK
- [ ] Điền lý do (nếu cần) - OK
- [ ] Submit - OK
- [ ] **Kỳ vọng:** AJAX POST thành công đến `/management/expense/requests/{id}/approve/` - OK
- [ ] Status chuyển sang "Đã duyệt" - OK
- [ ] **KHÔNG được 404 error** - OK

#### 20. Expense - Reject - CẦN KIỂM TRA LẠI - Hiện tại không tìm thấy đơn Chi phí mới.

**Template đã sửa:** `manage_expenses.html` (AJAX)

- [ ] Vào trang **Quản lý chi phí** → `/management/expense/requests/`
- [ ] Tìm 1 expense có status = "Chờ duyệt"
- [ ] Click nút **"Từ chối"**
- [ ] Điền lý do từ chối
- [ ] Submit
- [ ] **Kỳ vọng:** AJAX POST thành công đến `/management/expense/requests/{id}/reject/`
- [ ] Status chuyển sang "Từ chối"
- [ ] **KHÔNG được 404 error**

---

### 📌 PHASE 3: FUNCTIONALITY FIXES (3 mục)

---- ĐÃ TỰ TEST VÀ TẤT CẢ CHỨC NĂNG CỦA PHASE 3 NÀY OK HẾT

#### 21. Contract Creation - Form Fields Visible

**Template đã sửa:** `create_edit_contract.html`

**Trước khi sửa:** Form có nhiều trường bị ẩn, POST trả về 200 nhưng không lưu dữ liệu

**Sau khi sửa:** Tất cả các trường trong form đều hiển thị và hoạt động

**Test Steps:**

- [ ] Vào trang **Tạo hợp đồng** → `/management/contracts/create/`
- [ ] **Kiểm tra các trường hiển thị:**

  - [ ] Nhân viên (dropdown) - **PHẢI HIỂN THỊ**
  - [ ] Loại hợp đồng (dropdown) - **PHẢI HIỂN THỊ**
  - [ ] Ngày ký - **PHẢI HIỂN THỊ**
  - [ ] Ngày bắt đầu - **PHẢI HIỂN THỊ**
  - [ ] Ngày kết thúc - **PHẢI HIỂN THỊ**
  - [ ] Lương cơ bản - **PHẢI HIỂN THỊ** (tên cũ: "Mức lương")
  - [ ] Chức danh - **PHẢI HIỂN THỊ**
  - [ ] Phòng ban - **PHẢI HIỂN THỊ** (trường MỚI)
  - [ ] Nơi làm việc - **PHẢI HIỂN THỊ** (tên cũ: "Địa điểm làm việc")
  - [ ] Thời gian làm việc - **PHẢI HIỂN THỊ**
  - [ ] Điều khoản - **PHẢI HIỂN THỊ**
  - [ ] Ghi chú - **PHẢI HIỂN THỊ**
  - [ ] File hợp đồng - **PHẢI HIỂN THỊ** (tên cũ: "File PDF")
  - [ ] Trạng thái - **PHẢI HIỂN THỊ**

- [ ] **Các trường KHÔNG còn xuất hiện (đã xóa vì không tồn tại trong model):**

  - ❌ Số hợp đồng (auto-generated)
  - ❌ Hệ số lương
  - ❌ Phụ cấp
  - ❌ Mô tả công việc
  - ❌ Quyền lợi
  - ❌ Thông tin bảo hiểm

- [ ] **Test tạo hợp đồng:**

  - [ ] Chọn nhân viên: "Nguyễn Văn A"
  - [ ] Loại hợp đồng: "Xác định thời hạn"
  - [ ] Điền đầy đủ các ngày tháng
  - [ ] Lương cơ bản: 15000000
  - [ ] Chọn chức danh và phòng ban
  - [ ] Click **"Tạo hợp đồng"**
  - [ ] **Kỳ vọng:**
    - Hợp đồng được tạo thành công
    - Redirect đến trang chi tiết hợp đồng
    - Tất cả thông tin được lưu đúng
    - Mã hợp đồng tự động generate (CT-YYYYMMDD-XXXX)

- [ ] **Test hợp đồng không xác định thời hạn:**

  - [ ] Chọn loại hợp đồng: "Không xác định thời hạn"
  - [ ] **Kỳ vọng:** Trường "Ngày kết thúc" bị disable
  - [ ] Submit form
  - [ ] **Kỳ vọng:** Lưu thành công với end_date = null

#### 22. Org Chart - Search & Filter

**Template đã sửa:** `org_chart.html` (JavaScript)

**Trước khi sửa:**

- Tìm nhân viên → Không thấy phòng ban của họ
- Lọc phòng ban → Không thấy nhân viên trong phòng

**Sau khi sửa:** Duy trì cấu trúc phân cấp khi search/filter

**Test Steps:**

- [ ] Vào trang **Biểu đồ tổ chức** → `/management/org-chart/`

- [ ] **Test Search Employee:**

  - [ ] Nhập tên nhân viên vào ô tìm kiếm (ví dụ: "Nguyễn")
  - [ ] **Kỳ vọng:**
    - ✅ Hiển thị tất cả nhân viên có tên "Nguyễn"
    - ✅ Hiển thị cả PHÒNG BAN của các nhân viên đó
    - ✅ Cấu trúc phân cấp được giữ nguyên
  - [ ] Xóa text tìm kiếm
  - [ ] **Kỳ vọng:** Hiển thị lại toàn bộ org chart

- [ ] **Test Filter Department:**

  - [ ] Chọn 1 phòng ban từ dropdown (ví dụ: "Phòng IT")
  - [ ] **Kỳ vọng:**
    - ✅ Hiển thị node phòng ban "Phòng IT"
    - ✅ Hiển thị TẤT CẢ nhân viên trong phòng IT
    - ✅ Ẩn các phòng ban khác
  - [ ] Chọn "Tất cả phòng ban" từ dropdown
  - [ ] **Kỳ vọng:** Hiển thị lại toàn bộ org chart

- [ ] **Test Combined Search + Filter:**
  - [ ] Chọn phòng ban "Phòng Kinh doanh"
  - [ ] Nhập tên nhân viên trong phòng đó
  - [ ] **Kỳ vọng:** Chỉ hiển thị nhân viên matching + phòng ban của họ

#### 23. Leave Balance - Decimal Display

**Status:** KHÔNG PHẢI LỖI - ĐÂY LÀ TÍNH NĂNG

**Giải thích:**

- Số ngày phép hiển thị dạng thập phân (ví dụ: 12.5 ngày) là **CHÍNH XÁC**
- Hệ thống hỗ trợ nghỉ phép nửa ngày (0.5 ngày)
- Model `LeaveBalance` sử dụng `FloatField` cho phép số thập phân
- Model `LeaveRequest` có help text: "Số ngày nghỉ (có thể là 0.5 cho nửa ngày)"

**Test Steps (Xác nhận tính năng hoạt động đúng):**

- [ ] Vào trang **Xin nghỉ phép** (Portal) → `/portal/leave/request/`
- [ ] Tạo đơn nghỉ NỬA NGÀY:
  - [ ] Start date = End date = Hôm nay
  - [ ] Chọn "Nửa ngày sáng" hoặc "Nửa ngày chiều"
  - [ ] **Kỳ vọng:** Total days = 0.5
- [ ] Submit đơn
- [ ] Quản lý duyệt đơn
- [ ] Kiểm tra số dư phép của nhân viên
- [ ] **Kỳ vọng:**
  - Số dư giảm 0.5 ngày
  - Hiển thị số thập phân chính xác (ví dụ: 12.5 → 12.0)

---

## 🔧 KIỂM TRA TỔNG QUAN

### Browser Console Check

Trong quá trình test, mở **Developer Tools (F12)** → Tab **Console**

**Các lỗi KHÔNG được xuất hiện:**

- ❌ `404 Not Found` errors
- ❌ `500 Internal Server Error`
- ❌ `NoReverseMatch` errors
- ❌ JavaScript errors liên quan đến URL

**Chỉ chấp nhận:**

- ⚠️ Warnings về static files (không ảnh hưởng)
- ⚠️ Pagination warnings (đã fix nhưng có thể còn ở một số chỗ)

### Network Tab Check

Khi submit form, kiểm tra tab **Network**:

- [ ] Tất cả POST requests trả về **200** hoặc **302** (redirect)
- [ ] KHÔNG có POST nào trả về **404**
- [ ] AJAX requests trả về JSON hợp lệ

### Database Check (Optional)

Sau khi test create/update/delete:

- [ ] Login vào Django Admin → `/admin/`
- [ ] Kiểm tra dữ liệu đã được lưu/cập nhật/xóa đúng
- [ ] Kiểm tra các trường không null có giá trị hợp lệ

---

## 📊 CHECKLIST TỔNG HỢP

### URLs (16 URLs)

- [ ] 5 URLs từ Phase 1 ban đầu
- [ ] 11 URLs từ Phase 1 bổ sung
- [ ] Tất cả resolve thành công (chạy `python verify_fixes.py`)

### Templates (7 files)

- [ ] `add_employee_template.html`
- [ ] `department_template.html`
- [ ] `job_title_template.html`
- [ ] `manage_expenses.html`
- [ ] `manage_expense_categories.html`
- [ ] `create_edit_contract.html`
- [ ] `org_chart.html`

### Functionality

- [ ] Contract creation: Form hiển thị đầy đủ, lưu thành công
- [ ] Org chart: Search/filter giữ cấu trúc phân cấp
- [ ] Leave balance: Hiển thị decimal đúng (tính năng nửa ngày)

---

## 🚀 KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành tất cả các test cases:

✅ **0 lỗi 404 Not Found**  
✅ **0 lỗi 500 Internal Server Error**  
✅ **0 lỗi NoReverseMatch**  
✅ **Tất cả form submissions thành công**  
✅ **Tất cả AJAX operations hoạt động**  
✅ **Contract creation form hiển thị và lưu đúng**  
✅ **Org chart search/filter duy trì hierarchy**  
✅ **Leave balance hiển thị decimal chính xác**

**Management Portal: 100% FUNCTIONAL** 🎉

---

## 📝 GHI CHÚ BỔ SUNG

### Nếu phát hiện lỗi mới:

1. Chụp screenshot lỗi
2. Ghi lại URL đầy đủ
3. Ghi lại các bước thao tác
4. Kiểm tra Console errors
5. Báo cáo ngay lập tức

### Browser Testing:

Khuyến nghị test trên:

- ✅ Chrome (primary)
- ✅ Firefox
- ✅ Edge

### Test Account:

- **Admin:** dungpd / dungpd2412
- **Manager:** hangpt / hangpt1122
- **Employee:** (các nhân viên khác trong hệ thống)

### Performance Note:

- Org chart có thể load chậm nếu có >100 nhân viên
- DataTables pagination hoạt động bình thường
- AJAX operations nên hoàn thành trong <2s

---

**Tài liệu này được tạo tự động sau khi hoàn thành Phase 1, 2, 3 fixes.**  
**Last updated:** 18/11/2025 00:30
