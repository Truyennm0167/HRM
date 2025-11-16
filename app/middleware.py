"""
Custom middleware for security enhancements
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Type sniffing prevention
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class UserGroupMiddleware(MiddlewareMixin):
    """
    Ensure authenticated users have appropriate group assignment
    Log users without groups for investigation
    """
    
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # Check if user has any groups
            if not request.user.groups.exists():
                logger.warning(
                    f'User {request.user.username} ({request.user.email}) '
                    f'has no group assignment. IP: {self.get_client_ip(request)}'
                )
                
                # Don't block access, but log for admin review
                # Optionally add a message
                if not request.path.startswith('/admin/'):
                    messages.warning(
                        request,
                        'Tài khoản của bạn chưa được phân quyền. Vui lòng liên hệ HR.'
                    )
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginAttemptMiddleware(MiddlewareMixin):
    """
    Track failed login attempts and log suspicious activity
    """
    
    def process_request(self, request):
        # Only track login POST requests
        if request.path == reverse('login') and request.method == 'POST':
            # Log login attempt
            username = request.POST.get('username', 'unknown')
            ip = self.get_client_ip(request)
            
            logger.info(f'Login attempt for username: {username} from IP: {ip}')
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
