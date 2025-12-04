"""
Email Service for HRM System
Handles all email notifications for leave requests, expenses, appraisals, contracts, etc.
"""

import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Centralized email service for HRM notifications
    """
    
    @staticmethod
    def _send_email(subject, template_name, context, recipient_list, fail_silently=True):
        """
        Internal method to send HTML emails
        
        Args:
            subject: Email subject
            template_name: Path to email template (without .html)
            context: Context dictionary for template
            recipient_list: List of recipient email addresses
            fail_silently: Whether to suppress exceptions
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Filter out empty emails
            recipient_list = [email for email in recipient_list if email]
            
            if not recipient_list:
                logger.warning(f"No valid recipients for email: {subject}")
                return False
            
            # Render HTML content
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send
            email.send(fail_silently=fail_silently)
            logger.info(f"Email sent successfully: {subject} to {recipient_list}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {subject}. Error: {str(e)}")
            if not fail_silently:
                raise
            return False

    # ==================== LEAVE REQUEST EMAILS ====================
    
    @classmethod
    def send_leave_approved(cls, leave_request):
        """Send email when leave request is approved"""
        context = {
            'employee_name': leave_request.employee.name,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'days': leave_request.total_days,
            'approved_by': leave_request.approved_by.name if leave_request.approved_by else 'HR',
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Đơn nghỉ phép đã được duyệt - {leave_request.leave_type.name}',
            template_name='leave_approved',
            context=context,
            recipient_list=[leave_request.employee.email]
        )
    
    @classmethod
    def send_leave_rejected(cls, leave_request, reason=''):
        """Send email when leave request is rejected"""
        context = {
            'employee_name': leave_request.employee.name,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'days': leave_request.total_days,
            'reason': reason or leave_request.rejection_reason or 'Không đủ điều kiện',
            'rejected_by': leave_request.approved_by.name if leave_request.approved_by else 'HR',
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Đơn nghỉ phép bị từ chối - {leave_request.leave_type.name}',
            template_name='leave_rejected',
            context=context,
            recipient_list=[leave_request.employee.email]
        )
    
    @classmethod
    def send_leave_request_notification(cls, leave_request, approver_email):
        """Notify approver about new leave request"""
        context = {
            'employee_name': leave_request.employee.name,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'days': leave_request.total_days,
            'reason': leave_request.reason,
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Đơn nghỉ phép mới cần duyệt - {leave_request.employee.name}',
            template_name='leave_request_new',
            context=context,
            recipient_list=[approver_email]
        )

    # ==================== EXPENSE EMAILS ====================
    
    @classmethod
    def send_expense_approved(cls, expense):
        """Send email when expense is approved"""
        context = {
            'employee_name': expense.employee.name,
            'category': expense.category.name if expense.category else 'Khác',
            'amount': expense.amount,
            'description': expense.description,
            'expense_date': expense.date,
            'approved_by': expense.approved_by.name if expense.approved_by else 'HR',
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Chi phí đã được duyệt - {expense.amount:,.0f} VNĐ',
            template_name='expense_approved',
            context=context,
            recipient_list=[expense.employee.email]
        )
    
    @classmethod
    def send_expense_rejected(cls, expense, reason=''):
        """Send email when expense is rejected"""
        context = {
            'employee_name': expense.employee.name,
            'category': expense.category.name if expense.category else 'Khác',
            'amount': expense.amount,
            'description': expense.description,
            'expense_date': expense.date,
            'reason': reason or expense.rejection_reason or 'Không đủ điều kiện',
            'rejected_by': expense.approved_by.name if expense.approved_by else 'HR',
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Chi phí bị từ chối - {expense.amount:,.0f} VNĐ',
            template_name='expense_rejected',
            context=context,
            recipient_list=[expense.employee.email]
        )

    # ==================== APPRAISAL EMAILS ====================
    
    @classmethod
    def send_appraisal_reminder(cls, employee, period):
        """Send reminder for pending self-assessment
        
        Args:
            employee: Employee model instance
            period: Can be a string (e.g., "Q1 2024") or an AppraisalPeriod object
        """
        # Handle both string period and object period
        if isinstance(period, str):
            period_name = period
            context = {
                'employee_name': employee.name,
                'period_name': period_name,
                'start_date': None,
                'end_date': None,
                'self_assessment_deadline': None,
                'company_name': 'HRM System',
            }
        else:
            period_name = period.name
            context = {
                'employee_name': employee.name,
                'period_name': period.name,
                'start_date': period.start_date,
                'end_date': period.end_date,
                'self_assessment_deadline': getattr(period, 'self_assessment_deadline', None),
                'company_name': 'HRM System',
            }
        
        return cls._send_email(
            subject=f'[HRM] Nhắc nhở: Hoàn thành tự đánh giá - {period_name}',
            template_name='appraisal_reminder',
            context=context,
            recipient_list=[employee.email]
        )
    
    @classmethod
    def send_appraisal_completed(cls, appraisal):
        """Notify employee when appraisal is completed"""
        context = {
            'employee_name': appraisal.employee.name,
            'period_name': appraisal.period if isinstance(appraisal.period, str) else appraisal.period.name,
            'final_score': getattr(appraisal, 'final_score', None),
            'rating': getattr(appraisal, 'rating', appraisal.manager_rating),
            'company_name': 'HRM System',
        }
        
        period_name = context['period_name']
        return cls._send_email(
            subject=f'[HRM] Kết quả đánh giá - {period_name}',
            template_name='appraisal_completed',
            context=context,
            recipient_list=[appraisal.employee.email]
        )
    
    @classmethod
    def send_manager_review_reminder(cls, manager, pending_appraisals, period=''):
        """Remind manager about pending team reviews
        
        Args:
            manager: Employee instance (manager)
            pending_appraisals: QuerySet of pending appraisals or integer count
            period: String period name (e.g., "Q1 2024")
        """
        if isinstance(pending_appraisals, int):
            pending_count = pending_appraisals
            pending_employees = []
        else:
            pending_count = pending_appraisals.count()
            pending_employees = [a.employee.name for a in pending_appraisals[:10]]
        
        context = {
            'manager_name': manager.name,
            'pending_count': pending_count,
            'pending_employees': pending_employees,
            'period': period,
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Nhắc nhở: {pending_count} đánh giá đang chờ duyệt',
            template_name='manager_review_reminder',
            context=context,
            recipient_list=[manager.email]
        )

    # ==================== CONTRACT EMAILS ====================
    
    @classmethod
    def send_contract_expiring_alert(cls, employee, days_remaining):
        """Alert employee about expiring contract
        
        Args:
            employee: Employee model instance
            days_remaining: Number of days until contract expires
        """
        from datetime import date, timedelta
        from django.utils import timezone
        
        # Calculate contract end date
        today = timezone.localtime(timezone.now()).date()
        contract_end_date = today + timedelta(days=days_remaining)
        
        # Try to get active contract info
        contract_type = 'N/A'
        contract_start = None
        try:
            active_contract = employee.contracts.filter(status='active').order_by('-start_date').first()
            if active_contract:
                contract_type = active_contract.get_contract_type_display()
                contract_start = active_contract.start_date
                contract_end_date = active_contract.end_date
        except:
            pass
        
        context = {
            'employee_name': employee.name,
            'contract_type': contract_type,
            'start_date': contract_start,
            'end_date': contract_end_date,
            'days_remaining': days_remaining,
            'department': employee.department.name if employee.department else 'N/A',
            'company_name': 'HRM System',
        }
        
        # Send to employee
        return cls._send_email(
            subject=f'[HRM] Hợp đồng sắp hết hạn - Còn {days_remaining} ngày',
            template_name='contract_expiring_employee',
            context=context,
            recipient_list=[employee.email]
        )
    
    @classmethod
    def send_contract_renewed(cls, employee):
        """Notify employee when contract is renewed"""
        context = {
            'employee_name': employee.name,
            'contract_duration': f"{employee.contract_duration} tháng" if employee.contract_duration else 'N/A',
            'start_date': employee.contract_start_date,
            'department': employee.department.name if employee.department else 'N/A',
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject=f'[HRM] Hợp đồng đã được gia hạn',
            template_name='contract_renewed',
            context=context,
            recipient_list=[employee.email]
        )

    # ==================== EMPLOYEE EMAILS ====================
    
    @classmethod
    def send_welcome_email(cls, employee, username=None, password=None):
        """Send welcome email to new employee"""
        context = {
            'employee_name': employee.name,
            'department': employee.department.name if employee.department else 'N/A',
            'job_title': employee.job_title.name if employee.job_title else 'N/A',
            'start_date': employee.contract_start_date,
            'username': username,
            'password': password,  # Only include if auto-generated
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject='[HRM] Chào mừng bạn gia nhập công ty!',
            template_name='welcome',
            context=context,
            recipient_list=[employee.email]
        )
    
    @classmethod
    def send_account_created(cls, employee, username, temp_password):
        """Send account credentials to employee"""
        context = {
            'employee_name': employee.name,
            'username': username,
            'temp_password': temp_password,
            'login_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject='[HRM] Tài khoản của bạn đã được tạo',
            template_name='account_created',
            context=context,
            recipient_list=[employee.email]
        )

    # ==================== REWARD/DISCIPLINE EMAILS ====================
    
    @classmethod
    def send_reward_notification(cls, reward):
        """Notify employee about reward"""
        context = {
            'employee_name': reward.employee.name,
            'description': reward.description,
            'amount': reward.amount,
            'date': reward.date,
            'cash_payment': reward.cash_payment,
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject='[HRM] Thông báo khen thưởng',
            template_name='reward_notification',
            context=context,
            recipient_list=[reward.employee.email]
        )
    
    @classmethod
    def send_discipline_notification(cls, discipline):
        """Notify employee about discipline"""
        context = {
            'employee_name': discipline.employee.name,
            'description': discipline.description,
            'amount': discipline.amount,
            'date': discipline.date,
            'company_name': 'HRM System',
        }
        
        return cls._send_email(
            subject='[HRM] Thông báo kỷ luật',
            template_name='discipline_notification',
            context=context,
            recipient_list=[discipline.employee.email]
        )


# Convenience functions for direct import
send_leave_approved = EmailService.send_leave_approved
send_leave_rejected = EmailService.send_leave_rejected
send_expense_approved = EmailService.send_expense_approved
send_expense_rejected = EmailService.send_expense_rejected
send_appraisal_reminder = EmailService.send_appraisal_reminder
send_welcome_email = EmailService.send_welcome_email
send_contract_expiring_alert = EmailService.send_contract_expiring_alert
send_reward_notification = EmailService.send_reward_notification
send_discipline_notification = EmailService.send_discipline_notification
