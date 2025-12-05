# Phase 3 Implementation - Testing Guide

## Server Status

✅ **Server running at:** http://127.0.0.1:8000/  
✅ **All imports resolved** (reportlab installed)  
✅ **No Django system errors**

---

## Feature 1 & 2: Search, Filter & Pagination

### Test 1.1: Employee Leaves List

**URL:** `/portal/leaves/`

**Test Steps:**

1. Navigate to Portal → Nghỉ phép - LỖI
   AttributeError at /portal/leaves/
   'Employee' object has no attribute 'annual_leave_balance'
2. Verify stats cards show: Used/Pending/Remaining leaves - CHƯA TEST ĐƯỢC
3. Click "Bộ lọc nâng cao" to expand filter form - CHƯA TEST ĐƯỢC

**Test Filters:**

- [ ] **Text Search:** Enter keyword in search box → Submit
- [ ] **Leave Type:** Select a leave type from dropdown → Submit
- [ ] **Status:** Select Pending/Approved/Rejected/Cancelled → Submit
- [ ] **Year:** Select 2024 or 2025 → Submit
- [ ] **Combined Filters:** Select multiple filters → Submit
- [ ] **Reset Button:** Click Reset → All filters cleared

**Test Pagination:**

- [ ] Page shows "Hiển thị X-Y / Total đơn" at top right
- [ ] If more than 25 records, pagination controls appear at bottom
- [ ] Click page 2 → Filters remain applied
- [ ] Click Next (›) → Filters persist
- [ ] Click Previous (‹) → Filters persist
- [ ] Click First page («) or Last page (») → Filters persist

**Expected Results:**

- Only matching records displayed
- Pagination shows max 25 items per page
- URL contains all filter params: `?status=Pending&leave_type=1&year=2024&q=search&page=2`
- Stats cards update based on filters

=> FAILED
AttributeError at /portal/leaves/
'Employee' object has no attribute 'annual_leave_balance'

---

### Test 1.2: Employee Expenses List

**URL:** `/portal/expenses/`

**Test Steps:**

1. Navigate to Portal → Chi phí - OK
2. Verify stats cards show: Pending Amount/Approved Amount/Total Expenses
3. Click "Bộ lọc nâng cao" to expand filter form

**Test Filters:**

- [ ] **Text Search:** Search by description keyword → Submit
- [ ] **Category:** Select expense category → Submit
- [ ] **Status:** Select Pending/Approved/Rejected/Paid → Submit
- [ ] **Year:** Select year → Submit
- [ ] **Combined Filters:** Multiple filters together
- [ ] **Reset Button:** Clears all filters

**Test Pagination:**

- [ ] Shows item count at top right
- [ ] 25 items per page
- [ ] Pagination controls work with filters preserved
- [ ] URL format: `?status=Pending&category=1&year=2024&q=search&page=2`

=> FAIL:

- Danh sách đơn hoàn tiền không hiển thị Loại chi phí, Ngày phát sinh
- Số tiền không được định dạng đúng (không phân cách đơn vị tiền tệ)

---

### Test 1.3: Employee Payroll List

**URL:** `/portal/payroll/`

**Test Steps:**

1. Navigate to Portal → Bảng lương - OK
2. Click "Bộ lọc" to expand filter form

**Test Filters:**

- [ ] **Year:** Select year (2023-2026) → Submit
- [ ] **Month:** Select month (1-12) → Submit
- [ ] **Status:** Select pending/approved/paid → Submit
- [ ] **Combined Filters:** Year + Month + Status
- [ ] **Reset Button:** Clear filters

**Test Pagination:**

- [ ] Shows item count
- [ ] 25 items per page
- [ ] Pagination preserves filters
- [ ] URL format: `?year=2024&month=11&status=paid&page=2`

=> FAIL:

