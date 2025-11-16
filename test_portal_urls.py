"""
Script để test tất cả các URL trong Portal System
Chạy: python test_portal_urls.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.contrib.auth.models import User

def test_portal_urls():
    """Test tất cả các portal URLs"""
    
    print("=" * 80)
    print("🧪 TESTING PORTAL SYSTEM URLs")
    print("=" * 80)
    
    # Tạo client
    client = Client()
    
    # Login với user có sẵn (thay đổi username/password nếu cần)
    try:
        user = User.objects.filter(is_staff=True).first()
        if user:
            client.force_login(user)
            print(f"✅ Logged in as: {user.username}\n")
        else:
            print("⚠️  No staff user found, some tests may fail\n")
    except Exception as e:
        print(f"⚠️  Login failed: {e}\n")
    
    # Danh sách các portal URLs cần test
    portal_urls = [
        # Public & Auth
        ('login', 'Login Page'),
        ('portal_dashboard', 'Portal Dashboard'),
        
        # Leave Management
        ('portal_leaves', 'Leaves List'),
        ('portal_leaves_create', 'Create Leave'),
        
        # Payroll
        ('portal_payroll', 'Payroll List'),
        
        # Attendance
        ('portal_attendance', 'Attendance List'),
        
        # Expenses
        ('portal_expenses', 'Expenses List'),
        ('portal_expenses_create', 'Create Expense'),
        
        # Profile
        ('portal_profile', 'Profile View'),
        ('portal_profile_edit', 'Profile Edit'),
        ('portal_change_password', 'Change Password'),
        
        # Manager Approvals
        ('portal_approvals_dashboard', 'Approvals Dashboard'),
        ('portal_team_leaves', 'Team Leaves'),
        ('portal_team_expenses', 'Team Expenses'),
    ]
    
    print("📋 Testing Portal URLs:")
    print("-" * 80)
    
    success_count = 0
    error_count = 0
    redirect_count = 0
    
    for url_name, description in portal_urls:
        try:
            # Reverse URL
            url = reverse(url_name)
            
            # Make request
            response = client.get(url, follow=False)
            
            # Check status
            if response.status_code == 200:
                print(f"✅ {description:30s} | {url:40s} | Status: 200 OK")
                success_count += 1
            elif response.status_code == 302:
                print(f"↪️  {description:30s} | {url:40s} | Status: 302 Redirect")
                redirect_count += 1
            elif response.status_code == 404:
                print(f"❌ {description:30s} | {url:40s} | Status: 404 Not Found")
                error_count += 1
            elif response.status_code == 500:
                print(f"💥 {description:30s} | {url:40s} | Status: 500 Error")
                error_count += 1
            else:
                print(f"⚠️  {description:30s} | {url:40s} | Status: {response.status_code}")
                error_count += 1
                
        except NoReverseMatch as e:
            print(f"❌ {description:30s} | URL not found: {url_name}")
            error_count += 1
        except Exception as e:
            print(f"💥 {description:30s} | Error: {str(e)[:50]}")
            error_count += 1
    
    # Management URLs (backward compatibility)
    print("\n" + "=" * 80)
    print("📋 Testing Management URLs (Backward Compatibility):")
    print("-" * 80)
    
    management_urls = [
        ('admin_home', 'Management Home'),
        ('manage_contracts', 'Manage Contracts'),
        ('employee_list', 'Employee List'),
        ('department_page', 'Departments'),
        ('request_leave', 'Request Leave (Old URL)'),
    ]
    
    for url_name, description in management_urls:
        try:
            url = reverse(url_name)
            response = client.get(url, follow=False)
            
            if response.status_code == 200:
                print(f"✅ {description:30s} | {url:40s} | Status: 200 OK")
                success_count += 1
            elif response.status_code == 302:
                print(f"↪️  {description:30s} | {url:40s} | Status: 302 Redirect")
                redirect_count += 1
            else:
                print(f"⚠️  {description:30s} | {url:40s} | Status: {response.status_code}")
                
        except NoReverseMatch:
            print(f"❌ {description:30s} | URL not found: {url_name}")
            error_count += 1
        except Exception as e:
            print(f"💥 {description:30s} | Error: {str(e)[:50]}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Success (200):     {success_count}")
    print(f"↪️  Redirects (302):   {redirect_count}")
    print(f"❌ Errors:            {error_count}")
    print(f"📝 Total:             {success_count + redirect_count + error_count}")
    
    if error_count == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {error_count} tests failed. Please check the errors above.")
    
    print("=" * 80)

if __name__ == '__main__':
    test_portal_urls()
