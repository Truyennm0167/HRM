# Self-Service Portal Module - Complete Guide

## Overview

The Self-Service Portal is a comprehensive employee self-service module that allows employees to:

- View personal dashboard with statistics and recent activities
- Access and view their complete profile information
- Update limited personal information (phone, address, avatar)
- View salary history with filtering and statistics
- Track attendance records with monthly/yearly filtering

## Module Structure

### 1. Views (`app/HodViews.py`)

#### `employee_dashboard(request)`

**Purpose**: Main portal homepage displaying employee statistics and recent activities

**Features**:

- Profile summary card with avatar
- Current month statistics:
  - Total working days
  - Total working hours
  - Current month salary
  - Remaining leave days
- Pending actions counters:
  - Pending leave requests
  - Pending expense claims
- Quick action links
- This month expenses summary
- Recent activities timeline (last 10 leave requests + expenses)

**Location**: Lines 1597-1698

**Dependencies**: Employee, Attendance, Payroll, LeaveRequest, LeaveBalance, Expense models

---

#### `employee_profile(request)`

**Purpose**: Display complete employee profile information (read-only)

**Features**:

- Personal information (name, gender, birthday, nationality, etc.)
- Contact information (email, phone, address)
- Work information (job title, department, salary, start date)
- Employment history (if available)

**Location**: Lines 1699-1713

**Dependencies**: Employee model

---

#### `edit_employee_profile(request)`

**Purpose**: Allow employees to update limited personal information

**Editable Fields**:

- Phone number
- Address
- Place of residence
- Avatar image

**Features**:

- GET: Display form with current values
- POST: Validate and save changes
- Avatar upload with validation
- Unique filename generation (UUID)
- Success/error messages

**Location**: Lines 1714-1760

**Validation**:

- Avatar: Image files only (validate_image_file)
- Phone: Required field
- File size limits apply

---

#### `my_payrolls(request)`

**Purpose**: Display employee salary history with filtering

**Features**:

- Payroll listing (12 per page)
- Year filter dropdown
- Statistics:
  - Total salary (all time)
  - Average salary
- Detailed view modal (AJAX)
- Status badges (pending/confirmed)

**Location**: Lines 1761-1806

**Query Parameters**:

- `year`: Filter by specific year

---

#### `my_attendance(request)`

**Purpose**: Display employee attendance records with filtering

**Features**:

- Attendance listing (31 per page)
- Month and year filters
- Statistics (for selected period):
  - Total working days
  - Total working hours
  - Leave days
  - Absent days
- Status badges (working/leave/absent)

**Location**: Lines 1807-1869

**Query Parameters**:

- `month`: Filter by month (1-12)
- `year`: Filter by year

---

### 2. Templates (`app/templates/hod_template/`)

#### `employee_dashboard.html`

**Components**:

- Profile card (top)
- 4 statistics small-boxes
- 2 pending action info-boxes
- Quick actions card
- This month expense card
- Recent activities timeline

**AdminLTE Elements**:

- `.small-box` (statistics)
- `.info-box` (pending actions)
- `.timeline` (activities)
- Status badges

---

#### `employee_profile.html`

**Layout**: 2-column responsive

**Left Column**:

- Profile card with avatar
- Employment information card

**Right Column**:

- Personal information card
- Contact information card
- Work history card

**Features**:

- Icons for each field type
- Status badges
- Responsive grid layout

---

#### `edit_employee_profile.html`

**Layout**: 2-column

**Left Column**:

- Profile preview card
- Notice card (edit limitations)

**Right Column**:

- Edit form
- Editable fields (4)
- Disabled fields (read-only reference)

**JavaScript**:

- Avatar preview on file select
- Phone number validation (digits only, 10-11 length)

**Form Attributes**:

- `enctype="multipart/form-data"` (for file upload)
- CSRF token

---

#### `my_payrolls.html`

**Components**:

- 2 statistics boxes (total, average)
- Year filter in card-tools
- Payroll table
- View details modal
- Pagination

**Table Columns**:

1. Month/Year
2. Base Salary
3. Coefficient
4. Working Hours
5. Bonus
6. Penalty
7. Total Salary
8. Status
9. Actions (View button)

**Features**:

- Currency formatting (VNĐ with commas)
- Status badges
- AJAX modal loading
- Responsive table

---

#### `my_attendance.html`

**Components**:

- 4 statistics small-boxes
- Month/year filter form
- Attendance table
- Summary info-boxes
- Pagination

**Table Columns**:

1. Date (formatted)
2. Day of Week
3. Status Badge
4. Working Hours
5. Notes

**Status Colors**:

- Success (green): "Có làm việc"
- Warning (yellow): "Nghỉ phép"
- Danger (red): "Nghỉ không phép"

---

### 3. URLs (`hrm/urls.py`)

