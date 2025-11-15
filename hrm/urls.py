from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from hrm import settings
from app import views as home
from app import HodViews
from ai_recruitment import views as ai_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('',HodViews.admin_home, name='admin_home'),
    path('add_employee',HodViews.add_employee, name='add_employee'),
    path('add_employee_save', HodViews.add_employee_save, name='add_employee_save'),
    path('employee_list',HodViews.employee_list, name='employee_list'),
    path('employee/<int:employee_id>/', HodViews.employee_detail_view, name='employee_detail'),
    path('employee/update/<int:employee_id>/', HodViews.update_employee, name='update_employee'),
    path("update_employee_save/", HodViews.update_employee_save, name="update_employee_save"),
    path('employee/delete/<int:employee_id>/', HodViews.delete_employee, name='delete_employee'),
    path("department/", HodViews.department_page, name="department_page"),
    path("add_department_save/", HodViews.add_department_save, name="add_department_save"),
    path("delete_department/<int:department_id>/", HodViews.delete_department, name="delete_department"),
    path('job_title',HodViews.job_title, name='job_title'),
    path('view_job_title/<int:job_title_id>/', HodViews.view_job_title, name='view_job_title'),
    path('add_job_title_save',HodViews.add_job_title_save, name='add_job_title_save'),
    path('delete_job_title/<int:job_title_id>/', HodViews.delete_job_title, name='delete_job_title'),
    
    # Attendance URLs
    path('attendance/add/', HodViews.add_attendance, name='add_attendance'),
    path('attendance/add/save/', HodViews.add_attendance_save, name='add_attendance_save'),
    path('attendance/manage/', HodViews.manage_attendance, name='manage_attendance'),
    path('attendance/check-date/', HodViews.check_attendance_date, name='check_attendance_date'),
    path('attendance/get-data/', HodViews.get_attendance_data, name='get_attendance_data'),
    path('attendance/edit/<int:attendance_id>/', HodViews.edit_attendance, name='edit_attendance'),
    path('attendance/delete/', HodViews.delete_attendance, name='delete_attendance'),
    path('attendance/export/', HodViews.export_attendance, name='export_attendance'),

    # Payroll URLs
    path('payroll/calculate/', HodViews.calculate_payroll, name='calculate_payroll'),
    path('payroll/get-data/', HodViews.get_payroll_data, name='get_payroll_data'),
    path('payroll/save/', HodViews.save_payroll, name='save_payroll'),
    path('payroll/manage/', HodViews.manage_payroll, name='manage_payroll'),
    path('payroll/edit/<int:payroll_id>/', HodViews.edit_payroll, name='edit_payroll'),
    path('payroll/delete/', HodViews.delete_payroll, name='delete_payroll'),
    path('payroll/confirm/', HodViews.confirm_payroll, name='confirm_payroll'),
    path('payroll/view/<int:payroll_id>/', HodViews.view_payroll, name='view_payroll'),
    path('payroll/export/', HodViews.export_payroll, name='export_payroll'),

    # Leave Management URLs
    path('leave/types/', HodViews.manage_leave_types, name='manage_leave_types'),
    path('leave/types/save/', HodViews.add_leave_type_save, name='add_leave_type_save'),
    path('leave/types/delete/<int:leave_type_id>/', HodViews.delete_leave_type, name='delete_leave_type'),
    path('leave/request/', HodViews.request_leave, name='request_leave'),
    path('leave/history/', HodViews.leave_history, name='leave_history'),
    path('leave/manage/', HodViews.manage_leave_requests, name='manage_leave_requests'),
    path('leave/view/<int:request_id>/', HodViews.view_leave_request, name='view_leave_request'),
    path('leave/approve/<int:request_id>/', HodViews.approve_leave_request, name='approve_leave_request'),
    path('leave/reject/<int:request_id>/', HodViews.reject_leave_request, name='reject_leave_request'),
    path('leave/cancel/<int:request_id>/', HodViews.cancel_leave_request, name='cancel_leave_request'),

    # Expense Management URLs
    path('expense/categories/', HodViews.manage_expense_categories, name='manage_expense_categories'),
    path('expense/category/add/', HodViews.add_expense_category_save, name='add_expense_category_save'),
    path('expense/category/edit/', HodViews.edit_expense_category_save, name='edit_expense_category_save'),
    path('expense/category/delete/<int:category_id>/', HodViews.delete_expense_category, name='delete_expense_category'),
    path('expense/create/', HodViews.create_expense, name='create_expense'),
    path('expense/history/', HodViews.expense_history, name='expense_history'),
    path('expense/manage/', HodViews.manage_expenses, name='manage_expenses'),
    path('expense/view/<int:expense_id>/', HodViews.view_expense, name='view_expense'),
    path('expense/approve/<int:expense_id>/', HodViews.approve_expense, name='approve_expense'),
    path('expense/reject/<int:expense_id>/', HodViews.reject_expense, name='reject_expense'),
    path('expense/mark-paid/<int:expense_id>/', HodViews.mark_expense_as_paid, name='mark_expense_as_paid'),
    path('expense/cancel/<int:expense_id>/', HodViews.cancel_expense, name='cancel_expense'),

    # Self-Service Portal URLs
    path('portal/dashboard/', HodViews.employee_dashboard, name='employee_dashboard'),
    path('portal/profile/', HodViews.employee_profile, name='employee_profile'),
    path('portal/profile/edit/', HodViews.edit_employee_profile, name='edit_employee_profile'),
    path('portal/payrolls/', HodViews.my_payrolls, name='my_payrolls'),
    path('portal/attendance/', HodViews.my_attendance, name='my_attendance'),

    # AI Recruitment URLs
    path('ai/upload-resume/', ai_views.upload_resume, name='upload_resume'),
    path('ai/create-job-description/', ai_views.create_job_description, name='create_job_description'),
    path('ai/job-descriptions/', ai_views.job_description_list, name='job_description_list'),
    path('ai/job-description/<int:jd_id>/', ai_views.view_job_description, name='view_job_description'),
    path('ai/job-description/<int:jd_id>/delete/', ai_views.delete_job_description, name='delete_job_description'),
    path('ai/score-resume/<int:resume_id>/<int:jd_id>/', ai_views.score_resume, name='score_resume'),
    path('ai/resumes/', ai_views.resume_list, name='resume_list'),
    path('ai/resume/<int:resume_id>/', ai_views.view_resume, name='view_resume'),
    path('ai/resume/<int:resume_id>/delete/', ai_views.delete_resume, name='delete_resume'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
