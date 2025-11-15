from django.contrib import admin
from .models import JobDescription, Resume

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'required_years_experience', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'required_years_experience')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'created_at', 'updated_at')
    list_filter = ('created_at', 'employee')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_code')
