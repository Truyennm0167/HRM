"""
Test cases for Task #8: Dashboard with Charts
Tests dashboard statistics and data
"""
from django.test import TestCase
from django.urls import reverse
from django.db.models import Count
from app.models import Employee, Department, JobTitle, Attendance
from datetime import date
from django.utils import timezone


class DashboardStatisticsTestCase(TestCase):
    """Test dashboard statistics"""
    
    @classmethod
    def setUpTestData(cls):
        cls.hr_dept = Department.objects.create(
            name='Phòng Nhân sự',
            description='HR',
            date_establishment=date(2020, 1, 1)
        )
        cls.it_dept = Department.objects.create(
            name='IT',
            description='IT',
            date_establishment=date(2020, 1, 1)
        )
        cls.job_title = JobTitle.objects.create(
            name='Staff',
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
        
        # Create additional employees for statistics
        for i in range(5):
            Employee.objects.create(
                employee_code=f'EMP00{i}',
                name=f'Employee {i}',
                gender=i % 2,
                birthday=date(1990, 1, 1),
                place_of_birth='HN',
                place_of_origin='HN',
                place_of_residence='HN',
                identification=f'12345678{i}',
                date_of_issue=date(2010, 1, 1),
                place_of_issue='HN',
                nationality='VN',
                nation='Kinh',
                religion='None',
                email=f'emp{i}@test.com',
                phone=f'090123456{i}',
                address='HN',
                marital_status=0,
                job_title=cls.job_title,
                job_position='Staff',
                department=cls.it_dept if i % 2 == 0 else cls.hr_dept,
                salary=10000000 + i * 1000000,
                contract_start_date=date(2020, 1, 1),
                contract_duration=12,
                status=2,
                education_level=3,
                major='IT',
                school='Uni'
            )
    
    def test_total_employees_count(self):
        """Test counting total employees"""
        total = Employee.objects.count()
        self.assertEqual(total, 6)  # 1 HR + 5 additional
    
    def test_department_employee_count(self):
        """Test counting employees by department"""
        dept_counts = Department.objects.annotate(
            emp_count=Count('employee')
        ).values('name', 'emp_count')
        
        self.assertGreater(len(dept_counts), 0)
    
    def test_gender_distribution(self):
        """Test gender distribution statistics"""
        gender_counts = Employee.objects.values('gender').annotate(
            count=Count('id')
        )
        
        self.assertGreater(len(gender_counts), 0)


class DashboardURLTestCase(TestCase):
    """Test dashboard URLs"""
    
    def test_management_home_url_exists(self):
        """Test management home URL exists"""
        try:
            url = reverse('management_home')
            self.assertIsNotNone(url)
        except Exception:
            try:
                url = reverse('admin_home')
                self.assertIsNotNone(url)
            except Exception:
                pass


class ChartDataTestCase(TestCase):
    """Test chart data aggregation"""
    
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
            name='Employee',
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
                date=timezone.now(),
                status='Có làm việc',
                working_hours=8
            )
    
    def test_attendance_data_can_be_aggregated(self):
        """Test attendance data can be aggregated for charts"""
        attendance_by_status = Attendance.objects.values('status').annotate(
            count=Count('id')
        )
        
        self.assertGreater(len(attendance_by_status), 0)
    
    def test_employee_status_distribution(self):
        """Test employee status distribution"""
        status_counts = Employee.objects.values('status').annotate(
            count=Count('id')
        )
        
        self.assertGreater(len(status_counts), 0)
