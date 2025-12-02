"""
Test cases for Task #2: Performance Appraisal
Tests manager appraisal functionality and company feedback field
"""
from django.test import TestCase
from app.models import (
    Employee, Department, JobTitle, Appraisal, AppraisalPeriod, AppraisalCriteria
)
from datetime import date
from decimal import Decimal


class AppraisalModelTestCase(TestCase):
    """Test Appraisal model including company_feedback field"""
    
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
        cls.manager = Employee.objects.create(
            employee_code='MGR001',
            name='Test Manager',
            gender=0,
            birthday=date(1985, 1, 1),
            place_of_birth='HN',
            place_of_origin='HN',
            place_of_residence='HN',
            identification='987654321',
            date_of_issue=date(2010, 1, 1),
            place_of_issue='HN',
            nationality='VN',
            nation='Kinh',
            religion='None',
            email='mgr@test.com',
            phone='0901234568',
            address='HN',
            marital_status=0,
            job_title=cls.job_title,
            job_position='Manager',
            department=cls.department,
            is_manager=True,
            salary=15000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='CS',
            school='University'
        )
        cls.period = AppraisalPeriod.objects.create(
            name='Q4 2024',
            start_date=date(2024, 10, 1),
            end_date=date(2024, 12, 31),
            self_assessment_deadline=date(2024, 12, 15),
            manager_review_deadline=date(2024, 12, 25),
            status='active'
        )
    
    def test_appraisal_has_company_feedback_field(self):
        """Test that Appraisal model has company_feedback field"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_self',
            company_feedback='Công ty nên cải thiện chế độ phúc lợi'
        )
        self.assertEqual(appraisal.company_feedback, 'Công ty nên cải thiện chế độ phúc lợi')
    
    def test_appraisal_company_feedback_can_be_blank(self):
        """Test that company_feedback can be blank"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_self'
        )
        self.assertEqual(appraisal.company_feedback, '')
    
    def test_appraisal_status_choices(self):
        """Test appraisal status transitions"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_self'
        )
        
        appraisal.status = 'pending_manager'
        appraisal.save()
        self.assertEqual(appraisal.status, 'pending_manager')
    
    def test_appraisal_overall_rating_choices(self):
        """Test overall rating choices"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='completed',
            overall_rating='meets'
        )
        self.assertEqual(appraisal.overall_rating, 'meets')
    
    def test_appraisal_str_representation(self):
        """Test appraisal string representation"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_self'
        )
        expected_str = f"{self.employee.name} - {self.period.name}"
        self.assertEqual(str(appraisal), expected_str)


class AppraisalPeriodTestCase(TestCase):
    """Test AppraisalPeriod model"""
    
    def test_create_appraisal_period(self):
        """Test creating an appraisal period"""
        period = AppraisalPeriod.objects.create(
            name='Q1 2025',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            self_assessment_deadline=date(2025, 3, 15),
            manager_review_deadline=date(2025, 3, 25),
            status='draft'
        )
        self.assertEqual(period.name, 'Q1 2025')
        self.assertEqual(period.status, 'draft')
    
    def test_period_status_choices(self):
        """Test period status choices"""
        period = AppraisalPeriod.objects.create(
            name='Annual 2025',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            self_assessment_deadline=date(2025, 12, 15),
            manager_review_deadline=date(2025, 12, 25),
            status='active'
        )
        self.assertEqual(period.status, 'active')


class AppraisalCriteriaTestCase(TestCase):
    """Test AppraisalCriteria model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.period = AppraisalPeriod.objects.create(
            name='Q1 2025',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            self_assessment_deadline=date(2025, 3, 15),
            manager_review_deadline=date(2025, 3, 25),
            status='draft'
        )
    
    def test_create_appraisal_criteria(self):
        """Test creating appraisal criteria"""
        criteria = AppraisalCriteria.objects.create(
            period=self.period,
            name='Quality of Work',
            description='Quality of work delivered',
            category='performance',
            weight=20,
            max_score=5
        )
        self.assertEqual(criteria.name, 'Quality of Work')
        self.assertEqual(criteria.category, 'performance')
    
    def test_criteria_categories(self):
        """Test different criteria categories"""
        categories = ['performance', 'behavior', 'skill', 'leadership', 'development']
        
        for i, cat in enumerate(categories):
            criteria = AppraisalCriteria.objects.create(
                period=self.period,
                name=f'Test Criteria {i}',
                description=f'Description {i}',
                category=cat,
                weight=20,
                max_score=5
            )
            self.assertEqual(criteria.category, cat)


