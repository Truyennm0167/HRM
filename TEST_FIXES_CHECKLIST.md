# CHECKLIST TEST CÁC FIX - Phase 3

**Server:** http://127.0.0.1:8000/
**Date:** November 23, 2025

---

## ✅ FIX #1: Split Filter Error - Leaves List

**URL:** http://127.0.0.1:8000/portal/leaves/

### Test Steps:

1. [ ] Navigate to Portal → Nghỉ phép
2. [ ] Click "Bộ lọc nâng cao" to expand filter
3. [ ] Check dropdown "Năm"
   - **Expected:** Shows options: Tất cả, 2023, 2024, 2025, 2026
   - **Expected:** No TemplateSyntaxError about 'split' filter
4. [ ] Select year "2025" → Click "Lọc"
5. [ ] Verify filter works without errors

**Status:** FAIL
**Notes:**

- Chưa hiển thị Loại phép trong Danh sách đơn nghỉ phép
- Lọc theo Trạng thái không hoạt động
- Tìm kiếm theo lý do đang hoạt động không ok lắm, Khi tôi search "Đám giỗ" thì không hiển thị các record có lý do liên quan đến đám giỗ. Khi search "đám giỗ" thì mới hiển thị ra các record "Về quê có đám giỗ", "Nhà có đám giỗ"
- Khi bấm reset thì mặc định ô tìm kiếm theo Lý do sẽ mặc định là None, tôi cần bạn bỏ chữ None này ra, vì khi tôi muốn lọc theo Năm thì truy vấn trên url lại có thêm None vào (/portal/leaves/?q=None&leave_type=&status=&year=2025)
- Tôi muốn Thống kê nghỉ phép trong trang Nghỉ phép /portal/leaves/ sẽ hiển thị các thống kê sau: Phép năm còn lại, Chờ duyệt, Số ngày nghỉ tháng xx (tháng hiện tại), Số ngày nghỉ Năm xx (năm hiện tại)
- Không thể xem chi tiết Đơn nghỉ phép:
  NoReverseMatch at /portal/leaves/97/
  Reverse for 'portal_leaves_list' not found. 'portal_leaves_list' is not a valid view function or pattern name.
- Hủy đơn nghỉ phép đang lỗi. Khi tôi bấm hủy đơn và xác nhận hủy thì nhận được thông báo Có lỗi xảy ra khi hủy đơn, nhưng khi tải lại trang thì đơn đã được hủy
- Tính năng xem lịch nhóm chưa hoạt động

---

## ✅ FIX #2: Payroll Filter Status Values

**URL:** http://127.0.0.1:8000/portal/payroll/

### Test Steps:

1. [ ] Navigate to Portal → Bảng lương
2. [ ] Click "Bộ lọc" to expand
3. [ ] Check "Trạng thái" dropdown
   - **Expected:** Shows: Tất cả, Chưa xác nhận, Đã xác nhận
   - **Expected:** NO "Đã duyệt" or "Đã thanh toán" options
4. [ ] Select "Chưa xác nhận" → Click "Lọc"
5. [ ] Verify only pending payrolls show

**Status:** FAIL
**Notes:**

- Hủy đơn chi phí đang lỗi. Khi tôi bấm hủy đơn và xác nhận hủy thì nhận được thông báo Có lỗi xảy ra khi hủy đơn, nhưng khi tải lại trang thì đơn đã được hủy
- Thống kê Chờ duyệt, Đã duyệt đang hiển thị chưa đúng (0đ) trong khi đang có đơn chờ duyệt và đã duyệt

---

## ✅ FIX #3: Expense Detail Display Fields

**URL:** http://127.0.0.1:8000/portal/expenses/
**Then:** Click any expense → View detail

### Test Steps:

1. [ ] Navigate to Chi phí → Click any expense
2. [ ] Verify "Loại chi phí" displays correctly (not "get_expense_type_display")
3. [ ] Verify "Ngày phát sinh" displays in d/m/Y format
4. [ ] If expense is approved, check "Người phê duyệt" shows name (not "get_full_name")
5. [ ] Verify no AttributeError or missing field errors

