"""
Main URL Configuration for HRM System
Routes to Portal, Management, and Public modules
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from hrm import settings
from ai_recruitment import views as ai_views

urlpatterns = [
    # Django Admin (built-in)
    path('admin/', admin.site.urls),
    
    # Authentication (login, logout)
    path('', include('app.urls')),
    
    # Employee Portal (Self-service for all employees)
    path('portal/', include('app.urls_portal')),
    
    # Management Portal (Admin/HR/Manager features)
    path('management/', include('app.urls_management')),
    
    # Public Pages (Recruitment - no login required)
    path('', include('app.urls_public')),
    
    # AI Recruitment URLs (Management only)
    path('management/ai/upload-resume/', ai_views.upload_resume, name='management_upload_resume'),
    path('management/ai/create-job-description/', ai_views.create_job_description, name='management_create_job_description'),
    path('management/ai/job-descriptions/', ai_views.job_description_list, name='management_job_description_list'),
    path('management/ai/job-description/<int:jd_id>/', ai_views.view_job_description, name='management_view_job_description'),
    path('management/ai/job-description/<int:jd_id>/delete/', ai_views.delete_job_description, name='management_delete_job_description'),
    path('management/ai/score-resume/<int:resume_id>/<int:jd_id>/', ai_views.score_resume, name='management_score_resume'),
    path('management/ai/resumes/', ai_views.resume_list, name='management_resume_list'),
    path('management/ai/resume/<int:resume_id>/', ai_views.view_resume, name='management_view_resume'),
    path('management/ai/resume/<int:resume_id>/delete/', ai_views.delete_resume, name='management_delete_resume'),
    
    # ===== LEGACY URLs (Keep for backward compatibility) =====
    # TODO: These should redirect to new portal/management URLs
    # Will be removed in future versions
    
    # Legacy management URLs (redirect to /management/)
    path('add_employee', lambda request: __import__('django.shortcuts').redirect('management_add_employee')),
    path('employee_list', lambda request: __import__('django.shortcuts').redirect('management_employee_list')),
    path('department/', lambda request: __import__('django.shortcuts').redirect('management_departments')),
    path('job_title', lambda request: __import__('django.shortcuts').redirect('management_job_titles')),
    
    # Legacy portal URLs (redirect to /portal/)
    path('portal/dashboard/', lambda request: __import__('django.shortcuts').redirect('portal_dashboard')),
    path('portal/profile/', lambda request: __import__('django.shortcuts').redirect('portal_profile')),
    path('portal/payrolls/', lambda request: __import__('django.shortcuts').redirect('portal_payroll')),
    path('portal/attendance/', lambda request: __import__('django.shortcuts').redirect('portal_attendance')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
