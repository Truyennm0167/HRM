from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from hrm import settings
from app import views, HodViews
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

    # Contract Management URLs
    path('contracts/', HodViews.manage_contracts, name='manage_contracts'),
    path('contracts/create/', HodViews.create_contract, name='create_contract'),
    path('contracts/<int:contract_id>/', HodViews.contract_detail, name='contract_detail'),
    path('contracts/<int:contract_id>/edit/', HodViews.edit_contract, name='edit_contract'),
    path('contracts/<int:contract_id>/renew/', HodViews.renew_contract, name='renew_contract'),
    path('contracts/<int:contract_id>/delete/', HodViews.delete_contract, name='delete_contract'),
    path('contracts/expiring/', HodViews.expiring_contracts, name='expiring_contracts'),
    path('contracts/employee/<int:employee_id>/', HodViews.employee_contracts, name='employee_contracts'),

    # Public Career Pages (No login required)
    path('careers/', views.careers_list, name='careers_list'),
    path('careers/<int:job_id>/', views.careers_detail, name='careers_detail'),
    path('careers/<int:job_id>/apply/', views.careers_apply, name='careers_apply'),
    
    # Recruitment Admin URLs (Login required)
    path('recruitment/jobs/', HodViews.list_jobs_admin, name='list_jobs_admin'),
    path('recruitment/jobs/create/', HodViews.create_job, name='create_job'),
    path('recruitment/jobs/<int:job_id>/', HodViews.job_detail_admin, name='job_detail_admin'),
    path('recruitment/jobs/<int:job_id>/edit/', HodViews.edit_job, name='edit_job'),
    path('recruitment/jobs/<int:job_id>/delete/', HodViews.delete_job, name='delete_job'),
    path('recruitment/applications/', HodViews.applications_kanban, name='applications_kanban'),
    path('recruitment/applications/<int:application_id>/', HodViews.application_detail, name='application_detail'),
    path('recruitment/applications/<int:application_id>/update/', HodViews.update_application, name='update_application'),
    path('recruitment/applications/<int:application_id>/status/', HodViews.update_application_status, name='update_application_status'),
    path('recruitment/applications/<int:application_id>/note/', HodViews.add_application_note, name='add_application_note'),
    path('recruitment/applications/<int:application_id>/convert/', HodViews.convert_to_employee, name='convert_to_employee'),

    # Org Chart URL
    path('org-chart/', HodViews.org_chart, name='org_chart'),

    # Salary Rules URLs
    path('salary-rules/components/', HodViews.salary_components, name='salary_components'),
    path('salary-rules/components/create/', HodViews.create_salary_component, name='create_salary_component'),
    path('salary-rules/components/<int:component_id>/edit/', HodViews.edit_salary_component, name='edit_salary_component'),
    path('salary-rules/components/<int:component_id>/delete/', HodViews.delete_salary_component, name='delete_salary_component'),
    path('salary-rules/employee/<int:employee_id>/', HodViews.employee_salary_rules, name='employee_salary_rules'),
    path('salary-rules/employee/<int:employee_id>/assign/', HodViews.assign_salary_rule, name='assign_salary_rule'),
    path('salary-rules/rule/<int:rule_id>/delete/', HodViews.delete_salary_rule, name='delete_salary_rule'),
    path('salary-rules/employee/<int:employee_id>/preview/', HodViews.calculate_salary_preview, name='calculate_salary_preview'),
    path('salary-rules/bulk-assign/', HodViews.bulk_assign_salary_rules, name='bulk_assign_salary_rules'),
    path('salary-rules/templates/', HodViews.salary_rule_templates, name='salary_rule_templates'),
    path('salary-rules/templates/create/', HodViews.create_salary_rule_template, name='create_salary_rule_template'),
    path('salary-rules/templates/<int:template_id>/edit/', HodViews.edit_salary_rule_template, name='edit_salary_rule_template'),
    path('salary-rules/template-item/<int:item_id>/delete/', HodViews.delete_template_item, name='delete_template_item'),
    path('salary-rules/template/<int:template_id>/apply/<int:employee_id>/', HodViews.apply_template_to_employee, name='apply_template_to_employee'),
    path('salary-rules/history/', HodViews.salary_calculation_history, name='salary_calculation_history'),

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
