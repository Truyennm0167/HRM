from django.contrib import admin
from .models import (
    JobTitle, Department, Employee, Attendance, Reward, Discipline, 
    Payroll, Evaluation, LeaveType, LeaveRequest, LeaveBalance,
    ExpenseCategory, Expense, PermissionAuditLog,
    AppraisalPeriod, AppraisalCriteria, Appraisal, AppraisalScore, AppraisalComment,
    DocumentCategory, Document, DocumentDownload, Announcement, AnnouncementRead
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

@admin.register(PermissionAuditLog)
class PermissionAuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'username', 'action', 'resource_type', 'resource_id', 'permission_required', 'ip_address']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['username', 'reason', 'view_name', 'url_path']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    readonly_fields = [
        'user', 'username', 'user_groups', 'action', 'resource_type', 
        'resource_id', 'permission_required', 'timestamp', 'ip_address', 
        'user_agent', 'reason', 'view_name', 'url_path', 'extra_data'
    ]
    
    def has_add_permission(self, request):
        # Audit logs should only be created by the system
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete audit logs
        return request.user.is_superuser


# Appraisal Module Admin

@admin.register(AppraisalPeriod)
class AppraisalPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    filter_horizontal = ['applicable_departments', 'applicable_job_titles']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AppraisalCriteria)
class AppraisalCriteriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'period', 'category', 'weight', 'max_score']
    list_filter = ['period', 'category']
    search_fields = ['name', 'description']
    ordering = ['period', 'category', 'name']

@admin.register(Appraisal)
class AppraisalAdmin(admin.ModelAdmin):
    list_display = ['employee', 'period', 'manager', 'status', 'final_score', 'overall_rating', 'created_at']
    list_filter = ['status', 'overall_rating', 'period']
    search_fields = ['employee__name', 'manager__name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'self_assessment_date', 'manager_review_date', 'final_review_date']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('period', 'employee', 'manager', 'status')
        }),
        ('Tự đánh giá', {
            'fields': ('self_assessment', 'self_achievements', 'self_challenges', 'self_goals', 'self_overall_score', 'self_assessment_date')
        }),
        ('Đánh giá của quản lý', {
            'fields': ('manager_review', 'manager_strengths', 'manager_weaknesses', 'manager_recommendations', 'manager_overall_score', 'manager_review_date')
        }),
        ('Đánh giá cuối cùng của HR', {
            'fields': ('hr_comments', 'final_score', 'overall_rating', 'salary_adjustment', 'final_review_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(AppraisalScore)
class AppraisalScoreAdmin(admin.ModelAdmin):
    list_display = ['appraisal', 'criteria', 'self_score', 'manager_score', 'final_score']
    list_filter = ['criteria__category']
    search_fields = ['appraisal__employee__name', 'criteria__name']
    ordering = ['appraisal', 'criteria']

@admin.register(AppraisalComment)
class AppraisalCommentAdmin(admin.ModelAdmin):
    list_display = ['appraisal', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['appraisal__employee__name', 'author__name', 'comment']
    date_hierarchy = 'created_at'


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order', 'name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'visibility', 'uploaded_by', 'downloads_count', 'created_at', 'is_active']
    list_filter = ['visibility', 'category', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    filter_horizontal = ['departments', 'specific_employees']
    readonly_fields = ['downloads_count', 'file_size', 'file_type', 'created_at', 'updated_at']


@admin.register(DocumentDownload)
class DocumentDownloadAdmin(admin.ModelAdmin):
    list_display = ['document', 'employee', 'downloaded_at', 'ip_address']
    list_filter = ['downloaded_at']
    search_fields = ['document__title', 'employee__name']
    date_hierarchy = 'downloaded_at'
    readonly_fields = ['downloaded_at']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'is_pinned', 'is_active', 'publish_at', 'created_by']
    list_filter = ['category', 'priority', 'is_pinned', 'is_active', 'publish_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'publish_at'
    filter_horizontal = ['target_departments', 'target_employees']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'employee', 'read_at']
    list_filter = ['read_at']
    search_fields = ['announcement__title', 'employee__name']
    date_hierarchy = 'read_at'
    readonly_fields = ['read_at']
    ordering = ['-read_at']
