# Contract Management - Test Checklist

## Test Environment

- **Server**: http://127.0.0.1:8000/
- **Test Account**: nv0001 / password123 (hoặc admin account)
- **Test Date**: November 15, 2025

## Test Data Created

✅ **3 Sample Contracts**:

1. **HD2025001** - Active, ends in 180 days (normal)
2. **HD2025002** - Active, ends in 20 days (⚠️ expiring soon!)
3. **HD2025003** - Draft, starts in 30 days (probation)

## Testing Tasks

### 1. List View (`/contracts/`)

**URL**: http://127.0.0.1:8000/contracts/

- [ ] Page loads without errors
- [ ] Statistics boxes display correctly:
  - [ ] Total contracts: 3
  - [ ] Active contracts: 2
  - [ ] Expiring contracts: 1
- [ ] Contract table displays all 3 contracts
- [ ] Status badges show correct colors:
  - [ ] Active = green badge
  - [ ] Draft = gray badge
- [ ] Expiring warning badge shows on HD2025002
- [ ] "Tạo hợp đồng mới" button visible

**Filters:**

- [ ] Search by contract number works (try "HD2025")
- [ ] Status filter works (select "Active", "Draft")
- [ ] Contract type filter works
- [ ] "Xóa bộ lọc" button clears all filters
- [ ] Filter "Expiring soon" shows only HD2025002

**Actions:**

- [ ] Eye icon (view) works for each contract
- [ ] Edit icon appears only for active/draft contracts
- [ ] Pagination works (if more than 15 contracts)

---

### 2. Contract Detail View (`/contracts/<id>/`)

**Test URLs**:

- HD2025001: http://127.0.0.1:8000/contracts/1/
- HD2025002: http://127.0.0.1:8000/contracts/2/
- HD2025003: http://127.0.0.1:8000/contracts/3/

**For HD2025002 (Expiring Soon)**:

- [ ] Yellow alert banner displays: "Hợp đồng này sẽ hết hạn sau 20 ngày"
- [ ] "Gia hạn hợp đồng" button is visible
- [ ] Expiring badge shows in end date field

**For HD2025003 (Draft)**:

- [ ] "Sửa hợp đồng" button visible
- [ ] "Xóa hợp đồng" button visible
- [ ] Status badge shows "Nháp" (gray)

**Information Display**:

- [ ] Basic info card shows all fields correctly
- [ ] Employee info card displays employee details
- [ ] Financial info card shows salary breakdown
- [ ] Job info card displays workplace and hours
- [ ] Terms & Conditions section readable
- [ ] Metadata shows created_at, updated_at

**2-Column Layout**:

- [ ] Left column: Basic, Employee, Financial cards
- [ ] Right column: Job, Terms, Metadata cards
- [ ] Responsive (stacks on mobile)

---

### 3. Create Contract (`/contracts/create/`)

**URL**: http://127.0.0.1:8000/contracts/create/

**Form Display**:

- [ ] All required fields marked with red asterisk (\*)
- [ ] Employee dropdown populated
- [ ] Contract type dropdown has all 5 types
- [ ] Date inputs use HTML5 date picker
- [ ] Salary inputs have proper formatting hints

**Form Submission**:

1. Fill in all required fields:

   - Contract number: HD2025004
   - Employee: Select any
   - Contract type: definite
   - Signed date: today
   - Start date: tomorrow
   - End date: 1 year from start
   - Salary: 15000000
   - Workplace: Test location
   - Working hours: 8 hours/day
   - Terms: Test terms
   - Status: active

2. Submit form:
   - [ ] No validation errors
   - [ ] Success message appears
   - [ ] Redirects to contract detail page
   - [ ] New contract displays correctly

**Validation Tests**:

- [ ] Try duplicate contract number → Error
- [ ] Try end date before start date → Error
- [ ] Try salary = 0 → Error
- [ ] Try indefinite contract with end date → Error
- [ ] Try definite contract without end date → Error

---

### 4. Edit Contract (`/contracts/<id>/edit/`)

**Test with HD2025003 (Draft)**:

**URL**: http://127.0.0.1:8000/contracts/3/edit/

- [ ] Form pre-filled with current values
- [ ] Can modify contract number
- [ ] Can change dates
- [ ] Can update salary
- [ ] Submit saves changes
- [ ] Success message displays
- [ ] Redirects to detail page
- [ ] Changes reflected on detail page

**Test with HD2025002 (Active)**:

- [ ] Edit button visible on detail page
- [ ] Form allows editing
- [ ] Can modify most fields
- [ ] Save works correctly

**Restriction Test**:

- [ ] Try editing after changing status to "terminated" → Should show error
- [ ] Try editing expired contract → Should show error

---

### 5. Renew Contract (`/contracts/<id>/renew/`)

**Test with HD2025002 (Expiring Soon)**:

