"""
Employee Portal Views
Self-service portal for all employees to manage their own data
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    Employee, LeaveType, LeaveRequest, LeaveBalance, 
    Payroll, Attendance, Expense, ExpenseCategory,
    Appraisal, AppraisalScore
)
from .forms import LeaveRequestForm, ExpenseForm
from .permissions import require_manager_permission, get_user_employee


# ======================== DASHBOARD ========================

@login_required
def dashboard(request):
    """
    Employee Portal Dashboard
    Hiển thị thông tin tổng quan, thông báo, quick actions
    """
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # Get current year
    current_year = timezone.now().year
    current_month = timezone.now().month
    
    # Leave balance
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    ).select_related('leave_type')
    
    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='pending'
    ).count()
    
    # Recent payrolls (last 3 months)
    recent_payrolls = Payroll.objects.filter(
        employee=employee
    ).order_by('-year', '-month')[:3]
    
    # This month attendance
    attendance_count = Attendance.objects.filter(
        employee=employee,
        date__year=timezone.now().year,
        date__month=timezone.now().month
    ).count()
    
    # Pending expenses
    pending_expenses = Expense.objects.filter(
        employee=employee,
        status='pending'
    ).count()
    
    # Pending appraisals
    pending_appraisals = Appraisal.objects.filter(
        employee=employee,
        status='pending_self'
    ).count()
    
    # Manager notifications (if manager)
    manager_notifications = {}
    if employee.is_manager:
        manager_notifications = {
            'pending_leaves': LeaveRequest.objects.filter(
                employee__department=employee.department,
                status='pending'
            ).exclude(employee=employee).count(),
            'pending_expenses': Expense.objects.filter(
                employee__department=employee.department,
                status='pending'
            ).exclude(employee=employee).count(),
        }
    
    context = {
        'employee': employee,
        'leave_balances': leave_balances,
        'pending_leaves': pending_leaves,
        'recent_payrolls': recent_payrolls,
        'attendance_count': attendance_count,
        'pending_expenses': pending_expenses,
        'pending_appraisals': pending_appraisals,
        'manager_notifications': manager_notifications,
    }
    
    return render(request, 'portal/dashboard.html', context)


# ======================== LEAVE MANAGEMENT ========================

@login_required
def leaves_list(request):
    """Danh sách đơn nghỉ phép của nhân viên"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    current_year = timezone.now().year
    
    # Leave balances
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    ).select_related('leave_type')
    
    # Leave requests
    leave_requests = LeaveRequest.objects.filter(
        employee=employee
    ).select_related('leave_type', 'approved_by').order_by('-created_at')
    
    context = {
        'employee': employee,
        'leave_balances': leave_balances,
        'leave_requests': leave_requests,
        'current_year': current_year,
    }
    
    return render(request, 'portal/leaves/list.html', context)


@login_required
def leave_create(request):
    """Tạo đơn xin nghỉ phép mới"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.status = 'pending'
            leave_request.save()
            messages.success(request, 'Đã gửi đơn xin nghỉ phép thành công!')
            return redirect('portal_leaves')
    else:
        form = LeaveRequestForm()
    
    # Get leave balances
    current_year = timezone.now().year
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    ).select_related('leave_type')
    
    context = {
        'employee': employee,
        'form': form,
        'leave_balances': leave_balances,
    }
    
    return render(request, 'portal/leaves/create.html', context)


@login_required
def leave_detail(request, leave_id):
    """Chi tiết đơn nghỉ phép"""
    employee = get_user_employee(request.user)
    leave_request = get_object_or_404(LeaveRequest, id=leave_id, employee=employee)
    
    context = {
        'employee': employee,
        'leave_request': leave_request,
    }
    
    return render(request, 'portal/leaves/detail.html', context)


@login_required
def leave_cancel(request, leave_id):
    """Hủy đơn nghỉ phép (chỉ khi pending)"""
    employee = get_user_employee(request.user)
    leave_request = get_object_or_404(LeaveRequest, id=leave_id, employee=employee)
    
    if leave_request.status == 'pending':
        leave_request.status = 'cancelled'
        leave_request.save()
        messages.success(request, 'Đã hủy đơn xin nghỉ phép.')
    else:
        messages.error(request, 'Không thể hủy đơn đã được duyệt/từ chối.')
    
    return redirect('portal_leaves')


# ======================== PAYROLL ========================

@login_required
def payroll_list(request):
    """Danh sách bảng lương"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    payrolls = Payroll.objects.filter(
        employee=employee
    ).order_by('-year', '-month')
    
    context = {
        'employee': employee,
        'payrolls': payrolls,
    }
    
    return render(request, 'portal/payroll/list.html', context)


