# Self-Service Portal - Test Checklist

## Test Account

- **Username**: nv0001
- **Password**: password123
- **Employee**: NV0001 (truyen113113@gmail.com)

## Test Data Created

- ✅ 10 Attendance records (current month)
- ✅ 6 Payroll records (last 6 months)

## Testing Steps

### 1. Login & Authentication

- [ ] Navigate to http://127.0.0.1:8000/accounts/login/
- [ ] Login with nv0001 / password123
- [ ] Check redirect to home page
- [ ] Verify "Portal Nhân Viên" menu appears in sidebar

### 2. Employee Dashboard (`/portal/dashboard/`)

**Test URL**: http://127.0.0.1:8000/portal/dashboard/

**Expected Elements:**

- [ ] Profile card with avatar at top
- [ ] Statistics boxes:
  - [ ] Total working days (current month)
  - [ ] Total working hours (current month)
  - [ ] Current month salary
  - [ ] Remaining leave days
- [ ] Pending actions info-boxes (if any)
- [ ] Quick actions card with 5 links
- [ ] This month expense card
- [ ] Recent activities timeline

**Test Cases:**

- [ ] All statistics show correct values
- [ ] Quick action links work correctly
- [ ] Timeline shows recent activities (if any)
- [ ] Responsive layout on different screen sizes

### 3. Employee Profile (`/portal/profile/`)

**Test URL**: http://127.0.0.1:8000/portal/profile/

**Expected Elements:**

- [ ] Profile card with avatar and basic info
- [ ] Employment information card
- [ ] Personal information card
- [ ] Contact information card
- [ ] Work history card (if any)

**Test Cases:**

- [ ] All employee data displayed correctly
- [ ] Avatar shows (or default image if not set)
- [ ] All fields have proper labels and icons
- [ ] Layout is 2-column on desktop

### 4. Edit Profile (`/portal/profile/edit/`)

**Test URL**: http://127.0.0.1:8000/portal/profile/edit/

**Expected Elements:**

- [ ] Profile preview card (left column)
- [ ] Notice card about limited edit permissions
- [ ] Edit form (right column)
- [ ] Editable fields:
  - [ ] Avatar upload
  - [ ] Phone number
  - [ ] Address
  - [ ] Place of residence
- [ ] Disabled (read-only) fields for other data

**Test Cases:**

- [ ] Form loads with current values
- [ ] Avatar upload works (select image file)
- [ ] Avatar preview shows before submit
- [ ] Phone validation (10-11 digits only)
- [ ] Form submission successful
- [ ] Success message displayed
- [ ] Data saved correctly to database
- [ ] Redirect back to profile page

### 5. My Payrolls (`/portal/payrolls/`)

**Test URL**: http://127.0.0.1:8000/portal/payrolls/

**Expected Elements:**

- [ ] Statistics boxes:
  - [ ] Total salary (sum of all)
  - [ ] Average salary
- [ ] Year filter dropdown
- [ ] Payroll table with columns:
  - [ ] Month/Year
  - [ ] Base salary
  - [ ] Coefficient
  - [ ] Working hours
  - [ ] Bonus
  - [ ] Penalty
  - [ ] Total salary
  - [ ] Status badge
  - [ ] View button
- [ ] Pagination (if > 12 records)

**Test Cases:**

- [ ] Table shows all payroll records
- [ ] Statistics calculated correctly
- [ ] Year filter works
- [ ] Status badges show correct colors
- [ ] View button opens modal with details
- [ ] Pagination works (if applicable)
- [ ] Currency formatted with thousands separator

### 6. My Attendance (`/portal/attendance/`)

**Test URL**: http://127.0.0.1:8000/portal/attendance/

**Expected Elements:**

- [ ] Statistics small-boxes:
  - [ ] Total working days
  - [ ] Total working hours
  - [ ] Leave days
  - [ ] Absent days
- [ ] Month filter dropdown
- [ ] Year filter dropdown
- [ ] Attendance table with columns:
  - [ ] Date
  - [ ] Day of week
  - [ ] Status badge
  - [ ] Working hours
  - [ ] Notes
- [ ] Summary section with info-boxes
- [ ] Pagination (if > 31 records)

**Test Cases:**

- [ ] Table shows attendance records
- [ ] Statistics calculated correctly
- [ ] Month filter works
- [ ] Year filter works
- [ ] Status badges show correct colors:
  - Success (green) for "Có làm việc"
  - Warning (yellow) for "Nghỉ phép"
  - Danger (red) for "Nghỉ không phép"
- [ ] Alert shows current filter or "current month"
- [ ] Pagination works (if applicable)

### 7. Navigation & UI

- [ ] Sidebar "Portal Nhân Viên" menu highlights when active
- [ ] All submenu items highlight correctly
- [ ] Breadcrumbs show correct path
- [ ] All icons display properly
- [ ] AdminLTE theme consistent throughout
- [ ] No JavaScript errors in console
- [ ] No CSS layout issues

### 8. Permissions & Security

- [ ] Employee can only see their own data
- [ ] Cannot access other employees' data by changing URL
- [ ] @login_required works (redirects to login if not authenticated)
- [ ] Cannot edit sensitive fields (salary, job title, etc.)
- [ ] Avatar upload validates file type (images only)

### 9. Error Handling

- [ ] Graceful handling when no attendance records
- [ ] Graceful handling when no payroll records
- [ ] Proper message when no data available
- [ ] Default avatar image when not uploaded
- [ ] Form validation errors display correctly

### 10. Performance

- [ ] Pages load quickly (< 2 seconds)
- [ ] Queries optimized (no N+1 queries)
- [ ] Images load properly
- [ ] No console errors

## Issues Found

(Document any issues found during testing)

## Notes

- Browser tested:
- Date tested:
- Tester:

## Status Summary

- Total test cases: ~60
- Passed:
- Failed:
- Blocked:
- Not Tested:
