# Recruitment Workflow - Implementation Summary

## Overview

Recruitment module with **public job posting pages** (no login) and **admin management** (login required).

## Implementation Status: **60% Complete** ✅

### ✅ Completed

1. **Models** (app/models.py):

   - `JobPosting` - 24 fields including title, department, description, requirements, deadline, salary range, status
   - `Application` - 35 fields including candidate info, resume, status (9 stages), interview details
   - `ApplicationNote` - Notes and comments on applications

2. **Forms** (app/forms.py):

   - `JobPostingForm` - Admin form to create/edit jobs
   - `ApplicationForm` - Public form for candidates (no login)
   - `ApplicationReviewForm` - HR review form with status, rating, notes

3. **Views**:

   - **Public Views** (app/views.py) - 4 views:

     - `careers_list` - Job listing with search/filter
     - `careers_detail` - Job details with related jobs
     - `careers_apply` - Application form
     - `application_success` - Thank you page

   - **Admin Views** (app/HodViews.py) - 11 views:
     - `list_jobs_admin` - All jobs with statistics
     - `create_job` - Create new job posting
     - `job_detail_admin` - Job details with application stats
     - `edit_job` - Edit job posting
     - `delete_job` - Delete job (if no applications)
     - `applications_kanban` - Kanban board view
     - `update_application_status` - AJAX endpoint for status update
     - `application_detail` - Full application details
     - `update_application` - Update application info
     - `add_application_note` - Add notes
     - `convert_to_employee` - Convert accepted candidate to Employee

4. **URLs** (hrm/urls.py) - 15 routes added:

   - **Public** (no login):

     - `/careers/` - List all open jobs
     - `/careers/<id>/` - Job detail
     - `/careers/<id>/apply/` - Apply form

   - **Admin** (login required):
     - `/recruitment/jobs/` - List jobs (admin)
     - `/recruitment/jobs/create/` - Create job
     - `/recruitment/jobs/<id>/` - Job detail (admin)
     - `/recruitment/jobs/<id>/edit/` - Edit job
     - `/recruitment/jobs/<id>/delete/` - Delete job
     - `/recruitment/applications/` - Kanban board
     - `/recruitment/applications/<id>/` - Application detail
     - `/recruitment/applications/<id>/update/` - Update application
     - `/recruitment/applications/<id>/status/` - AJAX status update
     - `/recruitment/applications/<id>/note/` - Add note
     - `/recruitment/applications/<id>/convert/` - Convert to employee

5. **Migration**:
   - `0015_application_jobposting_applicationnote_and_more.py` - Applied successfully

### 🚧 In Progress

- **Public Templates** (app/templates/public/):
  - careers_list.html
  - careers_detail.html
  - apply_form.html

### ⏳ Pending

- **Admin Templates** (app/templates/hod_template/):

  - list_jobs_admin.html
  - job_detail_admin.html
  - create_edit_job.html
  - applications_kanban.html (with drag-drop)
  - application_detail.html
  - update_application.html

- **Sidebar Menu** - Add "Tuyển dụng" section

- **Kanban Drag-Drop** - Implement with SortableJS

- **Email Notifications** - Configure Django email settings

- **Testing** - Full workflow testing

---

## Key Features

### 1. Public Job Posting

- ✅ Modern job listing page (no login required)
- ✅ Search by keyword
- ✅ Filter by department, employment type, experience level
- ✅ Pagination (12 jobs per page)
- ✅ View counter for each job
- ✅ Apply online with resume upload

### 2. Application Form

- ✅ Full candidate information capture
- ✅ Resume upload (PDF/DOC)
- ✅ Cover letter
- ✅ Portfolio and LinkedIn URLs
- ✅ Expected salary and availability
- ✅ Auto-generated application code
- ✅ Form validation

### 3. Admin Job Management

- ✅ Create/edit/delete job postings
- ✅ Multiple job statuses: draft, open, closed, cancelled
- ✅ Employment types: fulltime, parttime, contract, internship
- ✅ Experience levels: entry, junior, mid, senior, expert
- ✅ Salary range or negotiable
- ✅ Deadline management
- ✅ View statistics: total applications, by status

### 4. Kanban Board

- ✅ View organized by application status
- ✅ 9 status stages:
  - new - Mới
  - screening - Sơ tuyển
  - phone_interview - Phỏng vấn điện thoại
  - interview - Phỏng vấn
  - test - Làm bài test
  - offer - Đề nghị
  - accepted - Chấp nhận
  - rejected - Từ chối
  - withdrawn - Rút lui
- ✅ AJAX status update endpoint
- ⏳ Drag-and-drop (pending SortableJS implementation)

### 5. Application Review

