"""
Admin Management Portal URLs
Management interface for HR/Managers with appropriate permissions
"""
from django.urls import path
from app import management_views

urlpatterns = [
    # Dashboard
    path('', management_views.admin_home, name='management_home'),
    
    # Employee Management
    path('employees/', management_views.employee_list, name='management_employee_list'),
    path('employees/add/', management_views.add_employee, name='management_add_employee'),
    path('employees/add/save/', management_views.add_employee_save, name='management_add_employee_save'),
    path('employees/<int:employee_id>/', management_views.employee_detail_view, name='management_employee_detail'),
    path('employees/<int:employee_id>/edit/', management_views.update_employee, name='management_update_employee'),
    path('employees/<int:employee_id>/edit/save/', management_views.update_employee_save, name='management_update_employee_save'),
    path('employees/<int:employee_id>/delete/', management_views.delete_employee, name='management_delete_employee'),
    
    # Department Management
    path('departments/', management_views.department_page, name='management_departments'),
    path('departments/add/', management_views.add_department_save, name='management_add_department_save'),
    path('departments/<int:department_id>/delete/', management_views.delete_department, name='management_delete_department'),
    
    # Job Title Management
    path('job-titles/', management_views.job_title, name='management_job_titles'),
    path('job-titles/<int:job_title_id>/', management_views.view_job_title, name='management_view_job_title'),
    path('job-titles/add/', management_views.add_job_title_save, name='management_add_job_title_save'),
    path('job-titles/<int:job_title_id>/delete/', management_views.delete_job_title, name='management_delete_job_title'),
    
    # Org Chart
    path('org-chart/', management_views.org_chart, name='management_org_chart'),
    
    # Attendance Management
    path('attendance/add/', management_views.add_attendance, name='management_add_attendance'),
    path('attendance/add/save/', management_views.add_attendance_save, name='management_add_attendance_save'),
    path('attendance/manage/', management_views.manage_attendance, name='management_manage_attendance'),
    path('attendance/check-date/', management_views.check_attendance_date, name='management_check_attendance_date'),
    path('attendance/get-data/', management_views.get_attendance_data, name='management_get_attendance_data'),
    path('attendance/<int:attendance_id>/edit/', management_views.edit_attendance, name='management_edit_attendance'),
    path('attendance/delete/', management_views.delete_attendance, name='management_delete_attendance'),
    path('attendance/export/', management_views.export_attendance, name='management_export_attendance'),
    
    # Payroll Management
    path('payroll/calculate/', management_views.calculate_payroll, name='management_calculate_payroll'),
    path('payroll/get-data/', management_views.get_payroll_data, name='management_get_payroll_data'),
    path('payroll/save/', management_views.save_payroll, name='management_save_payroll'),
    path('payroll/manage/', management_views.manage_payroll, name='management_manage_payroll'),
    path('payroll/<int:payroll_id>/edit/', management_views.edit_payroll, name='management_edit_payroll'),
    path('payroll/delete/', management_views.delete_payroll, name='management_delete_payroll'),
    path('payroll/confirm/', management_views.confirm_payroll, name='management_confirm_payroll'),
    path('payroll/<int:payroll_id>/', management_views.view_payroll, name='management_view_payroll'),
    path('payroll/export/', management_views.export_payroll, name='management_export_payroll'),
    
    # Leave Management
    path('leave/types/', management_views.manage_leave_types, name='management_manage_leave_types'),
    path('leave/types/save/', management_views.add_leave_type_save, name='management_add_leave_type_save'),
    path('leave/types/<int:leave_type_id>/delete/', management_views.delete_leave_type, name='management_delete_leave_type'),
    path('leave/requests/', management_views.manage_leave_requests, name='management_manage_leave_requests'),
    path('leave/requests/<int:request_id>/', management_views.view_leave_request, name='management_view_leave_request'),
    path('leave/requests/<int:request_id>/approve/', management_views.approve_leave_request, name='management_approve_leave_request'),
    path('leave/requests/<int:request_id>/reject/', management_views.reject_leave_request, name='management_reject_leave_request'),
    
    # Expense Management
    path('expense/categories/', management_views.manage_expense_categories, name='management_manage_expense_categories'),
    path('expense/categories/add/', management_views.add_expense_category_save, name='management_add_expense_category_save'),
    path('expense/categories/<int:category_id>/edit/', management_views.edit_expense_category_save, name='management_edit_expense_category_save'),
    path('expense/categories/<int:category_id>/delete/', management_views.delete_expense_category, name='management_delete_expense_category'),
    path('expense/requests/', management_views.manage_expenses, name='management_manage_expenses'),
    path('expense/requests/<int:expense_id>/', management_views.view_expense, name='management_view_expense'),
    path('expense/requests/<int:expense_id>/approve/', management_views.approve_expense, name='management_approve_expense'),
    path('expense/requests/<int:expense_id>/reject/', management_views.reject_expense, name='management_reject_expense'),
    path('expense/requests/<int:expense_id>/mark-paid/', management_views.mark_expense_as_paid, name='management_mark_expense_as_paid'),
    
    # Contract Management
    path('contracts/', management_views.manage_contracts, name='management_manage_contracts'),
    path('contracts/create/', management_views.create_contract, name='management_create_contract'),
    path('contracts/<int:contract_id>/', management_views.contract_detail, name='management_contract_detail'),
    path('contracts/<int:contract_id>/edit/', management_views.edit_contract, name='management_edit_contract'),
    path('contracts/<int:contract_id>/renew/', management_views.renew_contract, name='management_renew_contract'),
    path('contracts/<int:contract_id>/delete/', management_views.delete_contract, name='management_delete_contract'),
    path('contracts/expiring/', management_views.expiring_contracts, name='management_expiring_contracts'),
    path('contracts/employee/<int:employee_id>/', management_views.employee_contracts, name='management_employee_contracts'),
    
    # Recruitment Management
    path('recruitment/jobs/', management_views.list_jobs_admin, name='management_list_jobs_admin'),
    path('recruitment/jobs/create/', management_views.create_job, name='management_create_job'),
    path('recruitment/jobs/<int:job_id>/', management_views.job_detail_admin, name='management_job_detail_admin'),
    path('recruitment/jobs/<int:job_id>/edit/', management_views.edit_job, name='management_edit_job'),
    path('recruitment/jobs/<int:job_id>/delete/', management_views.delete_job, name='management_delete_job'),
    path('recruitment/applications/', management_views.applications_kanban, name='management_applications_kanban'),
    path('recruitment/applications/<int:application_id>/', management_views.application_detail, name='management_application_detail'),
    path('recruitment/applications/<int:application_id>/update/', management_views.update_application, name='management_update_application'),
    path('recruitment/applications/<int:application_id>/status/', management_views.update_application_status, name='management_update_application_status'),
    path('recruitment/applications/<int:application_id>/note/', management_views.add_application_note, name='management_add_application_note'),
    path('recruitment/applications/<int:application_id>/convert/', management_views.convert_to_employee, name='management_convert_to_employee'),
    
    # Salary Rules Management
    path('salary-rules/components/', management_views.salary_components, name='management_salary_components'),
    path('salary-rules/components/create/', management_views.create_salary_component, name='management_create_salary_component'),
    path('salary-rules/components/<int:component_id>/edit/', management_views.edit_salary_component, name='management_edit_salary_component'),
    path('salary-rules/components/<int:component_id>/delete/', management_views.delete_salary_component, name='management_delete_salary_component'),
    path('salary-rules/employee/<int:employee_id>/', management_views.employee_salary_rules, name='management_employee_salary_rules'),
    path('salary-rules/employee/<int:employee_id>/assign/', management_views.assign_salary_rule, name='management_assign_salary_rule'),
    path('salary-rules/rule/<int:rule_id>/delete/', management_views.delete_salary_rule, name='management_delete_salary_rule'),
    path('salary-rules/employee/<int:employee_id>/preview/', management_views.calculate_salary_preview, name='management_calculate_salary_preview'),
    path('salary-rules/bulk-assign/', management_views.bulk_assign_salary_rules, name='management_bulk_assign_salary_rules'),
    path('salary-rules/templates/', management_views.salary_rule_templates, name='management_salary_rule_templates'),
    path('salary-rules/templates/create/', management_views.create_salary_rule_template, name='management_create_salary_rule_template'),
    path('salary-rules/templates/<int:template_id>/edit/', management_views.edit_salary_rule_template, name='management_edit_salary_rule_template'),
    path('salary-rules/template-item/<int:item_id>/delete/', management_views.delete_template_item, name='management_delete_template_item'),
    path('salary-rules/template/<int:template_id>/apply/<int:employee_id>/', management_views.apply_template_to_employee, name='management_apply_template_to_employee'),
    path('salary-rules/history/', management_views.salary_calculation_history, name='management_salary_calculation_history'),
    
    # Appraisal Management
    path('appraisal/periods/', management_views.appraisal_periods, name='management_appraisal_periods'),
    path('appraisal/periods/create/', management_views.create_appraisal_period, name='management_create_appraisal_period'),
    path('appraisal/periods/<int:period_id>/', management_views.appraisal_period_detail, name='management_appraisal_period_detail'),
    path('appraisal/periods/<int:period_id>/add-criteria/', management_views.add_appraisal_criteria, name='management_add_appraisal_criteria'),
    path('appraisal/periods/<int:period_id>/generate/', management_views.generate_appraisals, name='management_generate_appraisals'),
    path('appraisal/manager/', management_views.manager_appraisals, name='management_manager_appraisals'),
    path('appraisal/<int:appraisal_id>/manager-review/', management_views.manager_review, name='management_manager_review'),
    path('appraisal/hr/', management_views.hr_appraisals, name='management_hr_appraisals'),
    path('appraisal/<int:appraisal_id>/hr-review/', management_views.hr_final_review, name='management_hr_final_review'),
    path('appraisal/<int:appraisal_id>/detail/', management_views.appraisal_detail, name='management_appraisal_detail'),
    
    # ========================================
    # BACKWARD COMPATIBILITY ALIASES
    # Old URL names for existing templates
    # ========================================
    
    # Old names without 'management_' prefix
    path('', management_views.admin_home, name='admin_home'),
    path('contracts/', management_views.manage_contracts, name='manage_contracts'),
    path('contracts/create/', management_views.create_contract, name='create_contract'),
    path('contracts/<int:contract_id>/', management_views.contract_detail, name='contract_detail'),
    path('contracts/<int:contract_id>/edit/', management_views.edit_contract, name='edit_contract'),
    path('contracts/<int:contract_id>/renew/', management_views.renew_contract, name='renew_contract'),
    path('contracts/<int:contract_id>/delete/', management_views.delete_contract, name='delete_contract'),
    path('contracts/expiring/', management_views.expiring_contracts, name='expiring_contracts'),
    path('contracts/employee/<int:employee_id>/', management_views.employee_contracts, name='employee_contracts'),
    
    path('employees/', management_views.employee_list, name='employee_list'),
    path('employees/add/', management_views.add_employee, name='add_employee'),
    path('employees/<int:employee_id>/', management_views.employee_detail_view, name='employee_detail'),
    path('employees/<int:employee_id>/edit/', management_views.update_employee, name='update_employee'),
    
    path('departments/', management_views.department_page, name='department_page'),
    path('job-titles/', management_views.job_title, name='job_title'),
    path('org-chart/', management_views.org_chart, name='org_chart'),
    
    path('attendance/add/', management_views.add_attendance, name='add_attendance'),
    path('attendance/manage/', management_views.manage_attendance, name='manage_attendance'),
    path('attendance/<int:attendance_id>/edit/', management_views.edit_attendance, name='edit_attendance'),
    
    path('payroll/calculate/', management_views.calculate_payroll, name='calculate_payroll'),
    path('payroll/manage/', management_views.manage_payroll, name='manage_payroll'),
    path('payroll/<int:payroll_id>/edit/', management_views.edit_payroll, name='edit_payroll'),
    path('payroll/<int:payroll_id>/', management_views.view_payroll, name='view_payroll'),
    
    path('leave/types/', management_views.manage_leave_types, name='manage_leave_types'),
    path('leave/requests/', management_views.manage_leave_requests, name='manage_leave_requests'),
    path('leave/requests/', management_views.manage_leave_requests, name='request_leave'),  # Backward compatibility
    path('leave/history/', management_views.manage_leave_requests, name='leave_history'),  # Backward compatibility - redirects to leave requests
    path('leave/requests/<int:request_id>/approve/', management_views.approve_leave_request, name='approve_leave_request'),
    
    path('expense/categories/', management_views.manage_expense_categories, name='manage_expense_categories'),
    path('expense/requests/', management_views.manage_expenses, name='manage_expenses'),
    path('expense/requests/', management_views.manage_expenses, name='create_expense'),  # Backward compatibility
    path('expense/requests/', management_views.manage_expenses, name='expense_history'),  # Backward compatibility
    path('expense/requests/<int:expense_id>/approve/', management_views.approve_expense, name='approve_expense'),
    
    path('recruitment/jobs/', management_views.list_jobs_admin, name='list_jobs_admin'),
    path('recruitment/applications/', management_views.applications_kanban, name='applications_kanban'),
    
    path('salary-rules/components/', management_views.salary_components, name='salary_components'),
    path('salary-rules/employee/<int:employee_id>/', management_views.employee_salary_rules, name='employee_salary_rules'),
    
    path('appraisal/periods/', management_views.appraisal_periods, name='appraisal_periods'),
    path('appraisal/manager/', management_views.manager_appraisals, name='manager_appraisals'),
    path('appraisal/hr/', management_views.hr_appraisals, name='hr_appraisals'),
]
