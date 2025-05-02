from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from hrm import settings
from app import views as home
from app import HodViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',HodViews.admin_home),
    path('add_employee',HodViews.add_employee),
    path('add_employee_save', HodViews.add_employee_save),
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
    path('add_job_title_save',HodViews.add_job_title_save),
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
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
