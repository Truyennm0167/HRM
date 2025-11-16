"""
Template tags for permission checking in templates.
Usage:
    {% load permission_tags %}
    
    {% if user|has_group:'HR' %}
        <button>Create Contract</button>
    {% endif %}
    
    {% if user|has_permission:'app.add_contract' %}
        <a href="#">Add</a>
    {% endif %}
"""
from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Check if user belongs to a specific group.
    
    Args:
        user: Django User object
        group_name: Name of the group (e.g., 'HR', 'Manager', 'Employee')
    
    Returns:
        bool: True if user is in the group or is superuser, False otherwise
    
    Usage:
        {% if user|has_group:'HR' %}
            <!-- Content for HR users -->
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    try:
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False


# Alias for backward compatibility
@register.filter(name='user_in_group')
def user_in_group(user, group_name):
    """Alias for has_group for backward compatibility"""
    return has_group(user, group_name)


@register.filter(name='has_permission')
def has_permission(user, permission_codename):
    """
    Check if user has a specific permission.
    
    Args:
        user: Django User object
        permission_codename: Permission codename in format 'app.codename' 
                           (e.g., 'app.add_contract', 'app.approve_leave_request')
    
    Returns:
        bool: True if user has the permission or is superuser, False otherwise
    
    Usage:
        {% if user|has_permission:'app.add_contract' %}
            <button>Create Contract</button>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    try:
        return user.has_perm(permission_codename)
    except Exception:
        return False


@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    """
    Check if user belongs to any of the specified groups.
    
    Args:
        user: Django User object
        group_names: Comma-separated group names (e.g., 'HR,Manager')
    
    Returns:
        bool: True if user is in any of the groups or is superuser, False otherwise
    
    Usage:
        {% if user|has_any_group:'HR,Manager' %}
            <!-- Content for HR or Manager users -->
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    try:
        group_list = [g.strip() for g in group_names.split(',')]
        return user.groups.filter(name__in=group_list).exists()
    except Exception:
        return False


# Alias for backward compatibility
@register.filter(name='user_in_groups')
def user_in_groups(user, group_names):
    """Alias for has_any_group for backward compatibility"""
    return has_any_group(user, group_names)


@register.filter(name='has_all_groups')
def has_all_groups(user, group_names):
    """
    Check if user belongs to all of the specified groups.
    
    Args:
        user: Django User object
        group_names: Comma-separated group names (e.g., 'HR,Manager')
    
    Returns:
        bool: True if user is in all of the groups or is superuser, False otherwise
    
    Usage:
        {% if user|has_all_groups:'HR,Manager' %}
            <!-- Content for users who are both HR and Manager -->
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    try:
        group_list = [g.strip() for g in group_names.split(',')]
        user_groups = user.groups.values_list('name', flat=True)
        return all(group in user_groups for group in group_list)
    except Exception:
        return False


@register.filter(name='user_groups')
def user_groups(user):
    """
    Get list of group names for a user.
    
    Args:
        user: Django User object
    
    Returns:
        list: List of group names the user belongs to
    
    Usage:
        {% with groups=user|user_groups %}
            <p>Groups: {{ groups|join:', ' }}</p>
        {% endwith %}
    """
    if not user or not user.is_authenticated:
        return []
    
    try:
        return list(user.groups.values_list('name', flat=True))
    except Exception:
        return []


@register.simple_tag(takes_context=True)
def can_manage_contract(context, contract):
    """
    Check if current user can manage a specific contract.
    Uses row-level permission logic from permissions.py
    
    Args:
        context: Template context
        contract: Contract object
    
    Returns:
        bool: True if user can manage the contract
    
    Usage:
        {% can_manage_contract contract as can_manage %}
        {% if can_manage %}
            <button>Edit</button>
        {% endif %}
    """
    from app.permissions import can_manage_contract as check_permission
    
    user = context.get('user')
    if not user or not user.is_authenticated:
        return False
    
    try:
        return check_permission(user, contract)
    except Exception:
        return False


@register.simple_tag(takes_context=True)
def can_view_employee_salary(context, employee):
    """
    Check if current user can view an employee's salary.
    
    Args:
        context: Template context
        employee: Employee object
    
    Returns:
        bool: True if user can view the salary
    
    Usage:
        {% can_view_employee_salary employee as can_view_salary %}
        {% if can_view_salary %}
            <p>Salary: {{ employee.base_salary }}</p>
        {% endif %}
    """
    from app.permissions import can_view_employee_salary as check_permission
    
    user = context.get('user')
    if not user or not user.is_authenticated:
        return False
    
    try:
        return check_permission(user, employee)
    except Exception:
        return False


@register.simple_tag(takes_context=True)
def can_approve_leave(context, leave_request):
    """
    Check if current user can approve a leave request.
    
    Args:
        context: Template context
        leave_request: LeaveRequest object
    
    Returns:
        bool: True if user can approve the leave
    
    Usage:
        {% can_approve_leave leave_request as can_approve %}
        {% if can_approve %}
            <button>Approve</button>
        {% endif %}
    """
    from app.permissions import can_approve_leave as check_permission
    
    user = context.get('user')
    if not user or not user.is_authenticated:
        return False
    
    try:
        return check_permission(user, leave_request)
    except Exception:
        return False


@register.simple_tag(takes_context=True)
def can_approve_expense(context, expense):
    """
    Check if current user can approve an expense.
    
    Args:
        context: Template context
        expense: Expense object
    
    Returns:
        bool: True if user can approve the expense
    
    Usage:
        {% can_approve_expense expense as can_approve %}
        {% if can_approve %}
            <button>Approve</button>
        {% endif %}
    """
    from app.permissions import can_approve_expense as check_permission
    
    user = context.get('user')
    if not user or not user.is_authenticated:
        return False
    
    try:
        return check_permission(user, expense)
    except Exception:
        return False
