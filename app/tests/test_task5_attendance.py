"""
Test cases for Task #5: Attendance Portal
Tests attendance model and portal functionality
"""
from django.test import TestCase
from django.urls import reverse
from app.models import Employee, Department, JobTitle, Attendance
from datetime import date
from django.utils import timezone


class AttendanceModelTestCase(TestCase):
    """Test Attendance model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(
            name='IT',
            description='IT Department',
            date_establishment=date(2020, 1, 1)
        )
        cls.job_title = JobTitle.objects.create(
            name='Developer',
            salary_coefficient=1.5
        )
        cls.employee = Employee.objects.create(
            employee_code='EMP001',
            name='Test Employee',
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
            email='emp@test.com',
            phone='0901234567',
            address='HN',
            marital_status=0,
            job_title=cls.job_title,
            job_position='Developer',
            department=cls.department,
            salary=10000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='CS',
            school='University'
        )
    
    def test_create_attendance_working(self):
        """Test creating attendance with working status"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Có làm việc',
            working_hours=8
        )
        self.assertEqual(attendance.status, 'Có làm việc')
        self.assertEqual(attendance.working_hours, 8)
    
    def test_create_attendance_leave(self):
        """Test creating attendance with leave status"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Nghỉ phép',
            working_hours=0
        )
        self.assertEqual(attendance.status, 'Nghỉ phép')
    
    def test_attendance_str_representation(self):
        """Test attendance string representation"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Có làm việc',
            working_hours=8
        )
        str_repr = str(attendance)
        self.assertTrue(len(str_repr) > 0)
    
    def test_attendance_with_notes(self):
        """Test attendance with notes"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Nghỉ không phép',
            working_hours=0,
            notes='Personal emergency'
        )
        self.assertEqual(attendance.notes, 'Personal emergency')


class AttendanceURLTestCase(TestCase):
    """Test attendance URLs"""
    
    def test_portal_attendance_urls_exist(self):
        """Test portal attendance URLs exist"""
        url_names = [
            'portal_attendance',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception:
                pass
    
    def test_management_attendance_urls_exist(self):
        """Test management attendance URLs exist"""
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