@login_required
def payroll_detail(request, payroll_id):
    """Chi tiết bảng lương"""
    employee = get_user_employee(request.user)
    payroll = get_object_or_404(Payroll, id=payroll_id, employee=employee)
    
    context = {
        'employee': employee,
        'payroll': payroll,
    }
    
    return render(request, 'portal/payroll/detail.html', context)


@login_required
def payroll_download(request, payroll_id):
    """Download payslip PDF"""
    employee = get_user_employee(request.user)
    payroll = get_object_or_404(Payroll, id=payroll_id, employee=employee)
    
    # TODO: Implement PDF generation
    messages.info(request, 'Tính năng download PDF sẽ được cập nhật sau.')
    return redirect('portal_payroll_detail', payroll_id=payroll_id)


# ======================== ATTENDANCE ========================

@login_required
def attendance_list(request):
    """Lịch sử chấm công"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # Get current month or filter by month/year
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).order_by('-date')
    
    # Statistics
    total_days = attendances.count()
    working_days = attendances.filter(status='present').count()
    late_days = attendances.filter(status='late').count()
    absent_days = attendances.filter(status='absent').count()
    total_hours = sum([a.working_hours or 0 for a in attendances])
    
    context = {
        'employee': employee,
        'attendances': attendances,
        'year': year,
        'month': month,
        'stats': {
            'total_days': total_days,
            'working_days': working_days,
            'late_days': late_days,
            'absent_days': absent_days,
            'total_hours': total_hours,
        }
    }
    
    return render(request, 'portal/attendance/list.html', context)


@login_required
def attendance_calendar(request):
    """Xem chấm công dạng calendar"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # TODO: Implement calendar view
    messages.info(request, 'Tính năng calendar view sẽ được cập nhật sau.')
    return redirect('portal_attendance')


# ======================== EXPENSES ========================

@login_required
def expenses_list(request):
    """Danh sách đơn hoàn tiền"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    expenses = Expense.objects.filter(
        employee=employee
    ).select_related('category', 'approved_by', 'paid_by').order_by('-date')
    
    context = {
        'employee': employee,
        'expenses': expenses,
    }
    
    return render(request, 'portal/expenses/list.html', context)


@login_required
def expense_create(request):
    """Tạo đơn hoàn tiền mới"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.employee = employee
            expense.status = 'pending'
            expense.save()
            messages.success(request, 'Đã tạo đơn hoàn tiền thành công!')
            return redirect('portal_expenses')
    else:
        form = ExpenseForm()
    
    context = {
        'employee': employee,
        'form': form,
    }
    
    return render(request, 'portal/expenses/create.html', context)


@login_required
def expense_detail(request, expense_id):
    """Chi tiết đơn hoàn tiền"""
    employee = get_user_employee(request.user)
    expense = get_object_or_404(Expense, id=expense_id, employee=employee)
    
    context = {
        'employee': employee,
        'expense': expense,
    }
    
    return render(request, 'portal/expenses/detail.html', context)


