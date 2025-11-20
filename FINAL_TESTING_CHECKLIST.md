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

- [ ] Navigate: `/management/employees/add/`
- [ ] Điền đầy đủ thông tin bắt buộc (\*, email unique)
- [ ] Click **"Lưu"**
- [ ] **Expected:**
  - POST thành công → 200/302
  - Redirect đến hồ sơ nhân viên mới tạo
  - Dữ liệu lưu chính xác

#### ✅ Test 1.2: Sửa Nhân Viên

**BUG FIXED:** Template thiếu employee_id trong URL

- [ ] Navigate: `/management/employees/{id}/edit/`
- [ ] Form action giờ là: `{% url 'update_employee_save' employee.id %}`
- [ ] Sửa tên hoặc email
- [ ] Click **"Cập nhật"**
- [ ] **Expected:**
  - POST đến `/management/employees/{id}/edit/save/` (KHÔNG thiếu ID)
  - Cập nhật thành công
  - KHÔNG có NoReverseMatch

#### ✅ Test 1.3: Xóa Nhân Viên

- [ ] Navigate: `/management/employees/`
- [ ] Click vào 1 nhân viên → Click **"Xóa nhân viên"**
- [ ] **Expected:**
  - Modal xác nhận xuất hiện
  - KHÔNG có lỗi 500 NoReverseMatch

---

### 📌 SECTION 2: ATTENDANCE MANAGEMENT

#### ✅ Test 2.1: Thêm Điểm Danh

**BUG FIXED:** Thiếu URL `get_attendance_data`

- [ ] Navigate: `/management/attendance/add/`
- [ ] **Expected:**
  - Trang load thành công (KHÔNG NoReverseMatch)
  - Có thể chọn nhân viên và ngày
- [ ] Chọn nhân viên + ngày → Submit
- [ ] **Expected:** Điểm danh được lưu

#### ✅ Test 2.2: Quản Lý Điểm Danh

**BUG FIXED:** Template gọi `delete_attendance` không đúng cách

- [ ] Navigate: `/management/attendance/manage/`
- [ ] **Expected:**
  - Trang load thành công
  - Hiển thị bảng điểm danh với DataTable
- [ ] Click **"Xóa"** trên 1 bản ghi
- [ ] **Expected:** Xóa thành công (URL có attendance_id)

---

### 📌 SECTION 3: DEPARTMENT & JOB TITLE MANAGEMENT

#### ✅ Test 3.1: Thêm Phòng Ban

- [ ] Navigate: `/management/departments/`
- [ ] Điền tên phòng ban mới
- [ ] Click **"Lưu"**
- [ ] **Expected:**
  - POST thành công → `/management/departments/add/`
  - Phòng ban xuất hiện trong danh sách

#### ✅ Test 3.2: Xóa Phòng Ban

**BUG FIXED:** JavaScript dùng GET (window.location), đã đổi thành POST form

- [ ] Navigate: `/management/departments/`
- [ ] Click **"Sửa"** → Click **"Xóa phòng ban"** (màu đỏ)
- [ ] **Expected:**
  - JavaScript tạo form POST với CSRF token
  - Submit POST request → `/management/departments/{id}/delete/`
  - KHÔNG còn lỗi 405 Method Not Allowed
  - Xóa thành công

#### ✅ Test 3.3: Thêm Chức Vụ

- [ ] Navigate: `/management/job-titles/`
- [ ] Điền tên + hệ số lương
- [ ] Click **"Lưu"**
- [ ] **Expected:** POST thành công, chức vụ xuất hiện

#### ✅ Test 3.4: Xóa Chức Vụ

**BUG FIXED:** JavaScript dùng GET, đã đổi thành POST form

- [ ] Navigate: `/management/job-titles/`
- [ ] Click **"Sửa"** → Click **"Xóa chức vụ"** (màu đỏ)
- [ ] **Expected:**
  - JavaScript tạo form POST với CSRF token
  - Submit POST request → `/management/job-titles/{id}/delete/`
  - KHÔNG còn lỗi 405 Method Not Allowed
  - Xóa thành công

---

### 📌 SECTION 4: PAYROLL MANAGEMENT

#### ✅ Test 4.1: Tính Lương

