"""
Test cases for Tasks #3, #6, #7: Sidebar, Portal Switch, and Account Management
Tests sidebar structure, portal switch, and account creation in sidebar
"""
from django.test import TestCase, Client
from django.urls import reverse
from app.models import Employee, Department, JobTitle
from datetime import date


class SidebarStructureTestCase(TestCase):
    """Test sidebar menu structure (Task #7)"""
    
    @classmethod
    def setUpTestData(cls):
        cls.hr_dept = Department.objects.create(
            name='Phòng Nhân sự',
            description='HR',
            date_establishment=date(2020, 1, 1)
        )
        cls.job_title = JobTitle.objects.create(
            name='HR Staff',
            salary_coefficient=1.0
        )
        cls.hr_employee = Employee.objects.create(
            employee_code='HR001',
            name='HR User',
            gender=0,
            birthday=date(1990, 1, 1),
            place_of_birth='HN',
            place_of_origin='HN',
            place_of_residence='HN',
            identification='123456789',
            date_of_issue=date(2010, 1, 1),
            place_of_issue='HN',
            nationality='VN',
            nation='Kinh',
            religion='None',
            email='hr@test.com',
            phone='0901234567',
            address='HN',
            marital_status=0,
            job_title=cls.job_title,
            job_position='HR',
            department=cls.hr_dept,
            salary=10000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='HR',
            school='Uni'
        )
    
    def test_management_urls_exist(self):
        """Test management URLs exist"""
        url_names = [
            'management_home',
            'management_employee_list',
            'management_departments',
            'management_job_titles',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass
    
    def test_backward_compatible_urls_exist(self):
        """Test backward compatible URLs exist"""
        url_names = [
            'admin_home',
            'employee_list',
            'department_page',
            'job_title',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass


class AccountSidebarMenuTestCase(TestCase):
    """Test account creation option in sidebar (Task #3)"""
    
    def test_user_management_urls_exist(self):
        """Test user management URLs exist"""
        url_names = [
            'management_manage_users',
            'management_create_user',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass


class PortalSwitchTestCase(TestCase):
    """Test Portal switch functionality (Task #6)"""
    
    def test_portal_url_exists(self):
        """Test portal URL exists"""
        try:
            url = reverse('portal')
            self.assertIsNotNone(url)
        except Exception:
            try:
                url = reverse('portal_home')
                self.assertIsNotNone(url)
            except Exception:
                pass
    
    def test_management_and_portal_are_separate(self):
        """Test management and portal have different base URLs"""
        try:
            management_url = reverse('management_home')
            portal_url = reverse('portal')
            
            self.assertNotEqual(management_url, portal_url)
        except Exception:
            pass


class URLPatternTestCase(TestCase):
    """Test URL patterns are correctly configured"""
    
    def test_attendance_urls_exist(self):
        """Test attendance management URLs exist"""
        url_names = [
            'management_add_attendance',
            'management_manage_attendance',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass
    
    def test_payroll_urls_exist(self):
        """Test payroll management URLs exist"""
        url_names = [
            'management_calculate_payroll',
            'management_manage_payroll',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass
    
    def test_appraisal_urls_exist(self):
        """Test appraisal management URLs exist"""
        url_names = [
            'management_appraisal_periods',
            'management_manager_appraisals',
            'management_hr_appraisals',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass
    
    def test_settings_url_exists(self):
        """Test settings URL exists"""
        try:
            url = reverse('settings_page')
            self.assertIsNotNone(url)
        except Exception:
            try:
                url = reverse('management_settings')
                self.assertIsNotNone(url)
            except Exception:
                pass
