"""
Portal Redirect Middleware
Automatically redirects users to appropriate portal after login based on their role

Permission Logic:
- HR (phòng HR hoặc group HR): Full access /management
- Manager: Chỉ /portal, KHÔNG được vào /management
- Employee: Chỉ /portal
"""
from django.shortcuts import redirect
from django.urls import reverse
from app.permissions import user_can_access_management, is_hr_user


class PortalRedirectMiddleware:
    """
    Middleware to handle automatic redirection after login
    
    Logic:
    1. After successful login, redirect based on role:
       - HR/Admin → Management Portal
       - Manager/Employee → Employee Portal
    2. Remember user's last chosen portal in session
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
            # Check if user can access management
            can_access_mgmt = user_can_access_management(request.user)
            
            if can_access_mgmt:
                # HR/Admin - go to management by default
                preferred_portal = request.session.get('preferred_portal', 'management')
                if preferred_portal == 'management':
                    return redirect('management_home')
                else:
                    return redirect('portal_dashboard')
            else:
                # Manager/Employee - always go to portal
                return redirect('portal_dashboard')
        
        return None


class ManagementAccessMiddleware:
    """
    Middleware to restrict access to management URLs
    
    CHỈ HR và Admin mới được truy cập Management Portal.
    Manager và Employee sẽ bị redirect về Portal.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Các URL patterns của management portal
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
            '/rewards/',
            '/disciplines/',
            '/settings/',
            '/ai/',
        ]
    
    def __call__(self, request):
        # Chỉ kiểm tra với authenticated users
        if request.user.is_authenticated:
            # Kiểm tra có phải URL management không
            is_management_url = any(request.path.startswith(url) for url in self.management_urls)
            
            if is_management_url:
                # Kiểm tra quyền - CHỈ HR và Admin
                if not user_can_access_management(request.user):
                    from django.contrib import messages
                    messages.warning(
                        request, 
                        'Khu vực này chỉ dành cho nhân viên Phòng Nhân sự. '
                        'Bạn đã được chuyển về Portal Nhân viên.'
                    )
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
