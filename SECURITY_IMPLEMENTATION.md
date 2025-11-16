# SECURITY IMPLEMENTATION GUIDE

## Overview

This document describes the security enhancements implemented in the HRM system, including Django Groups, permission checks, and password policies.

---

## 1. Django Groups & Permissions

### Groups Created

#### **HR Group**

- **Full Access** to all modules
- Can manage all employees, departments, payroll, attendance, leave, contracts
- Can create and manage appraisal periods
- Can finalize appraisals
- Can manage recruitment

**Permissions**: ~100+ permissions across all models

#### **Manager Group**

- **Team Management** capabilities
- Can view team members
- Can approve team leave requests
- Can manage team attendance
- Can review team appraisals
- Can view recruitment applications

**Permissions**: ~25 permissions focused on team management

#### **Employee Group**

- **Self-Service** capabilities
- Can view own profile
- Can submit leave requests
- Can view own payroll
- Can self-assess appraisals
- Can view job postings

**Permissions**: ~15 permissions for personal data access

---

## 2. Setup Commands

### Initial Setup

```bash
# Step 1: Create groups and assign permissions
python manage.py setup_groups_permissions

# Step 2: Assign users to groups (dry-run first)
python manage.py assign_user_groups --dry-run

# Step 3: Apply changes
python manage.py assign_user_groups
```

### Manual Assignment

In Django Admin:

1. Go to **Users** → Select user
2. Scroll to **Groups** section
3. Select appropriate group (HR/Manager/Employee)
4. Save

---

## 3. Password Policies

### Requirements

All passwords must meet the following criteria:

