"""
Employee Portal URLs
Self-service portal for all employees
"""
from django.urls import path
from app import portal_views

urlpatterns = [
    # Dashboard
    path('', portal_views.dashboard, name='portal_dashboard'),
    path('dashboard/', portal_views.dashboard, name='portal_dashboard_alt'),
    
    # Leave Management
    path('leaves/', portal_views.leaves_list, name='portal_leaves'),
    path('leaves/create/', portal_views.leave_create, name='portal_leave_create'),
    path('leaves/<int:leave_id>/', portal_views.leave_detail, name='portal_leave_detail'),
    path('leaves/<int:leave_id>/cancel/', portal_views.leave_cancel, name='portal_leave_cancel'),
    
    # Payroll
    path('payroll/', portal_views.payroll_list, name='portal_payroll'),
    path('payroll/<int:payroll_id>/', portal_views.payroll_detail, name='portal_payroll_detail'),
    path('payroll/<int:payroll_id>/download/', portal_views.payroll_download, name='portal_payroll_download'),
    
    # Attendance
    path('attendance/', portal_views.attendance_list, name='portal_attendance'),
    path('attendance/calendar/', portal_views.attendance_calendar, name='portal_attendance_calendar'),
    
    # Expenses
    path('expenses/', portal_views.expenses_list, name='portal_expenses'),
    path('expenses/create/', portal_views.expense_create, name='portal_expense_create'),
    path('expenses/<int:expense_id>/', portal_views.expense_detail, name='portal_expense_detail'),
    path('expenses/<int:expense_id>/cancel/', portal_views.expense_cancel, name='portal_expense_cancel'),
    
    # Profile
    path('profile/', portal_views.profile_view, name='portal_profile'),
    path('profile/edit/', portal_views.profile_edit, name='portal_profile_edit'),
    path('profile/password/', portal_views.password_change, name='portal_password_change'),
    
    # Documents & Announcements (Future implementation)
    path('documents/', portal_views.documents_list, name='portal_documents'),
    path('announcements/', portal_views.announcements_list, name='portal_announcements'),
    
    # Manager Features (Only for managers)
    path('approvals/', portal_views.approvals_dashboard, name='portal_approvals'),
    path('team/leaves/', portal_views.team_leaves, name='portal_team_leaves'),
    path('team/leaves/<int:leave_id>/approve/', portal_views.team_leave_approve, name='portal_team_leave_approve'),
    path('team/leaves/<int:leave_id>/reject/', portal_views.team_leave_reject, name='portal_team_leave_reject'),
    path('team/expenses/', portal_views.team_expenses, name='portal_team_expenses'),
    path('team/expenses/<int:expense_id>/approve/', portal_views.team_expense_approve, name='portal_team_expense_approve'),
    path('team/expenses/<int:expense_id>/reject/', portal_views.team_expense_reject, name='portal_team_expense_reject'),
    path('team/reports/', portal_views.team_reports, name='portal_team_reports'),
    
    # Appraisal (Employee self-assessment)
    path('appraisal/', portal_views.my_appraisals, name='portal_my_appraisals'),
    path('appraisal/<int:appraisal_id>/', portal_views.appraisal_detail, name='portal_appraisal_detail'),
    path('appraisal/<int:appraisal_id>/self-assess/', portal_views.self_assessment, name='portal_self_assessment'),
    
    # ========================================
    # BACKWARD COMPATIBILITY ALIASES
    # Old URL names for existing templates
    # ========================================
    path('', portal_views.dashboard, name='employee_dashboard'),  # Old name for dashboard
    path('profile/', portal_views.profile_view, name='employee_profile'),  # Old name for profile
    path('payroll/', portal_views.payroll_list, name='my_payrolls'),  # Old name for payroll
    path('attendance/', portal_views.attendance_list, name='my_attendance'),  # Old name for attendance
]