**BUG FIXED:** Thiếu URL `get_payroll_data`

- [ ] Navigate: `/management/payroll/calculate/`
- [ ] **Expected:**
  - Trang load thành công (KHÔNG NoReverseMatch)
  - Có thể chọn tháng/năm
- [ ] Click **"Tính lương"**
- [ ] **Expected:** Hiển thị bảng lương tạm tính

#### ✅ Test 4.2: Lưu Bảng Lương

- [ ] Sau khi tính lương xong → Click **"Lưu bảng lương"**
- [ ] **Expected:**
  - POST thành công → `/management/payroll/save/`
  - Lưu vào database

#### ✅ Test 4.3: Quản Lý Bảng Lương

**BUG FIXED:** Thiếu URL `delete_payroll`

- [ ] Navigate: `/management/payroll/manage/`
- [ ] **Expected:**
  - Trang load thành công (KHÔNG NoReverseMatch)
  - Hiển thị danh sách bảng lương
- [ ] Click **"Xóa"** trên 1 bảng lương
- [ ] **Expected:** Xóa thành công

#### ✅ Test 4.4: Xuất Excel

- [ ] Tại trang quản lý → Click **"Xuất Excel"**
- [ ] **Expected:** File .xlsx tải về thành công

---

### 📌 SECTION 5: EXPENSE MANAGEMENT

#### ✅ Test 5.1: Sửa Danh Mục Chi Phí

**BUG FIXED:** View nhận sai parameter (từ POST data → URL parameter)

- [ ] Navigate: `/management/expense/categories/`
- [ ] Click **"Sửa"** trên 1 danh mục
- [ ] Modal mở với dữ liệu đúng
- [ ] Sửa tên → Submit
- [ ] **Expected:**
  - POST thành công → `/management/expense/categories/{id}/edit/`
  - KHÔNG còn lỗi `unexpected keyword argument 'category_id'`
  - Cập nhật thành công

#### ✅ Test 5.2: Duyệt/Từ Chối Chi Phí

- [ ] Navigate: `/management/expense/requests/`
- [ ] Tìm expense "Chờ duyệt"
- [ ] Click **"Duyệt"** → Submit
- [ ] **Expected:**
  - AJAX POST thành công → `/management/expense/requests/{id}/approve/`
  - Status → "Đã duyệt"
- [ ] Với expense khác → Click **"Từ chối"** → Submit
- [ ] **Expected:** Status → "Từ chối"

#### ✅ Test 5.3: Đánh Dấu Đã Thanh Toán

- [ ] Tìm expense "Đã duyệt"
- [ ] Click **"Đánh dấu đã thanh toán"** → Submit
- [ ] **Expected:**
  - AJAX POST → `/management/expense/requests/{id}/mark-paid/`
  - Status → "Đã thanh toán"

---

### 📌 SECTION 6: RECRUITMENT MANAGEMENT

#### ✅ Test 6.1: Sửa Job Posting

**BUG FIXED:** Thiếu URL `delete_job`

- [ ] Navigate: `/management/recruitment/jobs/`
- [ ] Click **"Sửa"** trên 1 job
- [ ] **Expected:**
  - Trang edit load thành công
  - KHÔNG còn NoReverseMatch cho delete_job

#### ✅ Test 6.2: Xem Chi Tiết Ứng Viên

**BUG FIXED:** Thiếu URL `update_application`

- [ ] Navigate: `/management/recruitment/applications/`
- [ ] Click vào 1 ứng viên
- [ ] **Expected:**
  - Trang chi tiết load thành công
  - KHÔNG còn NoReverseMatch cho update_application

#### ✅ Test 6.3: Chuyển Trạng Thái Ứng Viên

- [ ] Tại trang chi tiết ứng viên
- [ ] Chọn trạng thái mới (Screening, Interview, Offer, v.v.)
- [ ] Click **"Cập nhật"**
- [ ] **Expected:** Trạng thái thay đổi thành công

---

### 📌 SECTION 7: SALARY RULES MANAGEMENT

#### ✅ Test 7.1: Sửa Thành Phần Lương

