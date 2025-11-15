from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Resume, JobDescription
from .services.resume_service import ResumeService
from .forms import ResumeUploadForm, JobDescriptionForm
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
import uuid
from app.validators import validate_document_file
from django.core.exceptions import ValidationError

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # handle file with sanitized unique filename
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                try:
                    validate_document_file(uploaded_file)
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('upload_resume')
                filename = get_valid_filename(uploaded_file.name)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                saved_path = default_storage.save(f"resumes/{unique_name}", uploaded_file)
                resume = form.save(commit=False)
                # set file field to saved_path (relative path)
                resume.file.name = saved_path
            else:
                resume = form.save(commit=False)

            # Try to assign employee if exists
            try:
                if hasattr(request.user, 'employee'):
                    resume.employee = request.user.employee
            except Exception:
                pass
            resume.save()
            messages.success(request, "CV đã được upload thành công!")
            return redirect('view_resume', resume_id=resume.id)
    else:
        form = ResumeUploadForm()
    
    return render(request, 'ai_recruitment/upload_resume.html', {'form': form})

@login_required
def create_job_description(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_description = form.save()
            messages.success(request, "Job description created successfully!")
            return redirect('view_job_description', jd_id=job_description.id)
    else:
        form = JobDescriptionForm()
    
    return render(request, 'ai_recruitment/create_job_description.html', {'form': form})

@login_required
def job_description_list(request):
    """View to display list of all job descriptions."""
    job_descriptions = JobDescription.objects.all().order_by('-created_at')
    return render(request, 'ai_recruitment/job_description_list.html', {'job_descriptions': job_descriptions})

@login_required
def view_job_description(request, jd_id):
    """View to display detailed information about a job description."""
    jd = get_object_or_404(JobDescription, id=jd_id)
    return render(request, 'ai_recruitment/view_job_description.html', {'jd': jd})

@login_required
@require_POST
def delete_job_description(request, jd_id):
    """Delete a job description."""
    jd = get_object_or_404(JobDescription, id=jd_id)
    jd.delete()
    return JsonResponse({'status': 'success'})

@login_required
def score_resume(request, resume_id, jd_id):
    try:
        resume = Resume.objects.get(id=resume_id)
        job_description = JobDescription.objects.get(id=jd_id)
        
        service = ResumeService()
        success = service.process_resume(resume, job_description)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'scores': resume.scores
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Error processing resume'
            }, status=500)
    
    except (Resume.DoesNotExist, JobDescription.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'Resume or Job Description not found'
        }, status=404)

@login_required
def resume_list(request):
    """View to display list of all resumes."""
    resumes = Resume.objects.all().order_by('-created_at')
    return render(request, 'ai_recruitment/resume_list.html', {'resumes': resumes})

@login_required
def view_resume(request, resume_id):
    """View to display detailed information about a resume."""
    resume = get_object_or_404(Resume, id=resume_id)
    job_descriptions = JobDescription.objects.all().order_by('-created_at')
    return render(request, 'ai_recruitment/view_resume.html', {
        'resume': resume,
        'job_descriptions': job_descriptions
    })

@login_required
@require_POST
def delete_resume(request, resume_id):
    """Delete a resume."""
    resume = get_object_or_404(Resume, id=resume_id)
    resume.delete()
    return JsonResponse({'status': 'success'})