```python
# Self-Service Portal
path('portal/dashboard/', employee_dashboard, name='employee_dashboard'),
path('portal/profile/', employee_profile, name='employee_profile'),
path('portal/profile/edit/', edit_employee_profile, name='edit_employee_profile'),
path('portal/payrolls/', my_payrolls, name='my_payrolls'),
path('portal/attendance/', my_attendance, name='my_attendance'),
```

**URL Naming Convention**: `{feature}_{action}` or `{feature}_view`

---

### 4. Sidebar Navigation

**Menu Location**: Between "Quản lý chi phí" and AI sections

**Menu Structure**:

```
Portal Nhân Viên (fas fa-user-circle)
├── Dashboard (fas fa-tachometer-alt)
├── Hồ sơ cá nhân (fas fa-user)
├── Bảng lương (fas fa-money-bill-wave)
└── Chấm công (fas fa-calendar-check)
```

**Active State**: Highlights when `/portal` in URL path

---

## Data Flow

### Employee Identification

All views use the same pattern:

```python
employee = Employee.objects.get(email=request.user.email)
```

**Assumption**: User email matches Employee email (1-to-1 relationship)

### Statistics Calculation

**Dashboard**:

```python
# Current month attendance
current_month_attendance = Attendance.objects.filter(
    employee=employee,
    date__month=now.month,
    date__year=now.year,
    status='Có làm việc'
).aggregate(
    total_days=Count('id'),
    total_hours=Sum('working_hours')
)

# Current month payroll
current_payroll = Payroll.objects.filter(
    employee=employee,
    month=now.month,
    year=now.year
).first()
```

**Payrolls**:

```python
# Statistics
total_salary = payrolls.aggregate(total=Sum('total_salary'))['total']
avg_salary = total_salary / payrolls.count() if payrolls.count() > 0 else 0
```

**Attendance**:

```python
# Monthly statistics
stats = Attendance.objects.filter(
    employee=employee,
    date__month=selected_month,
    date__year=selected_year
).aggregate(
    total_days=Count('id'),
    total_hours=Sum('working_hours', filter=Q(status='Có làm việc')),
    leave_days=Count('id', filter=Q(status='Nghỉ phép')),
    absent_days=Count('id', filter=Q(status='Nghỉ không phép'))
)
```

---

## Security & Permissions

### Authentication

- All views protected with `@login_required` decorator
- Unauthenticated users redirected to login page

### Authorization

- Employees can only access their own data
- Employee lookup via `request.user.email`
- No cross-employee data access possible

### Edit Restrictions

Only these fields can be edited by employees:

1. Phone number
2. Address
3. Place of residence
4. Avatar image

**Protected Fields** (read-only):

- Name, Gender, Birthday
- Identification, Nationality
- Job Title, Department
- Salary, Employment status
- All HR-managed fields

### File Upload Security

- Avatar validation: `validate_image_file` (images only)
- Unique filenames: UUID-based naming
- Storage location: `media/avatars/`
- File size limits enforced

---

## Pagination

### Payrolls

- **Items per page**: 12
- **Reason**: Typical year display (12 months)
- **Preserves filters**: Year parameter maintained in pagination links

### Attendance

- **Items per page**: 31
- **Reason**: Maximum days in a month
- **Preserves filters**: Month and year parameters maintained

---

## Filtering

### Payrolls

- **Year filter**: Dropdown with all available years
- **Default**: All records
- **Implementation**: QuerySet filter + GET parameter

### Attendance

- **Month filter**: Dropdown (1-12)
- **Year filter**: Dropdown (dynamic list)
- **Default**: Current month
- **Implementation**: QuerySet filter + GET parameters

---

## UI/UX Features

### AdminLTE Components Used

1. **small-box**: Statistics cards (colored backgrounds)
2. **info-box**: Pending actions counters
3. **card**: Main content containers
4. **timeline**: Activity feed
5. **badge**: Status indicators
6. **modal**: Detail views
7. **pagination**: Page navigation

### Color Scheme

- **Primary (blue)**: Main actions, links
- **Success (green)**: Working status, confirmed
- **Warning (yellow)**: Pending, leave
- **Danger (red)**: Absent, rejected
- **Info (cyan)**: Statistics, information

### Icons (FontAwesome 5)

- Dashboard: `fa-tachometer-alt`
- Profile: `fa-user`, `fa-id-card`
- Payroll: `fa-money-bill-wave`, `fa-coins`
- Attendance: `fa-calendar-check`, `fa-clock`
- Actions: `fa-edit`, `fa-eye`, `fa-save`

---

## Usage Guide

### For Employees

#### 1. Accessing the Portal

1. Login to system
2. Click "Portal Nhân Viên" in sidebar
3. Navigate to desired section

#### 2. Viewing Dashboard

- See current month statistics
- Check pending requests
- View recent activities
- Access quick actions

#### 3. Viewing Profile

- Review all personal information
- Check employment details
- Verify contact information

#### 4. Updating Profile

1. Go to "Hồ sơ cá nhân"
2. Click edit button or navigate to edit page
3. Update allowed fields
4. Upload new avatar (optional)
5. Click "Lưu thay đổi"
6. Verify success message

