"""
Django management command to create test data for Appraisal module
Usage: python manage.py create_appraisal_testdata
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import (
    Employee, Department, JobTitle, 
    AppraisalPeriod, AppraisalCriteria, Appraisal, AppraisalScore
)


class Command(BaseCommand):
    help = 'Create test data for Performance Appraisal module'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating Appraisal test data...'))
        
        # Check if we have employees
        if Employee.objects.count() < 5:
            self.stdout.write(self.style.ERROR('Not enough employees. Please create at least 5 employees first.'))
            return
        
        # Create AppraisalPeriod
        self.stdout.write('Creating Appraisal Period...')
        period, created = AppraisalPeriod.objects.get_or_create(
            name='Đánh giá Q4 2024',
            defaults={
                'description': 'Kỳ đánh giá hiệu suất quý 4 năm 2024',
                'start_date': timezone.now().date() - timedelta(days=90),
                'end_date': timezone.now().date() + timedelta(days=30),
                'self_assessment_deadline': timezone.now().date() + timedelta(days=7),
                'manager_review_deadline': timezone.now().date() + timedelta(days=14),
                'status': 'active',
                'created_by': Employee.objects.filter(is_manager=True).first() or Employee.objects.first()
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created period: {period.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Period already exists: {period.name}'))
        
        # Create Criteria
        self.stdout.write('Creating Appraisal Criteria...')
        criteria_data = [
            {
                'name': 'Hoàn thành công việc đúng hạn',
                'description': 'Khả năng hoàn thành các nhiệm vụ được giao đúng thời hạn cam kết',
                'category': 'performance',
                'weight': 25,
                'max_score': 10
            },
            {
                'name': 'Chất lượng công việc',
                'description': 'Chất lượng và độ chính xác của công việc được thực hiện',
                'category': 'performance',
                'weight': 25,
                'max_score': 10
            },
            {
                'name': 'Kỹ năng chuyên môn',
                'description': 'Trình độ chuyên môn và khả năng áp dụng vào công việc',
                'category': 'competency',
                'weight': 20,
                'max_score': 10
            },
            {
                'name': 'Tinh thần làm việc nhóm',
                'description': 'Khả năng làm việc và phối hợp với đồng nghiệp',
                'category': 'behavior',
                'weight': 15,
                'max_score': 10
            },
            {
                'name': 'Chủ động và sáng tạo',
                'description': 'Khả năng chủ động tìm giải pháp và đưa ra ý tưởng mới',
                'category': 'behavior',
                'weight': 15,
                'max_score': 10
            }
        ]
        
        created_criteria = []
        for criteria_info in criteria_data:
            criteria, created = AppraisalCriteria.objects.get_or_create(
                period=period,
                name=criteria_info['name'],
                defaults={
                    'description': criteria_info['description'],
                    'category': criteria_info['category'],
                    'weight': criteria_info['weight'],
                    'max_score': criteria_info['max_score']
                }
            )
            created_criteria.append(criteria)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created criteria: {criteria.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Criteria already exists: {criteria.name}'))
        
        # Create Appraisals
        self.stdout.write('Creating Appraisals for employees...')
        
        # Get all active employees
        employees = Employee.objects.filter(status__in=[1, 2])[:10]  # Limit to 10 for testing
        
        created_count = 0
        for employee in employees:
            # Find manager
            manager = Employee.objects.filter(
                department=employee.department,
                is_manager=True
            ).exclude(id=employee.id).first()
            
            # Check if appraisal already exists
            appraisal, created = Appraisal.objects.get_or_create(
                period=period,
                employee=employee,
                defaults={
                    'manager': manager,
                    'status': 'pending_self'
                }
            )
            
            if created:
                # Create AppraisalScore for each criteria
                for criteria in created_criteria:
                    AppraisalScore.objects.create(
                        appraisal=appraisal,
                        criteria=criteria
                    )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created appraisal for: {employee.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  Appraisal already exists for: {employee.name}'))
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('TEST DATA CREATION SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Period: {period.name}')
        self.stdout.write(f'Criteria: {len(created_criteria)} items (Total weight: {sum(c.weight for c in created_criteria)}%)')
        self.stdout.write(f'Appraisals: {created_count} new appraisals created')
        self.stdout.write(f'Total appraisals in period: {period.appraisals.count()}')
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✓ Test data creation completed!'))
        self.stdout.write('='*60)
        
        # Instructions
        self.stdout.write('\n' + self.style.WARNING('NEXT STEPS:'))
        self.stdout.write('1. Visit /appraisal/periods/ to view the period')
        self.stdout.write('2. Visit /appraisal/my-appraisals/ as employee to self-assess')
        self.stdout.write('3. Visit /appraisal/manager/ as manager to review')
        self.stdout.write('4. Visit /appraisal/hr/ as HR to finalize')
        self.stdout.write('')
