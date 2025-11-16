"""
Email utilities for HRM System
Handles sending various types of emails with templates
"""

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_email_with_template(subject, template_name, context, recipient_list, 
                             from_email=None, fail_silently=False):
    """
    Send email using HTML template with fallback to plain text
    
    Args:
        subject: Email subject
        template_name: Template path (without extension)
        context: Dictionary of context variables for template
        recipient_list: List of recipient email addresses
        from_email: Sender email (uses DEFAULT_FROM_EMAIL if None)
        fail_silently: Whether to suppress exceptions
        
    Returns:
        Number of emails sent (0 or 1)
    """
    try:
        # Use default from email if not specified
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        # Render HTML template
        html_content = render_to_string(f'{template_name}.html', context)
        
        # Create plain text version
        text_content = strip_tags(html_content)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        result = email.send(fail_silently=fail_silently)
        
        logger.info(f"Email sent: {subject} to {recipient_list}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {recipient_list}: {e}")
        if not fail_silently:
            raise
        return 0


# ============================================================
# Application/Recruitment Emails
# ============================================================

def send_application_received_email(application):
    """
    Send confirmation email when application is received
    
    Args:
        application: Application model instance
    """
    subject = f"Đơn ứng tuyển của bạn đã được tiếp nhận - {application.job.title}"
    
    context = {
        'applicant_name': application.full_name,
        'job_title': application.job.title,
        'application_code': application.application_code,
        'company_name': 'Công ty HRM',
        'application_date': application.applied_at,
        'job': application.job,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/application_received',
        context=context,
        recipient_list=[application.email],
        fail_silently=True
    )


def send_application_status_update_email(application):
    """
    Send email when application status changes
    
    Args:
        application: Application model instance
    """
    status_messages = {
        'reviewing': 'đang được xem xét',
        'shortlisted': 'đã được chọn vào vòng tiếp theo',
        'interview_scheduled': 'đã được lên lịch phỏng vấn',
        'rejected': 'không phù hợp lần này',
        'accepted': 'đã được chấp nhận',
    }
    
    status_text = status_messages.get(application.status, application.get_status_display())
    
    subject = f"Cập nhật đơn ứng tuyển - {application.job.title}"
    
    context = {
        'applicant_name': application.full_name,
        'job_title': application.job.title,
        'application_code': application.application_code,
        'status': application.get_status_display(),
        'status_text': status_text,
        'company_name': 'Công ty HRM',
        'application': application,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/application_status_update',
        context=context,
        recipient_list=[application.email],
        fail_silently=True
    )


# ============================================================
# Leave Request Emails
# ============================================================

def send_leave_request_submitted_email(leave_request):
    """
    Send email when leave request is submitted
    
    Args:
        leave_request: LeaveRequest model instance
    """
    subject = f"Đơn xin nghỉ phép đã được gửi - {leave_request.employee.name}"
    
    context = {
        'employee_name': leave_request.employee.name,
        'leave_type': leave_request.leave_type.name,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'duration': leave_request.duration,
        'reason': leave_request.reason,
        'leave_request': leave_request,
    }
    
    # Send to employee
    send_email_with_template(
        subject=subject,
        template_name='emails/leave_request_submitted',
        context=context,
        recipient_list=[leave_request.employee.email],
        fail_silently=True
    )
    
    # Notify manager if exists
    if leave_request.employee.department and leave_request.employee.department:
        from app.models import Employee
        managers = Employee.objects.filter(
            department=leave_request.employee.department,
            is_manager=True
        ).exclude(id=leave_request.employee.id)
        
        if managers.exists():
            manager_emails = [m.email for m in managers]
            send_leave_approval_request_email(leave_request, manager_emails)


def send_leave_approval_request_email(leave_request, manager_emails):
    """
    Send email to managers requesting leave approval
    
    Args:
        leave_request: LeaveRequest model instance
        manager_emails: List of manager email addresses
    """
    subject = f"Yêu cầu phê duyệt nghỉ phép - {leave_request.employee.name}"
    
    context = {
        'employee_name': leave_request.employee.name,
        'leave_type': leave_request.leave_type.name,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'duration': leave_request.duration,
        'reason': leave_request.reason,
        'leave_request': leave_request,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/leave_approval_request',
        context=context,
        recipient_list=manager_emails,
        fail_silently=True
    )


def send_leave_approved_email(leave_request):
    """
    Send email when leave request is approved
    
    Args:
        leave_request: LeaveRequest model instance
    """
    subject = f"Đơn xin nghỉ phép đã được phê duyệt"
    
    context = {
        'employee_name': leave_request.employee.name,
        'leave_type': leave_request.leave_type.name,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'duration': leave_request.duration,
        'status': leave_request.get_status_display(),
        'approved_by': leave_request.approved_by.name if leave_request.approved_by else 'HR',
        'leave_request': leave_request,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/leave_approved',
        context=context,
        recipient_list=[leave_request.employee.email],
        fail_silently=True
    )


