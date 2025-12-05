# 🧪 HƯỚNG DẪN TEST ROUND 4 - CHI TIẾT

**Ngày tạo:** 20/11/2025  
**Phiên bản:** 4.0  
**Trạng thái:** 10/13 bugs đã fix

---

## 📋 DANH SÁCH CÁC CHỨC NĂNG CẦN TEST

### ✅ NHÓM 1: URL & ROUTING (2 tests)

- Test 1: convert_to_employee URL
- Test 2: Delete attendance AJAX

### ✅ NHÓM 2: TÍNH TOÁN & LOGIC (1 test)

- Test 3: Hourly wage calculation

### ✅ NHÓM 3: TEMPLATE & UI (2 tests)

- Test 4: Month dropdown
- Test 5: Employee form defaults

### ✅ NHÓM 4: PERMISSIONS & VISIBILITY (1 test)

- Test 6: Payroll visibility

### ✅ NHÓM 5: FILTERS & EXPORT (1 test)

- Test 7: Export with filters

### ✅ NHÓM 6: FORM DEFAULTS (2 tests)

- Test 8: Attendance date default
- Test 9: Edit payroll form data

### ✅ NHÓM 7: FORM SUBMISSION (1 test)

- Test 10: Add appraisal criteria

---

## 🔍 CHI TIẾT TỪNG TEST CASE

---

### TEST 1: convert_to_employee URL ✅

**Mục đích:** Kiểm tra URL alias đã được thêm đúng chưa

**Trước khi fix:**

```
NoReverseMatch at /management/recruitment/applications/1/
Reverse for 'convert_to_employee' not found.
```

**File đã fix:** `app/urls_management.py` line 207

**Các bước test:**

1. **Đăng nhập** với tài khoản HR

   - Username: `admin` / Password: `admin123`

2. **Navigate đến trang ứng tuyển:**

   ```
   http://127.0.0.1:8000/management/recruitment/applications/
   ```

3. **Click vào một application** bất kỳ để xem chi tiết

4. **Kiểm tra page load:**
   - ✅ Page load thành công (không có NoReverseMatch error)
   - ✅ Có button "Chuyển thành nhân viên" hoặc tương tự
   - ✅ Console không có error

**Expected Result:**

```
✅ Page loads successfully
✅ URL: /management/recruitment/applications/{id}/
✅ No 404 or NoReverseMatch errors
```

**Actual Result:**

```
[X] PASS
[ ] FAIL - Lỗi: _______________________
```

---

### TEST 2: Delete Attendance Button ✅

**Mục đích:** Kiểm tra nút xóa attendance đã hoạt động chưa

**Trước khi fix:**

- Click button "Xóa" → Không có phản hồi
- AJAX request không gửi đi

**File đã fix:** `app/management_views.py` line 658

**Các bước test:**

1. **Đăng nhập** với tài khoản có quyền quản lý attendance

2. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/attendance/manage/
   ```

3. **Tìm một record attendance** để xóa

4. **Click nút "Xóa"**

5. **Confirm trong popup** (nếu có)

6. **Kiểm tra kết quả:**
   - ✅ Record bị xóa khỏi table
   - ✅ Page reload hoặc table refresh
   - ✅ Success message hiện ra
   - ✅ Database không còn record đó

**Verify trong database:**

```sql
-- Check trước khi xóa
SELECT * FROM app_attendance WHERE id = {attendance_id};

-- Check sau khi xóa
SELECT * FROM app_attendance WHERE id = {attendance_id};
-- Should return 0 rows
```

**Expected Result:**

```
✅ Attendance record deleted
✅ Success message shown
✅ Table updated
✅ Record removed from database
```

**Actual Result:**

```
[ ] PASS
[X] FAIL - Lỗi: Nút Xóa không phản hồi
```

---

### TEST 3: Hourly Wage Calculation ✅ **[CRITICAL]**

**Mục đích:** Kiểm tra công thức tính lương theo giờ

**Trước khi fix:**

```
Lương cơ bản: 26,000,000 VNĐ
Hệ số: 4.5
Ngày công chuẩn: 21 ngày
Kết quả sai: 7,738,095,238,095,238 VNĐ ❌
```

**Sau khi fix:**

```python
hourly_rate = (base_salary * coefficient) / (standard_working_days * 8)
hourly_rate = (26,000,000 * 4.5) / (21 * 8)
hourly_rate = 117,000,000 / 168
hourly_rate = 696,428.57 VNĐ ✅
```

**File đã fix:** `app/management_views.py` line 774-783

**Các bước test:**

1. **Đăng nhập** với tài khoản HR

2. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/payroll/calculate/
   ```

