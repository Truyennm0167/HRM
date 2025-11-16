"""
Management command to setup Django Groups and Permissions for HRM System
Usage: python manage.py setup_groups_permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import (
    Employee, Department, JobTitle, Payroll, Attendance, 
    LeaveRequest, Reward, Discipline, Evaluation,
    JobPosting, Application, 
    AppraisalPeriod, Appraisal, AppraisalCriteria, AppraisalScore, AppraisalComment
)


class Command(BaseCommand):
    help = 'Setup Django Groups (HR, Manager, Employee) with appropriate permissions'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n=== Starting Groups & Permissions Setup ===\n'))

        # Create Groups
        hr_group, created = Group.objects.get_or_create(name='HR')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created HR group'))
        else:
            self.stdout.write('  HR group already exists')

        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Manager group'))
        else:
            self.stdout.write('  Manager group already exists')

        employee_group, created = Group.objects.get_or_create(name='Employee')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Employee group'))
        else:
            self.stdout.write('  Employee group already exists')

        self.stdout.write('\n--- Assigning Permissions ---\n')

        # ============= HR GROUP PERMISSIONS (Full Access) =============
        self.stdout.write(self.style.WARNING('Configuring HR permissions...'))
        
        hr_permissions = []
        
        # Employee Management - Full CRUD
        hr_permissions.extend(Permission.objects.filter(content_type__model='employee'))
        
        # Department & Job Title - Full CRUD
        hr_permissions.extend(Permission.objects.filter(content_type__model='department'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='jobtitle'))
        
        # Payroll - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='payroll'))
        
        # Attendance - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='attendance'))
        
        # Leave Management - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='leaverequest'))
        
        # Rewards & Discipline - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='reward'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='discipline'))
        
        # Evaluation - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='evaluation'))
        
        # Recruitment - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='jobposting'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='application'))
        
        # Appraisal - Full Access
        hr_permissions.extend(Permission.objects.filter(content_type__model='appraisalperiod'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='appraisal'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='appraisalcriteria'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='appraisalscore'))
        hr_permissions.extend(Permission.objects.filter(content_type__model='appraisalcomment'))
        
        hr_group.permissions.set(hr_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Assigned {len(hr_permissions)} permissions to HR group'))

        # ============= MANAGER GROUP PERMISSIONS (Team Management) =============
        self.stdout.write(self.style.WARNING('\nConfiguring Manager permissions...'))
        
        manager_permissions = []
        
        # Employee - View team members + limited fields
        manager_permissions.append(Permission.objects.get(codename='view_employee'))
        manager_permissions.append(Permission.objects.get(codename='view_team_employees'))
        
        # Attendance - View and manage team attendance
        manager_permissions.append(Permission.objects.get(codename='view_attendance'))
        manager_permissions.append(Permission.objects.get(codename='add_attendance'))
        manager_permissions.append(Permission.objects.get(codename='change_attendance'))
        
        # Leave - Approve team leave requests
        manager_permissions.append(Permission.objects.get(codename='view_leaverequest'))
        manager_permissions.append(Permission.objects.get(codename='change_leaverequest'))
        
        # Evaluation - View and create team evaluations
        manager_permissions.append(Permission.objects.get(codename='view_evaluation'))
        manager_permissions.append(Permission.objects.get(codename='add_evaluation'))
        manager_permissions.append(Permission.objects.get(codename='change_evaluation'))
        
        # Appraisal - Review team appraisals
        manager_permissions.append(Permission.objects.get(codename='view_appraisal'))
        manager_permissions.append(Permission.objects.get(codename='change_appraisal'))
        manager_permissions.append(Permission.objects.get(codename='view_appraisalscore'))
        manager_permissions.append(Permission.objects.get(codename='change_appraisalscore'))
        manager_permissions.append(Permission.objects.get(codename='view_appraisalcomment'))
        manager_permissions.append(Permission.objects.get(codename='add_appraisalcomment'))
        
        # Recruitment - View applications for department
        manager_permissions.append(Permission.objects.get(codename='view_application'))
        
        # Department & JobTitle - View only
        manager_permissions.append(Permission.objects.get(codename='view_department'))
        manager_permissions.append(Permission.objects.get(codename='view_jobtitle'))
        
        manager_group.permissions.set(manager_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Assigned {len(manager_permissions)} permissions to Manager group'))

        # ============= EMPLOYEE GROUP PERMISSIONS (Self-Service) =============
        self.stdout.write(self.style.WARNING('\nConfiguring Employee permissions...'))
        
        employee_permissions = []
        
        # Employee - View own profile only (controlled by view logic)
        employee_permissions.append(Permission.objects.get(codename='view_employee'))
        
        # Attendance - View own attendance
        employee_permissions.append(Permission.objects.get(codename='view_attendance'))
        
        # Leave - Submit and view own leave requests
        employee_permissions.append(Permission.objects.get(codename='view_leaverequest'))
        employee_permissions.append(Permission.objects.get(codename='add_leaverequest'))
        
        # Payroll - View own payroll (view logic restricts)
        employee_permissions.append(Permission.objects.get(codename='view_payroll'))
        
        # Evaluation - View own evaluations
        employee_permissions.append(Permission.objects.get(codename='view_evaluation'))
        
        # Appraisal - Self-assess own appraisals
        employee_permissions.append(Permission.objects.get(codename='view_appraisal'))
        employee_permissions.append(Permission.objects.get(codename='change_appraisal'))
        employee_permissions.append(Permission.objects.get(codename='view_appraisalscore'))
        employee_permissions.append(Permission.objects.get(codename='change_appraisalscore'))
        employee_permissions.append(Permission.objects.get(codename='view_appraisalcomment'))
        employee_permissions.append(Permission.objects.get(codename='add_appraisalcomment'))
        
        # Recruitment - Apply for jobs (public access, but good to have)
        employee_permissions.append(Permission.objects.get(codename='view_jobposting'))
        
        # Department & JobTitle - View only
        employee_permissions.append(Permission.objects.get(codename='view_department'))
        employee_permissions.append(Permission.objects.get(codename='view_jobtitle'))
        
        employee_group.permissions.set(employee_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Assigned {len(employee_permissions)} permissions to Employee group'))

        # ============= SUMMARY =============
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\n✓✓✓ Groups & Permissions Setup Complete! ✓✓✓\n'))
        self.stdout.write('='*60)
        self.stdout.write(f'''
Groups Created:
  - HR Group: {hr_group.permissions.count()} permissions
  - Manager Group: {manager_group.permissions.count()} permissions  
  - Employee Group: {employee_group.permissions.count()} permissions

Next Steps:
  1. Assign users to groups in Django Admin
  2. Or use: python manage.py assign_user_groups
  3. Apply @permission_required decorators to views
  4. Test permission checks in views
        ''')
        self.stdout.write('='*60 + '\n')
