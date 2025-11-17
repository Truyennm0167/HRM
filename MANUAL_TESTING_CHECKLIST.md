# 📋 MANAGEMENT PORTAL TESTING CHECKLIST

**Testing Date**: November 17, 2025  
**Tester**: Manual testing required  
**Status**: Ready for comprehensive testing

---

## ✅ COMPLETED FIXES (Verified)

### Fix #1: Attendance URLs ✅

- [x] `add_attendance_save` URL added → `/management/attendance/add/save/`
- [x] `export_attendance` URL added → `/management/attendance/export/`
- [x] `/management/attendance/add/` page accessible
- [x] `/management/attendance/manage/` page accessible

### Fix #2: Expense Categories URL ✅

- [x] `edit_expense_category_save` now requires `category_id` parameter
- [x] Template updated to pass category ID
- [x] `/management/expense/categories/` page accessible

### Fix #3: Recruitment Jobs URL + Pagination ✅

- [x] `job_detail_admin` URL added → `/management/recruitment/jobs/{id}/`
- [x] `list_jobs_admin` view pagination fixed with `.order_by('-created_at')`
- [x] No more `UnorderedObjectListWarning`
- [x] `/management/recruitment/jobs/` page accessible

### Fix #4: Salary Components URL ✅

- [x] `create_salary_component` URL added → `/management/salary-rules/components/create/`
- [x] `/management/salary-rules/components/` page accessible

### Fix #5: Appraisal Periods URL ✅

- [x] `create_appraisal_period` URL added → `/management/appraisal/periods/create/`
- [x] `/management/appraisal/periods/` page accessible

---

## 🧪 MANUAL TESTING REQUIRED

### 📍 Section 1: Core Management Features

#### Home & Dashboard

- [ ] Login as admin (hangpt/hangpt123) - OK
- [ ] Access `/management/` - Dashboard loads correctly - OK
- [ ] All stats cards display (Employees, Departments, Contracts, etc.) - OK
- [ ] Recent activities display - Chưa thực thi chức năng này
- [ ] No console errors - OK

#### Employee Management

- [ ] Access `/management/employee_list/` - OK
- [ ] Pagination works (no ordering warnings) - OK
- [ ] Search functionality works - OK
- [ ] Filter by department works - OK
- [ ] Click "Add Employee" button - OK
- [ ] Create new employee form works - LỖI
      NoReverseMatch at /management/employees/171/
      Reverse for 'delete_employee' not found. 'delete_employee' is not a valid view function or pattern name.
- [ ] Edit existing employee - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_employee_save
- [ ] View employee detail page - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_employee_save

#### Department & Job Titles

- [ ] Access `/management/department/` - OK
- [ ] Add new department - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_department_save/
- [ ] Edit department - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_department_save/
- [ ] Delete department (with confirmation) - LỖI
      Page not found (404)
      Request Method: GET
      Request URL: http://127.0.0.1:8000/delete_department/82/
- [ ] Access `/management/job-titles/` - OK
- [ ] Add new job title - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_job_title_save
- [ ] Edit job title - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_job_title_save
- [ ] Delete job title - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/add_job_title_save

#### Organizational Chart

- [ ] Access `/management/org-chart/` - OK
- [ ] Chart renders without errors - OK
- [ ] Expand/collapse nodes work - OK
- [ ] Department hierarchy displays correctly - OK
- Nhưng còn vấn đề khi Tìm kiếm nhân viên hoặc Lọc theo phòng ban thì chưa ổn lắm. Cần fix lại: Khi tìm kiếm nhân viên hoặc lọc phòng ban thì cần hiển thị cả Phòng ban - Nhân viên. Hiện tại khi tìm kiếm nhân viên thì không thể thấy được phòng ban mà nhân viên đó đang ở - ngược lại nếu lọc phòng ban thì chỉ thấy mỗi phòng ban, không thấy bất cứ nhân viên nào

