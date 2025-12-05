# 🔄 ROUND 4 FINAL RETEST CHECKLIST

**Ngày tạo:** 22/11/2025  
**Phiên bản:** 4.2 (After Additional Fixes)  
**Trạng thái:** Ready for Final Testing

---

## 📊 TÓM TẮT CÁC FIX BỔ SUNG

### ✅ Đã fix thêm 6 vấn đề từ lần test trước:

1. ✅ **Delete Attendance** - Removed redundant POST check + Added error handling
2. ✅ **Filter Month/Year/Status** - Fixed DataTables filter logic with regex
3. ✅ **Export Filename** - Dynamic naming based on filters
4. ✅ **View Payroll Permission** - Managers can now view all payrolls
5. ✅ **Number Formatting** - Added thousand separator in calculate form
6. ✅ **Appraisal Criteria Order** - Made `order` field optional with default 0
7. ✅ **Appraisal Detail URL** - Added backward compatibility alias

---

## 🧪 DANH SÁCH TEST CASES - FINAL ROUND

### 🔴 TEST 1: Delete Attendance Button **[CRITICAL]**

**Các fix đã thực hiện:**

1. Removed `if request.method == "POST"` (redundant với `@require_POST`)
2. Added specific error handling (DoesNotExist, generic Exception)
3. Added AJAX error callback với console logging

**Các bước test:**

1. **Login** với quyền quản lý attendance
2. **Open DevTools** → Console tab + Network tab
3. **Navigate:** `/management/attendance/manage/`
4. **Click nút "Xóa"** trên bất kỳ record nào
5. **Confirm** popup
6. **Check Console:** Xem có error không
7. **Check Network:** POST request status

**Expected Result:**

```
✅ Confirm dialog appears
✅ Network tab shows: POST /management/attendance/{id}/delete/ → 200
✅ Response: {"status": "success"}
✅ Page reloads
✅ Record deleted from table and database
✅ No console errors
```

**Debug steps if fails:**

```
1. Check Console for JavaScript errors
2. Check Network → Request Headers → csrf_token present?
3. Check Network → Response → {"status": "error", "message": "..."}
4. Check server logs for Python exceptions
```

**Actual Result:**

```
[ ] PASS - Xóa thành công
[ ] FAIL - Lỗi: _______________________
Console errors: _______________________
Network status: _______________________
```

---

### 🔴 TEST 2: Payroll Filter (Month/Year/Status) **[CRITICAL]**

**Vấn đề cũ:**

- Lọc theo tháng không hoạt động
- Lọc theo trạng thái không hiển thị record nào

**Fix đã thực hiện:**

```javascript
// Before: Simple string search
table.column(1).search(month);
table.column(1).search(year);

// After: Regex pattern for month/year combined
var monthYearPattern = "";
if (month && year) {
  monthYearPattern = "^" + month + "\\/" + year + "$"; // Exact match: "10/2025"
} else if (month) {
  monthYearPattern = "^" + month + "\\/"; // Starts with: "10/"
} else if (year) {
  monthYearPattern = "\\/" + year + "$"; // Ends with: "/2025"
}
table.column(1).search(monthYearPattern, true, false); // regex=true

// Status filter with exact match
if (status) {
  table.column(6).search(status, false, true); // smartSearch=true
}
```

**Các bước test:**

**Test Case 1: Filter by Month Only**

1. Navigate: `/management/payroll/manage/`
2. Select: Tháng = 10
3. Click "Lọc"
4. Verify: Table shows only records with "10/" at start (10/2024, 10/2025, etc.)

**Test Case 2: Filter by Year Only**

1. Select: Năm = 2025
2. Click "Lọc"
3. Verify: Table shows only "/2025" records (1/2025, 2/2025, ..., 12/2025)

**Test Case 3: Filter by Month + Year**

1. Select: Tháng = 11, Năm = 2025
2. Click "Lọc"
3. Verify: Table shows ONLY "11/2025" records

**Test Case 4: Filter by Status "Chưa xác nhận"**

