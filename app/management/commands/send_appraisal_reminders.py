"""
Django management command to send appraisal reminders.
Run monthly via cron job: python manage.py send_appraisal_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Employee, Appraisal
from app.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send email reminders for pending appraisals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            help='Specific period to check (e.g., "Q1 2024"). If not provided, uses current period.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without sending actual emails'
        )
        parser.add_argument(
            '--to-managers',
            action='store_true',
            help='Send reminders to managers about pending team appraisals'
        )

    def get_current_period(self):
        """Get current appraisal period based on quarter"""
        now = timezone.localtime(timezone.now())
        quarter = (now.month - 1) // 3 + 1
        return f"Q{quarter} {now.year}"

    def handle(self, *args, **options):
        period = options['period'] or self.get_current_period()
        dry_run = options['dry_run']
        to_managers = options['to_managers']
        
        self.stdout.write(f'Checking appraisals for period: {period}')
        
        # Get all active employees
        active_employees = Employee.objects.filter(status='active')
        
        if to_managers:
            self.send_manager_reminders(active_employees, period, dry_run)
        else:
            self.send_employee_reminders(active_employees, period, dry_run)

    def send_employee_reminders(self, employees, period, dry_run):
        """Send reminders to employees who haven't completed self-appraisal"""
        # Find employees without appraisal for this period
        employees_with_appraisal = Appraisal.objects.filter(
            period=period
        ).values_list('employee_id', flat=True)
        
        employees_without_appraisal = employees.exclude(
            id__in=employees_with_appraisal
        )
        
        if not employees_without_appraisal.exists():
            self.stdout.write(
                self.style.SUCCESS(f'All employees have submitted appraisals for {period}.')
            )
            return
        
        count = employees_without_appraisal.count()
        self.stdout.write(f'Found {count} employees without appraisal for {period}.')
        
        success_count = 0
        error_count = 0
        
        for employee in employees_without_appraisal:
            if not employee.email:
                self.stdout.write(
                    self.style.WARNING(f'  - Skipping {employee.name} (no email)')
                )
                continue
            
            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] Would send reminder to {employee.name} ({employee.email})'
                )
            else:
                try:
                    EmailService.send_appraisal_reminder(employee, period)
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Sent reminder to {employee.name}')
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Failed to send to {employee.name}: {e}')
                    )
                    error_count += 1
        
        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would send {count} emails'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Sent: {success_count}, Failed: {error_count}')
            )

    def send_manager_reminders(self, employees, period, dry_run):
        """Send reminders to managers about pending team appraisals to review"""
        # Get all managers
        managers = employees.filter(is_manager=True)
        
        if not managers.exists():
            self.stdout.write(self.style.WARNING('No managers found.'))
            return
        
        success_count = 0
        error_count = 0
        
        for manager in managers:
            # Get team members in their department
            team_members = employees.filter(
                department=manager.department
            ).exclude(id=manager.id)
            
            # Get appraisals pending manager review
            pending_appraisals = Appraisal.objects.filter(
                employee__in=team_members,
                period=period,
                manager_rating__isnull=True  # Manager hasn't reviewed yet
            ).select_related('employee')
            
            if not pending_appraisals.exists():
                continue
            
            if not manager.email:
                self.stdout.write(
                    self.style.WARNING(f'  - Skipping manager {manager.name} (no email)')
                )
                continue
            
            pending_count = pending_appraisals.count()
            pending_names = [a.employee.name for a in pending_appraisals[:5]]
            
            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] Would send reminder to manager {manager.name} '
                    f'about {pending_count} pending appraisals'
                )
            else:
                try:
                    EmailService.send_manager_review_reminder(
                        manager, 
                        pending_appraisals, 
                        period
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Sent reminder to manager {manager.name} '
                            f'({pending_count} pending reviews)'
                        )
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Failed to send to {manager.name}: {e}')
                    )
                    error_count += 1
        
        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN complete'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Sent: {success_count}, Failed: {error_count}')
            )