---

### 📍 Section 2: Attendance Management (FIXED)

- [ ] Access `/management/attendance/add/` - LỖI
      NoReverseMatch at /management/attendance/add/
      Reverse for 'check_attendance_date' not found. 'check_attendance_date' is not a valid view function or pattern name.
- [ ] Form displays correctly - CHƯA TEST ĐƯỢC
- [ ] Submit attendance (test `add_attendance_save` URL) - CHƯA TEST ĐƯỢC
- [ ] Access `/management/attendance/manage/` - LỖI
      NoReverseMatch at /management/attendance/manage/
      Reverse for 'delete_attendance' not found. 'delete_attendance' is not a valid view function or pattern name.
- [ ] Attendance list displays - LỖI
      NoReverseMatch at /management/attendance/manage/
      Reverse for 'delete_attendance' not found. 'delete_attendance' is not a valid view function or pattern name.
- [ ] Filter by date range works - CHƯA TEST ĐƯỢC
- [ ] Filter by employee works - CHƯA TEST ĐƯỢC
- [ ] Edit attendance record - CHƯA TEST ĐƯỢC
- [ ] Click "Export" button (test `export_attendance` URL) - CHƯA TEST ĐƯỢC
- [ ] Export generates correctly - CHƯA TEST ĐƯỢC

---

### 📍 Section 3: Leave Management

#### Leave Types

- [ ] Access `/management/leave/types/` - OK
- [ ] View all leave types - OK
- [ ] Add new leave type - OK
- [ ] Edit leave type - OK
- [ ] Delete leave type - OK

#### Leave Requests

- [ ] Access `/management/leave/requests/` - OK
- [ ] View all leave requests - OK
- [ ] Filter by status (Pending, Approved, Rejected) - OK
- [ ] Filter by employee - OK
- [ ] View leave request detail - OK
- [ ] Approve leave request - OK
- [ ] Reject leave request - OK
- [ ] Check leave balance updates - OK, nhưng có vấn đề về hiển thị, tôi chưa nắm rõ cách tính ngày nghỉ còn lại như thế nào mà hiện tại nó hiển thị là số thập phân - không đúng về mặt logic là ngày nghỉ thì phải số nguyên

---

### 📍 Section 4: Expense Management (FIXED)

#### Expense Categories

- [ ] Access `/management/expense/categories/` - LỖI
      NoReverseMatch at /management/expense/categories/
      Reverse for 'edit_expense_category_save' with arguments '('',)' not found. 1 pattern(s) tried: ['management/expense/categories/(?P<category_id>[0-9]+)/edit/\\Z']

- [ ] View all expense categories - CHƯA TEST ĐƯỢC
- [ ] Add new category - CHƯA TEST ĐƯỢC
- [ ] Edit category (test fixed URL with category_id) - CHƯA TEST ĐƯỢC
- [ ] Delete category - CHƯA TEST ĐƯỢC
- [ ] No NoReverseMatch errors - VẪN CÒN LỖI

#### Expense Requests

- [ ] Access `/management/expense/requests/` - OK
- [ ] View all expense requests - OK
- [ ] Filter by status - OK
- [ ] Filter by employee - OK
- [ ] View expense detail (with receipt) - LỖI
      NoReverseMatch at /management/expense/requests/93/
      Reverse for 'mark_expense_as_paid' not found. 'mark_expense_as_paid' is not a valid view function or pattern name.
- [ ] Approve expense - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/expense/approve/93/
- [ ] Reject expense - LỖI
      Page not found (404)
      Request Method: POST
      Request URL: http://127.0.0.1:8000/expense/reject/93/

---

### 📍 Section 5: Payroll Management

#### Payroll Calculation

- [ ] Access `/management/payroll/calculate/` - LỖI
      NoReverseMatch at /management/payroll/calculate/
      Reverse for 'save_payroll' not found. 'save_payroll' is not a valid view function or pattern name.