class AppraisalPermissionsTestCase(TestCase):
    """Test appraisal access permissions"""
    
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
        
        cls.manager = Employee.objects.create(
            employee_code='MGR001',
            name='Manager',
            gender=0,
            birthday=date(1985, 1, 1),
            place_of_birth='HN',
            place_of_origin='HN',
            place_of_residence='HN',
            identification='123456789',
            date_of_issue=date(2010, 1, 1),
            place_of_issue='HN',
            nationality='VN',
            nation='Kinh',
            religion='None',
            email='mgr@test.com',
            phone='0901234567',
            address='HN',
            marital_status=0,
            job_title=cls.job_title,
            job_position='Manager',
            department=cls.department,
            is_manager=True,
            salary=15000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='IT',
            school='Uni'
        )
        
        cls.employee = Employee.objects.create(
            employee_code='EMP001',
            name='Employee',
            gender=0,
            birthday=date(1990, 1, 1),
            place_of_birth='HN',
            place_of_origin='HN',
            place_of_residence='HN',
            identification='987654321',
            date_of_issue=date(2010, 1, 1),
            place_of_issue='HN',
            nationality='VN',
            nation='Kinh',
            religion='None',
            email='emp@test.com',
            phone='0901234568',
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
            major='IT',
            school='Uni'
        )
        
        cls.period = AppraisalPeriod.objects.create(
            name='Q4 2024',
            start_date=date(2024, 10, 1),
            end_date=date(2024, 12, 31),
            self_assessment_deadline=date(2024, 12, 15),
            manager_review_deadline=date(2024, 12, 25),
            status='active'
        )
    
    def test_can_manager_review_when_status_pending_manager(self):
        """Test manager can review when status is pending_manager"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_manager'
        )
        
        result = appraisal.can_manager_review(self.manager)
        self.assertTrue(result)
    
    def test_cannot_manager_review_with_wrong_status(self):
        """Test manager cannot review when status is not pending_manager"""
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_self'
        )
        
        result = appraisal.can_manager_review(self.manager)
        self.assertFalse(result)
    
    def test_cannot_manager_review_if_not_assigned_manager(self):
        """Test other managers cannot review"""
        other_manager = Employee.objects.create(
            employee_code='MGR002',
            name='Other Manager',
            gender=0,
            birthday=date(1985, 1, 1),
            place_of_birth='HN',
            place_of_origin='HN',
            place_of_residence='HN',
            identification='111222333',
            date_of_issue=date(2010, 1, 1),
            place_of_issue='HN',
            nationality='VN',
            nation='Kinh',
            religion='None',
            email='other@test.com',
            phone='0901234569',
            address='HN',
            marital_status=0,
            job_title=self.job_title,
            job_position='Manager',
            department=self.department,
            is_manager=True,
            salary=15000000,
            contract_start_date=date(2020, 1, 1),
            contract_duration=12,
            status=2,
            education_level=3,
            major='IT',
            school='Uni'
        )
        
        appraisal = Appraisal.objects.create(
            period=self.period,
            employee=self.employee,
            manager=self.manager,
            status='pending_manager'
        )
        
        result = appraisal.can_manager_review(other_manager)
        self.assertFalse(result)