3. **Chọn thông tin:**

   - **Nhân viên:** Chọn nhân viên có lương 26,000,000 VNĐ
   - **Tháng:** 10
   - **Năm:** 2025
   - **Ngày công chuẩn:** 21

4. **Click "Tính lương"**

5. **Kiểm tra các giá trị:**

   | Field              | Expected Value   | Actual Value       |
   | ------------------ | ---------------- | ------------------ |
   | Lương cơ bản       | 26,000,000       | \***\*\_\*\***     |
   | Hệ số chức vụ      | 4.5              | \***\*\_\*\***     |
   | Ngày công chuẩn    | 21               | \***\*\_\*\***     |
   | **Lương theo giờ** | **~696,429 VNĐ** | **\*\***\_**\*\*** |
   | Tổng lương         | 117,000,000      | \***\*\_\*\***     |

**Test với nhiều giá trị:**

```python
# Test Case 1: 21 ngày
hourly_rate = (26,000,000 * 4.5) / (21 * 8) = 696,428.57 VNĐ ✅

# Test Case 2: 22 ngày
hourly_rate = (26,000,000 * 4.5) / (22 * 8) = 664,772.73 VNĐ ✅

# Test Case 3: 20 ngày
hourly_rate = (26,000,000 * 4.5) / (20 * 8) = 731,250 VNĐ ✅

# Test Case 4: 0 ngày (edge case)
hourly_rate = 0 VNĐ (không chia cho 0) ✅
```

**Expected Result:**

```
✅ Hourly rate calculated correctly
✅ No division by zero error
✅ Value in reasonable range (500k - 1M VNĐ)
✅ No trillion VNĐ values
```

**Actual Result:**

```
[X] PASS - Giá trị: ___________ VNĐ
[ ] FAIL - Lỗi: _______________________
```

---

### TEST 4: Month Dropdown ✅

**Mục đích:** Kiểm tra dropdown tháng hiển thị đúng 1-12

**Trước khi fix:**

```html
<!-- Dropdown showed: 1,2,3,4,5,6,7,8,9,1,0,1,1,1,2 -->
```

**Sau khi fix:**

```html
<!-- Dropdown shows: 1,2,3,4,5,6,7,8,9,10,11,12 -->
```

**File đã fix:** `app/templates/hod_template/calculate_payroll.html` lines 29-45

**Các bước test:**

1. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/payroll/calculate/
   ```

2. **Click vào dropdown "Tháng"**

3. **Kiểm tra options:**

   - ✅ Option 1: value="1", text="1"
   - ✅ Option 2: value="2", text="2"
   - ✅ Option 3: value="3", text="3"
   - ...
   - ✅ Option 10: value="10", text="10" (KHÔNG phải "1", "0")
   - ✅ Option 11: value="11", text="11" (KHÔNG phải "1", "1")
   - ✅ Option 12: value="12", text="12" (KHÔNG phải "1", "2")

4. **Test chọn từng tháng:**
   - Chọn tháng 10 → Form accept
   - Chọn tháng 11 → Form accept
   - Chọn tháng 12 → Form accept

**Screenshot requirement:**

```
📸 Chụp màn hình dropdown showing all 12 months correctly
```

**Expected Result:**

```
✅ 12 distinct options (1 to 12)
✅ No duplicate values
✅ Values sorted correctly
```

**Actual Result:**

```
[X] PASS
[ ] FAIL - Options hiển thị: _______________________
```

---

### TEST 5: Employee Form Defaults ✅

**Mục đích:** Kiểm tra form thêm nhân viên có default values

**File đã fix:** `app/templates/hod_template/add_employee_template.html` lines 62-78

**Các bước test:**

1. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/employees/add/
   ```