- Trạng thái hiển thị chưa đúng, hiện tại chỉ hiển thị trạng thái Đang xử lý
- Chức năng lọc theo trạng thái chưa dùng được
- Số tiền chưa được định dạng đúng (không phân cách đơn vị tiền tệ)
- Xem chi tiết Bảng lương hiện tại số tiền cũng chưa hiển thị đúng, Không hiển thị tên nhân viên, chức vụ, và khi in phiếu lương thì có những nội dung "rác"

---

## Feature 3: Bulk Actions for Managers

### Test 3.1: Team Leaves Bulk Actions

**URL:** `/portal/team/leaves/`  
**Prerequisites:** Must be logged in as a manager with pending leave requests in team

**Test Steps:**

1. **Checkbox Selection:**

   - [ ] Only pending leaves have checkboxes
   - [ ] Approved/Rejected leaves don't have checkboxes
   - [ ] Click individual checkboxes → Selected count updates
   - [ ] Click "Select All" checkbox in header → All pending selected
   - [ ] Uncheck "Select All" → All deselected
   - [ ] Select some (not all) → "Select All" shows indeterminate state
         => FAIL: Không chọn được Tất cả, không chọn được từng nhân viên

2. **Bulk Approve:**

   - [ ] Select 2-3 pending leaves
   - [ ] Button shows "Duyệt đã chọn (3)"
   - [ ] Button enabled only when items selected
   - [ ] Click bulk approve button
   - [ ] Confirm dialog appears: "Duyệt 3 đơn nghỉ phép?"
   - [ ] Click "Duyệt tất cả"
   - [ ] Success message appears
   - [ ] Page reloads, leaves now show "Đã duyệt"
   - [ ] Leave balances deducted correctly
         => FAIL: Không dùng được tính năng này

3. **Bulk Reject:**

   - [ ] Select multiple pending leaves
   - [ ] Button shows "Từ chối đã chọn"
   - [ ] Click bulk reject button
   - [ ] Reason textarea appears in dialog
   - [ ] Try submitting without reason → Validation error
   - [ ] Enter reason → Click "Từ chối tất cả"
   - [ ] Success message appears
   - [ ] Leaves now show "Đã từ chối"
         => FAIL: Không dùng được tính năng này

4. **Error Handling:**
   - [ ] Select leave with insufficient balance → Partial success message
   - [ ] Shows which leaves failed and why
         => CHƯA TEST ĐƯỢC

**DataTables Compatibility:**

- [ ] Filter buttons work (Tất cả/Chờ duyệt/Đã duyệt/Đã từ chối)
- [ ] Checkboxes remain functional with DataTables
      => CHƯA TEST ĐƯỢC

FAIL:

- Các thông tin như Đơn chờ duyệt, Đã duyệt,...chưa hiển thị đúng
- Không dùng filter Tất cả, Chờ duyệt, Đã duyệt, Đã từ chối được
- Thông tin ở cột Trạng thái không hiển thị
- Không xem được chi tiết Đơn nghỉ phép:
  Page not found (404)
  No LeaveRequest matches the given query.

---

### Test 3.2: Team Expenses Bulk Actions

**URL:** `/portal/team/expenses/`  
**Prerequisites:** Manager with pending expense requests

**Test Steps:**

1. **Checkbox Selection:**

   - [ ] Only pending expenses have checkboxes
   - [ ] Select All checkbox works
   - [ ] Selected count updates correctly
   - [ ] Indeterminate state for partial selection

2. **Bulk Approve:**

   - [ ] Select multiple expenses
   - [ ] Button shows correct count
   - [ ] Confirm dialog appears
   - [ ] Expenses approved successfully
   - [ ] Status changes to "Đã duyệt"

3. **Bulk Reject:**

   - [ ] Select expenses → Click reject
   - [ ] Reason textarea required
   - [ ] Reason saved to all rejected expenses
   - [ ] Success message shows count

4. **DataTables Integration:**
   - [ ] Filter by status works
   - [ ] Pagination doesn't break checkboxes
   - [ ] Column search works

FAIL:

- Danh sách đơn hoàn tiền hiển thị chưa đúng: Không hiển thị Loại chi phí, Ngày phát sinh, Trạng thái.
- Không xem được Chi tiết đơn hoàn tiền:
  Page not found (404)
  No Expense matches the given query.
- Không dùng được filter Tất cả, Chờ duyệt, Đã duyệt, Đã từ chối được
- Số tiền chưa được định dạng đúng (không phân cách đơn vị tiền tệ)

---

## Feature 4: Validation Error Display

### Test 4.1: Leave Request Form

**URL:** `/portal/leaves/create/`

**Test Steps:**

1. **Missing Required Fields:**

   - [ ] Submit form empty
   - [ ] Error appears under each field with icon: "⚠️ This field is required"
   - [ ] Error has red background (invalid-feedback class)
   - [ ] Error is clearly visible below field
         => PASS

2. **Invalid Dates:**

   - [ ] Enter end_date before start_date → Submit
   - [ ] Error shows: "End date must be after start date"
   - [ ] Error formatted with icon
         => FAIL:

- Hệ thống thông báo "Vui lòng kiểm tra lại thông tin form."
- Thông tin số dư phép không hiển thị
- Không truy cập được trang Nghỉ phép:
  AttributeError at /portal/leaves/
  'Employee' object has no attribute 'annual_leave_balance'

3. **Insufficient Balance:**
   - [ ] Request more days than available
   - [ ] Django message appears at top (not form field error)
   - [ ] Form persists entered data
         => CHƯA TEST ĐƯỢC

**Visual Check:**

- [ ] Errors have `invalid-feedback d-block` class
- [ ] Icon `fas fa-exclamation-circle` appears before text
- [ ] Red text color
- [ ] Appears below form field
      => CHƯA TEST ĐƯỢC

---

### Test 4.2: Expense Request Form

**URL:** `/portal/expenses/create/`

**Test Steps:**

1. **Field Validation:**

   - [ ] Submit empty → All required fields show errors
   - [ ] Errors formatted with icons and red background
   - [ ] File upload errors show below upload field
         => FAIL: Không hiển thị bất cứ thông báo nào

2. **File Size Validation:**

   - [ ] Upload file > 5MB
   - [ ] Error appears: "Kích thước file quá lớn!"
   - [ ] Error formatted consistently
         => PASS

3. **Amount Validation:**
   - [ ] Enter negative amount → Error
   - [ ] Enter non-numeric → Error
   - [ ] Errors clear when corrected
         => PASS

**Visual Check:**

- [ ] Same styling as leave form errors
- [ ] Icons consistent across all fields
      => PASS

---

### Test 4.3: Profile Edit Form

**URL:** `/portal/profile/edit/`

**Test Steps:**

1. **Phone Validation:**

   - [ ] Clear phone field → Submit
   - [ ] Error: "This field is required"
   - [ ] Formatted with icon and red background
         => PASS

2. **Email Validation:**

   - [ ] Enter invalid email format → Submit
   - [ ] Error: "Enter a valid email address"
   - [ ] Formatted consistently
         => PASS

3. **Avatar Upload:**

   - [ ] Upload file > 2MB
   - [ ] Error appears below avatar field
   - [ ] Upload non-image file (e.g., .txt)
   - [ ] Error shows allowed formats
         => PASS

4. **Address Validation:**
   - [ ] Clear address → Submit
   - [ ] Error formatted with icon
         => PASS
         **Visual Check:**

- [ ] All errors use `invalid-feedback d-block`
- [ ] Icons appear on all errors
- [ ] Consistent red styling
      => PASS

Ngoài những tính năng trong phase 3, tôi còn test lại các chức năng khác của portal thì phát hiện có thêm các lỗi sau:

- Không thể check-in:
  ERROR Internal Server Error: /portal/attendance/check-in/
  ERROR "POST /portal/attendance/check-in/ HTTP/1.1" 500 89
