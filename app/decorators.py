"""
Custom decorators for permission checks in HRM System
Provides role-based and permission-based access control
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from app.models import Employee


def group_required(*group_names):
    """
    Decorator to restrict access to users in specific groups
    Usage: @group_required('HR', 'Manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(group in user_groups for group in group_names):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            raise PermissionDenied
        
        return wrapped_view
    return decorator


def hr_required(view_func):
    """
    Decorator to restrict access to HR staff only
    Usage: @hr_required
    """
    return group_required('HR')(view_func)


def manager_or_hr_required(view_func):
    """
    Decorator to restrict access to Managers and HR staff
    Usage: @manager_or_hr_required
    """
    return group_required('HR', 'Manager')(view_func)


def check_employee_access(view_func):
    """
    Decorator to check if user can access employee data
    - HR: Access all employees
    - Manager: Access team members only
    - Employee: Access own data only
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Get employee_id from URL kwargs
        employee_id = kwargs.get('employee_id') or kwargs.get('pk')
        
        if not employee_id:
            # If no specific employee, check if user is HR or Manager
            if request.user.groups.filter(name__in=['HR', 'Manager']).exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Bạn không có quyền truy cập.')
                raise PermissionDenied
        
        # Check access level
        user_groups = request.user.groups.values_list('name', flat=True)
        
        # HR can access all
        if 'HR' in user_groups:
            return view_func(request, *args, **kwargs)
        
        # Get current user's employee record
        try:
            current_employee = Employee.objects.get(email=request.user.email)
        except Employee.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin nhân viên.')
            raise PermissionDenied
        
        # Manager can access team members
        if 'Manager' in user_groups and current_employee.is_manager:
            target_employee = Employee.objects.filter(
                id=employee_id,
                department=current_employee.department
            ).first()
            
            if target_employee:
                return view_func(request, *args, **kwargs)
        
        # Employee can access own data only
        if str(current_employee.id) == str(employee_id):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Bạn không có quyền xem thông tin nhân viên này.')
        raise PermissionDenied
    
    return wrapped_view


def check_salary_access(view_func):
    """
    Decorator to restrict access to salary information
    Only HR and the employee themselves can view salary
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # HR can access all salary info
        if request.user.groups.filter(name='HR').exists():
            return view_func(request, *args, **kwargs)
        
        # Employee can view own salary only
        employee_id = kwargs.get('employee_id') or kwargs.get('pk')
        if employee_id:
            try:
                employee = Employee.objects.get(email=request.user.email)
                if str(employee.id) == str(employee_id):
                    return view_func(request, *args, **kwargs)
            except Employee.DoesNotExist:
                pass
        
        messages.error(request, 'Bạn không có quyền xem thông tin lương.')
        raise PermissionDenied
    
    return wrapped_view


def check_appraisal_access(view_func):
    """
    Decorator for appraisal access control
    - Employee: Own appraisals only
    - Manager: Team appraisals
    - HR: All appraisals
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # HR has full access
        if is_hr_staff(request.user):
            return view_func(request, *args, **kwargs)
        
        # Get appraisal_id if provided
        appraisal_id = kwargs.get('appraisal_id') or kwargs.get('pk')
        
        try:
            current_employee = Employee.objects.get(email=request.user.email)
        except Employee.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin nhân viên.')
            raise PermissionDenied
        
        if appraisal_id:
            from app.models import Appraisal
            try:
                appraisal = Appraisal.objects.get(id=appraisal_id)
                
                # Employee can access own appraisal
                if appraisal.employee.id == current_employee.id:
                    return view_func(request, *args, **kwargs)
                
                # Manager can access team appraisals
                if current_employee.is_manager and appraisal.manager == current_employee:
                    return view_func(request, *args, **kwargs)
                
            except Appraisal.DoesNotExist:
                pass
        else:
            # List views - managers can see team, employees see own
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Bạn không có quyền truy cập đánh giá này.')
        raise PermissionDenied
    
    return wrapped_view


def _get_employee_from_user(user):
    """Helper to get Employee object from User"""
    try:
        return Employee.objects.get(email=user.email)
    except Employee.DoesNotExist:
        return None


def _is_hr_department(employee):
    """
    Kiểm tra nhân viên có thuộc phòng HR không
    """
    if not employee or not employee.department:
        return False
    
    hr_department_names = ['hr', 'nhân sự', 'human resources', 'phòng nhân sự', 'bộ phận nhân sự']
    return employee.department.name.lower().strip() in hr_department_names


def is_hr_staff(user):
    """
    Helper function to check if user is HR staff
    
    HR được xác định bởi:
    1. superuser/admin
    2. Thuộc group 'HR'
    3. Thuộc phòng ban HR
    """
    if not user.is_authenticated:
        return False
        
    if user.is_superuser:
        return True
    
    # Check group HR
    if user.groups.filter(name='HR').exists():
        return True
    
    # Check HR department
    employee = _get_employee_from_user(user)
    if employee and _is_hr_department(employee):
        return True
    
    return False


def is_manager(user):
    """Helper function to check if user is a manager"""
    if user.is_superuser:
        return True
    try:
        employee = Employee.objects.get(email=user.email)
        return employee.is_manager
    except Employee.DoesNotExist:
        return False


def is_manager_or_hr(user):
    """Helper function to check if user is manager or HR"""
    return is_manager(user) or is_hr_staff(user)


def hr_only(view_func):
    """
    Decorator to restrict access to HR staff only
    
    CHỈ cho phép:
    - superuser/admin
    - User thuộc group 'HR'
    - Nhân viên thuộc phòng HR
    
    Manager và Employee sẽ bị redirect về Portal
    
    Usage: @hr_only
    """
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):
        if is_hr_staff(request.user):
            return view_func(request, *args, **kwargs)
        
        messages.warning(
            request, 
            'Tính năng này chỉ dành cho nhân viên Phòng Nhân sự.'
        )
        return redirect('portal_dashboard')
    
    return wrapped_view