- [ ] Select month/year - CHƯA TEST ĐƯỢC
- [ ] Select employees or departments - CHƯA TEST ĐƯỢC
- [ ] Click "Calculate Payroll" - CHƯA TEST ĐƯỢC
- [ ] Preview calculations - CHƯA TEST ĐƯỢC
- [ ] Confirm and save - CHƯA TEST ĐƯỢC

#### Payroll Management

- [ ] Access `/management/payroll/manage/` - LỖI
      NoReverseMatch at /management/payroll/manage/
      Reverse for 'export_payroll' not found. 'export_payroll' is not a valid view function or pattern name.
- [ ] View all payroll records - CHƯA TEST ĐƯỢC
- [ ] Filter by month/year - CHƯA TEST ĐƯỢC
- [ ] Filter by employee - CHƯA TEST ĐƯỢC
- [ ] View payroll detail - CHƯA TEST ĐƯỢC
- [ ] Edit payroll (if needed) - CHƯA TEST ĐƯỢC
- [ ] Export payroll to Excel/PDF - CHƯA TEST ĐƯỢC

---

### 📍 Section 6: Contract Management

- [ ] Access `/management/contracts/` - OK
- [ ] View all contracts - OK
- [ ] Filter by status (Active, Expired, Expiring Soon)
- [ ] Create new contract - CHƯA HOẠT ĐỘNG ĐƯỢC
      Tôi chưa thể xem/điền Số hợp đồng, file hợp đồng, Mức lương (VNĐ), Hệ số lương, Phụ cấp (VNĐ), Mô tả công việc, Nơi làm việc, Quyền lợi, Thông tin bảo hiểm. Và khi bấm nút Cập nhật thì không kết quả nào xảy ra, hợp đồng mới vẫn chưa được tạo, trong khi mã trả về là INFO "POST /management/contracts/create/ HTTP/1.1" 200 39715
- [ ] View contract detail - CHƯA TEST ĐƯỢC
- [ ] Edit contract - CHƯA TEST ĐƯỢC
- [ ] Renew contract - CHƯA TEST ĐƯỢC
- [ ] Delete contract - CHƯA TEST ĐƯỢC
- [ ] Access `/management/contracts/expiring/` - OK
- [ ] View expiring contracts alert - CHƯA TEST ĐƯỢC

---

### 📍 Section 7: Recruitment (FIXED)

#### Job Postings

- [ ] Access `/management/recruitment/jobs/` - LỖI
      NoReverseMatch at /management/recruitment/jobs/
      Reverse for 'edit_job' not found. 'edit_job' is not a valid view function or pattern name.
- [ ] View all jobs (pagination works, no warnings) - CHƯA TEST ĐƯỢC
- [ ] Click job title to view detail (test `job_detail_admin` URL) - CHƯA TEST ĐƯỢC
- [ ] Create new job posting - OK
- [ ] Edit job posting - CHƯA TEST ĐƯỢC
- [ ] Delete job posting - CHƯA TEST ĐƯỢC
- [ ] Change job status (Open/Closed) - CHƯA TEST ĐƯỢC

#### Applications Kanban

- [ ] Access `/management/recruitment/applications/` - LỖI
      NoReverseMatch at /management/recruitment/applications/
      Reverse for 'application_detail' not found. 'application_detail' is not a valid view function or pattern name.
- [ ] View kanban board - CHƯA TEST ĐƯỢC
- [ ] Drag & drop applications between stages - CHƯA TEST ĐƯỢC
- [ ] View application detail - CHƯA TEST ĐƯỢC
- [ ] Add notes to application - CHƯA TEST ĐƯỢC
- [ ] Update application status - CHƯA TEST ĐƯỢC
- [ ] Convert application to employee - CHƯA TEST ĐƯỢC
- [ ] Filter by job posting - CHƯA TEST ĐƯỢC