2. **Kiểm tra các field có default value:**

   | Field            | Expected Default                                             | Actual Value   |
   | ---------------- | ------------------------------------------------------------ | -------------- |
   | **Nơi cấp CCCD** | CỤC TRƯỞNG CỤC CẢNH SÁT QUẢN LÝ HÀNH CHÍNH VỀ TRẬT TỰ XÃ HỘI | \***\*\_\*\*** |
   | **Quốc tịch**    | Việt Nam                                                     | \***\*\_\*\*** |
   | **Dân tộc**      | Kinh                                                         | \***\*\_\*\*** |
   | **Tôn giáo**     | Không                                                        | \***\*\_\*\*** |

3. **Test submit với default values:**
   - Fill required fields only (họ tên, ngày sinh, etc.)
   - Leave default fields unchanged
   - Submit form
   - Check database for saved defaults

**Verify trong database:**

```sql
SELECT
    first_name,
    last_name,
    place_of_issue,  -- Should be "CỤC TRƯỞNG..."
    nationality,      -- Should be "Việt Nam"
    nation,          -- Should be "Kinh"
    religion         -- Should be "Không"
FROM app_employee
ORDER BY id DESC
LIMIT 1;
```

**Expected Result:**

```
✅ All 4 fields have default values pre-filled
✅ User can change defaults if needed
✅ Defaults saved to database correctly
```

**Actual Result:**

```
[X] PASS
[ ] FAIL - Field nào sai: _______________________
```

---

### TEST 6: Payroll Visibility ✅

**Mục đích:** Kiểm tra manager có thể xem tất cả payroll

**Trước khi fix:**

- Manager (hangpt) chỉ xem được payroll của phòng "Giám đốc"
- Không thấy payroll của phòng khác

**Sau khi fix:**

- HR → Xem tất cả payroll
- Manager → Xem tất cả payroll
- Employee → Chỉ xem payroll của mình

**File đã fix:** `app/management_views.py` line 913-941

**Các bước test:**

**Test Case 1: Login as HR**

1. Login: `admin` / `admin123`
2. Navigate: `/management/payroll/manage/`
3. Count records visible
4. Expected: See ALL payrolls from ALL departments

**Test Case 2: Login as Manager**

1. Login: `hangpt` (Manager account)
2. Navigate: `/management/payroll/manage/`
3. Count records visible
4. Expected: See ALL payrolls from ALL departments

**Test Case 3: Login as Employee**

1. Login with regular employee account
2. Navigate: `/management/payroll/manage/`
3. Count records visible
4. Expected: See ONLY own payroll records

**Verification table:**

| User Type        | Expected Visibility | Actual Count   |
| ---------------- | ------------------- | -------------- |
| HR (admin)       | ALL records         | \***\*\_\*\*** |
| Manager (hangpt) | ALL records         | \***\*\_\*\*** |
| Employee         | Own records only    | \***\*\_\*\*** |

**Database verification:**

```sql
-- Total payrolls in system
SELECT COUNT(*) FROM app_payroll;

-- Payrolls by department
SELECT d.name, COUNT(p.id)
FROM app_payroll p
JOIN app_employee e ON p.employee_id = e.id
JOIN app_department d ON e.department_id = d.id
GROUP BY d.name;
```

**Expected Result:**

```
✅ HR sees all payrolls
✅ Manager sees all payrolls
✅ Employee sees only own payroll
✅ No permission errors
```

**Actual Result:**

```
[ ] PASS
[X] FAIL - User nào sai:
Hiện tại user hangpt (quyền cao nhất) chỉ xem được bảng lương của mình, không xem được tất cả bảng lương của toàn bộ nhân sự
```

---

### TEST 7: Export with Filters ✅

**Mục đích:** Kiểm tra export Excel có apply filters

**Trước khi fix:**

- Export button export tất cả records
- Ignore filters đã chọn

**Sau khi fix:**

- Export button lấy filter parameters từ URL
- Chỉ export records thỏa mãn filters

**File đã fix:** `app/management_views.py` line 1037-1075

**Các bước test:**

**Test Case 1: Export with Month filter**

1. Navigate: `/management/payroll/manage/`
2. Select filters:
   - Tháng: 10
   - Năm: 2025
3. Click "Lọc" button
4. Click "Xuất Excel" button
5. Open downloaded Excel file
6. Verify: Only October 2025 records

**Test Case 2: Export with Department filter**

