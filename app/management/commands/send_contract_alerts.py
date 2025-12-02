"""
Django management command to send contract expiring alerts.
Run daily via cron job: python manage.py send_contract_alerts
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import Employee
from app.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send email alerts for contracts expiring soon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days before contract expiration to send alert (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without sending actual emails'
        )

    def handle(self, *args, **options):
        days_threshold = options['days']
        dry_run = options['dry_run']
        
        today = timezone.localtime(timezone.now()).date()
        alert_date = today + timedelta(days=days_threshold)
        
        # Find employees with contracts expiring within threshold
        # Calculate contract end date: contract_start_date + contract_duration (months)
        expiring_employees = []
        
        employees = Employee.objects.filter(
            status='active',
            contract_start_date__isnull=False,
            contract_duration__isnull=False,
            contract_duration__gt=0
        )
        
        for employee in employees:
            try:
                # Calculate contract end date
                start_date = employee.contract_start_date
                duration_months = employee.contract_duration
                
                # Add months to start date
                end_year = start_date.year + (start_date.month + duration_months - 1) // 12
                end_month = (start_date.month + duration_months - 1) % 12 + 1
                
                # Handle day overflow (e.g., Jan 31 + 1 month)
                import calendar
                max_day = calendar.monthrange(end_year, end_month)[1]
                end_day = min(start_date.day, max_day)
                
                from datetime import date
                contract_end_date = date(end_year, end_month, end_day)
                
                # Check if contract expires within threshold
                days_remaining = (contract_end_date - today).days
                
                if 0 <= days_remaining <= days_threshold:
                    expiring_employees.append({
                        'employee': employee,
                        'contract_end_date': contract_end_date,
                        'days_remaining': days_remaining
                    })
            except Exception as e:
                logger.error(f"Error calculating contract end date for {employee.name}: {e}")
                continue
        
        if not expiring_employees:
            self.stdout.write(
                self.style.SUCCESS(f'No contracts expiring within {days_threshold} days.')
            )
            return
        
        self.stdout.write(f'Found {len(expiring_employees)} contracts expiring within {days_threshold} days.')
        
        success_count = 0
        error_count = 0
        
        for item in expiring_employees:
            employee = item['employee']
            days_remaining = item['days_remaining']
            
            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] Would send alert to {employee.name} ({employee.email}) - '
                    f'Contract expires in {days_remaining} days'
                )
            else:
                try:
                    EmailService.send_contract_expiring_alert(employee, days_remaining)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Sent alert to {employee.name} ({employee.email}) - '
                            f'Contract expires in {days_remaining} days'
                        )
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Failed to send to {employee.name} ({employee.email}): {e}'
                        )
                    )
                    error_count += 1
        
        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would send {len(expiring_employees)} emails'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Sent: {success_count}, Failed: {error_count}')
            )