**Status:** PASS
**Notes:**

---

## ✅ FIX #4 & #5: Expense List Filter & Status Display

**URL:** http://127.0.0.1:8000/portal/expenses/

### Test Steps - Filters:

1. [ ] Click "Bộ lọc nâng cao"
2. [ ] Check search box - should be empty by default (not "None")
3. [ ] Check "Trạng thái" dropdown:
   - **Expected:** Tất cả, Chờ duyệt, Đã duyệt, Từ chối
   - **Expected:** NO "Đã thanh toán" option
4. [ ] Select "Chờ duyệt" → Click "Lọc"
5. [ ] Verify filter works

### Test Steps - Status Badges:

1. [ ] Look at status column in expense list
2. [ ] Verify badges show correctly:
   - **Pending:** Yellow badge "Chờ duyệt"
   - **Approved:** Green badge "Đã duyệt"
   - **Rejected:** Red badge "Bị từ chối"
   - **Cancelled:** Gray badge "Đã hủy"
3. [ ] No blank status columns

**Status:** FAIL
**Notes:** => Không có bộ lọc theo trạng thái Đã hủy

---

## ✅ FIX #6: Profile Page - joining_date Error

**URL:** http://127.0.0.1:8000/portal/profile/

### Test Steps:

1. [ ] Navigate to Portal → Hồ sơ
2. [ ] Verify NO AttributeError about 'joining_date'
3. [ ] Check "Ngày vào" field displays correctly
4. [ ] Check work duration calculation shows (X năm Y tháng)
5. [ ] Verify all stats display: leaves taken, attendance days, late count, expenses count

**Status:** FAIL
**Notes:**
AttributeError at /portal/profile/
'Employee' object has no attribute 'date_of_joining'

---

## ✅ FIX #8 & #9: Approvals Dashboard

**URL:** http://127.0.0.1:8000/portal/approvals/
**Note:** Must login as Manager

### Test Steps - Leaves Section:

1. [ ] Navigate to Phê duyệt
2. [ ] Check "Đơn nghỉ phép chờ duyệt" section
3. [ ] Verify employee names display correctly (not "full_name")
4. [ ] Verify leave type shows name (e.g., "Phép năm") not object
5. [ ] Click green ✓ button (Approve)
   - **Expected:** SweetAlert popup appears
   - **Expected:** "Duyệt đơn nghỉ phép?" dialog
6. [ ] Click "Duyệt" → Should send POST request via AJAX
7. [ ] Click red ✗ button (Reject)
   - **Expected:** Dialog asks for reason
8. [ ] Test same for expenses section

### Test Steps - Expenses Section:

1. [ ] Check "Chi phí chờ duyệt" section
2. [ ] Verify employee names display
3. [ ] Verify money amounts have thousand separators (1,000,000đ not 1000000đ)
4. [ ] Test approve/reject buttons same as leaves

**Status:** FAIL
**Notes:**
TemplateSyntaxError at /portal/approvals/
Invalid filter: 'intcomma'

---

## ✅ FIX #10: Team Leaves - View Detail (404 Fix)

**URL:** http://127.0.0.1:8000/portal/team/leaves/
**Note:** Must login as Manager

### Test Steps:

1. [ ] Navigate to Duyệt nghỉ phép - Nhóm của tôi
2. [ ] Click "Xem" (eye icon) on any leave request
3. [ ] Verify detail page opens WITHOUT 404 error
4. [ ] URL should be: `/portal/team/leaves/{id}/`
5. [ ] Manager can see team member's leave details
6. [ ] Can approve/reject from detail page

**Status:** FAIL
**Notes:**
Page not found (404)
No LeaveRequest matches the given query.
Request Method: GET
Request URL: http://127.0.0.1:8000/portal/leaves/95/
Raised by: app.portal_views.leave_detail
Using the URLconf defined in hrm.urls, Django tried these URL patterns, in this order:

admin/
login/ [name='login']
logout/ [name='logout']
test-login/ [name='test_login']
portal/ [name='portal_dashboard']
portal/ dashboard/ [name='portal_dashboard_alt']
portal/ leaves/ [name='portal_leaves']
portal/ leaves/create/ [name='portal_leave_create']
portal/ leaves/<int:leave_id>/ [name='portal_leave_detail']
The current path, portal/leaves/95/, matched the last one.

