"""
RBAC Permission Decorators for HRMS

Provides role-based access control decorators for views.
Usage:
    @require_hr
    def my_view(request):
        ...
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


def log_permission_denial(user, resource_type, permission_required, reason, request=None, resource_id=None):
    """
    Log permission denial to audit log
    
    Args:
        user: Django User object
        resource_type: String like 'Contract', 'LeaveRequest', etc.
        permission_required: Permission name like 'HR', 'Manager', 'approve_leave'
        reason: Explanation of denial
        request: HttpRequest object (optional, for IP and user agent)
        resource_id: ID of resource being accessed (optional)
    """
    from .models import PermissionAuditLog
    
    try:
        # Get user's groups
        user_groups = list(user.groups.values_list('name', flat=True)) if user.is_authenticated else []
        
        # Get IP address and user agent from request
        ip_address = None
        user_agent = ''
        url_path = ''
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            url_path = request.path[:500]
        
        # Create audit log entry
        PermissionAuditLog.objects.create(
            user=user if user.is_authenticated else None,
            username=user.username if user.is_authenticated else 'anonymous',
            user_groups=user_groups,
            action='denied',
            resource_type=resource_type,
            resource_id=resource_id,
            permission_required=permission_required,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            url_path=url_path,
        )
        
        logger.warning(
            f"Permission denied: {user.username if user.is_authenticated else 'anonymous'} "
            f"tried to access {resource_type} (ID: {resource_id}) - "
            f"Required: {permission_required} - Reason: {reason}"
        )
    except Exception as e:
        logger.error(f"Failed to log permission denial: {e}")


def log_permission_granted(user, resource_type, permission_required, request=None, resource_id=None):
    """
    Log successful permission grant (optional, for full audit trail)
    """
    from .models import PermissionAuditLog
    
    try:
        user_groups = list(user.groups.values_list('name', flat=True)) if user.is_authenticated else []
        
        ip_address = None
        url_path = ''
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            url_path = request.path[:500]
        
        PermissionAuditLog.objects.create(
            user=user if user.is_authenticated else None,
            username=user.username if user.is_authenticated else 'anonymous',
            user_groups=user_groups,
            action='granted',
            resource_type=resource_type,
            resource_id=resource_id,
            permission_required=permission_required,
            reason='Permission check passed',
            ip_address=ip_address,
            url_path=url_path,
        )
    except Exception as e:
        logger.error(f"Failed to log permission grant: {e}")


def user_in_group(user, group_name):
    """Check if user belongs to a specific group"""
    return user.groups.filter(name=group_name).exists()


def user_in_groups(user, group_names):
    """Check if user belongs to any of the specified groups"""
    return user.groups.filter(name__in=group_names).exists()


def require_group(group_name):
    """
    Decorator to require user to be in a specific group.
    
    Usage:
        @require_group('HR')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                # Superusers bypass all checks
                return view_func(request, *args, **kwargs)
            
            if not user_in_group(request.user, group_name):
                # Log permission denial
                log_permission_denial(
                    user=request.user,
                    resource_type='View',
                    permission_required=group_name,
                    reason=f"User not in required group: {group_name}",
                    request=request
                )
                
                messages.error(
                    request, 
                    f'Bạn không có quyền truy cập. Yêu cầu vai trò: {group_name}'
                )
                raise PermissionDenied(f"User must be in '{group_name}' group")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_groups(*group_names):
    """
    Decorator to require user to be in at least one of the specified groups.
    
    Usage:
        @require_groups('HR', 'Manager')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not user_in_groups(request.user, group_names):
                # Log permission denial
                log_permission_denial(
                    user=request.user,
                    resource_type='View',
                    permission_required=f"One of: {', '.join(group_names)}",
                    reason=f"User not in any of required groups: {', '.join(group_names)}",
                    request=request
                )
                
                messages.error(
                    request, 
                    f'Bạn không có quyền truy cập. Yêu cầu vai trò: {", ".join(group_names)}'
                )
                raise PermissionDenied(f"User must be in one of: {group_names}")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# Convenience decorators for common roles
require_hr = require_group('HR')
require_manager = require_group('Manager')
require_employee = require_group('Employee')
require_hr_or_manager = require_groups('HR', 'Manager')


def can_view_employee(user, employee):
    """
    Check if user can view a specific employee's details.
    
    Rules:
    - HR: Can view all employees
    - Manager: Can view employees in their department
    - Employee: Can only view themselves
    - Superuser: Can view all
    
    Args:
        user: Django User object
        employee: Employee object to check access for
    
    Returns:
        Boolean indicating if access is allowed
    """
    if user.is_superuser:
        return True
    
    # HR can view all
    if user_in_group(user, 'HR'):
        return True
    
    # Get user's employee profile
    try:
        user_employee = user.employee
    except:
        return False
    
    # Manager can view department employees
    if user_in_group(user, 'Manager') and user_employee.is_manager:
        if user_employee.department == employee.department:
            return True
    
    # Employee can view themselves
    if user_employee == employee:
        return True
    
    return False


def can_view_employee_salary(user, employee):
    """
    Check if user can view salary information of an employee.
    
    Rules:
    - HR: Can view all salaries
    - Manager: Can view department employees' salaries
    - Employee: Can only view own salary
    - Superuser: Can view all
    """
    if user.is_superuser:
        return True
    
    # HR with explicit permission
    if user_in_group(user, 'HR') and user.has_perm('app.view_employee_salary'):
        return True
    
    try:
        user_employee = user.employee
    except:
        return False
    
    # Manager in same department
    if user_in_group(user, 'Manager') and user_employee.is_manager:
        if user_employee.department == employee.department:
            return True
    
    # Self
    if user_employee == employee:
        return True
    
    return False


def can_manage_contract(user, contract=None):
    """
    Check if user can manage contracts.
    
    Rules:
    - HR: Can manage all contracts
    - Manager: Can view department contracts (read-only)
    - Superuser: Can manage all
    """
    if user.is_superuser:
        return True
    
    # HR has full access
    if user_in_group(user, 'HR'):
        return True
    
    # Manager has read-only access to department contracts
    if contract and user_in_group(user, 'Manager'):
        try:
            user_employee = user.employee
            if user_employee.is_manager:
                return contract.employee.department == user_employee.department
        except:
            pass
    
    return False


def can_approve_leave(user, leave_request):
    """
    Check if user can approve a leave request.
    
    Rules:
    - HR: Can approve all
    - Manager: Can approve department employees' requests
    - Must have 'approve_leave_request' permission
    """
    if user.is_superuser:
        return True
    
    if not user.has_perm('app.approve_leave_request'):
        return False
    
    # HR can approve all
    if user_in_group(user, 'HR'):
        return True
    
    # Manager can approve department requests
    if user_in_group(user, 'Manager'):
        try:
            user_employee = user.employee
            if user_employee.is_manager:
                return leave_request.employee.department == user_employee.department
        except:
            pass
    
    return False


def can_approve_expense(user, expense):
    """
    Check if user can approve an expense claim.
    
    Rules:
    - HR: Can approve all
    - Manager: Can approve department employees' expenses
    - Must have 'approve_expense' permission
    """
    if user.is_superuser:
        return True
    
    if not user.has_perm('app.approve_expense'):
        return False
    
    # HR can approve all
    if user_in_group(user, 'HR'):
        return True
    
    # Manager can approve department expenses
    if user_in_group(user, 'Manager'):
        try:
            user_employee = user.employee
            if user_employee.is_manager:
                return expense.employee.department == user_employee.department
        except:
            pass
    
    return False


def row_level_permission_required(check_func, obj_param_name='pk'):
    """
    Generic decorator for row-level permissions.
    
    Usage:
        @row_level_permission_required(can_view_employee, 'employee_id')
        def view_employee_detail(request, employee_id):
            ...
    
    Args:
        check_func: Function that takes (user, obj) and returns boolean
        obj_param_name: Name of the URL parameter containing object ID
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            from app.models import Employee, Contract, LeaveRequest, Expense
            
            # Get object ID from URL parameters
            obj_id = kwargs.get(obj_param_name)
            if not obj_id:
                raise PermissionDenied("Object ID not found in URL")
            
            # Determine model type from check_func name
            if 'employee' in check_func.__name__:
                obj = Employee.objects.get(pk=obj_id)
            elif 'contract' in check_func.__name__:
                obj = Contract.objects.get(pk=obj_id)
            elif 'leave' in check_func.__name__:
                obj = LeaveRequest.objects.get(pk=obj_id)
            elif 'expense' in check_func.__name__:
                obj = Expense.objects.get(pk=obj_id)
            else:
                raise ValueError(f"Unknown check function: {check_func.__name__}")
            
            # Check permission
            if not check_func(request.user, obj):
                messages.error(request, 'Bạn không có quyền truy cập tài nguyên này.')
                raise PermissionDenied("Insufficient permissions for this resource")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# ======================== HELPER FUNCTIONS FOR NEW PORTAL SYSTEM ========================

