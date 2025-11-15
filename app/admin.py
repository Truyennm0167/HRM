from django.contrib import admin
from .models import (
    JobTitle, Department, Employee, Attendance, Reward, Discipline, 
    Payroll, Evaluation, LeaveType, LeaveRequest, LeaveBalance,
    ExpenseCategory, Expense
)

# Register your models here.

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ['name', 'salary_coefficient', 'created_at']
    search_fields = ['name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_establishment', 'created_at']
    search_fields = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'name', 'email', 'department', 'job_title', 'status']
    list_filter = ['status', 'department', 'gender']
    search_fields = ['employee_code', 'name', 'email', 'phone']
    ordering = ['-created_at']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'working_hours']
    list_filter = ['status', 'date']
    search_fields = ['employee__name']
    date_hierarchy = 'date'

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['number', 'employee', 'amount', 'date', 'cash_payment']
    list_filter = ['cash_payment', 'date']
    search_fields = ['employee__name', 'description']

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['number', 'employee', 'amount', 'date']
    list_filter = ['date']
    search_fields = ['employee__name', 'description']

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'total_salary', 'status']
    list_filter = ['status', 'month', 'year']
    search_fields = ['employee__name']
    ordering = ['-year', '-month']

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'period', 'score', 'created_at']
    list_filter = ['period']
    search_fields = ['employee__name']

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'max_days_per_year', 'requires_approval', 'is_paid', 'is_active']
    list_filter = ['requires_approval', 'is_paid', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__name', 'reason']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'total_days', 'used_days', 'remaining_days']
    list_filter = ['year', 'leave_type']
    search_fields = ['employee__name']
    ordering = ['-year', 'employee__name']

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['employee', 'category', 'amount', 'date', 'status', 'created_at']
    list_filter = ['status', 'category', 'date']
    search_fields = ['employee__name', 'description']
    date_hierarchy = 'date'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
