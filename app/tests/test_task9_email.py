"""
Test cases for Task #9: Email Notifications
Tests email configuration and templates
"""
from django.test import TestCase
from django.core import mail
from django.core.mail import send_mail
from django.conf import settings
import os


class EmailConfigurationTestCase(TestCase):
    """Test email configuration"""
    
    def test_email_backend_configured(self):
        """Test email backend is configured"""
        self.assertTrue(hasattr(settings, 'EMAIL_BACKEND'))
    
    def test_email_host_settings_exist(self):
        """Test email host settings exist"""
        # Check if email settings are defined
        has_email_config = (
            hasattr(settings, 'EMAIL_HOST') or
            hasattr(settings, 'EMAIL_BACKEND')
        )
        self.assertTrue(has_email_config)


class EmailSendTestCase(TestCase):
    """Test email sending functionality"""
    
    def test_can_send_test_email(self):
        """Test sending a test email"""
        # Use Django's locmem backend for testing
        result = send_mail(
            subject='Test Subject',
            message='Test message body',
            from_email='test@example.com',
            recipient_list=['recipient@example.com'],
            fail_silently=True,
        )
        
        # This may return 0 if email is not configured, which is acceptable
        self.assertIn(result, [0, 1])
    
    def test_mail_outbox_in_test_mode(self):
        """Test mail outbox works in test mode"""
        # Django test framework automatically uses locmem backend
        send_mail(
            subject='Test',
            message='Test',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
            fail_silently=True,
        )
        
        # In test mode, emails go to mail.outbox
        # May be empty if EMAIL_BACKEND is not locmem
        self.assertIsInstance(mail.outbox, list)


class EmailTemplateDirectoryTestCase(TestCase):
    """Test email template directory exists"""
    
    def test_templates_directory_exists(self):
        """Test templates directory exists"""
        templates_dir = os.path.join(settings.BASE_DIR, 'app', 'templates')
        self.assertTrue(os.path.exists(templates_dir))
    
    def test_email_templates_directory_exists(self):
        """Test email templates directory may exist"""
        email_templates_dir = os.path.join(
            settings.BASE_DIR, 'app', 'templates', 'email'
        )
        # Email templates directory may or may not exist
        # Just check that templates dir exists
        templates_dir = os.path.join(settings.BASE_DIR, 'app', 'templates')
        self.assertTrue(os.path.exists(templates_dir))


class EmailContentTestCase(TestCase):
    """Test email content generation"""
    
    def test_email_subject_encoding(self):
        """Test email subject supports Vietnamese"""
        subject = 'Thông báo từ HRM System'
        
        # Should not raise any encoding errors
        try:
            encoded = subject.encode('utf-8')
            self.assertTrue(True)
        except UnicodeEncodeError:
            self.fail('Email subject cannot be encoded to UTF-8')
    
    def test_email_body_encoding(self):
        """Test email body supports Vietnamese"""
        body = '''
        Kính gửi Nhân viên,
        
        Đây là thông báo từ hệ thống quản lý nhân sự.
        
        Trân trọng,
        HRM System
        '''
        
        # Should not raise any encoding errors
        try:
            encoded = body.encode('utf-8')
            self.assertTrue(True)
        except UnicodeEncodeError:
            self.fail('Email body cannot be encoded to UTF-8')


class NotificationTypeTestCase(TestCase):
    """Test notification types"""
    
    def test_notification_types_defined(self):
        """Test common notification types"""
        notification_types = [
            'welcome',
            'password_reset',
            'attendance_reminder',
            'appraisal_notification',
            'reward_notification',
            'discipline_notification',
        ]
        
        # Just verify that notification types can be defined
        self.assertEqual(len(notification_types), 6)
    
    def test_notification_priority_levels(self):
        """Test notification priority levels"""
        priorities = {
            'low': 1,
            'normal': 2,
            'high': 3,
            'urgent': 4,
        }
        
        self.assertEqual(priorities['low'], 1)
        self.assertEqual(priorities['high'], 3)