- ✅ Full candidate profile view
- ✅ Resume download
- ✅ Rating system (1-5 stars)
- ✅ Internal notes (with important flag)
- ✅ Assign to HR staff
- ✅ Schedule interview (date, location, interviewer)
- ✅ Rejection reason tracking

### 6. Convert to Employee

- ✅ One-click conversion from accepted candidate
- ✅ Auto-fill employee data from application:
  - Basic info: name, email, phone, DOB, gender, address
  - Education: school, major, level
  - Job info: department, job title, position
  - Salary: expected or job's min salary
- ✅ Auto-generate employee code
- ✅ Initial status: Onboarding
- ✅ Link application to employee record

### 7. Email Notifications (TODO)

- ⏳ Application received confirmation
- ⏳ Status change notifications
- ⏳ Interview invitation
- ⏳ Offer letter
- ⏳ Rejection notification

---

## Database Schema

### JobPosting Model

```python
# Basic Information
title, code, department FK, job_title FK

# Job Details
description, requirements, responsibilities, benefits

# Employment
employment_type, experience_level, number_of_positions

# Location & Salary
location, salary_min, salary_max, salary_negotiable

# Dates
deadline, start_date

# Status & Contact
status, contact_person, contact_email, contact_phone

# Metadata
views_count, applications_count, created_by FK, created_at, updated_at
```

### Application Model

```python
# Job & Candidate
job FK, application_code, full_name, email, phone, DOB, gender, address

# Professional
current_position, current_company, years_of_experience,
education_level, school, major

# Application
resume (file), cover_letter, portfolio_url, linkedin_url

# Availability
expected_salary, available_start_date, notice_period_days

# Status & Tracking
status, source, rating, notes

# Interview
interview_date, interview_location, interviewer FK

# Decision
offer_made_date, offer_accepted_date, rejection_reason

# Conversion
converted_to_employee, employee FK (OneToOne)

# Assignment
assigned_to FK, created_at, updated_at
```

### ApplicationNote Model

```python
application FK, author FK, note, is_important, created_at
```

---

## URL Structure

### Public URLs (No Authentication)

```
GET  /careers/                     - List all open jobs
GET  /careers/<id>/                - Job detail
GET  /careers/<id>/apply/          - Application form
POST /careers/<id>/apply/          - Submit application
```

### Admin URLs (Authentication Required)

```
# Jobs Management
GET  /recruitment/jobs/                         - List all jobs (admin)
GET  /recruitment/jobs/create/                  - Create job form
POST /recruitment/jobs/create/                  - Save new job
GET  /recruitment/jobs/<id>/                    - Job detail (admin)
GET  /recruitment/jobs/<id>/edit/               - Edit job form
POST /recruitment/jobs/<id>/edit/               - Update job
POST /recruitment/jobs/<id>/delete/             - Delete job

# Applications Management
GET  /recruitment/applications/                 - Kanban board
GET  /recruitment/applications/<id>/            - Application detail
GET  /recruitment/applications/<id>/update/     - Update form
POST /recruitment/applications/<id>/update/     - Save updates
POST /recruitment/applications/<id>/status/     - AJAX status update
POST /recruitment/applications/<id>/note/       - Add note
POST /recruitment/applications/<id>/convert/    - Convert to employee
```

---

## File Structure

```
app/
├── models.py              ✅ JobPosting, Application, ApplicationNote
├── forms.py               ✅ JobPostingForm, ApplicationForm, ApplicationReviewForm
├── views.py               ✅ Public career views (4)
├── HodViews.py            ✅ Admin recruitment views (11)
└── templates/
    ├── public/            ⏳ Need to create
    │   ├── careers_list.html
    │   ├── careers_detail.html
    │   └── apply_form.html
    └── hod_template/      ⏳ Need to create
        ├── list_jobs_admin.html
        ├── job_detail_admin.html
        ├── create_edit_job.html
        ├── applications_kanban.html
        ├── application_detail.html
        └── update_application.html

hrm/
└── urls.py                ✅ 15 routes added

media/
└── resumes/               ✅ Auto-created for resume uploads
```

---

## Next Steps

### Priority 1: Templates

1. ⏳ Create public templates (3 files)
2. ⏳ Create admin templates (6 files)
3. ⏳ Update sidebar with Recruitment menu

### Priority 2: Kanban Enhancement

4. ⏳ Add SortableJS library
5. ⏳ Implement drag-and-drop in applications_kanban.html
6. ⏳ Test AJAX status updates

### Priority 3: Email Notifications

7. ⏳ Configure Django email settings
8. ⏳ Create email templates
9. ⏳ Implement send_mail in views

### Priority 4: Testing