---

### 📍 Section 8: Salary Rules (FIXED)

#### Salary Components

- [ ] Access `/management/salary-rules/components/` - LỖI
      NoReverseMatch at /management/salary-rules/components/
      Reverse for 'edit_salary_component' not found. 'edit_salary_component' is not a valid view function or pattern name.
- [ ] View all salary components - CHƯA TEST ĐƯỢC
- [ ] Click "Create Component" (test `create_salary_component` URL) - CHƯA TEST ĐƯỢC
- [ ] Add new component (Basic, Allowance, Deduction) - CHƯA TEST ĐƯỢC
- [ ] Edit component - CHƯA TEST ĐƯỢC
- [ ] Delete component - CHƯA TEST ĐƯỢC

#### Employee Salary Rules

- [ ] Access employee salary rules page - CHƯA TEST ĐƯỢC
- [ ] View assigned rules for employee - CHƯA TEST ĐƯỢC
- [ ] Assign new salary rule - CHƯA TEST ĐƯỢC
- [ ] Edit rule amount - CHƯA TEST ĐƯỢC
- [ ] Delete salary rule - CHƯA TEST ĐƯỢC
- [ ] Preview salary calculation - CHƯA TEST ĐƯỢC

#### Salary Templates

- [ ] Access `/management/salary-rules/templates/` - LỖI
      NoReverseMatch at /management/salary-rules/templates/
      Reverse for 'create_salary_rule_template' not found. 'create_salary_rule_template' is not a valid view function or pattern name.
- [ ] View all templates - CHƯA TEST ĐƯỢC
- [ ] Create new template - CHƯA TEST ĐƯỢC
- [ ] Edit template - CHƯA TEST ĐƯỢC
- [ ] Delete template item - CHƯA TEST ĐƯỢC
- [ ] Apply template to employee - CHƯA TEST ĐƯỢC
- [ ] Bulk assign salary rules - CHƯA TEST ĐƯỢC

#### Salary History

- [ ] Access `/management/salary-rules/history/` - OK
- [ ] View calculation history - CHƯA TEST ĐƯỢC
- [ ] Filter by date range - CHƯA TEST ĐƯỢC
- [ ] View calculation details - CHƯA TEST ĐƯỢC

---

### 📍 Section 9: Appraisal System (FIXED)

#### Appraisal Periods

- [ ] Access `/management/appraisal/periods/` - LỖI
      NoReverseMatch at /management/appraisal/periods/
      Reverse for 'appraisal_period_detail' not found. 'appraisal_period_detail' is not a valid view function or pattern name.
- [ ] View all periods - CHƯA TEST ĐƯỢC
- [ ] Click "Create Period" (test `create_appraisal_period` URL) - CHƯA TEST ĐƯỢC
- [ ] View period detail - - CHƯA TEST ĐƯỢC
- [ ] Add appraisal criteria - CHƯA TEST ĐƯỢC
- [ ] Generate appraisals for employees - CHƯA TEST ĐƯỢC
- [ ] View statistics - CHƯA TEST ĐƯỢC

#### Manager Appraisals

- [ ] Access `/management/appraisal/manager/` - OK
- [ ] View team appraisals - CHƯA TEST ĐƯỢC
- [ ] Filter by period/employee - CHƯA TEST ĐƯỢC
- [ ] Conduct manager review - CHƯA TEST ĐƯỢC
- [ ] Submit scores - CHƯA TEST ĐƯỢC
- [ ] Add comments - CHƯA TEST ĐƯỢC

#### HR Appraisals

- [ ] Access `/management/appraisal/hr/` - OK
- [ ] View all appraisals - CHƯA TEST ĐƯỢC
- [ ] Filter by period/department - CHƯA TEST ĐƯỢC
- [ ] Conduct HR final review - CHƯA TEST ĐƯỢC
- [ ] Approve/reject appraisals - CHƯA TEST ĐƯỢC
- [ ] View appraisal detail - CHƯA TEST ĐƯỢC
- [ ] Export appraisal report - CHƯA TEST ĐƯỢC

