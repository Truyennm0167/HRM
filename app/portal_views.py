"""
Employee Portal Views
Self-service portal for all employees to manage their own data
"""
import json
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models

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
    from django.core.paginator import Paginator
    
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
    
    # Leave requests with filters
    leave_requests = LeaveRequest.objects.filter(
        employee=employee
    ).select_related('leave_type', 'approved_by')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    
    leave_type_filter = request.GET.get('leave_type')
    if leave_type_filter:
        leave_requests = leave_requests.filter(leave_type_id=leave_type_filter)
    
    year_filter = request.GET.get('year')
    if year_filter:
        leave_requests = leave_requests.filter(start_date__year=year_filter)
    
    search_query = request.GET.get('q')
    if search_query:
        leave_requests = leave_requests.filter(
            models.Q(reason__icontains=search_query) |
            models.Q(leave_type__name__icontains=search_query)
        )
    
    leave_requests = leave_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(leave_requests, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all leave types for filter dropdown
    leave_types = LeaveType.objects.filter(is_active=True)
    
    # Calculate stats
    used_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Approved',
        start_date__year=current_year
    ).aggregate(models.Sum('total_days'))['total_days__sum'] or 0
    
    pending_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='Pending'
    ).aggregate(models.Sum('total_days'))['total_days__sum'] or 0
    
    remaining_leaves = employee.annual_leave_balance - used_leaves
    
    context = {
        'employee': employee,
        'leave_balances': leave_balances,
        'page_obj': page_obj,
        'leave_types': leave_types,
        'current_year': current_year,
        'used_leaves': used_leaves,
        'pending_leaves': pending_leaves,
        'remaining_leaves': remaining_leaves,
        'status_filter': status_filter,
        'leave_type_filter': leave_type_filter,
        'year_filter': year_filter,
        'search_query': search_query,
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


@login_required
def leave_calendar(request):
    """Xem calendar nghỉ phép"""
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'portal/leaves/calendar.html', context)


@login_required
def leave_calendar_data(request):
    """JSON data for FullCalendar"""
    employee = get_user_employee(request.user)
    if not employee:
        return JsonResponse({'error': 'Không tìm thấy thông tin nhân viên'}, status=403)
    
    # Get all leaves from same department (team visibility)
    leave_requests = LeaveRequest.objects.filter(
        employee__department=employee.department
    ).select_related('employee', 'leave_type').order_by('-created_at')
    
    # Format for FullCalendar
    events = []
    for leave in leave_requests:
        # Color by status
        if leave.status == 'Approved':
            color = '#28a745'  # Green
        elif leave.status == 'Pending':
            color = '#ffc107'  # Yellow
        elif leave.status == 'Rejected':
            color = '#dc3545'  # Red
        else:
            color = '#6c757d'  # Grey
        
        # Add border for own leaves
        border_width = '3px' if leave.employee == employee else '1px'
        
        events.append({
            'id': leave.id,
            'title': f"{leave.employee.name} - {leave.leave_type.name}",
            'start': leave.start_date.isoformat(),
            'end': (leave.end_date + timezone.timedelta(days=1)).isoformat(),  # FullCalendar exclusive end
            'backgroundColor': color,
            'borderColor': color,
            'borderWidth': border_width,
            'extendedProps': {
                'employee': leave.employee.name,
                'employee_code': leave.employee.employee_code,
                'leave_type': leave.leave_type.name,
                'total_days': leave.total_days,
                'status': leave.status,
                'reason': leave.reason,
                'is_mine': leave.employee == employee
            }
        })
    
    return JsonResponse(events, safe=False)


# ======================== PAYROLL ========================