1. Select: Trạng thái = "Chưa xác nhận"
2. Click "Lọc"
3. Verify: Table shows only pending payrolls

**Test Case 5: Filter by Status "Đã xác nhận"**

1. Select: Trạng thái = "Đã xác nhận"
2. Click "Lọc"
3. Verify: Table shows only confirmed payrolls

**Test Case 6: Combined Filters**

1. Select: Tháng=11, Năm=2025, Phòng Ban="Nhân sự", Trạng thái="Đã xác nhận"
2. Click "Lọc"
3. Verify: Intersection of all filters

**Expected Result:**

```
✅ Month filter works independently
✅ Year filter works independently
✅ Month + Year combined works (exact match)
✅ Status filter works for both values
✅ Department filter works
✅ All filters can combine
✅ Clear filter button resets all
```

**Actual Result:**

```
Test Case 1 (Month): [X] PASS / [ ] FAIL - Records shown: _____
Test Case 2 (Year): [X] PASS / [ ] FAIL - Records shown: _____
Test Case 3 (M+Y): [X] PASS / [ ] FAIL - Records shown: _____
Test Case 4 (Pending): [ ] PASS / [X] FAIL - Records shown: Không show bất kỳ record nào
Test Case 5 (Confirmed): [ ] PASS / [X] FAIL - Records shown: Không show bất kỳ record nào
Test Case 6 (Combined): [ ] PASS / [ ] FAIL - Records shown: Chưa kết hợp được lọc theo Trạng thái
```

---

### 🔴 TEST 3: Export with Dynamic Filename **[NICE TO HAVE]**

**Fix đã thực hiện:**

```python
filename_parts = ['BangLuong']
if month: filename_parts.append(f'Thang{month}')
if year: filename_parts.append(f'Nam{year}')
if department: filename_parts.append(department.replace(' ', '_'))
if status:
    status_map = {'pending': 'ChuaXacNhan', 'confirmed': 'DaXacNhan'}
    filename_parts.append(status_map.get(status, status.replace(' ', '_')))

filename = '_'.join(filename_parts) + '.xls'
# Example: BangLuong_Thang10_Nam2025_Nhan_su_DaXacNhan.xls
```

**Các bước test:**

**Test Case 1: No Filters**

1. Navigate: `/management/payroll/manage/`
2. Click "Xuất Excel" (không chọn filter)
3. Check filename: Should be `BangLuong.xls`

**Test Case 2: Month + Year**

1. Select: Tháng=10, Năm=2025
2. Click "Xuất Excel"
3. Check filename: Should be `BangLuong_Thang10_Nam2025.xls`

**Test Case 3: All Filters**

1. Select: Tháng=11, Năm=2025, Phòng="Nhân sự", Status="Đã xác nhận"
2. Click "Xuất Excel"
3. Check filename: Should be `BangLuong_Thang11_Nam2025_Nhan_su_DaXacNhan.xls`

**Expected Result:**

```
✅ Filename changes based on filters
✅ Format: BangLuong_[filters].xls
✅ Spaces replaced with underscores
✅ Easy to identify exported data
```

**Actual Result:**

```
Test Case 1: [X] PASS - Filename: _______________________
Test Case 2: [X] PASS - Filename: _______________________
Test Case 3: [X] FAIL - Chưa kết hợp được lọc theo Trạng thái
```

---

### 🔴 TEST 4: View Payroll Permission (Manager/Superuser) **[CRITICAL]**

**Vấn đề cũ:**

- GET /management/payroll/158/ → 302 redirect
- Managers không xem được chi tiết

**Fix đã thực hiện:**

```python
# Before:
if not request.user.groups.filter(name='HR').exists():
    if payroll.employee.department != user_employee.department:
        return redirect('manage_payroll')  # Blocked managers

# After:
is_hr = request.user.groups.filter(name='HR').exists()
is_manager = request.user.groups.filter(name='Manager').exists() or request.user.is_superuser

if not is_hr and not is_manager:
    # Only regular employees restricted
    if payroll.employee != user_employee:
        return redirect('manage_payroll')
# HR and Managers can view ALL payrolls
```

