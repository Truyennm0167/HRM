"""
Email Testing Script
Tests email configuration and templates
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime, timedelta

def test_basic_email():
    """Test basic email sending"""
    print("\n" + "="*60)
    print("TEST 1: Basic Email Configuration")
    print("="*60)
    
    print(f"\nEmail Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    if not settings.EMAIL_HOST_USER:
        print("\n⚠ WARNING: EMAIL_HOST_USER not configured!")
        print("Please set environment variables:")
        print("  EMAIL_HOST_USER=your-email@gmail.com")
        print("  EMAIL_HOST_PASSWORD=your-app-password")
        return False
    
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"Password Configured: {'✓ Yes' if settings.EMAIL_HOST_PASSWORD else '✗ No'}")
    
    return True


def test_send_simple_email(recipient_email):
    """Send a simple test email"""
    print("\n" + "="*60)
    print("TEST 2: Simple Email Send")
    print("="*60)
    
    try:
        subject = "Test Email từ HRM System"
        message = """
        Đây là email test từ hệ thống HRM.
        
        Nếu bạn nhận được email này, nghĩa là cấu hình email đã thành công!
        
        Thời gian: {}
        """.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        print(f"\nSending email...")
        print(f"From: {from_email}")
        print(f"To: {recipient_email}")
        print(f"Subject: {subject}")
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False
        )
        
        if result > 0:
            print(f"\n✓ Email sent successfully!")
            return True
        else:
            print(f"\n✗ Email failed to send")
            return False
            
    except Exception as e:
        print(f"\n✗ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_email(recipient_email):
    """Test email with HTML template"""
    print("\n" + "="*60)
    print("TEST 3: Application Received Template")
    print("="*60)
    
    try:
        subject = "Test - Đơn ứng tuyển đã được tiếp nhận"
        
        context = {
            'applicant_name': 'Nguyễn Văn Test',
            'job_title': 'Senior Python Developer',
            'application_code': 'APP20241116TEST01',
            'company_name': 'Công ty HRM Test',
            'application_date': datetime.now(),
            'job': {
                'title': 'Senior Python Developer',
                'department': type('obj', (object,), {'name': 'IT Department'})
            }
        }
        
        # Render HTML template
        html_content = render_to_string('emails/application_received.html', context)
        
        # Create plain text version
        from django.utils.html import strip_tags
        text_content = strip_tags(html_content)
        
        # Create email with both HTML and plain text
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        print(f"\nSending templated email...")
        print(f"Template: emails/application_received.html")
        print(f"To: {recipient_email}")
        
        result = email.send(fail_silently=False)
        
        if result > 0:
            print(f"\n✓ Template email sent successfully!")
            return True
        else:
            print(f"\n✗ Template email failed to send")
            return False
            
    except Exception as e:
        print(f"\n✗ Error sending template email: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_leave_approved_template(recipient_email):
    """Test leave approved template"""
    print("\n" + "="*60)
    print("TEST 4: Leave Approved Template")
    print("="*60)
    
    try:
        subject = "Test - Đơn nghỉ phép đã được phê duyệt"
        
        context = {
            'employee_name': 'Nguyễn Văn Test',
            'leave_type': 'Nghỉ phép năm',
            'start_date': datetime.now() + timedelta(days=7),
            'end_date': datetime.now() + timedelta(days=9),
            'duration': 3,
            'status': 'Đã phê duyệt',
            'approved_by': 'Trần Thị Manager',
            'company_name': 'Công ty HRM Test',
        }
        
        html_content = render_to_string('emails/leave_approved.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        print(f"\nSending leave approved email...")
        print(f"To: {recipient_email}")
        
        result = email.send(fail_silently=False)
        
        if result > 0:
            print(f"\n✓ Leave approved email sent successfully!")
            return True
        else:
            print(f"\n✗ Leave approved email failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contract_expiry_template(recipient_email):
    """Test contract expiry warning template"""
    print("\n" + "="*60)
    print("TEST 5: Contract Expiry Warning Template")
    print("="*60)
    
    try:
        subject = "Test - Thông báo hợp đồng sắp hết hạn"
        
        context = {
            'employee_name': 'Nguyễn Văn Test',
            'contract_type': 'Hợp đồng lao động xác định thời hạn',
            'start_date': datetime.now() - timedelta(days=365),
            'end_date': datetime.now() + timedelta(days=30),
            'days_until_expiry': 30,
            'company_name': 'Công ty HRM Test',
        }
        
        html_content = render_to_string('emails/contract_expiry_warning.html', context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        print(f"\nSending contract expiry warning...")
        print(f"To: {recipient_email}")
        
        result = email.send(fail_silently=False)
        
        if result > 0:
            print(f"\n✓ Contract expiry email sent successfully!")
            return True
        else:
            print(f"\n✗ Contract expiry email failed")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all email tests"""
    print("\n" + "="*70)
    print(" "*20 + "HRM EMAIL TESTING SUITE")
    print("="*70)
    
    # Test configuration
    if not test_basic_email():
        print("\n" + "="*70)
        print("⚠ Email configuration incomplete. Please configure:")
        print("  1. Set EMAIL_HOST_USER environment variable")
        print("  2. Set EMAIL_HOST_PASSWORD environment variable")
        print("  3. Use Gmail App Password (not regular password)")
        print("\nHow to generate Gmail App Password:")
        print("  1. Go to Google Account settings")
        print("  2. Security → 2-Step Verification")
        print("  3. App passwords → Generate")
        print("  4. Use generated 16-character password")
        print("="*70)
        return
    
    # Get recipient email
    if len(sys.argv) > 1:
        recipient_email = sys.argv[1]
    else:
        recipient_email = input("\nEnter test recipient email: ").strip()
    
    if not recipient_email:
        print("✗ No recipient email provided!")
        return
    
    print(f"\n📧 Test recipient: {recipient_email}")
    
    # Run tests
    results = []
    
    results.append(("Simple Email", test_send_simple_email(recipient_email)))
    
    input("\n\nPress Enter to test Application Received template...")
    results.append(("Application Template", test_template_email(recipient_email)))
    
    input("\nPress Enter to test Leave Approved template...")
    results.append(("Leave Approved Template", test_leave_approved_template(recipient_email)))
    
    input("\nPress Enter to test Contract Expiry template...")
    results.append(("Contract Expiry Template", test_contract_expiry_template(recipient_email)))
    
    # Summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<35} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed ({passed*100//total}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All email tests passed! Email system is working correctly.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check configuration.")
    
    print("\n📬 Check your inbox: " + recipient_email)
    print("="*70)


if __name__ == "__main__":
    main()