def get_user_employee(user):
    """
    Lấy đối tượng Employee từ User
    
    Returns:
        Employee object hoặc None
    """
    if not user.is_authenticated:
        return None
    
    try:
        from app.models import Employee
        return Employee.objects.get(email=user.email)
    except Employee.DoesNotExist:
        return None


def is_hr_department(employee):
    """
    Kiểm tra nhân viên có thuộc phòng HR không
    
    Args:
        employee: Employee object
    
    Returns:
        bool: True nếu thuộc phòng HR
    """
    if not employee or not employee.department:
        return False
    
    hr_department_names = ['hr', 'nhân sự', 'human resources', 'phòng nhân sự', 'bộ phận nhân sự']
    return employee.department.name.lower().strip() in hr_department_names


def is_hr_user(user):
    """
    Kiểm tra user có phải HR không
    
    HR được xác định bởi:
    1. superuser/admin
    2. Thuộc group 'HR'
    3. Thuộc phòng ban HR
    
    Returns:
        bool: True nếu là HR
    """
    if not user.is_authenticated:
        return False
    
    # Superuser luôn có quyền
    if user.is_superuser:
        return True
    
    # Kiểm tra group HR
    if user.groups.filter(name='HR').exists():
        return True
    
    # Kiểm tra phòng ban HR
    employee = get_user_employee(user)
    if employee and is_hr_department(employee):
        return True
    
    return False


def user_can_access_management(user):
    """
    Kiểm tra quyền truy cập Admin Management Portal
    
    CHỈ HR và Admin mới được truy cập Management Portal.
    Manager và Employee chỉ được truy cập Portal.
    
    Returns:
        bool: True nếu user là HR hoặc superuser
    """
    if not user.is_authenticated:
        return False
    
    # Chỉ HR và superuser mới được vào management
    return is_hr_user(user)


def user_is_manager(user):
    """
    Kiểm tra xem user có phải là Manager không
    
    Returns:
        bool: True nếu user là Manager
    """
    if not user.is_authenticated:
        return False
    
    employee = get_user_employee(user)
    return employee and employee.is_manager if employee else False