#### 5. Checking Salary

1. Navigate to "Bảng lương"
2. View all payroll records
3. Filter by year if needed
4. Click "View" for details
5. Check statistics (total, average)

#### 6. Checking Attendance

1. Navigate to "Chấm công"
2. View current month by default
3. Filter by month/year if needed
4. Review statistics
5. Check individual records

---

## Testing Checklist

### Functional Testing

- [ ] Login redirects to appropriate page
- [ ] Dashboard loads with correct statistics
- [ ] Profile displays all information
- [ ] Edit profile form submission works
- [ ] Avatar upload successful
- [ ] Payroll list displays correctly
- [ ] Payroll filtering works
- [ ] Attendance list displays correctly
- [ ] Attendance filtering works
- [ ] Pagination works on all pages

### Permission Testing

- [ ] Unauthenticated users redirected
- [ ] Employees see only their data
- [ ] Cannot edit protected fields
- [ ] File upload validation works

### UI Testing

- [ ] Responsive layout on mobile/tablet/desktop
- [ ] All icons display
- [ ] Status badges show correct colors
- [ ] Modals open/close properly
- [ ] Forms validate input
- [ ] Success/error messages display

### Performance Testing

- [ ] Pages load in < 2 seconds
- [ ] No N+1 query issues
- [ ] Large datasets paginate properly
- [ ] Filters don't cause timeouts

---

## Common Issues & Solutions

### Issue 1: Employee not found

**Symptom**: `DoesNotExist: Employee matching query does not exist`

**Cause**: User email doesn't match any Employee record

**Solution**: Ensure Employee.email matches User.email

### Issue 2: No statistics showing

**Symptom**: Dashboard shows zeros for all statistics

**Cause**: No Attendance or Payroll records for current period

**Solution**: Create sample data or wait for records to be generated

### Issue 3: Avatar not displaying

**Symptom**: Default image shown instead of uploaded avatar

**Cause**: MEDIA_URL not configured or file not found

**Solution**:

- Check `MEDIA_URL` and `MEDIA_ROOT` in settings
- Verify file exists in `media/avatars/`
- Check URL pattern serves media files in development

### Issue 4: Filter not working

**Symptom**: Filtering doesn't change results

**Cause**: GET parameters not preserved or query logic error

**Solution**:

- Check form method is GET
- Verify query parameter names match view logic
- Inspect QuerySet filters in view

---

## Future Enhancements

### Potential Features

1. **Leave Request Creation**: Allow employees to request leave directly
2. **Document Downloads**: Download payroll slips, tax documents
3. **Notifications**: Real-time updates for payroll, attendance
4. **Calendar View**: Interactive attendance calendar
5. **Performance Dashboard**: Personal KPIs and goals
6. **Team Directory**: View colleagues' contact info
7. **Mobile App**: Native mobile experience
8. **Export Functions**: PDF/Excel export for records

### Technical Improvements

1. **Caching**: Cache dashboard statistics
2. **Async Loading**: AJAX for statistics cards
3. **Real-time Updates**: WebSocket for live data
4. **API Endpoints**: RESTful API for mobile app
5. **Advanced Filtering**: Date ranges, multiple criteria
6. **Search**: Full-text search across records
7. **Charting**: Visualize salary trends, attendance patterns

---

## File Summary

### Python Files

- `app/HodViews.py`: 273 lines (5 new views)

### HTML Templates

- `employee_dashboard.html`: 265 lines
- `employee_profile.html`: 230 lines
- `edit_employee_profile.html`: 185 lines
- `my_payrolls.html`: 165 lines
- `my_attendance.html`: 225 lines
- **Total**: ~1,070 lines

### Configuration

- `hrm/urls.py`: 5 new URL patterns
- `sidebar_template.html`: 1 new menu section (4 items)

---

## Dependencies

### Django Apps

- `django.contrib.auth` (User authentication)
- `django.core.paginator` (Pagination)
- `django.db.models` (ORM queries)
- `django.contrib.messages` (Flash messages)

### Models Used

- `Employee` (main entity)
- `Attendance` (time tracking)
- `Payroll` (salary records)
- `LeaveRequest` (leave management)
- `LeaveBalance` (leave quotas)
- `Expense` (expense claims)

### External Libraries

- AdminLTE 3.x (UI framework)
- Bootstrap 4 (CSS framework)
- FontAwesome 5 (icons)
- jQuery (JavaScript utilities)

---

## Conclusion

The Self-Service Portal module provides a comprehensive employee self-service experience with:

- ✅ Complete profile visibility
- ✅ Limited self-editing capabilities
- ✅ Salary history tracking
- ✅ Attendance monitoring
- ✅ Dashboard with actionable insights
- ✅ Secure, permission-based access
- ✅ Responsive, modern UI

This module empowers employees to manage their own information while maintaining organizational control over sensitive data.

---

**Module Status**: ✅ Complete (95% - pending full testing)

**Created**: November 15, 2025

**Last Updated**: November 15, 2025