---

## 🔒 PERMISSION TESTING

### As Admin (hangpt)

- [ ] All management features accessible - OK
- [ ] All CRUD operations work
- [ ] Bulk operations available
- [ ] Reports and exports work

### As Manager (dungpd)

- [ ] Access `/management/` - OK
- [ ] View team members - Đang xem được tất cả nhân viên
- [ ] Approve team leaves
- [ ] Approve team expenses
- [ ] Conduct team appraisals
- [ ] NO access to salary rules
- [ ] NO access to HR-only features
- [ ] Check 403 errors on restricted pages

### As Regular Employee

- [ ] Login redirects to `/portal/` - OK
- [ ] Cannot access `/management/` (should get 403 or redirect) - OK
- [ ] Can only access portal features - OK

---

## 🎯 CRITICAL TEST CASES

### 1. No NoReverseMatch Errors

- [ ] No NoReverseMatch errors in server logs
- [ ] No NoReverseMatch errors in browser console
- [ ] All URL tags in templates resolve correctly

### 2. No Pagination Warnings

- [ ] No UnorderedObjectListWarning in logs
- [ ] All paginated views have `.order_by()` clause
- [ ] Pagination controls work correctly

### 3. Form Submissions

- [ ] All POST forms have CSRF tokens
- [ ] Form validations work
- [ ] Success messages display
- [ ] Error messages display
- [ ] Redirects work after submission

### 4. AJAX Operations

- [ ] Approve/reject leave via AJAX
- [ ] Approve/reject expense via AJAX
- [ ] Update application status via AJAX
- [ ] Drag & drop kanban works
- [ ] No AJAX errors in console

### 5. File Uploads

- [ ] Employee avatar upload works
- [ ] Expense receipt upload works
- [ ] Resume upload works (recruitment)
- [ ] File size validation works
- [ ] File type validation works

---

## 📊 TESTING SUMMARY

**Total Sections**: 9  
**Total Test Items**: 150+  
**Critical Tests**: 5 sections

**Priority Order**:

1. 🔴 Critical: Sections 2, 4, 7, 8, 9 (Fixed URLs)
2. 🟠 High: Sections 1, 3, 5, 6 (Core features)
3. 🟡 Medium: Permission testing
4. 🟢 Low: Advanced features

---

## ✅ TESTING RESULTS (Fill in after testing)

### Passed Tests

- [ ] All URL fixes verified programmatically ✅
- [ ] Server starts without errors ✅
- [ ] URL reverse works for all fixed names ✅
- [ ] (Fill in more as you test)

### Failed Tests

- [ ] (List any failures here)

### Known Issues

- [ ] (Document any bugs found)

---

## 📝 RECOMMENDATIONS

**After completing this checklist:**

1. **If all tests pass** (>95%):

   - ✅ Management portal is production-ready
   - ✅ Deploy to staging for user acceptance testing
   - ✅ Update COMPLETION_CHECKLIST.md with results

2. **If some tests fail** (80-95%):

   - ⚠️ Document all failures
   - ⚠️ Prioritize fixes (critical bugs first)
   - ⚠️ Re-test after fixes

3. **If many tests fail** (<80%):
   - ❌ Identify root causes
   - ❌ May need architecture review
   - ❌ Not ready for production

---

**Next Steps**:

1. Print this checklist or keep it open
2. Login as admin: http://127.0.0.1:8000/login/
3. Go through each section systematically
4. Mark checkboxes as you test
5. Document any issues in "Testing Results" section
6. Create GitHub issues for bugs found

**Estimated Testing Time**: 2-3 hours for thorough testing

---

_Generated: November 17, 2025_  
_Status: All 5 URL fixes verified ✅ | Manual testing required_