- Không thể lọc theo Tháng/Năm
- Chưa thống kê được số lần đi muộn và số lần về sớm
- Không thể truy cập trang Nghỉ phép:
  AttributeError at /portal/leaves/
  'Employee' object has no attribute 'annual_leave_balance'
- Hồ sơ cá nhân hiển thị thiếu Họ và tên, CCCD, Số điện thoại, Chức vụ, Phép năm, Trạng thái, Thống kê năm - Ngày nghỉ phép;Ngày làm việc;Lần đi muộn;Đơn hoàn tiền
- Đơn nghỉ phép chờ duyệt trong phần Phê duyệt chưa hiển thị Tên nhân sự, Loại nghỉ phép. Chưa dùng được tính năng duyệt nhanh hoặc từ chối nhanh
- Chi phí chờ duyệt trong trong phần Phê duyệt chưa hiển thị Tên nhân sự, số tiền chưa được định dạng lại. Chưa dùng được tính năng duyệt nhanh hoặc từ chối nhanh
- Nhân viên trong team hiện tại không hiển thị bất cứ thông tin gì ngoài Avatar
- Hiện tại portal chưa có tính năng Đánh giá hiệu suất dành cho Nhân viên và Quản lý
- Cần thêm Biểu đồ tổ chức vào portal nhân viên và tất cả người dùng đều xem được Biểu đồ tổ chức này
- Ở trang Dashboard hiện tại các số liệu biểu thị cho tiền thì chưa được định dạng

---

## General Testing

### Cross-Browser Testing

- [ ] **Chrome:** All features work
- [ ] **Firefox:** All features work
- [ ] **Edge:** All features work

### Mobile Responsive

- [ ] Filter forms collapse/expand properly
- [ ] Pagination controls stack on mobile
- [ ] Bulk action buttons responsive
- [ ] Error messages readable on small screens

### Performance

- [ ] Lists with 100+ items load quickly
- [ ] Pagination doesn't cause lag
- [ ] Bulk actions process multiple items smoothly
- [ ] Filter queries execute efficiently

### JavaScript Console

- [ ] No JavaScript errors
- [ ] AJAX calls succeed
- [ ] Checkbox events work correctly

---

## Known Limitations / Future Improvements

### Phase 3 Completed Features:

1. ✅ Advanced search & filter on 3 list views
2. ✅ Pagination with filter preservation
3. ✅ Bulk actions for managers (leaves & expenses)
4. ✅ Enhanced form validation display

### Not Yet Implemented (Phase 3 - Feature 5):

- ❌ Notification system with badge count
- ❌ Toast notifications
- ❌ Real-time notification updates

### Potential Issues to Watch:

1. **DataTables Pagination vs Django Pagination:** Currently using DataTables, may need to switch to Django pagination for consistency
2. **Filter Column Index:** DataTables column search uses fixed indices - ensure columns don't change order
3. **Checkbox State:** When filtering with DataTables, checkboxes may reset

---

## Bug Reporting

If you encounter issues, check:

1. Browser console for JavaScript errors
2. Django terminal for Python errors
3. Network tab for failed AJAX requests
4. Database for incorrect data updates

---

## Testing Summary Checklist

### Quick Test (10 minutes):

- [ ] Navigate to leaves list → Apply filters → Test pagination
- [ ] Navigate to expenses list → Apply filters → Test pagination
- [ ] As manager, test bulk approve 2 leaves
- [ ] Submit empty leave form → Check error display

### Full Test (30 minutes):

- [ ] Complete all Test 1.1, 1.2, 1.3 sections
- [ ] Complete Test 3.1 and 3.2
- [ ] Complete Test 4.1, 4.2, 4.3
- [ ] Test cross-browser compatibility
- [ ] Check mobile responsiveness

---

**Server Command:** `python manage.py runserver`  
**Test Date:** November 22, 2025  
**Phase:** Phase 3 - Medium Priority UX Enhancements  
**Status:** Ready for Testing ✅
