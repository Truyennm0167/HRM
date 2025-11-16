"""
Portal Redirect Middleware
Automatically redirects users to appropriate portal after login based on their role
"""
from django.shortcuts import redirect
from django.urls import reverse
from app.permissions import user_can_access_management


class PortalRedirectMiddleware:
    """
    Middleware to handle automatic redirection after login
    
    Logic:
    1. After successful login, redirect to Employee Portal by default
    2. Users with management access can switch to Management Portal
    3. Remember user's last chosen portal in session
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request before view
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Intercept views and handle redirects
        """
        # Only for authenticated users
        if not request.user.is_authenticated:
            return None
        
        # Check if accessing root URL
        if request.path == '/' or request.path == '/home/':
            # Get user's preferred portal from session
            preferred_portal = request.session.get('preferred_portal', 'employee')
            
            # Check if user can access management
            can_access_mgmt = user_can_access_management(request.user)
            
            # Redirect based on preference and permission
            if preferred_portal == 'management' and can_access_mgmt:
                return redirect('management_home')
            else:
                return redirect('portal_dashboard')
        
        return None


class ManagementAccessMiddleware:
    """
    Middleware to restrict access to management URLs
    Redirects to portal if user doesn't have permission
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.management_urls = [
            '/management/',
            '/add_employee',
            '/employee_list',
            '/department/',
            '/job_title',
            '/attendance/add/',
            '/attendance/manage/',
            '/payroll/calculate/',
            '/payroll/manage/',
            '/leave/types/',
            '/leave/manage/',
            '/expense/categories/',
            '/expense/manage/',
            '/contracts/',
            '/recruitment/',
            '/salary-rules/',
            '/appraisal/periods/',
            '/appraisal/hr/',
            '/org-chart/',
        ]
    
    def __call__(self, request):
        # Check if accessing management URL
        if request.user.is_authenticated:
            is_management_url = any(request.path.startswith(url) for url in self.management_urls)
            
            if is_management_url:
                if not user_can_access_management(request.user):
                    from django.contrib import messages
                    messages.error(request, 'Bạn không có quyền truy cập trang quản lý.')
                    return redirect('portal_dashboard')
        
        response = self.get_response(request)
        return response


class PortalSwitchMiddleware:
    """
    Handle portal switching (Employee <-> Management)
    Saves user preference in session
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for portal switch parameter
        if request.user.is_authenticated:
            switch_to = request.GET.get('switch_to')
            
            if switch_to == 'management':
                if user_can_access_management(request.user):
                    request.session['preferred_portal'] = 'management'
                    return redirect('management_home')
            elif switch_to == 'portal':
                request.session['preferred_portal'] = 'employee'
                return redirect('portal_dashboard')
        
        response = self.get_response(request)
        return response