- [ ] Navigate: `/management/salary-rules/components/`
- [ ] Click **"Sửa"** trên 1 component
- [ ] **Expected:** Modal mở với dữ liệu
- [ ] **⚠️ LƯU Ý:** Kiểm tra giá trị hiển thị đúng (không bị 0)
- [ ] Sửa giá trị → Submit
- [ ] **Expected:** Cập nhật thành công

#### ✅ Test 7.2: Quản Lý Mẫu Quy Tắc Lương

**BUG FIXED:** Thiếu URL `edit_salary_rule_template`

- [ ] Navigate: `/management/salary-rules/templates/`
- [ ] **Expected:**
  - Trang load thành công
  - KHÔNG còn NoReverseMatch
- [ ] Click **"Tạo mẫu mới"**
- [ ] **Expected:** Trang tạo mẫu load OK

#### ✅ Test 7.3: Sửa Mẫu Quy Tắc

- [ ] Tại trang templates → Click **"Sửa"** trên 1 mẫu
- [ ] **Expected:**
  - Trang edit load thành công
  - URL: `/management/salary-rules/templates/{id}/edit/`

---

### 📌 SECTION 8: APPRAISAL MANAGEMENT

#### ✅ Test 8.1: Xem Chi Tiết Kỳ Đánh Giá

**BUG FIXED:** Thiếu URL `generate_appraisals`

- [ ] Navigate: `/management/appraisal/periods/`
- [ ] Click vào 1 kỳ đánh giá
- [ ] **Expected:**
  - Trang chi tiết load thành công
  - KHÔNG còn NoReverseMatch cho generate_appraisals

#### ✅ Test 8.2: Tạo Phiếu Đánh Giá Tự Động

- [ ] Tại trang chi tiết kỳ đánh giá
- [ ] Click **"Tạo phiếu đánh giá"**
- [ ] **Expected:**
  - POST thành công → `/management/appraisal/periods/{id}/generate/`
  - Tạo phiếu cho tất cả nhân viên

---

### 📌 SECTION 9: CONTRACT MANAGEMENT

#### ✅ Test 9.1: Tạo Hợp Đồng

**BUG FIXED trong Phase 3:** Template field names không khớp form

- [ ] Navigate: `/management/contracts/create/`
- [ ] **Kiểm tra các trường hiển thị:**
  - ✅ Nhân viên, Loại HĐ, Ngày ký, Ngày bắt đầu/kết thúc
  - ✅ Lương cơ bản (NOT "hệ số lương")
  - ✅ Chức danh, Phòng ban
  - ✅ Nơi làm việc (NOT "workplace")
  - ✅ Thời gian làm việc, Điều khoản, Ghi chú, File đính kèm
  - ❌ KHÔNG CÒN: Số HĐ, Hệ số lương, Phụ cấp, Mô tả công việc, Quyền lợi, Bảo hiểm
- [ ] Điền đầy đủ → Click **"Tạo hợp đồng"**
- [ ] **Expected:**
  - Lưu thành công
  - Mã HĐ tự động: CT-YYYYMMDD-XXXX
  - Redirect đến chi tiết HĐ

#### ✅ Test 9.2: HĐ Không Xác Định Thời Hạn

- [ ] Chọn loại: "Không xác định thời hạn"
- [ ] **Expected:** Trường "Ngày kết thúc" bị disable
- [ ] Submit → Lưu với end_date = NULL

---

### 📌 SECTION 10: ORG CHART

#### ✅ Test 10.1: Tìm Kiếm Nhân Viên

**BUG FIXED trong Phase 3:** Search không giữ hierarchy

- [ ] Navigate: `/management/org-chart/`
- [ ] Nhập tên nhân viên (vd: "Nguyễn")
- [ ] **Expected:**
  - ✅ Hiển thị tất cả NV matching
  - ✅ Hiển thị cả PHÒNG BAN của họ
  - ✅ Cấu trúc phân cấp được giữ

#### ✅ Test 10.2: Lọc Theo Phòng Ban

- [ ] Chọn 1 phòng ban từ dropdown
- [ ] **Expected:**
  - ✅ Hiển thị node phòng ban
  - ✅ Hiển thị TẤT CẢ nhân viên trong phòng
  - ✅ Ẩn các phòng khác

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