1. Navigate: `/management/payroll/manage/`
2. Select filters:
   - Phòng ban: "Nhân sự"
3. Click "Lọc" button
4. Click "Xuất Excel" button
5. Open downloaded Excel file
6. Verify: Only "Nhân sự" department records

**Test Case 3: Export with multiple filters**

1. Navigate: `/management/payroll/manage/`
2. Select filters:
   - Tháng: 11
   - Năm: 2025
   - Phòng ban: "Giám đốc"
   - Trạng thái: "Đã duyệt"
3. Click "Lọc" button
4. Click "Xuất Excel" button
5. Open downloaded Excel file
6. Verify: Only matching records

**Verification checklist:**

| Filter     | Value    | Records in Excel | Expected      |
| ---------- | -------- | ---------------- | ------------- |
| Month      | 10       | \***\*\_\*\***   | Only month 10 |
| Year       | 2025     | \***\*\_\*\***   | Only 2025     |
| Department | Nhân sự  | \***\*\_\*\***   | Only HR dept  |
| Status     | Đã duyệt | \***\*\_\*\***   | Only approved |

**Expected Result:**

```
✅ Export applies filters correctly
✅ Excel contains only filtered records
✅ Record count matches filtered table
```

**Actual Result:**

```
[ ] PASS
[X] FAIL - Filter nào không work:
Hiện tại khi tải xuống thì luôn luôn là tất cả bảng chấm công
```

---

### TEST 8: Attendance Date Default ✅

**Mục đích:** Kiểm tra form attendance có default date = hôm nay

**File đã fix:**

- `app/management_views.py` line 587
- `app/templates/hod_template/add_attendance.html` line 17

**Các bước test:**

1. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/attendance/add/
   ```

2. **Kiểm tra field "Ngày Chấm Công":**

   - ✅ Field có value mặc định
   - ✅ Value = ngày hôm nay (20/11/2025)
   - ✅ Format: YYYY-MM-DD (2025-11-20)

3. **Test với các ngày khác:**

   - Change date to tomorrow → Accept
   - Change date to yesterday → Accept
   - Leave default → Should be today

4. **Submit form với default date:**
   - Select employee
   - Leave date as default (today)
   - Submit
   - Check database: attendance_date should be today

**Verify trong database:**

```sql
SELECT
    employee_id,
    attendance_date,
    DATE(attendance_date) = CURDATE() as is_today
FROM app_attendance
ORDER BY id DESC
LIMIT 1;
```

**Expected Result:**

```
✅ Date field shows today (2025-11-20)
✅ Format correct (YYYY-MM-DD)
✅ Can change date if needed
✅ Saves correctly to database
```

**Actual Result:**

```
[X] PASS - Date hiển thị: _________
[ ] FAIL - Lỗi: _______________________
```

---

### TEST 9: Edit Payroll Form Data ✅

**Mục đích:** Kiểm tra form edit payroll hiển thị data đúng

**File đã fix:** `app/management_views.py` line 950 (edit_mode context)

**Các bước test:**

1. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/payroll/manage/
   ```

2. **Click "Cập nhật"** trên một payroll record

3. **Kiểm tra form có hiển thị data không:**

   | Field        | Should Show   | Actual Value   |
   | ------------ | ------------- | -------------- |
   | Nhân viên    | Employee name | \***\*\_\*\*** |
   | Tháng        | 10 (example)  | \***\*\_\*\*** |
   | Năm          | 2025          | \***\*\_\*\*** |
   | Lương cơ bản | 26,000,000    | \***\*\_\*\*** |
   | Phụ cấp      | 2,000,000     | \***\*\_\*\*** |
   | Khấu trừ     | 500,000       | \***\*\_\*\*** |
   | Tổng lương   | 27,500,000    | \***\*\_\*\*** |

4. **Test submit với data đã sửa:**
   - Change "Phụ cấp" from 2,000,000 to 3,000,000
   - Submit form
   - Check if saved correctly

**Verify trong database:**

```sql
SELECT
    employee_id,
    month,
    year,
    base_salary,
    allowances,  -- Should update to 3,000,000
    deductions,
    total_salary
FROM app_payroll
WHERE id = {payroll_id};
```

**Expected Result:**