**URL**: http://127.0.0.1:8000/contracts/2/renew/

**Pre-fill Check**:

- [ ] Blue info box shows old contract details
- [ ] Form pre-filled with old contract data
- [ ] Start date defaults to day after old end date
- [ ] Employee field matches old contract
- [ ] Salary/terms copied from old contract

**Renewal Process**:

1. Update contract number: HD2025002-R1
2. Adjust start/end dates if needed
3. Modify salary if needed
4. Click "Gia hạn"

**Expected Results**:

- [ ] New contract created successfully
- [ ] New contract status = active
- [ ] Old contract (HD2025002) status changed to "renewed"
- [ ] New contract has `renewed_from` = HD2025002
- [ ] Redirects to new contract detail
- [ ] Renewal history shows on both contracts

**Test Renewal Chain**:

- [ ] View HD2025002 detail page
- [ ] "Renewal History" section shows successor contract
- [ ] View new contract detail page
- [ ] Shows "Hợp đồng này được gia hạn từ: HD2025002"

---

### 6. Terminate Contract (`/contracts/<id>/terminate/`)

**Test with HD2025001 (Active)**:

**Process**:

1. Open contract detail: http://127.0.0.1:8000/contracts/1/
2. Click "Chấm dứt hợp đồng" button
3. Modal opens

**Modal Form**:

- [ ] Termination date field displays
- [ ] Termination reason textarea displays
- [ ] Both fields are required
- [ ] "Xác nhận chấm dứt" button works

**Fill and Submit**:

- Termination date: Today
- Reason: "Nhan vien xin nghi viec"
- Click confirm

**Expected Results**:

- [ ] Contract status changes to "terminated"
- [ ] Status badge changes to red "Đã chấm dứt"
- [ ] Termination info card appears on detail page
- [ ] Shows termination date and reason
- [ ] "Chấm dứt" button no longer visible
- [ ] "Gia hạn" button no longer visible
- [ ] "Sửa" button no longer visible

---

### 7. Delete Contract (`/contracts/<id>/delete/`)

**Test with HD2025003 (Draft)**:

**Process**:

1. Open draft contract: http://127.0.0.1:8000/contracts/3/
2. Click "Xóa hợp đồng" button
3. Confirmation modal opens

**Modal**:

- [ ] Warning message displays
- [ ] "Hành động này không thể hoàn tác!" shown
- [ ] "Xác nhận xóa" button (red)

**Submit**:

- [ ] Click confirm
- [ ] Contract deleted from database
- [ ] Redirects to contract list
- [ ] Success message: "Hợp đồng HD2025003 đã được xóa!"
- [ ] Contract no longer in list
- [ ] Total count decreases

**Restriction Test**:

- [ ] Try deleting active contract → Button not visible
- [ ] Try accessing delete URL for active contract → Error message

---

### 8. Filters and Search

**Test on List Page**:

**Search**:

- [ ] Search "HD2025" → Shows all contracts starting with HD2025
- [ ] Search employee code → Shows that employee's contracts
- [ ] Search employee name → Works with partial match
- [ ] Clear search → Shows all contracts

**Status Filter**:

- [ ] Select "Active" → Shows only 2 active contracts
- [ ] Select "Draft" → Shows only 1 draft contract
- [ ] Select "Terminated" → Shows 0 or terminated contracts
- [ ] Select "All" → Shows all contracts

**Contract Type Filter**:

- [ ] Select "Definite" → Shows definite contracts
- [ ] Select "Probation" → Shows probation contracts
- [ ] Combine with status filter → Works correctly

**Department Filter**:

- [ ] Select department → Shows contracts for that department
- [ ] Works with other filters

**Expiring Filter**:

- [ ] Click "Xem chi tiết" on expiring box
- [ ] URL shows `?expiring=true`
- [ ] Only HD2025002 displays (20 days left)
- [ ] Other contracts hidden

**Combined Filters**:

- [ ] Apply multiple filters together
- [ ] Results correctly filtered
- [ ] Pagination preserves all filters

---

### 9. File Upload/Download

**Upload Test**:

1. Go to create/edit form
2. Select a PDF or DOC file
3. Submit form

**Expected**:

- [ ] File uploads successfully
- [ ] File saved to `media/contracts/` directory
- [ ] "Tải file HĐ" button appears on detail page
- [ ] Click download → File downloads correctly
- [ ] File opens properly

**File Validation**:

- [ ] Try uploading image file → Should show error (only PDF/DOC accepted)
- [ ] Try very large file → Check size limit

---

### 10. Expiration Alerts

**Visual Alerts**:

- [ ] HD2025002 shows yellow badge on list
- [ ] HD2025002 shows warning banner on detail
- [ ] Banner says "sẽ hết hạn sau 20 ngày"
- [ ] "Expiring soon" statistic box shows count = 1