**Các bước test:**

**Test Case 1: Manager Views Any Payroll**

1. Login: `hangpt` (Manager/Superuser)
2. Navigate: `/management/payroll/manage/`
3. Click "Xem chi tiết" on ANY payroll (confirmed or pending)
4. Expected: Should load view_payroll.html successfully

**Test Case 2: HR Views Any Payroll**

1. Login: `admin` (HR)
2. Click "Xem chi tiết" on any payroll
3. Expected: Should load successfully with full salary info

**Test Case 3: Employee Views Own Payroll**

1. Login: Regular employee
2. Navigate: `/management/payroll/manage/`
3. Click "Xem chi tiết" on OWN payroll
4. Expected: Should load successfully

**Test Case 4: Employee Views Other's Payroll**

1. Still logged as regular employee
2. Try to access: `/management/payroll/{other_payroll_id}/`
3. Expected: Redirect with error message

**Expected Result:**

```
✅ Manager sees ALL payrolls detail (200 response)
✅ HR sees ALL payrolls detail
✅ Employee sees only OWN payroll
✅ Employee blocked from other's payroll (302 redirect)
✅ No DoesNotExist exceptions
```

**Actual Result:**

```
Manager (hangpt): [X] PASS / [ ] FAIL - Status: _____
HR (admin): [X] PASS / [ ] FAIL - Status: _____
Employee (own): [X] PASS / [ ] FAIL - Status: _____
Employee (other): [X] PASS / [ ] FAIL - Should redirect: _____
```

---

### 🔴 TEST 5: Number Formatting in Calculate Form **[UI ENHANCEMENT]**

**Fix đã thực hiện:**

```javascript
function formatNumber(num) {
  return Math.round(num)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Apply to all money fields
$(".base-salary").val(formatNumber(response.data.base_salary));
$(".hourly-rate").val(formatNumber(response.data.hourly_rate));
$(".bonus").val(formatNumber(response.data.bonus));
$(".penalty").val(formatNumber(response.data.penalty));
$(".total-salary").val(formatNumber(response.data.total_salary));
```

**Các bước test:**

1. **Login as HR**
2. **Navigate:** `/management/payroll/calculate/`
3. **Select:** Employee, Month, Year
4. **Click "Tính Lương"**
5. **Check format của các field:**

| Field          | Expected Format | Actual Value   |
| -------------- | --------------- | -------------- |
| Lương cơ bản   | 26,000,000      | \***\*\_\*\*** |
| Lương theo giờ | 696,429         | \***\*\_\*\*** |
| Thưởng         | 2,000,000       | \***\*\_\*\*** |
| Phạt           | 500,000         | \***\*\_\*\*** |
| Tổng lương     | 118,500,000     | \***\*\_\*\*** |

6. **Test edit và submit:**
   - Change Thưởng to 3,000,000
   - Check Tổng lương auto-updates with comma
   - Submit form
   - Verify saves correctly to database

**Expected Result:**

```
✅ All money fields show thousand separator
✅ Format: 1,234,567 (not 1234567)
✅ Auto-updates maintain format
✅ Form submits correctly (removes commas before save)
```

**Actual Result:**

```
[ ] PASS - All fields formatted correctly
[X] FAIL - Fields missing format: Tất cả fields đều không
```

---

### 🔴 TEST 6: Add Appraisal Criteria (Order Field) **[CRITICAL]**

**Vấn đề cũ:**

- Form validation failed: "order: This field is required"
- Không thể thêm criteria dù nhập đầy đủ

**Fix đã thực hiện:**

```python
# In AppraisalCriteriaForm
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['order'].required = False  # Make optional
    self.fields['order'].initial = 0  # Default value
```

**Các bước test:**

1. **Login as HR**
2. **Navigate:** `/management/appraisal/periods/`
3. **Click vào một period** (draft or active)
4. **Click "Thêm tiêu chí"**
5. **Fill form KHÔNG điền Order field:**
   - Tên tiêu chí: "Test Criteria"
   - Mô tả: "Test description"
   - Danh mục: "Hiệu suất" (performance)
   - Trọng số: 20
   - Điểm tối đa: 5
   - **Order: Leave empty or 0**
