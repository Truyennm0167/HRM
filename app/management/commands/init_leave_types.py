"""
Management command to initialize default Leave Types
Usage: python manage.py init_leave_types
"""
from django.core.management.base import BaseCommand
from app.models import LeaveType


class Command(BaseCommand):
    help = 'Initialize default leave types for the system'

    def handle(self, *args, **options):
        leave_types = [
            {
                'name': 'Phép năm',
                'code': 'AL',
                'description': 'Nghỉ phép năm theo quy định của pháp luật',
                'max_days_per_year': 12,
                'requires_approval': True,
                'is_paid': True,
                'is_active': True
            },
            {
                'name': 'Nghỉ ốm',
                'code': 'SL',
                'description': 'Nghỉ ốm có xác nhận của bác sĩ',
                'max_days_per_year': 30,
                'requires_approval': True,
                'is_paid': True,
                'is_active': True
            },
            {
                'name': 'Nghỉ không lương',
                'code': 'UL',
                'description': 'Nghỉ việc riêng không hưởng lương',
                'max_days_per_year': 365,
                'requires_approval': True,
                'is_paid': False,
                'is_active': True
            },
            {
                'name': 'Nghỉ thai sản',
                'code': 'ML',
                'description': 'Nghỉ thai sản theo quy định (6 tháng)',
                'max_days_per_year': 180,
                'requires_approval': True,
                'is_paid': True,
                'is_active': True
            },
            {
                'name': 'Nghỉ cưới',
                'code': 'WL',
                'description': 'Nghỉ làm đám cưới',
                'max_days_per_year': 3,
                'requires_approval': True,
                'is_paid': True,
                'is_active': True
            },
            {
                'name': 'Nghỉ tang',
                'code': 'BL',
                'description': 'Nghỉ tang người thân',
                'max_days_per_year': 3,
                'requires_approval': True,
                'is_paid': True,
                'is_active': True
            },
            {
                'name': 'Nghỉ làm việc từ xa',
                'code': 'WFH',
                'description': 'Làm việc từ xa (Work From Home)',
                'max_days_per_year': 52,
                'requires_approval': True,
                'is_paid': True,
                'is_active': True
            },
        ]

        created_count = 0
        updated_count = 0

        for leave_type_data in leave_types:
            leave_type, created = LeaveType.objects.get_or_create(
                code=leave_type_data['code'],
                defaults=leave_type_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {leave_type.name} ({leave_type.code})')
                )
            else:
                # Update existing leave type
                for key, value in leave_type_data.items():
                    if key != 'code':
                        setattr(leave_type, key, value)
                leave_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {leave_type.name} ({leave_type.code})')
                )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {created_count} leave types'))
        self.stdout.write(self.style.SUCCESS(f'↻ Updated: {updated_count} leave types'))
        self.stdout.write('='*60)
