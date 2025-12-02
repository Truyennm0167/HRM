"""
Test cases for Task #4: Reward & Discipline Module
Tests CRUD operations for rewards/disciplines
"""
from django.test import TestCase
from app.models import Employee, Department, JobTitle, Reward, Discipline
from datetime import date
from django.utils import timezone


class RewardModelTestCase(TestCase):
    """Test Reward model"""
    
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
    
    def test_create_reward(self):
        """Test creating a reward"""
        reward = Reward.objects.create(
            employee=self.employee,
            number=1,
            description='Hoàn thành xuất sắc công việc',
            date=timezone.now(),
            amount=5000000,
            cash_payment=True
        )
        self.assertEqual(reward.employee, self.employee)
        self.assertEqual(reward.amount, 5000000)
    
    def test_reward_str_representation(self):
        """Test reward string representation"""
        reward = Reward.objects.create(
            employee=self.employee,
            number=2,
            description='Performance bonus',
            date=timezone.now(),
            amount=3000000,
            cash_payment=True
        )
        str_repr = str(reward)
        self.assertTrue(len(str_repr) > 0)
        self.assertIn('Reward', str_repr)
    
    def test_reward_can_be_non_cash(self):
        """Test reward can be non-cash (certificate only)"""
        reward = Reward.objects.create(
            employee=self.employee,
            number=3,
            description='Đóng góp ý tưởng',
            date=timezone.now(),
            amount=0,
            cash_payment=False
        )
        self.assertFalse(reward.cash_payment)


class DisciplineModelTestCase(TestCase):
    """Test Discipline model"""
    
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
            major='CS',
            school='Uni'
        )
    
    def test_create_discipline(self):
        """Test creating a discipline record"""
        discipline = Discipline.objects.create(
            employee=self.employee,
            number=1,
            description='Vi phạm quy định',
            date=timezone.now(),
            amount=0
        )
        self.assertEqual(discipline.employee, self.employee)
    
    def test_discipline_with_penalty(self):
        """Test discipline with financial penalty"""
        discipline = Discipline.objects.create(
            employee=self.employee,
            number=2,
            description='Vi phạm nghiêm trọng',
            date=timezone.now(),
            amount=1000000
        )
        self.assertEqual(discipline.amount, 1000000)
    
    def test_discipline_str_representation(self):
        """Test discipline string representation"""
        discipline = Discipline.objects.create(
            employee=self.employee,
            number=3,
            description='Late arrival',
            date=timezone.now(),
            amount=0
        )
        str_repr = str(discipline)
        self.assertTrue(len(str_repr) > 0)
        self.assertIn('Discipline', str_repr)