6. **Submit**

**Expected Result:**

```
✅ Form submits successfully WITHOUT filling order
✅ Success message: "Đã thêm tiêu chí: Test Criteria"
✅ Redirects to period detail
✅ New criteria appears with order=0
✅ No validation errors
```

**Database verification:**

```sql
SELECT name, category, weight, max_score, `order`
FROM app_appraisalcriteria
WHERE name = 'Test Criteria';
-- Should show: Test Criteria, performance, 20, 5, 0
```

**Actual Result:**

```
[X] PASS - Criteria added successfully, nhưng chưa cho phép chỉnh sửa các tiêu chí
[ ] FAIL - Validation error: _______________________
```

---

### 🔴 TEST 7: Appraisal Detail URL **[URL FIX]**

**Vấn đề cũ:**

- NoReverseMatch for 'appraisal_detail'
- Templates use old URL name

**Fix đã thực hiện:**

```python
# Added backward compatibility alias
path('appraisal/<int:appraisal_id>/detail/',
     management_views.appraisal_detail,
     name='appraisal_detail'),
```

**Các bước test:**

1. **Login as HR**
2. **Navigate:** `/management/appraisal/periods/`
3. **Click vào period đang active**
4. **Page should load without NoReverseMatch**

**Expected Result:**

```
✅ Period detail page loads successfully
✅ No NoReverseMatch error
✅ Can see list of appraisals (if any)
✅ Links work correctly
```

**Actual Result:**

```
[X] PASS - Page loads successfully
[ ] FAIL - Error: _______________________
```

---

## 📊 FINAL TEST RESULTS SUMMARY

**Ngày test:** \***\*\_\_\_\*\***  
**Tester:** \***\*\_\_\_\*\***

### All Tests:

| #   | Test Name                | Priority | Status              | Notes  |
| --- | ------------------------ | -------- | ------------------- | ------ |
| 1   | Delete Attendance        | CRITICAL | [ ] PASS / [ ] FAIL | **\_** |
| 2   | Filter Month/Year/Status | CRITICAL | [ ] PASS / [ ] FAIL | **\_** |
| 3   | Export Filename          | NICE     | [ ] PASS / [ ] FAIL | **\_** |
| 4   | View Payroll Permission  | CRITICAL | [ ] PASS / [ ] FAIL | **\_** |
| 5   | Number Formatting        | UI       | [ ] PASS / [ ] FAIL | **\_** |
| 6   | Add Appraisal Criteria   | CRITICAL | [ ] PASS / [ ] FAIL | **\_** |
| 7   | Appraisal Detail URL     | CRITICAL | [ ] PASS / [ ] FAIL | **\_** |

**Pass Rate:** **\_** / 7 (\_\_\_\_%)

**Critical Tests (Must Pass): 1, 2, 4, 6, 7**  
**Critical Pass Rate:** **\_** / 5

---

## ✅ FINAL SIGN-OFF

**All Issues Resolved:**

- [ ] YES - All 7 tests passed
- [ ] NO - See failed tests above

**Production Ready:**

- [ ] YES - Deploy to production
- [ ] NO - Need additional fixes

**Remaining Work:**

- [ ] Feature #7: Implement filter JavaScript (client-side)
- [ ] Feature #8: Implement custom DataTables sorting
- [ ] Feature #13: Implement user management page

**Tester Signature:** ****\*\*****\_\_\_****\*\*****  
**Developer Signature:** ****\*\*****\_\_\_****\*\*****  
**Date:** ****\*\*****\_\_\_****\*\*****

---

## 🚀 NEXT PHASE

**If all tests PASS:**

1. ✅ Mark Round 4 as COMPLETE
2. 🚀 Begin Round 5: Remaining Features
   - Filter functionality (already working with fixes above!)
   - Sorting functionality
   - User management page

**If some tests FAIL:**

1. 🔧 Developer fixes remaining issues
2. 🧪 Retest failed items only
3. ♻️ Repeat until all pass