```
✅ Form populated with payroll data
✅ All fields show correct values
✅ Can edit and save changes
✅ Changes reflected in database
```

**Actual Result:**

```
[ ] PASS
[X] FAIL - Field nào không show: Tất cả field đều không show được
```

---

### TEST 10: Add Appraisal Criteria ✅

**Mục đích:** Kiểm tra thêm tiêu chí đánh giá có lưu database

**File:** `app/management_views.py` (view exists)

**Các bước test:**

1. **Navigate đến:**

   ```
   http://127.0.0.1:8000/management/appraisal/periods/
   ```

2. **Click vào một appraisal period**

3. **Click "Thêm tiêu chí"**

4. **Fill form:**

   - Tên tiêu chí: "Kỹ năng giao tiếp"
   - Mô tả: "Đánh giá khả năng giao tiếp với đồng nghiệp"
   - Điểm tối đa: 10
   - Trọng số: 0.15

5. **Submit form**

6. **Kiểm tra:**
   - ✅ Success message hiện
   - ✅ Redirect về period detail
   - ✅ Tiêu chí mới xuất hiện trong list
   - ✅ Database có record mới

**Verify trong database:**

```sql
-- Check trước khi thêm
SELECT COUNT(*) FROM app_appraisalcriteria WHERE period_id = {period_id};

-- Check sau khi thêm
SELECT
    name,
    description,
    max_score,
    weight
FROM app_appraisalcriteria
WHERE period_id = {period_id}
ORDER BY id DESC
LIMIT 1;

-- Should show: "Kỹ năng giao tiếp", 10, 0.15
```

**Expected Result:**

```
✅ Form submits successfully
✅ Criteria saved to database
✅ Appears in period detail page
✅ All fields correct
```

**Actual Result:**

```
[ ] PASS
[X] FAIL - Lỗi: Không thể thêm tiêu chí đánh giá
```

---

## 📊 TEST RESULTS SUMMARY

### Test Execution Date: \***\*\_\_\*\***

| #   | Test Name               | Status              | Notes  |
| --- | ----------------------- | ------------------- | ------ |
| 1   | convert_to_employee URL | [ ] PASS / [ ] FAIL | **\_** |
| 2   | Delete Attendance       | [ ] PASS / [ ] FAIL | **\_** |
| 3   | Hourly Wage             | [ ] PASS / [ ] FAIL | **\_** |
| 4   | Month Dropdown          | [ ] PASS / [ ] FAIL | **\_** |
| 5   | Employee Defaults       | [ ] PASS / [ ] FAIL | **\_** |
| 6   | Payroll Visibility      | [ ] PASS / [ ] FAIL | **\_** |
| 7   | Export Filters          | [ ] PASS / [ ] FAIL | **\_** |
| 8   | Attendance Date         | [ ] PASS / [ ] FAIL | **\_** |
| 9   | Edit Payroll            | [ ] PASS / [ ] FAIL | **\_** |
| 10  | Appraisal Criteria      | [ ] PASS / [ ] FAIL | **\_** |

**Overall Pass Rate:** \_**\_ / 10 (\_\_**%)

**Critical Issues Found:**

```
1. _________________________________
2. _________________________________
3. _________________________________
```

**Minor Issues Found:**

```
1. _________________________________
2. _________________________________
```

---

## 🐛 BUG REPORTING TEMPLATE

Nếu phát hiện lỗi, report theo format sau:

```markdown
### BUG: [Tên lỗi ngắn gọn]

**Severity:** [ ] Critical / [ ] High / [ ] Medium / [ ] Low

**Test Case:** Test #\_\_\_ - [Tên test]

**Steps to Reproduce:**

1.
2.
3.

**Expected Result:**

**Actual Result:**

**Screenshots:**
[Attach screenshots if applicable]

**Console Errors:**
```

[Paste console errors here]

````

**Database State:**
```sql
[SQL query showing incorrect data]
````

**Additional Context:**

```

---

## ✅ SIGN-OFF

**Tester Name:** _______________________
**Date Completed:** _______________________
**Sign:** _______________________

**Status:**
- [ ] All tests PASSED - Ready for production
- [ ] Some tests FAILED - Needs fixes
- [ ] Major issues found - Requires developer attention

**Next Steps:**
1. _________________________________
2. _________________________________
3. _________________________________
```
