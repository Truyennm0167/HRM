from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from .models import JobPosting, Application
from .forms import ApplicationForm
import uuid

# Create your views here.
def get_home(request):
    return render(request, 'hod_template/home_content.html')


# ============= Public Career Views (No Login Required) =============

def careers_list(request):
    """Public page - danh sách tất cả công việc đang tuyển"""
    jobs = JobPosting.objects.filter(
        status='open',
        deadline__gte=timezone.now().date()
    ).select_related('department', 'job_title').order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )
    
    # Filter by department
    department_filter = request.GET.get('department')
    if department_filter:
        jobs = jobs.filter(department_id=department_filter)
    
    # Filter by employment type
    type_filter = request.GET.get('type')
    if type_filter:
        jobs = jobs.filter(employment_type=type_filter)
    
    # Filter by experience level
    exp_filter = request.GET.get('experience')
    if exp_filter:
        jobs = jobs.filter(experience_level=exp_filter)
    
    # Pagination
    paginator = Paginator(jobs, 12)  # 12 jobs per page
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    # Get filter options
    from .models import Department
    departments = Department.objects.all()
    
    context = {
        'jobs': jobs,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
        'type_filter': type_filter,
        'exp_filter': exp_filter,
        'EMPLOYMENT_TYPE_CHOICES': JobPosting.EMPLOYMENT_TYPE_CHOICES,
        'EXPERIENCE_LEVEL_CHOICES': JobPosting.EXPERIENCE_LEVEL_CHOICES,
    }
    return render(request, 'public/careers_list.html', context)


def careers_detail(request, job_id):
    """Public page - chi tiết công việc"""
    job = get_object_or_404(JobPosting, id=job_id, status='open')
    
    # Increment views count
    job.increment_views()
    
    # Get other jobs from same department
    related_jobs = JobPosting.objects.filter(
        department=job.department,
        status='open',
        deadline__gte=timezone.now().date()
    ).exclude(id=job.id)[:3]
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
    }
    return render(request, 'public/careers_detail.html', context)


def careers_apply(request, job_id):
    """Public page - form ứng tuyển"""
    job = get_object_or_404(JobPosting, id=job_id, status='open')
    
    # Check if deadline passed
    if job.deadline < timezone.now().date():
        messages.error(request, 'Đã hết hạn nộp hồ sơ cho vị trí này.')
        return redirect('careers_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            
            # Generate unique application code
            application.application_code = f"APP{timezone.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
            
            application.save()
            
            # Increment application count
            job.increment_applications()
            
            # TODO: Send confirmation email
            
            messages.success(
                request,
                f'Đơn ứng tuyển của bạn đã được gửi thành công! Mã đơn: {application.application_code}. '
                'Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất.'
            )
            return redirect('careers_detail', job_id=job.id)
    else:
        form = ApplicationForm()
    
    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'public/apply_form.html', context)


def application_success(request):
    """Trang thông báo ứng tuyển thành công"""
    return render(request, 'public/application_success.html')