**Alert Threshold**:

- Create contract expiring in 31 days
- [ ] Should NOT show expiring alert (threshold is 30 days)
- Create contract expiring in 29 days
- [ ] SHOULD show expiring alert

---

### 11. Permissions and Access Control

**Login Required**:

- [ ] Accessing any contract URL while logged out → Redirects to login
- [ ] After login → Redirects back to requested page

**Status-based Permissions**:

- [ ] Draft contracts: Can edit, can delete
- [ ] Active contracts: Can edit, can renew, can terminate
- [ ] Terminated contracts: Read-only, no actions
- [ ] Expired contracts: Read-only, no actions
- [ ] Renewed contracts: Read-only, shows successor

---

### 12. UI/UX

**Responsive Design**:

- [ ] Desktop: 2-column layout works
- [ ] Tablet: Columns stack appropriately
- [ ] Mobile: Single column, buttons accessible

**AdminLTE Components**:

- [ ] Small-boxes (statistics) render correctly
- [ ] Cards have proper borders and shadows
- [ ] Buttons have correct colors (success/warning/danger)
- [ ] Badges show proper colors by status
- [ ] Modals open/close smoothly
- [ ] Forms have proper spacing

**Navigation**:

- [ ] Breadcrumbs show correct path
- [ ] Sidebar "Quản lý hợp đồng" menu highlights
- [ ] Active page highlighted in submenu
- [ ] "Quay lại" button works on all pages

**Messages**:

- [ ] Success messages display after actions
- [ ] Error messages show when validation fails
- [ ] Messages auto-dismiss or have close button

---

### 13. Edge Cases

**Date Logic**:

- [ ] Create indefinite contract (no end date) → Works
- [ ] Try to renew indefinite contract → Check behavior
- [ ] Contract with start date in past → Allows
- [ ] Contract with start date in future → Allows

**Empty States**:

- [ ] Delete all contracts → List shows "Không tìm thấy hợp đồng"
- [ ] Filter with no results → Shows empty message
- [ ] Employee with no contracts → Create first contract works

**Renewal Chain**:

- [ ] Renew contract multiple times → Chain maintains
- [ ] View original contract → Shows all successors
- [ ] View latest contract → Shows chain back to original

**Concurrent Editing**:

- [ ] Open same contract in 2 tabs
- [ ] Edit in tab 1, save
- [ ] Edit in tab 2, save
- [ ] Check which version is saved (last write wins)

---

### 14. Performance

**Page Load**:

- [ ] List page loads in < 2 seconds
- [ ] Detail page loads in < 1 second
- [ ] Form page loads in < 1 second

**Query Optimization**:

- [ ] Check Django Debug Toolbar (if enabled)
- [ ] No N+1 queries on list page
- [ ] Detail page queries optimized with select_related

**Large Dataset**:

- [ ] Create 100+ contracts
- [ ] List page still loads quickly
- [ ] Pagination works correctly
- [ ] Filters don't timeout

---

### 15. Browser Compatibility

**Test in Multiple Browsers**:

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if on Mac)

**JavaScript Features**:

- [ ] Date pickers work
- [ ] Modals open/close
- [ ] Form validation triggers
- [ ] AJAX requests succeed

---

## Test Results Summary

### Functionality Tests

- Total Test Cases: ~120
- Passed: \_\_\_
- Failed: \_\_\_
- Blocked: \_\_\_
- Not Tested: \_\_\_

### Critical Issues Found

1.
2.
3.

### Minor Issues Found

1.
2.
3.

### Recommendations

1.
2.
3.

---

## Test Environment Details

- **OS**: Windows
- **Browser**:
- **Django**: 4.2.16
- **Python**: 3.13
- **Database**: SQLite
- **Date**: November 15, 2025

## Tester Notes

(Add any observations, suggestions, or additional findings here)

---

## Quick Test URLs

**Main Pages**:

- List: http://127.0.0.1:8000/contracts/
- Create: http://127.0.0.1:8000/contracts/create/

**Existing Contracts**:

- HD2025001 (Active, 180 days): http://127.0.0.1:8000/contracts/1/
- HD2025002 (Expiring, 20 days): http://127.0.0.1:8000/contracts/2/
- HD2025003 (Draft): http://127.0.0.1:8000/contracts/3/

**Actions**:

- Edit HD2025003: http://127.0.0.1:8000/contracts/3/edit/
- Renew HD2025002: http://127.0.0.1:8000/contracts/2/renew/
- Terminate HD2025001: http://127.0.0.1:8000/contracts/1/ (click button)

**Filters**:

- Expiring only: http://127.0.0.1:8000/contracts/?expiring=true
- Active only: http://127.0.0.1:8000/contracts/?status=active
- Draft only: http://127.0.0.1:8000/contracts/?status=draft

---

**Status**: Ready for manual testing ✅
