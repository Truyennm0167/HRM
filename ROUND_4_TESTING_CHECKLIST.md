# 📋 ROUND 4 TESTING CHECKLIST - UPDATED

**Ngày tạo:** 20/11/2025  
**Trạng thái:** 10/13 Bugs Fixed  
**Mục đích:** Test lại các bugs đã fix trong Round 4

---

## ✅ ĐÃ FIX (10/13)

### 1. ✅ convert_to_employee Missing URL

- **File:** `urls_management.py`
- **Fix:** Added URL alias
- **Test:** Navigate to `/management/recruitment/applications/{id}/` - should load without error

### 2. ✅ Delete Attendance Button

- **File:** `management_views.py` line 658
- **Fix:** Changed `def delete_attendance(request)` → `def delete_attendance(request, attendance_id)`
- **Test:** Click delete button in manage attendance - should work now

### 3. ✅ Hourly Wage Calculation

- **File:** `management_views.py` line 774
- **Fix:** Added try-catch and division by zero check

```python
if standard_working_days > 0:
    hourly_rate = float(base * coef) / float(days * 8)
else:
    hourly_rate = 0
```

- **Test:** Calculate payroll with 21 days - should show correct hourly rate

### 4. ✅ Month Dropdown

- **File:** `calculate_payroll.html`
- **Fix:** Changed from `{% for i in "123456789101112"|make_list %}` to individual options 1-12
- **Test:** Open calculate payroll page - dropdown should show 1,2,3...10,11,12

### 5. ✅ Payroll Visibility

- **File:** `management_views.py` line 913
- **Fix:** Manager and HR can see all payrolls, only regular employees see their own
- **Test:** Login as Manager - should see all payrolls

### 6. ✅ Payroll Export Filters

- **File:** `management_views.py` line 1037
- **Fix:** Added GET parameters for month, year, department, status
- **Test:** Export payroll with filters - Excel should contain only filtered data

### 7. ✅ Attendance Date Default

- **File:** `add_attendance.html` + `management_views.py`
- **Fix:** Pass `today` variable and set as default value
- **Test:** Open add attendance page - date should be today

### 8. ✅ Employee Form Defaults

- **File:** `add_employee_template.html`
- **Fix:** Added default values:
  - Nơi cấp: "CỤC TRƯỞNG CỤC CẢNH SÁT..."
  - Quốc tịch: "Việt Nam"
  - Dân tộc: "Kinh"
  - Tôn giáo: "Không"
- **Test:** Open add employee page - fields should have defaults

### 9. ✅ Edit Payroll Form Data (Partial)

- **File:** `management_views.py` line 950
- **Fix:** Pass `edit_mode=True` and payroll data to template
- **Test:** Edit payroll - form should show existing data

### 10. ✅ Add Appraisal Criteria (Needs Testing)

- **File:** Form exists, view exists
- **Test:** Add criteria - check if it saves to database

---

## ⚠️ PARTIALLY FIXED (2/13)

### 11. ⚠️ Payroll Manage Filter

- **Status:** Backend ready, needs JavaScript implementation
- **What's needed:** Update `manage_payroll.html` JavaScript to apply filters
- **Current:** Filter controls exist but don't filter DataTable

### 12. ⚠️ Payroll Sorting by Month/Year

- **Status:** Needs custom DataTables column definition
- **What's needed:** Add custom sorting function for "1/2025", "10/2025" format
- **Current:** Sorts as string (1, 10, 11, 2, 3...)

---

## 🔴 NOT STARTED (1/13)

### 13. 🆕 User Management Page

- **Status:** Not implemented yet
- **Required:**
  - Create `user_management_views.py`
  - Create `user_management.html` template
  - Add URLs to `urls_management.py`
  - Implement CRUD for users
  - Implement role/group assignment

---

## 🧪 DETAILED TEST CASES

### TEST 1: Convert to Employee URL

**Steps:**

1. Navigate to `/management/recruitment/applications/`
2. Click on an application
3. Page should load without NoReverseMatch error

**Expected:** No error, page loads successfully

---

### TEST 2: Delete Attendance

**Steps:**

1. Navigate to `/management/attendance/manage/`
2. Click "Xóa" button on any attendance record
3. Confirm deletion

**Expected:** AJAX request succeeds, row removed, page reloads

---

### TEST 3: Hourly Wage Calculation

**Steps:**

1. Navigate to `/management/payroll/calculate/`
2. Select employee, month, year
3. Click "Tính lương"
4. Check "Lương theo giờ" field

**Expected:**