@login_required
def expense_cancel(request, expense_id):
    """Hủy đơn hoàn tiền (chỉ khi pending)"""
    employee = get_user_employee(request.user)
    expense = get_object_or_404(Expense, id=expense_id, employee=employee)
    
    if expense.status == 'pending':
        expense.status = 'cancelled'
        expense.save()
        messages.success(request, 'Đã hủy đơn hoàn tiền.')
    else:
        messages.error(request, 'Không thể hủy đơn đã được duyệt/từ chối.')
    
    return redirect('portal_expenses')


# ======================== PROFILE ========================

@login_required
def profile_view(request):
    """Xem thông tin cá nhân"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'portal/profile/view.html', context)


@login_required
def profile_edit(request):
    """Chỉnh sửa thông tin cá nhân (giới hạn)"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # TODO: Implement profile edit form (only personal fields)
    messages.info(request, 'Tính năng chỉnh sửa profile sẽ được cập nhật sau.')
    return redirect('portal_profile')


@login_required
def password_change(request):
    """Đổi mật khẩu"""
    # TODO: Implement password change
    messages.info(request, 'Tính năng đổi mật khẩu sẽ được cập nhật sau.')
    return redirect('portal_profile')


# ======================== DOCUMENTS & ANNOUNCEMENTS ========================

@login_required
def documents_list(request):
    """Danh sách tài liệu công ty"""
    # TODO: Implement when Document model is created
    messages.info(request, 'Tính năng tài liệu sẽ được cập nhật sau.')
    return redirect('portal_dashboard')


@login_required
def announcements_list(request):
    """Danh sách thông báo"""
    # TODO: Implement when Announcement model is created
    messages.info(request, 'Tính năng thông báo sẽ được cập nhật sau.')
    return redirect('portal_dashboard')


# ======================== MANAGER FEATURES ========================

@login_required
@require_manager_permission
def approvals_dashboard(request):
    """Dashboard phê duyệt cho Manager"""
    employee = get_user_employee(request.user)
    
    # Get team members (same department)
    team_members = Employee.objects.filter(
        department=employee.department
    ).exclude(id=employee.id)
    
    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(
        employee__department=employee.department,
        status='pending'
    ).select_related('employee', 'leave_type').order_by('-created_at')
    
    # Pending expenses
    pending_expenses = Expense.objects.filter(
        employee__department=employee.department,
        status='pending'
    ).select_related('employee', 'category').order_by('-date')
    
    context = {
        'employee': employee,
        'team_members': team_members,
        'pending_leaves': pending_leaves,
        'pending_expenses': pending_expenses,
    }
    
    return render(request, 'portal/approvals/dashboard.html', context)


@login_required
@require_manager_permission
def team_leaves(request):
    """Danh sách đơn nghỉ phép của team"""
    employee = get_user_employee(request.user)
    
    leave_requests = LeaveRequest.objects.filter(
        employee__department=employee.department
    ).select_related('employee', 'leave_type', 'approved_by').order_by('-created_at')
    
    context = {
        'employee': employee,
        'leave_requests': leave_requests,
    }
    
    return render(request, 'portal/approvals/team_leaves.html', context)


@login_required
@require_manager_permission
def team_leave_approve(request, leave_id):
    """Phê duyệt đơn nghỉ phép"""
    employee = get_user_employee(request.user)
    leave_request = get_object_or_404(
        LeaveRequest, 
        id=leave_id, 
        employee__department=employee.department
    )
    
    if leave_request.status == 'pending':
        leave_request.status = 'approved'
        leave_request.approved_by = employee
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        # Update leave balance
        leave_balance = LeaveBalance.objects.get(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
        days = (leave_request.end_date - leave_request.start_date).days + 1
        leave_balance.used_days += days
        leave_balance.remaining_days -= days
        leave_balance.save()
        
        messages.success(request, 'Đã phê duyệt đơn nghỉ phép.')
    else:
        messages.error(request, 'Đơn này không ở trạng thái chờ duyệt.')
    
    return redirect('portal_team_leaves')


@login_required
@require_manager_permission
def team_leave_reject(request, leave_id):
    """Từ chối đơn nghỉ phép"""
    employee = get_user_employee(request.user)
    leave_request = get_object_or_404(
        LeaveRequest, 
        id=leave_id, 
        employee__department=employee.department
    )
    
    if leave_request.status == 'pending':
        leave_request.status = 'rejected'
        leave_request.approved_by = employee
        leave_request.approved_at = timezone.now()
        leave_request.save()
        messages.success(request, 'Đã từ chối đơn nghỉ phép.')
    else:
        messages.error(request, 'Đơn này không ở trạng thái chờ duyệt.')
    
    return redirect('portal_team_leaves')


@login_required
@require_manager_permission
def team_expenses(request):
    """Danh sách đơn hoàn tiền của team"""
    employee = get_user_employee(request.user)
    
    expenses = Expense.objects.filter(
        employee__department=employee.department
    ).select_related('employee', 'category', 'approved_by', 'paid_by').order_by('-date')
    
    context = {
        'employee': employee,
        'expenses': expenses,
    }
    
    return render(request, 'portal/approvals/team_expenses.html', context)


@login_required
@require_manager_permission
def team_expense_approve(request, expense_id):
    """Phê duyệt đơn hoàn tiền"""
    employee = get_user_employee(request.user)
    expense = get_object_or_404(
        Expense, 
        id=expense_id, 
        employee__department=employee.department
    )
    
    if expense.status == 'pending':
        expense.status = 'approved'
        expense.approved_by = employee
        expense.approved_at = timezone.now()
        expense.save()
        messages.success(request, 'Đã phê duyệt đơn hoàn tiền.')
    else:
        messages.error(request, 'Đơn này không ở trạng thái chờ duyệt.')
    
    return redirect('portal_team_expenses')


@login_required
@require_manager_permission
def team_expense_reject(request, expense_id):
    """Từ chối đơn hoàn tiền"""
    employee = get_user_employee(request.user)
    expense = get_object_or_404(
        Expense, 
        id=expense_id, 
        employee__department=employee.department
    )
    
    if expense.status == 'pending':
        expense.status = 'rejected'
        expense.approved_by = employee
        expense.approved_at = timezone.now()
        expense.save()
        messages.success(request, 'Đã từ chối đơn hoàn tiền.')
    else:
        messages.error(request, 'Đơn này không ở trạng thái chờ duyệt.')
    
    return redirect('portal_team_expenses')


@login_required
@require_manager_permission
def team_reports(request):
    """Báo cáo team"""
    # TODO: Implement team reports
    messages.info(request, 'Tính năng báo cáo team sẽ được cập nhật sau.')
    return redirect('portal_approvals')


# ======================== APPRAISAL ========================

@login_required
def my_appraisals(request):
    """Danh sách đánh giá của nhân viên"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    appraisals = Appraisal.objects.filter(
        employee=employee
    ).select_related('period', 'manager').order_by('-period__start_date')
    
    context = {
        'employee': employee,
        'appraisals': appraisals,
    }
    
    return render(request, 'portal/appraisal/list.html', context)


@login_required
def appraisal_detail(request, appraisal_id):
    """Chi tiết đánh giá"""
    employee = get_user_employee(request.user)
    appraisal = get_object_or_404(Appraisal, id=appraisal_id, employee=employee)
    
    context = {
        'employee': employee,
        'appraisal': appraisal,
    }
    
    return render(request, 'portal/appraisal/detail.html', context)


@login_required
def self_assessment(request, appraisal_id):
    """Tự đánh giá"""
    employee = get_user_employee(request.user)
    appraisal = get_object_or_404(Appraisal, id=appraisal_id, employee=employee)
    
    # TODO: Implement self assessment form
    messages.info(request, 'Tính năng tự đánh giá sẽ được cập nhật sau.')
    return redirect('portal_appraisal_detail', appraisal_id=appraisal_id)
