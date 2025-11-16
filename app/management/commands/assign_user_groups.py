"""
Management command to assign users to appropriate groups
Usage: python manage.py assign_user_groups
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from app.models import Employee


class Command(BaseCommand):
    help = 'Assign users to appropriate groups based on Employee records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE - No changes will be made ===\n'))
        else:
            self.stdout.write(self.style.SUCCESS('\n=== Assigning Users to Groups ===\n'))

        # Get groups
        try:
            hr_group = Group.objects.get(name='HR')
            manager_group = Group.objects.get(name='Manager')
            employee_group = Group.objects.get(name='Employee')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'ERROR: Groups not found! Please run: python manage.py setup_groups_permissions'
            ))
            return

        # Get all employees
        employees = Employee.objects.select_related('department', 'job_title').all()
        
        assigned_count = 0
        manager_count = 0
        hr_count = 0
        employee_count = 0
        skipped_count = 0

        for emp in employees:
            try:
                # Try to find corresponding User by email
                user = User.objects.get(email=emp.email)
                
                # Determine role based on Employee attributes
                is_hr = False
                is_manager = emp.is_manager
                
                # Check if HR department or HR job title
                if emp.department and 'hr' in emp.department.name.lower():
                    is_hr = True
                if emp.job_title and 'hr' in emp.job_title.name.lower():
                    is_hr = True
                if emp.job_position and 'hr' in emp.job_position.lower():
                    is_hr = True
                
                # Assign groups
                groups_to_assign = []
                
                if is_hr:
                    groups_to_assign.append(hr_group)
                    hr_count += 1
                elif is_manager:
                    groups_to_assign.append(manager_group)
                    manager_count += 1
                else:
                    groups_to_assign.append(employee_group)
                    employee_count += 1
                
                if not dry_run:
                    user.groups.set(groups_to_assign)
                
                group_names = ', '.join([g.name for g in groups_to_assign])
                self.stdout.write(
                    f'  ✓ {emp.name} ({emp.email}) → {group_names}'
                )
                assigned_count += 1
                
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ No user found for {emp.name} ({emp.email})')
                )
                skipped_count += 1
                continue

        # Summary
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN SUMMARY (No changes made) ===\n'))
        else:
            self.stdout.write(self.style.SUCCESS('\n=== ASSIGNMENT COMPLETE ===\n'))
        
        self.stdout.write(f'''
Users Assigned: {assigned_count}
  - HR: {hr_count}
  - Manager: {manager_count}
  - Employee: {employee_count}
Skipped (no user): {skipped_count}
        ''')
        
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(
                '\nNote: Users without matching email were skipped.'
                '\nCreate User accounts for these employees or update their emails.'
            ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\nThis was a dry run. Run without --dry-run to apply changes.'
            ))
        
        self.stdout.write('='*60 + '\n')
