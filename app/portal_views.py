"""
Employee Portal Views
Self-service portal for all employees to manage their own data
"""
from functools import wraps
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
from .forms import LeaveRequestForm, ExpenseForm, EmployeeProfileForm, PasswordChangeForm
from .permissions import get_user_employee
from .leave_helpers import (
    calculate_working_days, check_leave_balance, 
    update_leave_balance, approve_leave_request, 
    reject_leave_request, cancel_leave_request,
    get_leave_summary
)

# Decorator for manager-only views
def require_manager_permission(view_func):
    """Decorator to require manager permission"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        employee = get_user_employee(request.user)
        if not employee or not employee.is_manager:
            messages.error(request, 'Tính năng này chỉ dành cho Manager.')
            return redirect('portal_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


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
            
            # Calculate total days using helper function
            total_days = calculate_working_days(
                leave_request.start_date, 
                leave_request.end_date
            )
            leave_request.total_days = total_days
            
            # Check leave balance using helper function
            current_year = leave_request.start_date.year
            has_balance, message, leave_balance = check_leave_balance(
                employee=employee,
                leave_type=leave_request.leave_type,
                requested_days=total_days,
                year=current_year
            )
            
            if not has_balance:
                messages.error(request, message)
                # Re-render form with error
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
            
            # Update leave balance using helper function
            update_leave_balance(
                employee=employee,
                leave_type=leave_request.leave_type,
                days=total_days,
                operation='add',
                year=current_year
            )
            
            # Save leave request
            leave_request.save()
            
            messages.success(
                request, 
                f'Đã gửi đơn xin nghỉ phép thành công! '
                f'Số ngày: {total_days} ngày. '
                f'Đơn đang chờ phê duyệt.'
            )
            return redirect('portal_leaves')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin form.')
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
            
            # Validate file upload if provided
            if 'receipt' in request.FILES:
                receipt_file = request.FILES['receipt']
                
                # Check file size (max 5MB)
                max_size = 5 * 1024 * 1024  # 5MB in bytes
                if receipt_file.size > max_size:
                    messages.error(
                        request,
                        f'Kích thước file quá lớn! '
                        f'Tối đa 5MB, file của bạn: {receipt_file.size / (1024*1024):.2f}MB'
                    )
                    context = {
                        'employee': employee,
                        'form': form,
                    }
                    return render(request, 'portal/expenses/create.html', context)
                
                # Check file extension
                allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf']
                file_extension = receipt_file.name.split('.')[-1].lower()
                if file_extension not in allowed_extensions:
                    messages.error(
                        request,
                        f'Định dạng file không hợp lệ! '
                        f'Chỉ chấp nhận: {", ".join(allowed_extensions)}'
                    )
                    context = {
                        'employee': employee,
                        'form': form,
                    }
                    return render(request, 'portal/expenses/create.html', context)
            
            # Additional validation: Check if amount exceeds category limit (if exists)
            if hasattr(expense.category, 'max_amount') and expense.category.max_amount:
                if expense.amount > expense.category.max_amount:
                    messages.warning(
                        request,
                        f'Số tiền vượt quá hạn mức của danh mục '
                        f'({expense.category.max_amount:,.0f} VNĐ). '
                        f'Đơn cần được phê duyệt bởi cấp cao hơn.'
                    )
            
            # Save expense
            try:
                expense.save()
                messages.success(
                    request,
                    f'Đã tạo đơn hoàn tiền thành công! '
                    f'Số tiền: {expense.amount:,.0f} VNĐ. '
                    f'Đơn đang chờ phê duyệt.'
                )
                return redirect('portal_expenses')
            except Exception as e:
                messages.error(request, f'Lỗi khi lưu đơn: {str(e)}')
                context = {
                    'employee': employee,
                    'form': form,
                }
                return render(request, 'portal/expenses/create.html', context)
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin form.')
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
    
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            # Validate avatar file if provided
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                
                # Check file size (max 2MB)
                max_size = 2 * 1024 * 1024  # 2MB in bytes
                if avatar_file.size > max_size:
                    messages.error(
                        request,
                        f'Kích thước ảnh quá lớn! '
                        f'Tối đa 2MB, ảnh của bạn: {avatar_file.size / (1024*1024):.2f}MB'
                    )
                    context = {
                        'employee': employee,
                        'form': form,
                    }
                    return render(request, 'portal/profile/edit.html', context)
                
                # Check file extension
                allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
                file_extension = avatar_file.name.split('.')[-1].lower()
                if file_extension not in allowed_extensions:
                    messages.error(
                        request,
                        f'Định dạng ảnh không hợp lệ! '
                        f'Chỉ chấp nhận: {", ".join(allowed_extensions)}'
                    )
                    context = {
                        'employee': employee,
                        'form': form,
                    }
                    return render(request, 'portal/profile/edit.html', context)
            
            # Save profile changes
            try:
                form.save()
                messages.success(request, 'Đã cập nhật thông tin cá nhân thành công!')
                return redirect('portal_profile')
            except Exception as e:
                messages.error(request, f'Lỗi khi lưu thông tin: {str(e)}')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin form.')
    else:
        form = EmployeeProfileForm(instance=employee)
    
    context = {
        'employee': employee,
        'form': form,
    }
    
    return render(request, 'portal/profile/edit.html', context)


@login_required
def password_change(request):
    """Đổi mật khẩu"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Get new password from form
            new_password = form.cleaned_data['new_password']
            
            # Update password
            try:
                request.user.set_password(new_password)
                request.user.save()
                
                # Update session to prevent logout
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                
                messages.success(
                    request,
                    'Đã đổi mật khẩu thành công! '
                    'Vui lòng sử dụng mật khẩu mới cho lần đăng nhập tiếp theo.'
                )
                return redirect('portal_profile')
            except Exception as e:
                messages.error(request, f'Lỗi khi đổi mật khẩu: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'employee': employee,
        'form': form,
    }
    
    return render(request, 'portal/profile/password_change.html', context)


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
    """Phê duyệt đơn nghỉ phép (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    employee = get_user_employee(request.user)
    
    try:
        leave_request = get_object_or_404(
            LeaveRequest, 
            id=leave_id, 
            employee__department=employee.department
        )
        
        # Use helper function for approval
        success, message = approve_leave_request(leave_request, employee)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'leave': {
                    'id': leave_request.id,
                    'employee_name': leave_request.employee.name,
                    'leave_type': leave_request.leave_type.name,
                    'start_date': leave_request.start_date.strftime('%d/%m/%Y'),
                    'end_date': leave_request.end_date.strftime('%d/%m/%Y'),
                    'total_days': leave_request.total_days,
                    'status': leave_request.status,
                    'approved_by': employee.name,
                    'approved_at': leave_request.approved_at.strftime('%d/%m/%Y %H:%M') if leave_request.approved_at else None
                }
            })
        else:
            return JsonResponse({'success': False, 'message': message}, status=400)
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500)


@login_required
@require_manager_permission
def team_leave_reject(request, leave_id):
    """Từ chối đơn nghỉ phép (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    employee = get_user_employee(request.user)
    
    try:
        import json
        data = json.loads(request.body)
        rejection_reason = data.get('reason', '')
        
        if not rejection_reason:
            return JsonResponse({'success': False, 'message': 'Vui lòng nhập lý do từ chối'}, status=400)
        
        leave_request = get_object_or_404(
            LeaveRequest, 
            id=leave_id, 
            employee__department=employee.department
        )
        
        # Use helper function for rejection
        success, message = reject_leave_request(leave_request, employee, rejection_reason)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'leave': {
                    'id': leave_request.id,
                    'employee_name': leave_request.employee.name,
                    'leave_type': leave_request.leave_type.name,
                    'status': leave_request.status,
                    'rejection_reason': leave_request.rejection_reason,
                    'approved_by': employee.name,
                    'approved_at': leave_request.approved_at.strftime('%d/%m/%Y %H:%M') if leave_request.approved_at else None
                }
            })
        else:
            return JsonResponse({'success': False, 'message': message}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500)


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
    """Phê duyệt đơn hoàn tiền (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    employee = get_user_employee(request.user)
    
    try:
        expense = get_object_or_404(
            Expense, 
            id=expense_id, 
            employee__department=employee.department
        )
        
        if expense.status != 'pending':
            return JsonResponse({
                'success': False, 
                'message': 'Đơn này không ở trạng thái chờ duyệt'
            }, status=400)
        
        # Approve expense
        expense.status = 'approved'
        expense.approved_by = employee
        expense.approved_at = timezone.now()
        expense.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã phê duyệt đơn hoàn tiền thành công',
            'expense': {
                'id': expense.id,
                'employee_name': expense.employee.name,
                'category': expense.category.name,
                'amount': float(expense.amount),
                'amount_formatted': f'{expense.amount:,.0f} VNĐ',
                'date': expense.date.strftime('%d/%m/%Y'),
                'description': expense.description,
                'status': expense.status,
                'approved_by': employee.name,
                'approved_at': expense.approved_at.strftime('%d/%m/%Y %H:%M')
            }
        })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500)


@login_required
@require_manager_permission
def team_expense_reject(request, expense_id):
    """Từ chối đơn hoàn tiền (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    employee = get_user_employee(request.user)
    
    try:
        import json
        data = json.loads(request.body)
        rejection_reason = data.get('reason', '')
        
        if not rejection_reason:
            return JsonResponse({'success': False, 'message': 'Vui lòng nhập lý do từ chối'}, status=400)
        
        expense = get_object_or_404(
            Expense, 
            id=expense_id, 
            employee__department=employee.department
        )
        
        if expense.status != 'pending':
            return JsonResponse({
                'success': False, 
                'message': 'Đơn này không ở trạng thái chờ duyệt'
            }, status=400)
        
        # Reject expense
        expense.status = 'rejected'
        expense.approved_by = employee
        expense.approved_at = timezone.now()
        expense.rejection_reason = rejection_reason
        expense.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã từ chối đơn hoàn tiền',
            'expense': {
                'id': expense.id,
                'employee_name': expense.employee.name,
                'category': expense.category.name,
                'status': expense.status,
                'rejection_reason': expense.rejection_reason,
                'approved_by': employee.name,
                'approved_at': expense.approved_at.strftime('%d/%m/%Y %H:%M')
            }
        })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500)


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