1. **Minimum Length**: 10 characters
2. **Complexity**:
   - At least 1 uppercase letter (A-Z)
   - At least 1 lowercase letter (a-z)
   - At least 1 digit (0-9)
   - At least 1 special character (!@#$%^&\*(),.?":{}|<>)
3. **Maximum Length**: 128 characters
4. **No Spaces**: Password cannot contain spaces
5. **No Email Parts**: Cannot contain parts of user's email
6. **No Common Patterns**: Cannot contain '123456', 'password', 'qwerty', etc.
7. **Not Similar to Username**: Cannot be too similar to username
8. **Not Common Password**: Not in Django's common password list
9. **Not Entirely Numeric**: Cannot be all numbers

### Examples

✅ **Valid Passwords**:

- `MyP@ssw0rd2024!`
- `Secure#HRM$2024`
- `Tr0ng!An@2024`

❌ **Invalid Passwords**:

- `password123` (common pattern, no uppercase, no special char)
- `12345678` (entirely numeric, common pattern)
- `MyPassword` (no digit, no special char)
- `nguyen@hrm` (contains email part)
- `Pass word1!` (contains space)

### Implementation

Password validators configured in `settings.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    # Django built-in
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',

    # Custom validators
    'app.validators.PasswordComplexityValidator',
    'app.validators.MaximumLengthValidator',
    'app.validators.NoSpaceValidator',
    'app.validators.NoEmailInPasswordValidator',
    'app.validators.CommonPatternValidator',
]
```

---

## 4. Permission Decorators

### Available Decorators

#### `@hr_required`

Restricts access to HR staff only.

```python
from app.decorators import hr_required

@hr_required
def delete_employee(request, employee_id):
    # Only HR can delete employees
    pass
```

#### `@manager_or_hr_required`

Allows both Managers and HR staff.

```python
from app.decorators import manager_or_hr_required

@manager_or_hr_required
def view_team_attendance(request):
    # Managers and HR can view
    pass
```

#### `@group_required('GroupName1', 'GroupName2')`

Flexible decorator for multiple groups.

```python
from app.decorators import group_required

@group_required('HR', 'Manager')
def approve_leave(request, leave_id):
    # HR or Manager can approve
    pass
```

#### `@check_employee_access`

Smart access control for employee data:

- HR: Access all employees
- Manager: Access team members only
- Employee: Access own data only

```python
from app.decorators import check_employee_access

@check_employee_access
def view_employee(request, employee_id):
    # Access controlled by role
    pass
```

#### `@check_salary_access`

Restricts salary information:

- HR: View all salaries
- Employee: View own salary only
- Manager: No access to salaries

```python
from app.decorators import check_salary_access

@check_salary_access
def view_payroll(request, employee_id):
    # Salary access controlled
    pass
```

#### `@check_appraisal_access`

Controls appraisal access:

- HR: All appraisals
- Manager: Team appraisals (as manager)
- Employee: Own appraisals

```python
from app.decorators import check_appraisal_access

@check_appraisal_access
def view_appraisal(request, appraisal_id):
    # Appraisal access controlled
    pass
```

---

## 5. Critical Views Protected

### Employee Management

```python
# HR Only
@hr_required
def add_employee(request)

@hr_required
def delete_employee(request, employee_id)

# Role-based access
@check_employee_access
def view_employee(request, employee_id)

@check_employee_access
def edit_employee(request, employee_id)
```

### Payroll

```python
# Salary information restricted
@check_salary_access
def view_payroll(request, payroll_id)

@hr_required
def generate_payroll(request)

@hr_required
def export_payroll(request)
```

### Appraisal

```python
# HR only - Period management
@hr_required
def create_appraisal_period(request)

@hr_required
def generate_appraisals(request, period_id)

# Role-based appraisal access
@check_appraisal_access
def self_assessment(request, appraisal_id)

@check_appraisal_access
def manager_review(request, appraisal_id)

@hr_required
def hr_final_review(request, appraisal_id)
```

### Leave Management

```python
# Employees can submit
@login_required
def submit_leave_request(request)

# Managers and HR can approve
@manager_or_hr_required
def approve_leave(request, leave_id)

@manager_or_hr_required
def reject_leave(request, leave_id)
```

### Recruitment

```python
# HR only - Job posting management
@hr_required
def create_job_posting(request)

@hr_required
def edit_job_posting(request, job_id)

# Managers can view applications
@manager_or_hr_required
def view_applications(request)

# HR can manage candidates
@hr_required
def review_application(request, application_id)
```

---

## 6. Session Security

### Settings Configured

```python
# Session expires after 1 hour of inactivity
SESSION_COOKIE_AGE = 3600

# Session saved on every request
SESSION_SAVE_EVERY_REQUEST = True

# Session expires when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Cookies only sent via HTTP (not JavaScript)
SESSION_COOKIE_HTTPONLY = True

# Cookies only sent to same site
SESSION_COOKIE_SAMESITE = 'Strict'
```

### Production Settings

When `DEBUG = False`:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 7. Security Middleware

### SecurityHeadersMiddleware

Adds security headers to all responses:

- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### UserGroupMiddleware

- Checks if authenticated users have group assignments
- Logs users without groups
- Shows warning message to users without permissions

### LoginAttemptMiddleware

- Logs all login attempts
- Records username and IP address
- Helps track suspicious activity

---

## 8. Testing Security

### Test User Groups

```python
# In Django shell
python manage.py shell

from django.contrib.auth.models import User, Group

# Check user groups
user = User.objects.get(username='testuser')
print(user.groups.all())

# Check user permissions
print(user.get_all_permissions())

# Check specific permission
print(user.has_perm('app.add_employee'))
```

### Test Password Policy

```bash
# Try to create user with weak password
python manage.py createsuperuser

# Should reject passwords that don't meet requirements
```

### Test View Permissions

1. Login as Employee
2. Try to access HR-only pages (should be denied)
3. Try to view other employees (should be denied)
4. Try to view own data (should work)

---

## 9. Audit & Monitoring

### Logging

All security events are logged:

```python
# Check logs
tail -f hrm.log

# Look for:
# - Login attempts
# - Permission denied
# - Users without groups
# - Failed authentication
```

### Review Checklist

- [ ] All users assigned to appropriate groups
- [ ] All sensitive views have permission decorators
- [ ] Password policies enforced
- [ ] Session timeout working
- [ ] Security headers present
- [ ] HTTPS enabled in production
- [ ] Login attempts logged

---

## 10. Common Issues & Solutions

### Issue: User can't access any pages

**Solution**: Assign user to appropriate group

```bash
python manage.py assign_user_groups
```

### Issue: "You don't have permission" error

**Solution**:

1. Check user's group assignment in Django Admin
2. Verify group has required permissions
3. Re-run `setup_groups_permissions` if needed

### Issue: Password requirements too strict

**Solution**: Adjust validators in `settings.py`

```python
# Example: Reduce minimum length
'OPTIONS': {
    'min_length': 8,  # Changed from 10
}
```

### Issue: Session expires too quickly

**Solution**: Increase session timeout

```python
SESSION_COOKIE_AGE = 7200  # 2 hours
```

---

## 11. Best Practices

### For Developers

1. **Always use decorators** on sensitive views
2. **Check permissions in views** as well as templates
3. **Log security events** for audit trails
4. **Test with different user roles**
5. **Never bypass permission checks** in code

### For Administrators

1. **Review user groups** monthly
2. **Monitor login attempts** for suspicious activity
3. **Enforce strong passwords**
4. **Revoke access** for terminated employees immediately
5. **Regular security audits**

### For Users

1. **Use strong, unique passwords**
2. **Don't share credentials**
3. **Log out when done**
4. **Report suspicious activity**

---

## 12. Next Steps

### Immediate Actions

1. Run setup commands to create groups
2. Assign all users to appropriate groups
3. Test with different user roles
4. Review audit logs

### Future Enhancements

1. **Two-Factor Authentication (2FA)**
2. **Password expiration policy** (90 days)
3. **Account lockout** after failed attempts
4. **IP whitelisting** for admin access
5. **Email notifications** for security events
6. **Detailed audit trail** for all changes
7. **Role-based dashboard** (different for each group)

---

## Support

For security questions or issues:

- Review logs: `hrm.log`
- Check Django Admin: Users & Groups
- Run diagnostic: `python manage.py check --deploy`

**Last Updated**: 2024-11-16
**Version**: 1.0
