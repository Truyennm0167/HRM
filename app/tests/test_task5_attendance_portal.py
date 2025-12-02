"""
Test cases for Task #5: Attendance Portal
Tests attendance model and basic functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from app.models import Employee, Department, JobTitle, Attendance
from datetime import date, time, datetime, timedelta


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
        self.assertEqual(attendance.working_hours, 0)
    
    def test_create_attendance_unpaid_leave(self):
        """Test creating attendance with unpaid leave"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Nghỉ không phép',
            working_hours=0
        )
        self.assertEqual(attendance.status, 'Nghỉ không phép')
    
    def test_attendance_str_representation(self):
        """Test attendance string representation"""
        now = timezone.now()
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=now,
            status='Có làm việc',
            working_hours=8
        )
        expected_str = f"{now.date()} - {self.employee.name}"
        self.assertEqual(str(attendance), expected_str)
    
    def test_attendance_with_notes(self):
        """Test attendance with notes"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Có làm việc',
            working_hours=8,
            notes='Làm thêm giờ'
        )
        self.assertEqual(attendance.notes, 'Làm thêm giờ')
    
    def test_attendance_default_working_hours(self):
        """Test attendance default working hours is 0"""
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=timezone.now(),
            status='Nghỉ phép'
        )
        self.assertEqual(attendance.working_hours, 0)


class AttendanceQueryTestCase(TestCase):
    """Test attendance queries"""
    
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(
            name='IT',
            description='IT',
            date_establishment=date(2020, 1, 1)
        )
        cls.job_title = JobTitle.objects.create(
            name='Staff',
            salary_coefficient=1.0
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
            job_position='Staff',
            department=cls.department,
            salary=10000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='IT',
            school='Uni'
        )
        
        # Create attendance records
        for i in range(5):
            Attendance.objects.create(
                employee=cls.employee,
                date=timezone.now() - timedelta(days=i),
                status='Có làm việc',
                working_hours=8
            )
    
    def test_filter_attendance_by_employee(self):
        """Test filtering attendance by employee"""
        attendances = Attendance.objects.filter(employee=self.employee)
        self.assertEqual(attendances.count(), 5)
    
    def test_filter_attendance_by_status(self):
        """Test filtering attendance by status"""
        attendances = Attendance.objects.filter(status='Có làm việc')
        self.assertEqual(attendances.count(), 5)
    
    def test_calculate_total_working_hours(self):
        """Test calculating total working hours"""
        from django.db.models import Sum
        
        total_hours = Attendance.objects.filter(
            employee=self.employee
        ).aggregate(total=Sum('working_hours'))['total']
        
        self.assertEqual(total_hours, 40)  # 5 days * 8 hours


class AttendanceStatusChoicesTestCase(TestCase):
    """Test attendance status choices"""
    
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(
            name='IT',
            description='IT',
            date_establishment=date(2020, 1, 1)
        )
        cls.job_title = JobTitle.objects.create(
            name='Staff',
            salary_coefficient=1.0
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
            job_position='Staff',
            department=cls.department,
            salary=10000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='IT',
            school='Uni'
        )
    
    def test_all_status_choices_valid(self):
        """Test all status choices can be used"""
        statuses = ['Có làm việc', 'Nghỉ phép', 'Nghỉ không phép']
        
        for i, status in enumerate(statuses):
            attendance = Attendance.objects.create(
                employee=self.employee,
                date=timezone.now() + timedelta(days=i + 10),
                status=status,
                working_hours=8 if status == 'Có làm việc' else 0
            )
            self.assertEqual(attendance.status, status)


class AttendanceReportTestCase(TestCase):
    """Test attendance reporting functionality"""
    
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(
            name='IT',
            description='IT',
            date_establishment=date(2020, 1, 1)
        )
        cls.job_title = JobTitle.objects.create(
            name='Staff',
            salary_coefficient=1.0
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
            job_position='Staff',
            department=cls.department,
            salary=10000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='IT',
            school='Uni'
        )
        
        # Create mixed attendance records
        Attendance.objects.create(
            employee=cls.employee,
            date=timezone.now() - timedelta(days=1),
            status='Có làm việc',
            working_hours=8
        )
        Attendance.objects.create(
            employee=cls.employee,
            date=timezone.now() - timedelta(days=2),
            status='Có làm việc',
            working_hours=8
        )
        Attendance.objects.create(
            employee=cls.employee,
            date=timezone.now() - timedelta(days=3),
            status='Nghỉ phép',
            working_hours=0
        )
    
    def test_count_working_days(self):
        """Test counting working days"""
        working_days = Attendance.objects.filter(
            employee=self.employee,
            status='Có làm việc'
        ).count()
        
        self.assertEqual(working_days, 2)
    
    def test_count_leave_days(self):
        """Test counting leave days"""
        leave_days = Attendance.objects.filter(
            employee=self.employee,
            status='Nghỉ phép'
        ).count()
        
        self.assertEqual(leave_days, 1)
    
    def test_attendance_summary(self):
        """Test attendance summary aggregation"""
        from django.db.models import Count
        
        summary = Attendance.objects.filter(
            employee=self.employee
        ).values('status').annotate(count=Count('id'))
        
        summary_dict = {item['status']: item['count'] for item in summary}
        
        self.assertEqual(summary_dict.get('Có làm việc', 0), 2)
        self.assertEqual(summary_dict.get('Nghỉ phép', 0), 1)
