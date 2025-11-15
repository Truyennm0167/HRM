# RBAC Testing Guide

## ✅ Completed Tasks

### Task 6: Template Tags ✅

Created `app/templatetags/permission_tags.py` with:

- **Filters**: `has_group`, `has_permission`, `has_any_group`, `has_all_groups`, `user_groups`
- **Simple Tags**: `can_manage_contract`, `can_view_employee_salary`, `can_approve_leave`, `can_approve_expense`
- All tags support superuser bypass

### Task 7: Template Updates ✅

Updated templates with role-based UI:

- **list_contracts.html**: "Create Contract" button only for HR, "Expiring Contracts" for HR/Manager
- **contract_detail.html**: Edit/Delete/Renew buttons only for HR
- **create_edit_contract.html**: Added permission_tags load
- All templates load `{% load permission_tags %}`

### Task 8: Test Users & Contracts ✅

Created test data for RBAC testing:

**Test Users:**

1. **hr_user** (HR Group) - Full access
2. **manager_user** (Manager Group, IT Dept) - Department access
3. **manager_sales** (Manager Group, Sales Dept) - Department access
4. **employee_user** (Employee Group) - Self-service only

**Test Contracts:**

- 6 contracts total
- 3 in IT Department
- 1 in Sales Department
- 5 active contracts
- 1 expiring soon

---

## 🧪 RBAC Testing Instructions

### Test Environment

- **URL**: http://127.0.0.1:8000/
- **Contracts Page**: http://127.0.0.1:8000/contracts/

### Test Credentials

#### 1️⃣ HR User (Full Access)

```
Username: hr_user
Password: hr123456
Group: HR
Department: IT Department
```

**Expected Behavior:**

- ✅ See **ALL** contracts from all departments (IT + Sales)
- ✅ **"Create Contract"** button visible
- ✅ **"Expiring Contracts"** link visible
- ✅ **Edit** button on contracts (draft/active only)
- ✅ **Delete** button on draft contracts
- ✅ **Renew** button on active contracts with end_date
- ✅ Can access `/contracts/create/`
- ✅ Can edit any contract
- ✅ Can view employee contracts report for any department

**Test Steps:**

1. Login as `hr_user`
2. Navigate to "Hợp đồng" → "Danh sách hợp đồng"
3. Verify all 6 contracts are visible
4. Click "Tạo hợp đồng mới" → Should show create form
5. Click "HĐ sắp hết hạn" → Should show expiring contracts report
6. Click "Xem chi tiết" on a contract → Edit/Delete/Renew buttons should be visible
7. Try editing a contract → Should succeed
8. Filter by department → Should show contracts from selected department

---

#### 2️⃣ Manager User - IT (Department Access)

```
Username: manager_user
Password: manager123456
Group: Manager
Department: IT Department
```

**Expected Behavior:**

- ✅ See **ONLY IT Department** contracts (3 contracts)
- ❌ **"Create Contract"** button HIDDEN
- ✅ **"Expiring Contracts"** link visible (shows only IT Dept contracts)
- ❌ **Edit** button HIDDEN
- ❌ **Delete** button HIDDEN
- ❌ **Renew** button HIDDEN
- ✅ Can **view** contract details
- ❌ Cannot access `/contracts/create/` (redirect with error)
- ❌ Cannot edit contracts (redirect with error)
- ✅ Can view employee contracts report for IT Department only

**Test Steps:**

1. Login as `manager_user`
2. Navigate to "Hợp đồng" → "Danh sách hợp đồng"
3. Verify **ONLY 3 contracts** are visible (IT Dept only)
4. Verify "Tạo hợp đồng mới" button is **HIDDEN**
5. Click "HĐ sắp hết hạn" → Should show only IT Department expiring contracts
6. Click "Xem chi tiết" on a contract → Edit/Delete/Renew buttons should be **HIDDEN**
7. Try accessing `/contracts/create/` directly → Should redirect with "Bạn không có quyền" message
8. Try accessing edit URL directly → Should redirect with error
9. Filter by department → Should only show IT contracts (Sales contracts filtered out)

---

#### 3️⃣ Manager User - Sales (Department Access)

```
Username: manager_sales
Password: manager123456
Group: Manager
Department: Sales Department
```

**Expected Behavior:**

- ✅ See **ONLY Sales Department** contract (1 contract)
- ❌ **NOT** see IT Department contracts (should be filtered out)
- ❌ **"Create Contract"** button HIDDEN
- ✅ **"Expiring Contracts"** link visible (shows only Sales Dept contracts)
- ❌ **Edit/Delete/Renew** buttons HIDDEN
- ✅ Can **view** contract details for Sales Dept employees only
- ❌ Cannot access IT Department contracts (403 or redirect)

**Test Steps:**

1. Login as `manager_sales`
2. Navigate to "Hợp đồng" → "Danh sách hợp đồng"
3. Verify **ONLY 1 contract** is visible (Sales Manager contract)
4. Verify **NO IT Department** contracts are shown
5. Try accessing IT contract detail URL directly → Should redirect with "không có quyền" message
6. Click "HĐ sắp hết hạn" → Should show empty or only Sales Department contracts
7. Filter by IT Department → Should show empty (no access)