def send_leave_rejected_email(leave_request):
    """
    Send email when leave request is rejected
    
    Args:
        leave_request: LeaveRequest model instance
    """
    subject = f"Đơn xin nghỉ phép không được phê duyệt"
    
    context = {
        'employee_name': leave_request.employee.name,
        'leave_type': leave_request.leave_type.name,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'reason': leave_request.rejection_reason or 'Không có lý do cụ thể',
        'leave_request': leave_request,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/leave_rejected',
        context=context,
        recipient_list=[leave_request.employee.email],
        fail_silently=True
    )


# ============================================================
# Contract Emails
# ============================================================

def send_contract_expiry_warning_email(contract, days_until_expiry):
    """
    Send warning email about upcoming contract expiry
    
    Args:
        contract: Contract model instance
        days_until_expiry: Number of days until expiry
    """
    subject = f"Thông báo hợp đồng sắp hết hạn - {contract.employee.name}"
    
    context = {
        'employee_name': contract.employee.name,
        'contract_type': contract.get_contract_type_display(),
        'start_date': contract.start_date,
        'end_date': contract.end_date,
        'days_until_expiry': days_until_expiry,
        'contract': contract,
    }
    
    # Send to employee
    send_email_with_template(
        subject=subject,
        template_name='emails/contract_expiry_warning',
        context=context,
        recipient_list=[contract.employee.email],
        fail_silently=True
    )
    
    # Send to HR
    from django.contrib.auth.models import User, Group
    hr_group = Group.objects.filter(name='HR').first()
    if hr_group:
        hr_users = User.objects.filter(groups=hr_group)
        hr_emails = [u.email for u in hr_users if u.email]
        
        if hr_emails:
            send_email_with_template(
                subject=f"Nhắc nhở: Hợp đồng của {contract.employee.name} sắp hết hạn",
                template_name='emails/contract_expiry_hr_notification',
                context=context,
                recipient_list=hr_emails,
                fail_silently=True
            )


def send_contract_renewal_email(contract):
    """
    Send email when contract is renewed
    
    Args:
        contract: Contract model instance
    """
    subject = f"Hợp đồng đã được gia hạn"
    
    context = {
        'employee_name': contract.employee.name,
        'contract_type': contract.get_contract_type_display(),
        'start_date': contract.start_date,
        'end_date': contract.end_date,
        'contract': contract,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/contract_renewed',
        context=context,
        recipient_list=[contract.employee.email],
        fail_silently=True
    )


# ============================================================
# Appraisal Emails
# ============================================================

def send_appraisal_self_assessment_reminder(appraisal):
    """
    Send reminder for self-assessment
    
    Args:
        appraisal: Appraisal model instance
    """
    subject = f"Nhắc nhở: Tự đánh giá hiệu suất - {appraisal.period.name}"
    
    context = {
        'employee_name': appraisal.employee.name,
        'period_name': appraisal.period.name,
        'self_assessment_deadline': appraisal.period.self_assessment_deadline,
        'appraisal': appraisal,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/appraisal_self_assessment_reminder',
        context=context,
        recipient_list=[appraisal.employee.email],
        fail_silently=True
    )


def send_appraisal_manager_review_notification(appraisal):
    """
    Notify manager about pending review
    
    Args:
        appraisal: Appraisal model instance
    """
    if not appraisal.manager:
        return 0
        
    subject = f"Yêu cầu đánh giá nhân viên - {appraisal.employee.name}"
    
    context = {
        'manager_name': appraisal.manager.name,
        'employee_name': appraisal.employee.name,
        'period_name': appraisal.period.name,
        'manager_review_deadline': appraisal.period.manager_review_deadline,
        'appraisal': appraisal,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/appraisal_manager_review_notification',
        context=context,
        recipient_list=[appraisal.manager.email],
        fail_silently=True
    )


def send_appraisal_completed_email(appraisal):
    """
    Send email when appraisal is completed
    
    Args:
        appraisal: Appraisal model instance
    """
    subject = f"Đánh giá hiệu suất đã hoàn tất - {appraisal.period.name}"
    
    context = {
        'employee_name': appraisal.employee.name,
        'period_name': appraisal.period.name,
        'final_score': appraisal.final_score,
        'overall_rating': appraisal.get_overall_rating_display(),
        'appraisal': appraisal,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/appraisal_completed',
        context=context,
        recipient_list=[appraisal.employee.email],
        fail_silently=True
    )


# ============================================================
# System/Admin Emails
# ============================================================

def send_welcome_email(user, employee, temporary_password=None):
    """
    Send welcome email to new employee with login credentials
    
    Args:
        user: User model instance
        employee: Employee model instance
        temporary_password: Temporary password (if generated)
    """
    subject = "Chào mừng đến với hệ thống HRM"
    
    context = {
        'employee_name': employee.name,
        'username': user.username,
        'email': user.email,
        'temporary_password': temporary_password,
        'has_password': temporary_password is not None,
    }
    
    return send_email_with_template(
        subject=subject,
        template_name='emails/welcome',
        context=context,
        recipient_list=[employee.email],
        fail_silently=True
    )