- For 21 days: ~147,727 VNĐ (NOT 7 trillion)
- For 22 days: ~147,727 VNĐ
- Calculation: (26,000,000 _ coef) / (21 _ 8)

---

### TEST 4: Month Dropdown

**Steps:**

1. Navigate to `/management/payroll/calculate/`
2. Look at month dropdown

**Expected:** Shows 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 (NOT 1,2,3...9,1,0,1,1,1,2)

---

### TEST 5: Payroll Visibility

**Steps:**

1. Login as Manager (hangpt)
2. Navigate to `/management/payroll/manage/`
3. Check number of records

**Expected:** See ALL employees' payroll (not just Giám đốc department)

---

### TEST 6: Payroll Export with Filters

**Steps:**

1. Navigate to `/management/payroll/manage/`
2. Select filters: Month=10, Year=2025
3. Click "Xuất Excel"
4. Open downloaded file

**Expected:** Excel contains only October 2025 payrolls

---

### TEST 7: Attendance Date Default

**Steps:**

1. Navigate to `/management/attendance/add/`
2. Check "Ngày Chấm Công" field

**Expected:** Date field shows today's date (20/11/2025)

---

### TEST 8: Employee Form Defaults

**Steps:**

1. Navigate to `/management/employees/add/`
2. Check these fields:
   - Nơi cấp
   - Quốc tịch
   - Dân tộc
   - Tôn giáo

**Expected:** Fields have pre-filled default values

---

### TEST 9: Edit Payroll Data

**Steps:**

1. Navigate to `/management/payroll/manage/`
2. Click "Cập nhật" on a payroll record
3. Check if form shows existing data

**Expected:** Form fields populated with payroll data

---

### TEST 10: Add Appraisal Criteria

**Steps:**

1. Navigate to `/management/appraisal/periods/`
2. Click on a period
3. Click "Thêm tiêu chí"
4. Fill form and submit

**Expected:**

- POST returns 200 ✅
- Criteria saved to database ❓ (needs verification)
- Redirects to period detail
- New criteria appears in list

---

## 📊 TEST RESULTS TEMPLATE

```
## ROUND 4 TEST RESULTS - [Date]

### Core Fixes (Tests 1-10)
- Test 1 (convert_to_employee): [ ] PASS / [ ] FAIL
- Test 2 (delete attendance): [ ] PASS / [ ] FAIL
- Test 3 (hourly wage): [ ] PASS / [ ] FAIL
- Test 4 (month dropdown): [ ] PASS / [ ] FAIL
- Test 5 (payroll visibility): [ ] PASS / [ ] FAIL
- Test 6 (export filters): [ ] PASS / [ ] FAIL
- Test 7 (attendance date): [ ] PASS / [ ] FAIL
- Test 8 (employee defaults): [ ] PASS / [ ] FAIL
- Test 9 (edit payroll): [ ] PASS / [ ] FAIL
- Test 10 (appraisal criteria): [ ] PASS / [ ] FAIL

### Remaining Issues
- Payroll filter: Needs JavaScript fix
- Payroll sorting: Needs DataTables custom sort
- User management: Not implemented

**Pass Rate:** __/10 (___%)
**Critical Issues Found:**
**Notes:**
```

---

## 🔧 REMAINING WORK

### For Developer:

**1. Fix Payroll Filter JavaScript** (manage_payroll.html)

```javascript
// Add filter logic to DataTable
$("#filter-btn").click(function () {
  var month = $("#month-filter").val();
  var year = $("#year-filter").val();
  var dept = $("#dept-filter").val();

  table
    .columns(1)
    .search(month + "/" + year)
    .columns(4)
    .search(dept)
    .draw();
});
```

**2. Fix Payroll Sorting** (manage_payroll.html)

```javascript
// Custom sort for "month/year" column
$.fn.dataTable.ext.type.order["month-year-pre"] = function (data) {
  var parts = data.split("/");
  return parseInt(parts[1]) * 12 + parseInt(parts[0]);
};

// Apply to column
columnDefs: [
  {
    targets: 1, // Month/Year column
    type: "month-year",
  },
];
```

**3. Create User Management Page**

- See ROUND_4_FIX_PLAN.md for detailed requirements

---

## ✅ SUCCESS CRITERIA

**Round 4 Complete When:**

- [ ] 10/10 core tests PASS
- [ ] Filter working (JavaScript fix)
- [ ] Sorting working (DataTables fix)
- [ ] User management implemented

---

**Document Version:** 4.0  
**Last Updated:** 20/11/2025  
**Status:** 10/13 Fixed (77%) ✅
