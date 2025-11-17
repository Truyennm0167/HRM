"""
Helper functions for leave management
Handle leave balance calculation and payroll integration
"""
from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from .models import LeaveRequest, LeaveBalance


def calculate_working_days(start_date, end_date):
    """
    Calculate number of working days (Monday-Friday) between two dates
    
    Args:
        start_date: datetime.date - Start date
        end_date: datetime.date - End date
        
    Returns:
        int: Number of working days
    """
    total_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # 0 = Monday, 6 = Sunday
        if current_date.weekday() < 5:  # Monday to Friday
            total_days += 1
        current_date += timedelta(days=1)
    
    return total_days


def check_leave_balance(employee, leave_type, requested_days, year=None):
    """
    Check if employee has enough leave balance
    
    Args:
        employee: Employee object
        leave_type: LeaveType object
        requested_days: float - Number of days requested
        year: int - Year to check (default: current year)
        
    Returns:
        tuple: (bool, str, LeaveBalance or None)
            - bool: True if has enough balance
            - str: Message
            - LeaveBalance: Balance object or None
    """
    if year is None:
        year = timezone.now().year
    
    leave_balance = LeaveBalance.objects.filter(
        employee=employee,
        leave_type=leave_type,
        year=year
    ).first()
    
    if not leave_balance:
        # Create new leave balance if not exists
        leave_balance = LeaveBalance.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            total_days=leave_type.max_days_per_year,
            used_days=0
        )
    
    if leave_balance.remaining_days < requested_days:
        return (
            False, 
            f'Số ngày nghỉ phép không đủ! Còn lại: {leave_balance.remaining_days} ngày, Yêu cầu: {requested_days} ngày',
            leave_balance
        )
    
    return (True, 'OK', leave_balance)


@transaction.atomic
def update_leave_balance(employee, leave_type, days, operation='add', year=None):
    """
    Update leave balance when leave is approved/rejected/cancelled
    
    Args:
        employee: Employee object
        leave_type: LeaveType object
        days: float - Number of days to add/subtract
        operation: str - 'add' to add used_days, 'subtract' to remove used_days
        year: int - Year (default: current year)
        
    Returns:
        LeaveBalance: Updated balance object
    """
    if year is None:
        year = timezone.now().year
    
    leave_balance, created = LeaveBalance.objects.get_or_create(
        employee=employee,
        leave_type=leave_type,
        year=year,
        defaults={
            'total_days': leave_type.max_days_per_year,
            'used_days': 0
        }
    )
    
    if operation == 'add':
        leave_balance.used_days += days
    elif operation == 'subtract':
        leave_balance.used_days = max(0, leave_balance.used_days - days)
    
    leave_balance.save()  # Auto-calculate remaining_days in model
    
    return leave_balance


def approve_leave_request(leave_request, approved_by):
    """
    Approve a leave request and update balance
    
    Args:
        leave_request: LeaveRequest object
        approved_by: Employee object (manager/HR)
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    if leave_request.status != 'pending':
        return (False, f'Đơn nghỉ phép đã được xử lý (trạng thái: {leave_request.get_status_display()})')
    
    try:
        with transaction.atomic():
            # Check if balance was already updated (in case of duplicate approval)
            year = leave_request.start_date.year
            
            # Update leave request status
            leave_request.status = 'approved'
            leave_request.approved_by = approved_by
            leave_request.approved_at = timezone.now()
            leave_request.save()
            
            # Note: Leave balance was already updated when request was created
            # No need to update again here
            
            return (True, 'Đã duyệt đơn nghỉ phép thành công!')
    except Exception as e:
        return (False, f'Lỗi khi duyệt đơn: {str(e)}')


def reject_leave_request(leave_request, rejected_by, reason=''):
    """
    Reject a leave request and restore balance
    
    Args:
        leave_request: LeaveRequest object
        rejected_by: Employee object (manager/HR)
        reason: str - Reason for rejection
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    if leave_request.status != 'pending':
        return (False, f'Đơn nghỉ phép đã được xử lý (trạng thái: {leave_request.get_status_display()})')
    
    try:
        with transaction.atomic():
            year = leave_request.start_date.year
            
            # Restore leave balance (subtract used_days)
            update_leave_balance(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                days=leave_request.total_days,
                operation='subtract',
                year=year
            )
            
            # Update leave request status
            leave_request.status = 'rejected'
            leave_request.approved_by = rejected_by
            leave_request.approved_at = timezone.now()
            leave_request.rejection_reason = reason
            leave_request.save()
            
            return (True, 'Đã từ chối đơn nghỉ phép và hoàn lại số ngày phép!')
    except Exception as e:
        return (False, f'Lỗi khi từ chối đơn: {str(e)}')


def cancel_leave_request(leave_request):
    """
    Cancel a leave request (by employee) and restore balance
    
    Args:
        leave_request: LeaveRequest object
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    if leave_request.status not in ['pending', 'approved']:
        return (False, f'Không thể hủy đơn đã {leave_request.get_status_display()}')
    
    # Don't allow cancellation if leave has started
    today = timezone.now().date()
    if leave_request.start_date <= today:
        return (False, 'Không thể hủy đơn nghỉ phép đã bắt đầu hoặc trong quá khứ')
    
    try:
        with transaction.atomic():
            year = leave_request.start_date.year
            
            # Restore leave balance (subtract used_days)
            update_leave_balance(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                days=leave_request.total_days,
                operation='subtract',
                year=year
            )
            
            # Update leave request status
            leave_request.status = 'cancelled'
            leave_request.save()
            
            return (True, 'Đã hủy đơn nghỉ phép và hoàn lại số ngày phép!')
    except Exception as e:
        return (False, f'Lỗi khi hủy đơn: {str(e)}')


def get_leave_summary(employee, year=None):
    """
    Get leave summary for an employee
    
    Args:
        employee: Employee object
        year: int - Year (default: current year)
        
    Returns:
        dict: Summary of leave usage
    """
    if year is None:
        year = timezone.now().year
    
    balances = LeaveBalance.objects.filter(
        employee=employee,
        year=year
    ).select_related('leave_type')
    
    total_allocated = sum(b.total_days for b in balances)
    total_used = sum(b.used_days for b in balances)
    total_remaining = sum(b.remaining_days for b in balances)
    
    pending_requests = LeaveRequest.objects.filter(
        employee=employee,
        status='pending',
        start_date__year=year
    ).count()
    
    approved_requests = LeaveRequest.objects.filter(
        employee=employee,
        status='approved',
        start_date__year=year
    ).count()
    
    return {
        'year': year,
        'total_allocated': total_allocated,
        'total_used': total_used,
        'total_remaining': total_remaining,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'balances': list(balances),
    }
