"""
Django management command to send appraisal reminders.
Run monthly via cron job: python manage.py send_appraisal_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import Employee, Appraisal, AppraisalPeriod
from app.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send email reminders for pending appraisals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period-id',
            type=int,
            help='Specific period ID to check. If not provided, uses active periods.'
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

    def handle(self, *args, **options):
        period_id = options.get('period_id')
        dry_run = options['dry_run']
        to_managers = options['to_managers']
        
        self.stdout.write('')
        self.stdout.write('=' * 60)
        if to_managers:
            self.stdout.write('📋 GỬI NHẮC NHỞ ĐÁNH GIÁ CHO MANAGER')
        else:
            self.stdout.write('📋 GỬI NHẮC NHỞ TỰ ĐÁNH GIÁ CHO NHÂN VIÊN')
        self.stdout.write('=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 CHẾ ĐỘ DRY-RUN: Không gửi email thực sự'))
        self.stdout.write('=' * 60)
        self.stdout.write('')
        
        # Get appraisal periods
        if period_id:
            periods = AppraisalPeriod.objects.filter(id=period_id)
        else:
            periods = AppraisalPeriod.objects.filter(status='active')
        
        if not periods.exists():
            self.stdout.write(self.style.WARNING('⚠️ Không có kỳ đánh giá nào đang hoạt động.'))
            return
        
        for period in periods:
            self.stdout.write(f'📆 Kỳ đánh giá: {period.name}')
            self.stdout.write(f'   Thời gian: {period.start_date} - {period.end_date}')
            self.stdout.write('')
            
            if to_managers:
                self.send_manager_reminders(period, dry_run)
            else:
                self.send_employee_reminders(period, dry_run)

    def send_employee_reminders(self, period, dry_run):
        """Send reminders to employees who haven't completed self-appraisal"""
        
        # Find appraisals pending self-assessment
        pending_appraisals = Appraisal.objects.filter(
            period=period,
            status='pending_self'
        ).select_related('employee', 'employee__department')
        
        if not pending_appraisals.exists():
            self.stdout.write(self.style.SUCCESS(
                f'✅ Tất cả nhân viên đã hoàn thành tự đánh giá cho kỳ {period.name}.'
            ))
            return
        
        count = pending_appraisals.count()
        self.stdout.write(f'📊 Tìm thấy {count} nhân viên cần nhắc nhở:')
        self.stdout.write('')
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for appraisal in pending_appraisals:
            employee = appraisal.employee
            
            self.stdout.write(f'  👤 {employee.name} ({employee.employee_code})')
            self.stdout.write(f'     📧 Email: {employee.email or "N/A"}')
            self.stdout.write(f'     🏢 Phòng ban: {employee.department.name if employee.department else "N/A"}')
            
            if not employee.email:
                self.stdout.write(self.style.WARNING(f'     ⚠️ Không có email - bỏ qua'))
                skip_count += 1
                self.stdout.write('')
                continue
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'     🔍 [DRY-RUN] Bỏ qua gửi email'))
            else:
                try:
                    EmailService.send_appraisal_reminder(employee, period.name)
                    self.stdout.write(self.style.SUCCESS(f'     ✅ Đã gửi email thành công'))
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'     ❌ Lỗi gửi email: {str(e)}'))
                    error_count += 1
                    logger.error(f"Error sending appraisal reminder to {employee.email}: {e}")
            
            self.stdout.write('')
        
        # Summary
        self._print_summary(count, success_count, error_count, skip_count, dry_run)

    def send_manager_reminders(self, period, dry_run):
        """Send reminders to managers about pending team appraisals to review"""
        
        # Find appraisals pending manager review
        pending_appraisals = Appraisal.objects.filter(
            period=period,
            status='pending_manager'
        ).select_related('employee', 'employee__department', 'manager')
        
        if not pending_appraisals.exists():
            self.stdout.write(self.style.SUCCESS(
                f'✅ Không có đánh giá nào đang chờ manager duyệt cho kỳ {period.name}.'
            ))
            return
        
        # Group by manager
        managers_pending = {}
        for appraisal in pending_appraisals:
            manager = appraisal.manager
            if manager:
                if manager.id not in managers_pending:
                    managers_pending[manager.id] = {
                        'manager': manager,
                        'appraisals': []
                    }
                managers_pending[manager.id]['appraisals'].append(appraisal)
        
        if not managers_pending:
            self.stdout.write(self.style.WARNING('⚠️ Không tìm thấy manager nào.'))
            return
        
        self.stdout.write(f'📊 Tìm thấy {len(managers_pending)} manager cần nhắc nhở:')
        self.stdout.write('')
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for manager_id, data in managers_pending.items():
            manager = data['manager']
            appraisals = data['appraisals']
            pending_count = len(appraisals)
            
            self.stdout.write(f'  👤 {manager.name} ({manager.employee_code})')
            self.stdout.write(f'     📧 Email: {manager.email or "N/A"}')
            self.stdout.write(f'     🏢 Phòng ban: {manager.department.name if manager.department else "N/A"}')
            self.stdout.write(f'     📋 Số đánh giá chờ duyệt: {pending_count}')
            
            if not manager.email:
                self.stdout.write(self.style.WARNING(f'     ⚠️ Không có email - bỏ qua'))
                skip_count += 1
                self.stdout.write('')
                continue
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'     🔍 [DRY-RUN] Bỏ qua gửi email'))
            else:
                try:
                    EmailService.send_manager_review_reminder(
                        manager=manager,
                        pending_appraisals=appraisals,
                        period=period.name
                    )
                    self.stdout.write(self.style.SUCCESS(f'     ✅ Đã gửi email thành công'))
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'     ❌ Lỗi gửi email: {str(e)}'))
                    error_count += 1
                    logger.error(f"Error sending manager reminder to {manager.email}: {e}")
            
            self.stdout.write('')
        
        # Summary
        self._print_summary(len(managers_pending), success_count, error_count, skip_count, dry_run)
    
    def _print_summary(self, total, success, error, skip, dry_run):
        """Print summary of email sending"""
        self.stdout.write('=' * 60)
        self.stdout.write('📊 TỔNG KẾT:')
        self.stdout.write(f'   • Tổng số cần gửi: {total}')
        if not dry_run:
            self.stdout.write(f'   • Gửi email thành công: {success}')
            self.stdout.write(f'   • Gửi email thất bại: {error}')
            self.stdout.write(f'   • Bỏ qua (không có email): {skip}')
        else:
            self.stdout.write(self.style.WARNING(f'   • CHẾ ĐỘ DRY-RUN - Không gửi email'))
        self.stdout.write('=' * 60)
        self.stdout.write('')