10. ⏳ Test public career pages
11. ⏳ Test application submission
12. ⏳ Test admin job management
13. ⏳ Test kanban board
14. ⏳ Test convert to employee
15. ⏳ Test email notifications

---

## Technical Notes

### Form Validation

- ✅ Job deadline cannot be in the past
- ✅ Start date must be after deadline
- ✅ Salary min cannot exceed salary max
- ✅ Unique job code
- ✅ Phone number validation
- ✅ Available start date cannot be in the past

### Security

- ✅ Public views: No authentication
- ✅ Admin views: @login_required decorator
- ✅ File upload: Only PDF/DOC allowed
- ✅ AJAX endpoints: @require_POST + authentication

### Business Logic

- ✅ Auto-generate application code: APP{YYYYMMDD}{6-char-UUID}
- ✅ Auto-increment views counter
- ✅ Auto-increment applications counter
- ✅ Only accepted applications can be converted
- ✅ Jobs with applications cannot be deleted
- ✅ Convert pre-fills employee data from application

### Model Methods

```python
# JobPosting
- is_active()              # Check if job is still accepting applications
- days_until_deadline()    # Calculate days remaining
- get_salary_display()     # Format salary range
- increment_views()        # +1 view counter
- increment_applications() # +1 application counter

# Application
- can_convert_to_employee() # Check if status == 'accepted' and not converted
- get_age()                 # Calculate age from DOB
- days_since_applied()      # Days since created_at
```

---

## Statistics Available

### Job Posting

- Total jobs
- Open jobs
- Closing soon (within 7 days)
- Total views per job
- Total applications per job
- Applications by status (new, screening, interview, offer, accepted, rejected)

### Applications

- Total applications
- New applications (status='new')
- Interview scheduled (status in ['phone_interview', 'interview'])
- Applications grouped by status (for kanban)

---

## Testing Checklist

### Public Career Pages

- [ ] List jobs with filters working
- [ ] Search functionality
- [ ] Job detail displays correctly
- [ ] View counter increments
- [ ] Related jobs show
- [ ] Apply form renders
- [ ] Form validation works
- [ ] Resume upload successful
- [ ] Application code generated
- [ ] Success message displays
- [ ] Cannot apply after deadline

### Admin Job Management

- [ ] List jobs with statistics
- [ ] Create new job
- [ ] Edit existing job
- [ ] Delete job (no applications only)
- [ ] Job detail shows application stats
- [ ] Filter and search work

### Kanban Board

- [ ] Applications display in correct columns
- [ ] Filter by job works
- [ ] Search applications
- [ ] Drag and drop (when implemented)
- [ ] AJAX status update
- [ ] Statistics accurate

### Application Review

- [ ] Application detail shows all info
- [ ] Resume download works
- [ ] Update application info
- [ ] Add notes
- [ ] Rating system
- [ ] Assign to HR staff
- [ ] Schedule interview

### Convert to Employee

- [ ] Only available for accepted applications
- [ ] Employee created with correct data
- [ ] Employee code auto-generated
- [ ] Application linked to employee
- [ ] Status set to Onboarding
- [ ] Redirect to employee detail

### Email Notifications (When Implemented)

- [ ] Application received
- [ ] Status changed
- [ ] Interview scheduled
- [ ] Offer sent
- [ ] Rejection sent

---

## Configuration Required

### Settings.py

```python
# Email Configuration (TODO)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'HRM System <noreply@hrm.com>'
```

### Media Settings (Already Configured)

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## API Endpoints

### AJAX Endpoints

```javascript
// Update application status
POST /recruitment/applications/<id>/status/
Content-Type: application/json
Body: {"status": "interview"}
Response: {"success": true, "message": "..."}
```

---

## Dependencies

### Python Packages (Already Installed)

- Django 4.2.16
- Pillow (for image handling)

### Frontend Libraries (TODO)

- SortableJS (for drag-and-drop kanban)
- AdminLTE 3.x (already used)
- jQuery (already available)

---

## Known Issues / TODO

1. ⚠️ Email notifications not implemented yet
2. ⚠️ Drag-and-drop kanban needs SortableJS
3. ⚠️ Templates need to be created
4. ⚠️ Sidebar menu not added yet
5. ⚠️ No email validation on application submission
6. ⚠️ Resume file size limit not enforced

---

## Future Enhancements

- Interview scheduling calendar
- Bulk email to candidates
- Application timeline/history
- Advanced search filters
- Export applications to Excel
- Candidate pool management
- Application form customization per job
- Video interview integration
- Assessment/test integration
- Offer letter templates
- Background check tracking

---

**Implementation Date**: November 15, 2025  
**Status**: 60% Complete - Models, Forms, Views, URLs done. Templates pending.  
**Next Session**: Create templates and test workflow.