---

#### 4️⃣ Employee User (No Access)

```
Username: employee_user
Password: employee123456
Group: Employee
Department: IT Department
```

**Expected Behavior:**

- ❌ **Cannot access** `/contracts/` page at all
- ❌ Should get **403 Forbidden** or redirect with error message
- ❌ No "Quản lý hợp đồng" menu item visible
- ✅ Can access self-service portal features only

**Test Steps:**

1. Login as `employee_user`
2. Try navigating to `/contracts/` directly → Should redirect with "Bạn không có quyền" message
3. Verify "Quản lý hợp đồng" menu is hidden or disabled
4. Verify can access "Portal Nhân Viên" features

---

## 🔍 Key RBAC Features to Verify

### 1. Group-Level Access Control

- **Decorators**: `@require_hr`, `@require_manager`, `@require_hr_or_manager`
- **Views Protected**: All 8 Contract views
- **Test**: Try accessing views without proper group membership

### 2. Row-Level Filtering

- **Managers**: Automatically filtered to their department's contracts
- **Logic**: `contracts = contracts.filter(employee__department=user_employee.department)`
- **Test**: Manager should NEVER see contracts from other departments

### 3. Template-Level UI Control

- **Template Tags**: `{% if user|has_group:'HR' %}`, `{% if user|has_any_group:'HR,Manager' %}`
- **Buttons Hidden**: Create/Edit/Delete/Renew buttons for non-HR users
- **Test**: Inspect page source - buttons should not exist in HTML for unauthorized users

### 4. Statistics Filtering

- **Expiring Contracts Report**: Shows only department contracts for Managers
- **Employee Contracts Report**: Checks department permission before showing
- **Test**: Manager should see statistics only for their department

---

## 📊 Expected Test Results

| User              | Contracts Visible | Create | Edit | Delete | Renew | Expiring Report |
| ----------------- | ----------------- | ------ | ---- | ------ | ----- | --------------- |
| hr_user           | ALL (6)           | ✅     | ✅   | ✅     | ✅    | ✅ All Depts    |
| manager_user (IT) | IT Only (3)       | ❌     | ❌   | ❌     | ❌    | ✅ IT Only      |
| manager_sales     | Sales Only (1)    | ❌     | ❌   | ❌     | ❌    | ✅ Sales Only   |
| employee_user     | NO ACCESS         | ❌     | ❌   | ❌     | ❌    | ❌              |

---

## ⚠️ Security Tests

### 1. URL Direct Access

Try accessing URLs directly without permission:

```
❌ /contracts/create/ → HR only
❌ /contracts/1/edit/ → HR only
❌ /contracts/1/delete/ → HR only
❌ /contracts/1/renew/ → HR only
✅ /contracts/1/ → HR or Manager (with department check)
✅ /contracts/expiring/ → HR or Manager (department filtered)
```

### 2. Cross-Department Access

Manager from IT tries to access Sales contract:

```bash
# As manager_user (IT Dept)
# Try accessing Sales Manager contract ID directly
# Expected: Redirect with "Bạn không có quyền truy cập hợp đồng này"
```

### 3. Privilege Escalation

Employee user tries HR functions:

```bash
# As employee_user
# Try accessing /contracts/
# Expected: 403 Forbidden or redirect with error
```

---

## 🐛 Troubleshooting

### Issue: All buttons visible for Manager

**Cause**: Template tags not loaded
**Fix**: Check `{% load permission_tags %}` at top of template

### Issue: Manager sees all contracts

**Cause**: Row-level filtering not applied
**Fix**: Check `manage_contracts` view has department filter logic

### Issue: Employee can access contracts

**Cause**: View decorator missing or incorrect
**Fix**: Check `@require_hr_or_manager` is applied to view

### Issue: 403 page instead of redirect

**Cause**: PermissionDenied raised instead of redirect
**Fix**: Views should check permission and redirect with message

---

## 📝 RBAC Status Summary

**✅ Completed:**

- Django Groups created (HR, Manager, Employee)
- Custom permissions added (8 permissions)
- Permission decorators framework (300 lines)
- All 8 Contract views protected
- Row-level filtering for Managers
- Template tags for UI conditionals
- Templates updated with role checks
- Test users and contracts created

**⏳ Next Steps:**

- Extend RBAC to LeaveRequest views
- Extend RBAC to Expense views
- Extend RBAC to Payroll views
- Add audit logging for permission denials
- Create RBAC admin interface for role assignment

---

## 🌐 Quick Test Links

**After logging in as each user:**

1. **Contracts List**: http://127.0.0.1:8000/contracts/
2. **Create Contract**: http://127.0.0.1:8000/contracts/create/
3. **Expiring Contracts**: http://127.0.0.1:8000/contracts/expiring/
4. **Contract Detail**: http://127.0.0.1:8000/contracts/1/
5. **Edit Contract**: http://127.0.0.1:8000/contracts/1/edit/

**Admin Interface** (for managing groups):
http://127.0.0.1:8000/admin/

---

**Status**: Ready for testing! 🚀
**Server**: Running at http://127.0.0.1:8000/
**Test Data**: ✅ Created
**RBAC**: ✅ Fully Implemented