@login_required
def payroll_list(request):
    """Danh sách bảng lương"""
    from django.core.paginator import Paginator
    
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # Get filter parameters
    year_filter = request.GET.get('year')
    month_filter = request.GET.get('month')
    status_filter = request.GET.get('status')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    payrolls = Payroll.objects.filter(
        employee=employee
    ).order_by('-year', '-month')
    
    # Apply filters
    if year_filter:
        payrolls = payrolls.filter(year=year_filter)
    if month_filter:
        payrolls = payrolls.filter(month=month_filter)
    if status_filter:
        payrolls = payrolls.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(payrolls, 25)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employee': employee,
        'page_obj': page_obj,
        'year_filter': year_filter,
        'month_filter': month_filter,
        'status_filter': status_filter,
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
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from django.http import HttpResponse
    
    employee = get_user_employee(request.user)
    payroll = get_object_or_404(Payroll, id=payroll_id, employee=employee)
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        spaceAfter=8
    )
    
    # Title
    elements.append(Paragraph("PHIẾU LƯƠNG", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Employee info
    elements.append(Paragraph("Thông tin nhân viên", heading_style))
    emp_data = [
        ['Mã NV:', payroll.employee.employee_code or 'N/A', 'Tháng:', f"{payroll.month}/{payroll.year}"],
        ['Họ tên:', payroll.employee.name, 'Phòng ban:', payroll.employee.department.name if payroll.employee.department else 'N/A'],
        ['Chức vụ:', payroll.employee.position or 'N/A', 'Hệ số lương:', f"{payroll.salary_coefficient:.2f}"],
    ]
    emp_table = Table(emp_data, colWidths=[3*cm, 6*cm, 3*cm, 6*cm])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 0.7*cm))
    
    # Salary breakdown
    elements.append(Paragraph("Chi tiết lương", heading_style))
    salary_data = [
        ['Khoản mục', 'Số lượng', 'Đơn giá', 'Thành tiền'],
        ['Lương cơ bản', f"{payroll.standard_working_days} ngày", f"{payroll.base_salary:,.0f} đ", f"{payroll.base_salary:,.0f} đ"],
        ['Tổng giờ làm việc', f"{payroll.total_working_hours:.1f}h", f"{payroll.hourly_rate:,.0f} đ/h", f"{payroll.total_working_hours * payroll.hourly_rate:,.0f} đ"],
        ['Thưởng', '', '', f"{payroll.bonus:,.0f} đ"],
        ['Phạt', '', '', f"-{payroll.penalty:,.0f} đ"],
    ]
    salary_table = Table(salary_data, colWidths=[6*cm, 3*cm, 4*cm, 5*cm])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(salary_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Total salary
    total_data = [
        ['TỔNG LƯƠNG', f"{payroll.total_salary:,.0f} đ"]
    ]
    total_table = Table(total_data, colWidths=[12*cm, 6*cm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#4caf50')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 1*cm))
    
    # Notes
    if payroll.notes:
        elements.append(Paragraph("Ghi chú", heading_style))
        elements.append(Paragraph(payroll.notes, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        f"Phiếu lương được tạo tự động vào {timezone.now().strftime('%d/%m/%Y %H:%M')}<br/>Trạng thái: {payroll.get_status_display()}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return response
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Phieu_luong_{payroll.employee.employee_code}_{payroll.month}_{payroll.year}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


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


@login_required
def check_in(request):
    """Check-in chấm công"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    employee = get_user_employee(request.user)
    if not employee:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông tin nhân viên'}, status=403)
    
    today = timezone.now().date()
    
    # Check if already checked in today
    existing = Attendance.objects.filter(employee=employee, date=today).first()
    if existing and existing.check_in:
        return JsonResponse({
            'status': 'error',
            'message': 'Bạn đã check-in rồi!',
            'check_in_time': existing.check_in.strftime('%H:%M')
        })
    
    try:
        # Create or update attendance record
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': timezone.now(),
                'status': 'present'
            }
        )
        
        if not created:
            attendance.check_in = timezone.now()
            attendance.status = 'present'
            attendance.save()
        
        # Check if late (after 8:30 AM)
        check_in_time = attendance.check_in.time()
        from datetime import time
        standard_time = time(8, 30)  # 8:30 AM
        is_late = check_in_time > standard_time
        
        if is_late:
            attendance.is_late = True
            attendance.status = 'late'
            attendance.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Check-in thành công!' + (' (Đi muộn)' if is_late else ''),
            'check_in_time': attendance.check_in.strftime('%H:%M:%S'),
            'is_late': is_late
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def check_out(request):
    """Check-out chấm công"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    employee = get_user_employee(request.user)
    if not employee:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông tin nhân viên'}, status=403)
    
    today = timezone.now().date()
    
    # Find today's attendance
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    if not attendance or not attendance.check_in:
        return JsonResponse({
            'status': 'error',
            'message': 'Bạn chưa check-in!'
        })
    
    if attendance.check_out:
        return JsonResponse({
            'status': 'error',
            'message': 'Bạn đã check-out rồi!',
            'check_out_time': attendance.check_out.strftime('%H:%M')
        })
    
    try:
        attendance.check_out = timezone.now()
        
        # Calculate working hours
        delta = attendance.check_out - attendance.check_in
        hours = delta.total_seconds() / 3600
        attendance.working_hours = round(hours, 2)
        
        # Check if early leave (before 5:30 PM)
        from datetime import time
        check_out_time = attendance.check_out.time()
        standard_time = time(17, 30)  # 5:30 PM
        is_early = check_out_time < standard_time
        
        if is_early:
            attendance.is_early_leave = True
        
        attendance.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Check-out thành công!' + (' (Về sớm)' if is_early else ''),
            'check_out_time': attendance.check_out.strftime('%H:%M:%S'),
            'working_hours': attendance.working_hours,
            'is_early': is_early
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def today_attendance(request):
    """Get today's attendance status"""
    employee = get_user_employee(request.user)
    if not employee:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông tin nhân viên'}, status=403)
    
    today = timezone.now().date()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    if not attendance:
        return JsonResponse({
            'status': 'success',
            'has_checked_in': False,
            'has_checked_out': False
        })
    
    return JsonResponse({
        'status': 'success',
        'has_checked_in': bool(attendance.check_in),
        'has_checked_out': bool(attendance.check_out),
        'check_in_time': attendance.check_in.strftime('%H:%M:%S') if attendance.check_in else None,
        'check_out_time': attendance.check_out.strftime('%H:%M:%S') if attendance.check_out else None,
        'working_hours': attendance.working_hours,
        'is_late': attendance.is_late,
        'is_early_leave': attendance.is_early_leave
    })


# ======================== EXPENSES ========================

@login_required
def expenses_list(request):
    """Danh sách đơn hoàn tiền"""
    from django.core.paginator import Paginator
    from django.db.models import Q, Sum
    
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # Get filter parameters
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    year_filter = request.GET.get('year')
    search_query = request.GET.get('q')
    page_number = request.GET.get('page', 1)
    
    # Base queryset
    expenses = Expense.objects.filter(
        employee=employee
    ).select_related('category', 'approved_by', 'paid_by').order_by('-date')
    
    # Apply filters
    if status_filter:
        expenses = expenses.filter(status=status_filter)
    if category_filter:
        expenses = expenses.filter(category_id=category_filter)
    if year_filter:
        expenses = expenses.filter(date__year=year_filter)
    if search_query:
        expenses = expenses.filter(
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(expenses, 25)
    page_obj = paginator.get_page(page_number)
    
    # Get expense categories for filter dropdown
    expense_categories = ExpenseCategory.objects.filter(is_active=True).order_by('name')
    
    # Calculate stats
    current_year = datetime.now().year
    pending_amount = Expense.objects.filter(
        employee=employee, status='Pending', date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    approved_amount = Expense.objects.filter(
        employee=employee, status='Approved', date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = Expense.objects.filter(
        employee=employee, date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'employee': employee,
        'page_obj': page_obj,
        'expense_categories': expense_categories,
        'pending_amount': pending_amount,
        'approved_amount': approved_amount,
        'total_expenses': total_expenses,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'year_filter': year_filter,
        'search_query': search_query,
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
    from .models import Document, DocumentCategory
    
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # Get filter parameters
    category_id = request.GET.get('category')
    search_query = request.GET.get('q', '')
    
    # Base queryset - filter by visibility
    documents = Document.objects.filter(is_active=True)
    
    # Apply visibility filters
    visible_docs = documents.filter(visibility='all')
    
    # Department visibility
    if employee.department:
        dept_docs = documents.filter(visibility='department', departments=employee.department)
        visible_docs = visible_docs | dept_docs
    
    # Manager visibility
    if employee.is_manager:
        manager_docs = documents.filter(visibility='manager')
        visible_docs = visible_docs | manager_docs
    
    # Specific employee visibility
    specific_docs = documents.filter(visibility='specific', specific_employees=employee)
    visible_docs = visible_docs | specific_docs
    
    # Apply filters
    if category_id:
        visible_docs = visible_docs.filter(category_id=category_id)
    
    if search_query:
        visible_docs = visible_docs.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(description__icontains=search_query)
        )
    
    visible_docs = visible_docs.distinct().select_related('category', 'uploaded_by').order_by('-created_at')
    
    # Get categories
    categories = DocumentCategory.objects.filter(is_active=True)
    
    context = {
        'employee': employee,
        'documents': visible_docs,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'portal/documents/list.html', context)


@login_required
def document_download(request, document_id):
    """Download document and track"""
    from .models import Document, DocumentDownload
    
    employee = get_user_employee(request.user)
    if not employee:
        return JsonResponse({'error': 'Không tìm thấy thông tin nhân viên'}, status=403)
    
    # Check visibility
    document = get_object_or_404(Document, id=document_id, is_active=True)
    
    # Verify access
    has_access = False
    if document.visibility == 'all':
        has_access = True
    elif document.visibility == 'department' and employee.department in document.departments.all():
        has_access = True
    elif document.visibility == 'manager' and employee.is_manager:
        has_access = True
    elif document.visibility == 'specific' and employee in document.specific_employees.all():
        has_access = True
    
    if not has_access:
        messages.error(request, 'Bạn không có quyền tải tài liệu này.')
        return redirect('portal_documents')
    
    # Track download
    DocumentDownload.objects.create(
        document=document,
        employee=employee,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Increment counter
    document.downloads_count += 1
    document.save(update_fields=['downloads_count'])
    
    # Serve file
    from django.http import FileResponse
    import os
    
    if os.path.exists(document.file.path):
        response = FileResponse(document.file.open('rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(document.file.name)}"'
        return response
    else:
        messages.error(request, 'Tệp không tồn tại.')
        return redirect('portal_documents')


@login_required
def announcements_list(request):
    """Danh sách thông báo"""
    from .models import Announcement, AnnouncementRead
    from django.db.models import Exists, OuterRef
    
    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'Không tìm thấy thông tin nhân viên.')
        return redirect('login')
    
    # Get announcements visible to this employee
    now = timezone.now()
    announcements = Announcement.objects.filter(
        is_active=True,
        publish_at__lte=now
    ).filter(
        models.Q(expire_at__isnull=True) | models.Q(expire_at__gte=now)
    )
    
    # Filter by target
    visible_announcements = announcements.filter(target_all=True)
    
    if employee.department:
        dept_announcements = announcements.filter(target_departments=employee.department)
        visible_announcements = visible_announcements | dept_announcements
    
    specific_announcements = announcements.filter(target_employees=employee)
    visible_announcements = visible_announcements | specific_announcements
    
    # Annotate with read status
    visible_announcements = visible_announcements.annotate(
        is_read=Exists(AnnouncementRead.objects.filter(
            announcement=OuterRef('pk'),
            employee=employee
        ))
    ).distinct().select_related('created_by').order_by('-is_pinned', '-publish_at')
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        visible_announcements = visible_announcements.filter(category=category)
    
    # Unread count
    unread_count = visible_announcements.filter(is_read=False).count()
    
    context = {
        'employee': employee,
        'announcements': visible_announcements,
        'unread_count': unread_count,
        'selected_category': category,
    }
    
    return render(request, 'portal/announcements/list.html', context)


@login_required
def announcement_detail(request, announcement_id):
    """Chi tiết thông báo và mark as read"""
    from .models import Announcement, AnnouncementRead
    
    employee = get_user_employee(request.user)
    announcement = get_object_or_404(Announcement, id=announcement_id, is_active=True)
    
    # Verify access
    has_access = announcement.target_all
    if not has_access and employee.department:
        has_access = announcement.target_departments.filter(id=employee.department.id).exists()
    if not has_access:
        has_access = announcement.target_employees.filter(id=employee.id).exists()
    
    if not has_access:
        messages.error(request, 'Bạn không có quyền xem thông báo này.')
        return redirect('portal_announcements')
    
    # Mark as read
    AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        employee=employee
    )
    
    context = {
        'employee': employee,
        'announcement': announcement,
    }
    
    return render(request, 'portal/announcements/detail.html', context)


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
    
    # Calculate stats
    stats = {
        'team_members': team_members.count(),
        'pending_leaves': pending_leaves.count(),
        'pending_expenses': pending_expenses.count(),
        'total_pending': pending_leaves.count() + pending_expenses.count(),
    }
    
    context = {
        'employee': employee,
        'team_members': team_members,
        'pending_leaves': pending_leaves,
        'pending_expenses': pending_expenses,
        'stats': stats,
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
    
    # Calculate stats
    from datetime import date
    today = date.today()
    pending_count = leave_requests.filter(status='Pending').count()
    approved_count = leave_requests.filter(
        status='Approved', 
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    rejected_count = leave_requests.filter(
        status='Rejected',
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    team_size = Employee.objects.filter(department=employee.department).count()
    
    context = {
        'employee': employee,
        'leave_requests': leave_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'team_size': team_size,
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
def team_leaves_bulk_action(request):
    """Bulk approve/reject leave requests"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        leave_ids = data.get('leave_ids', [])
        reason = data.get('reason', '')
        
        if not action or not leave_ids:
            return JsonResponse({'success': False, 'message': 'Missing action or leave_ids'}, status=400)
        
        if action not in ['approve', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)
        
        employee = get_user_employee(request.user)
        if not employee or not employee.is_manager:
            return JsonResponse({'success': False, 'message': 'Không có quyền thực hiện'}, status=403)
        
        # Get leave requests
        leave_requests = LeaveRequest.objects.filter(
            id__in=leave_ids,
            employee__department=employee.department,
            status='Pending'
        )
        
        if not leave_requests.exists():
            return JsonResponse({'success': False, 'message': 'Không tìm thấy đơn hợp lệ'}, status=404)
        
        # Perform bulk action
        success_count = 0
        failed_items = []
        
        for leave in leave_requests:
            try:
                if action == 'approve':
                    # Check leave balance
                    has_balance, balance_msg, leave_balance = check_leave_balance(
                        employee=leave.employee,
                        leave_type=leave.leave_type,
                        requested_days=leave.total_days,
                        year=leave.start_date.year
                    )
                    
                    if has_balance:
                        leave.status = 'Approved'
                        leave.approved_by = employee
                        leave.approved_date = timezone.now()
                        leave.save()
                        
                        # Update leave balance
                        if leave_balance:
                            leave_balance.used_days += leave.total_days
                            leave_balance.remaining_days -= leave.total_days
                            leave_balance.save()
                        
                        success_count += 1
                    else:
                        failed_items.append(f"{leave.employee.admin.get_full_name()}: {balance_msg}")
                
                elif action == 'reject':
                    if not reason:
                        failed_items.append(f"{leave.employee.admin.get_full_name()}: Cần lý do từ chối")
                        continue
                    
                    leave.status = 'Rejected'
                    leave.approved_by = employee
                    leave.approved_date = timezone.now()
                    leave.admin_comment = reason
                    leave.save()
                    success_count += 1
                    
            except Exception as e:
                failed_items.append(f"{leave.employee.admin.get_full_name()}: {str(e)}")
        
        # Prepare response message
        if success_count > 0:
            action_text = 'duyệt' if action == 'approve' else 'từ chối'
            message = f'Đã {action_text} thành công {success_count} đơn'
            if failed_items:
                message += f'. Thất bại: {len(failed_items)} đơn'
            return JsonResponse({'success': True, 'message': message, 'failed_items': failed_items})
        else:
            return JsonResponse({'success': False, 'message': 'Không thể xử lý đơn nào', 'failed_items': failed_items}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500)


@login_required
@require_manager_permission
def team_expenses(request):
    """Danh sách đơn hoàn tiền của team"""
    employee = get_user_employee(request.user)
    
    expense_requests = Expense.objects.filter(
        employee__department=employee.department
    ).select_related('employee', 'category', 'approved_by', 'paid_by').order_by('-date')
    
    # Calculate stats
    from datetime import date
    from django.db.models import Sum
    today = date.today()
    pending_expenses = expense_requests.filter(status='pending')
    pending_count = pending_expenses.count()
    total_amount = pending_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    approved_count = expense_requests.filter(
        status='approved',
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    rejected_count = expense_requests.filter(
        status='rejected',
        created_at__year=today.year,
        created_at__month=today.month
    ).count()
    
    context = {
        'employee': employee,
        'expense_requests': expense_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_amount': total_amount,
    }
    
    return render(request, 'portal/approvals/team_expenses.html', context)


@login_required
@require_manager_permission
def team_expenses_bulk_action(request):
    """Bulk approve/reject expense requests"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        expense_ids = data.get('expense_ids', [])
        reason = data.get('reason', '')
        
        if not action or not expense_ids:
            return JsonResponse({'success': False, 'message': 'Missing action or expense_ids'}, status=400)
        
        if action not in ['approve', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)
        
        employee = get_user_employee(request.user)
        if not employee or not employee.is_manager:
            return JsonResponse({'success': False, 'message': 'Không có quyền thực hiện'}, status=403)
        
        # Get expense requests (handle both 'pending' and 'Pending' statuses)
        from django.db.models import Q
        expense_requests = Expense.objects.filter(
            id__in=expense_ids,
            employee__department=employee.department
        ).filter(Q(status='pending') | Q(status='Pending'))
        
        if not expense_requests.exists():
            return JsonResponse({'success': False, 'message': 'Không tìm thấy đơn hợp lệ'}, status=404)
        
        # Perform bulk action
        success_count = 0
        failed_items = []
        
        for expense in expense_requests:
            try:
                if action == 'approve':
                    expense.status = 'approved'
                    expense.approved_by = employee
                    expense.approved_at = timezone.now()
                    expense.save()
                    success_count += 1
                
                elif action == 'reject':
                    if not reason:
                        failed_items.append(f"{expense.employee.admin.get_full_name()}: Cần lý do từ chối")
                        continue
                    
                    expense.status = 'rejected'
                    expense.approved_by = employee
                    expense.approved_at = timezone.now()
                    expense.comment = reason
                    expense.save()
                    success_count += 1
                    
            except Exception as e:
                failed_items.append(f"{expense.employee.admin.get_full_name()}: {str(e)}")
        
        # Prepare response message
        if success_count > 0:
            action_text = 'duyệt' if action == 'approve' else 'từ chối'
            message = f'Đã {action_text} thành công {success_count} đơn'
            if failed_items:
                message += f'. Thất bại: {len(failed_items)} đơn'
            return JsonResponse({'success': True, 'message': message, 'failed_items': failed_items})
        else:
            return JsonResponse({'success': False, 'message': 'Không thể xử lý đơn nào', 'failed_items': failed_items}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi: {str(e)}'}, status=500)


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
    """Báo cáo team cho Manager"""
    from django.db.models import Count, Sum, Avg, Q
    from datetime import date, timedelta
    
    employee = get_user_employee(request.user)
    if not employee or not employee.is_manager:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('portal_dashboard')
    
    # Get date range filter
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Team members
    team_members = Employee.objects.filter(department=employee.department)
    team_size = team_members.count()
    
    # Attendance Statistics
    attendance_stats = Attendance.objects.filter(
        employee__department=employee.department,
        date__year=year,
        date__month=month
    ).aggregate(
        total_late=Count('id', filter=Q(is_late=True)),
        total_early_leave=Count('id', filter=Q(is_early_leave=True)),
        total_absent=Count('id', filter=Q(status='absent')),
        avg_working_hours=Avg('working_hours')
    )
    
    # Leave Statistics
    leave_stats = LeaveRequest.objects.filter(
        employee__department=employee.department,
        created_at__year=year,
        created_at__month=month
    ).aggregate(
        total_requests=Count('id'),
        pending_requests=Count('id', filter=Q(status='Pending')),
        approved_requests=Count('id', filter=Q(status='Approved')),
        rejected_requests=Count('id', filter=Q(status='Rejected')),
        total_leave_days=Sum('total_days', filter=Q(status='Approved'))
    )
    
    # Expense Statistics  
    expense_stats = Expense.objects.filter(
        employee__department=employee.department,
        created_at__year=year,
        created_at__month=month
    ).aggregate(
        total_expenses=Count('id'),
        pending_expenses=Count('id', filter=Q(status='pending')),
        approved_expenses=Count('id', filter=Q(status='approved')),
        total_amount=Sum('amount', filter=Q(status='approved'))
    )
    
    # Top performers (by attendance)
    top_attendance = Attendance.objects.filter(
        employee__department=employee.department,
        date__year=year,
        date__month=month
    ).values('employee__name', 'employee__employee_code').annotate(
        total_hours=Sum('working_hours'),
        late_count=Count('id', filter=Q(is_late=True))
    ).order_by('-total_hours')[:5]
    
    # Recent activities
    recent_leaves = LeaveRequest.objects.filter(
        employee__department=employee.department,
        status='Pending'
    ).select_related('employee', 'leave_type').order_by('-created_at')[:5]
    
    recent_expenses = Expense.objects.filter(
        employee__department=employee.department,
        status='pending'
    ).select_related('employee', 'category').order_by('-created_at')[:5]
    
    # Appraisal progress (if any)
    appraisal_progress = Appraisal.objects.filter(
        employee__department=employee.department,
        period__end_date__gte=date.today()
    ).values('status').annotate(count=Count('id'))
    
    context = {
        'employee': employee,
        'year': year,
        'month': month,
        'team_size': team_size,
        'attendance_stats': attendance_stats,
        'leave_stats': leave_stats,
        'expense_stats': expense_stats,
        'top_attendance': top_attendance,
        'recent_leaves': recent_leaves,
        'recent_expenses': recent_expenses,
        'appraisal_progress': appraisal_progress,
    }
    
    return render(request, 'portal/manager/team_reports.html', context)


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
    from .models import AppraisalCriteria
    
    employee = get_user_employee(request.user)
    appraisal = get_object_or_404(Appraisal, id=appraisal_id, employee=employee)
    
    # Only allow if status is pending or in_progress
    if appraisal.status not in ['pending', 'in_progress']:
        messages.error(request, 'Không thể chỉnh sửa đánh giá đã hoàn thành.')
        return redirect('portal_appraisal_detail', appraisal_id=appraisal_id)
    
    # Get all criteria for this period
    criteria_list = AppraisalCriteria.objects.filter(
        period=appraisal.period
    ).order_by('category', 'order', 'name')
    
    if request.method == 'POST':
        # Update status
        appraisal.status = 'in_progress'
        appraisal.self_assessment = request.POST.get('self_assessment', '')
        appraisal.self_achievements = request.POST.get('self_achievements', '')
        appraisal.self_challenges = request.POST.get('self_challenges', '')
        appraisal.self_goals = request.POST.get('self_goals', '')
        
        # Calculate self overall score
        total_score = 0
        total_weight = 0
        
        for criteria in criteria_list:
            score_key = f'score_{criteria.id}'
            comment_key = f'comment_{criteria.id}'
            
            if score_key in request.POST and request.POST[score_key]:
                score_value = int(request.POST[score_key])
                comment_value = request.POST.get(comment_key, '')
                
                # Get or create AppraisalScore
                appraisal_score, created = AppraisalScore.objects.get_or_create(
                    appraisal=appraisal,
                    criteria=criteria,
                    defaults={
                        'self_score': score_value,
                        'self_comment': comment_value
                    }
                )
                
                if not created:
                    appraisal_score.self_score = score_value
                    appraisal_score.self_comment = comment_value
                    appraisal_score.save()
                
                total_score += score_value * criteria.weight
                total_weight += criteria.weight
        
        # Calculate weighted average
        if total_weight > 0:
            appraisal.self_overall_score = round(total_score / total_weight, 2)
        
        # Check if should mark as completed self-assessment
        if 'submit_final' in request.POST:
            appraisal.self_assessment_date = timezone.now()
            appraisal.status = 'self_assessed'
            messages.success(request, 'Đã hoàn thành tự đánh giá! Quản lý sẽ xem xét đánh giá của bạn.')
        else:
            messages.success(request, 'Đã lưu bản nháp tự đánh giá.')
        
        appraisal.save()
        return redirect('portal_appraisal_detail', appraisal_id=appraisal_id)
    
    # GET request - prepare form data
    # Get existing scores
    existing_scores = {}
    for score in appraisal.scores.select_related('criteria'):
        existing_scores[score.criteria.id] = {
            'score': score.self_score,
            'comment': score.self_comment
        }
    
    # Group criteria by category
    criteria_by_category = {}
    for criteria in criteria_list:
        if criteria.category not in criteria_by_category:
            criteria_by_category[criteria.category] = []
        
        criteria_data = {
            'id': criteria.id,
            'name': criteria.name,
            'description': criteria.description,
            'weight': criteria.weight,
            'max_score': criteria.max_score,
            'existing_score': existing_scores.get(criteria.id, {}).get('score'),
            'existing_comment': existing_scores.get(criteria.id, {}).get('comment', '')
        }
        criteria_by_category[criteria.category].append(criteria_data)
    
    context = {
        'employee': employee,
        'appraisal': appraisal,
        'criteria_by_category': criteria_by_category,
        'can_edit': appraisal.status in ['pending', 'in_progress'],
    }
    
    return render(request, 'portal/appraisal/self_assessment.html', context)