---

## ✅ FIX #11: Team Expenses - View Detail & Money Format

**URL:** http://127.0.0.1:8000/portal/team/expenses/
**Note:** Must login as Manager

### Test Steps:

1. [ ] Navigate to Duyệt chi phí - Nhóm của tôi
2. [ ] Check "Tổng chờ duyệt" has thousand separators
3. [ ] Click "Xem" on any expense
4. [ ] Verify detail page opens WITHOUT 404 error
5. [ ] URL should be: `/portal/team/expenses/{id}/`
6. [ ] Manager can see team member's expense details
7. [ ] All money amounts formatted with commas

**Status:** FAIL
**Notes:**

- Tổng chờ duyệt không có phân cách hàng nghìn
- Tôi cần điều chỉnh lại Thống kế Chi phí: Đơn chờ duyệt, Đã từ chối (tháng hiện tại), Tổng đã duyệt tháng (tháng hiện tại), Tổng chờ duyệt
- Không dùng được tính năng Duyệt/Từ chối ở trang /portal/team/expenses/
- Không lọc theo Trạng thái được
- Lỗi khi xem chi tiết Chi phí
  Page not found (404)
  No Expense matches the given query.
  Request Method: GET
  Request URL: http://127.0.0.1:8000/portal/expenses/130/
  Raised by: app.portal_views.expense_detail
  Using the URLconf defined in hrm.urls, Django tried these URL patterns, in this order:

admin/
login/ [name='login']
logout/ [name='logout']
test-login/ [name='test_login']
portal/ [name='portal_dashboard']
portal/ dashboard/ [name='portal_dashboard_alt']
portal/ leaves/ [name='portal_leaves']
portal/ leaves/create/ [name='portal_leave_create']
portal/ leaves/<int:leave_id>/ [name='portal_leave_detail']
portal/ leaves/<int:leave_id>/cancel/ [name='portal_leave_cancel']
portal/ leaves/calendar/ [name='portal_leave_calendar']
portal/ leaves/calendar/data/ [name='portal_leave_calendar_data']
portal/ payroll/ [name='portal_payroll']
portal/ payroll/<int:payroll_id>/ [name='portal_payroll_detail']
portal/ payroll/<int:payroll_id>/download/ [name='portal_payroll_download']
portal/ attendance/ [name='portal_attendance']
portal/ attendance/calendar/ [name='portal_attendance_calendar']
portal/ attendance/check-in/ [name='portal_check_in']
portal/ attendance/check-out/ [name='portal_check_out']
portal/ attendance/today/ [name='portal_today_attendance']
portal/ expenses/ [name='portal_expenses']
portal/ expenses/create/ [name='portal_expense_create']
portal/ expenses/<int:expense_id>/ [name='portal_expense_detail']
The current path, portal/expenses/130/, matched the last one.

---

## 🔧 ADDITIONAL TESTS

### Test: Approve/Reject from Team Views

1. [ ] Go to `/portal/team/leaves/`
2. [ ] Select checkboxes for pending leaves
3. [ ] Click "Duyệt đã chọn" → Verify works
4. [ ] Click single approve button → Verify AJAX call works
5. [ ] Repeat for expenses

**Status:** FAIL
Note: Tính năng không hoạt động, các nút không phản hồi.

---

## 📋 SUMMARY

**Total Fixes:** 11
**Fixes Passed:** **\_ / 11
**Fixes Failed:** \_** / 11

### Critical Issues Found:

1. ***
2. ***
3. ***

### Notes:

---

---

---

---

## 🚀 NEXT STEPS AFTER TESTING

If all tests pass:

- [ ] Commit changes with message: "fix: Phase 3 critical bugs - templates, filters, approvals"
- [ ] Continue to Task #7: Test Attendance page
- [ ] Continue to Tasks #12-18: New features

If tests fail:

- [ ] Document failures in this checklist
- [ ] Request fixes for specific issues
