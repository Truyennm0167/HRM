"""
Test cases for Task #10: System Settings
Tests SystemSettings model, forms, and views
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from app.models import Employee, Department, JobTitle, SystemSettings
from datetime import date, time
from decimal import Decimal


class SystemSettingsModelTestCase(TestCase):
    """Test SystemSettings model"""
    
    def test_system_settings_singleton_pattern(self):
        """Test SystemSettings follows singleton pattern"""
        settings1 = SystemSettings.get_settings()
        settings2 = SystemSettings.get_settings()
        
        self.assertEqual(settings1.id, settings2.id)
    
    def test_system_settings_has_company_fields(self):
        """Test SystemSettings has company info fields"""
        settings = SystemSettings.get_settings()
        
        self.assertTrue(hasattr(settings, 'company_name'))
        self.assertTrue(hasattr(settings, 'company_address'))
        self.assertTrue(hasattr(settings, 'company_phone'))
        self.assertTrue(hasattr(settings, 'company_email'))
    
    def test_system_settings_has_work_fields(self):
        """Test SystemSettings has work time fields"""
        settings = SystemSettings.get_settings()
        
        self.assertTrue(hasattr(settings, 'work_start_time'))
        self.assertTrue(hasattr(settings, 'work_end_time'))
        self.assertTrue(hasattr(settings, 'standard_working_hours'))
        self.assertTrue(hasattr(settings, 'standard_working_days'))
    
    def test_system_settings_has_salary_fields(self):
        """Test SystemSettings has salary/insurance fields"""
        settings = SystemSettings.get_settings()
        
        self.assertTrue(hasattr(settings, 'social_insurance_rate'))
        self.assertTrue(hasattr(settings, 'health_insurance_rate'))
        self.assertTrue(hasattr(settings, 'unemployment_insurance_rate'))
        self.assertTrue(hasattr(settings, 'minimum_wage'))
    
    def test_system_settings_has_email_fields(self):
        """Test SystemSettings has email config fields"""
        settings = SystemSettings.get_settings()
        
        self.assertTrue(hasattr(settings, 'email_host'))
        self.assertTrue(hasattr(settings, 'email_port'))
        self.assertTrue(hasattr(settings, 'email_use_tls'))
    
    def test_system_settings_has_notification_fields(self):
        """Test SystemSettings has notification config fields"""
        settings = SystemSettings.get_settings()
        
        self.assertTrue(hasattr(settings, 'notify_leave_approved'))
        self.assertTrue(hasattr(settings, 'notify_expense_approved'))
        self.assertTrue(hasattr(settings, 'notify_contract_expiring'))
        self.assertTrue(hasattr(settings, 'notify_welcome_email'))


class SystemSettingsDefaultValuesTestCase(TestCase):
    """Test SystemSettings default values"""
    
    def test_default_work_hours(self):
        """Test default work hours"""
        settings = SystemSettings.get_settings()
        
        self.assertEqual(settings.standard_working_hours, Decimal('8'))
        self.assertEqual(settings.standard_working_days, 22)
    
    def test_default_work_times(self):
        """Test default work times"""
        settings = SystemSettings.get_settings()
        
        self.assertIsNotNone(settings.work_start_time)
        self.assertIsNotNone(settings.work_end_time)
    
    def test_default_insurance_rates(self):
        """Test default insurance rates"""
        settings = SystemSettings.get_settings()
        
        self.assertEqual(settings.social_insurance_rate, Decimal('8'))
        self.assertEqual(settings.health_insurance_rate, Decimal('1.5'))
        self.assertEqual(settings.unemployment_insurance_rate, Decimal('1'))
    
    def test_default_pagination_size(self):
        """Test default pagination size"""
        settings = SystemSettings.get_settings()
        
        self.assertEqual(settings.pagination_size, 20)
    
    def test_default_email_settings(self):
        """Test default email settings"""
        settings = SystemSettings.get_settings()
        
        self.assertEqual(settings.email_host, 'smtp.gmail.com')
        self.assertEqual(settings.email_port, 587)
        self.assertTrue(settings.email_use_tls)


class SystemSettingsCalculationsTestCase(TestCase):
    """Test SystemSettings calculations"""
    
    def test_total_employee_insurance_rate(self):
        """Test total employee insurance rate calculation"""
        settings = SystemSettings.get_settings()
        
        expected_total = (
            settings.social_insurance_rate +
            settings.health_insurance_rate +
            settings.unemployment_insurance_rate
        )
        
        self.assertEqual(settings.total_employee_insurance_rate, expected_total)
    
    def test_total_employer_insurance_rate(self):
        """Test total employer insurance rate calculation"""
        settings = SystemSettings.get_settings()
        
        expected_total = (
            settings.employer_social_insurance_rate +
            settings.employer_health_insurance_rate +
            settings.employer_unemployment_insurance_rate
        )
        
        self.assertEqual(settings.total_employer_insurance_rate, expected_total)


class SystemSettingsFormsTestCase(TestCase):
    """Test SystemSettings forms"""
    
    def test_company_settings_form_import(self):
        """Test CompanySettingsForm can be imported"""
        try:
            from app.forms import CompanySettingsForm
            self.assertTrue(True)
        except ImportError:
            self.fail("CompanySettingsForm could not be imported")
    
    def test_work_settings_form_import(self):
        """Test WorkSettingsForm can be imported"""
        try:
            from app.forms import WorkSettingsForm
            self.assertTrue(True)
        except ImportError:
            self.fail("WorkSettingsForm could not be imported")
    
    def test_salary_settings_form_import(self):
        """Test SalarySettingsForm can be imported"""
        try:
            from app.forms import SalarySettingsForm
            self.assertTrue(True)
        except ImportError:
            self.fail("SalarySettingsForm could not be imported")
    
    def test_email_settings_form_import(self):
        """Test EmailSettingsForm can be imported"""
        try:
            from app.forms import EmailSettingsForm
            self.assertTrue(True)
        except ImportError:
            self.fail("EmailSettingsForm could not be imported")
    
    def test_notification_settings_form_import(self):
        """Test NotificationSettingsForm can be imported"""
        try:
            from app.forms import NotificationSettingsForm
            self.assertTrue(True)
        except ImportError:
            self.fail("NotificationSettingsForm could not be imported")
    
    def test_general_settings_form_import(self):
        """Test GeneralSettingsForm can be imported"""
        try:
            from app.forms import GeneralSettingsForm
            self.assertTrue(True)
        except ImportError:
            self.fail("GeneralSettingsForm could not be imported")


class SettingsUpdateTestCase(TestCase):
    """Test Settings update functionality"""
    
    def test_can_update_company_name(self):
        """Test company name can be updated"""
        settings = SystemSettings.get_settings()
        settings.company_name = 'Test Company'
        settings.save()
        
        # Reload
        updated_settings = SystemSettings.get_settings()
        self.assertEqual(updated_settings.company_name, 'Test Company')
    
    def test_can_update_work_times(self):
        """Test work times can be updated"""
        settings = SystemSettings.get_settings()
        settings.work_start_time = time(9, 0)
        settings.work_end_time = time(18, 0)
        settings.save()
        
        updated_settings = SystemSettings.get_settings()
        self.assertEqual(updated_settings.work_start_time, time(9, 0))
        self.assertEqual(updated_settings.work_end_time, time(18, 0))
    
    def test_can_update_notification_settings(self):
        """Test notification settings can be updated"""
        settings = SystemSettings.get_settings()
        settings.notify_welcome_email = False
        settings.save()
        
        updated_settings = SystemSettings.get_settings()
        self.assertEqual(updated_settings.notify_welcome_email, False)
    
    def test_cannot_delete_settings(self):
        """Test settings cannot be deleted"""
        settings = SystemSettings.get_settings()
        settings.delete()
        
        # Should still exist
        settings_count = SystemSettings.objects.count()
        self.assertEqual(settings_count, 1)
    
    def test_singleton_enforced_on_save(self):
        """Test singleton pattern is enforced on save"""
        settings = SystemSettings()
        settings.company_name = 'New Company'
        settings.save()
        
        # Should still be pk=1
        self.assertEqual(settings.pk, 1)
        
        # Only one instance
        self.assertEqual(SystemSettings.objects.count(), 1)


class SystemSettingsStringRepresentationTestCase(TestCase):
    """Test SystemSettings string representation"""
    
    def test_str_returns_correct_value(self):
        """Test __str__ returns correct value"""
        settings = SystemSettings.get_settings()
        self.assertEqual(str(settings), "Cài đặt hệ thống")
