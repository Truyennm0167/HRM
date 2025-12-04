"""
Django management command to send contract expiring alerts.
Run daily via cron job: python manage.py send_contract_alerts --days 30
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import Contract, Employee
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
        
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('📋 CẢNH BÁO HỢP ĐỒNG SẮP HẾT HẠN')
        self.stdout.write('=' * 60)
        self.stdout.write(f'📅 Ngày hôm nay: {today}')
        self.stdout.write(f'⏰ Kiểm tra hợp đồng hết hạn trong: {days_threshold} ngày tới')
        self.stdout.write(f'📆 Ngày giới hạn: {alert_date}')
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 CHẾ ĐỘ DRY-RUN: Không gửi email thực sự'))
        self.stdout.write('=' * 60)
        self.stdout.write('')
        
        # Find contracts expiring within threshold
        # - status = 'active' (đang hiệu lực)
        # - end_date is not null (có ngày kết thúc)
        # - end_date >= today (chưa hết hạn)
        # - end_date <= alert_date (trong khoảng cảnh báo)
        # - employee status in [0, 1, 2] (Onboarding, Thử việc, Chính thức)
        expiring_contracts = Contract.objects.filter(
            status='active',
            end_date__isnull=False,
            end_date__gte=today,
            end_date__lte=alert_date,
            employee__status__in=[0, 1, 2]  # Onboarding, Thử việc, Chính thức
        ).select_related('employee', 'employee__department', 'job_title').order_by('end_date')
        
        if not expiring_contracts.exists():
            self.stdout.write(
                self.style.SUCCESS(f'✅ Không có hợp đồng nào hết hạn trong {days_threshold} ngày tới.')
            )
            return
        
        self.stdout.write(f'📊 Tìm thấy {expiring_contracts.count()} hợp đồng sắp hết hạn:')
        self.stdout.write('')
        
        success_count = 0
        error_count = 0
        skip_count = 0
        
        for contract in expiring_contracts:
            employee = contract.employee
            days_remaining = (contract.end_date - today).days
            
            # Hiển thị thông tin
            self.stdout.write(f'  👤 {employee.name} ({employee.employee_code})')
            self.stdout.write(f'     📧 Email: {employee.email or "N/A"}')
            self.stdout.write(f'     🏢 Phòng ban: {employee.department.name if employee.department else "N/A"}')
            self.stdout.write(f'     📄 Loại HĐ: {contract.get_contract_type_display()}')
            self.stdout.write(f'     📋 Mã HĐ: {contract.contract_code}')
            self.stdout.write(f'     📅 Ngày hết hạn: {contract.end_date}')
            self.stdout.write(f'     ⏳ Còn lại: {days_remaining} ngày')
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'     🔍 [DRY-RUN] Bỏ qua gửi email'))
            else:
                if not employee.email:
                    self.stdout.write(self.style.WARNING(f'     ⚠️ Không có email - bỏ qua'))
                    skip_count += 1
                else:
                    try:
                        EmailService.send_contract_expiring_alert(employee, days_remaining)
                        self.stdout.write(self.style.SUCCESS(f'     ✅ Đã gửi email thành công'))
                        success_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'     ❌ Lỗi gửi email: {str(e)}'))
                        error_count += 1
                        logger.error(f"Error sending contract alert to {employee.email}: {e}")
            
            self.stdout.write('')  # Dòng trống
        
        # Tổng kết
        self.stdout.write('=' * 60)
        self.stdout.write('📊 TỔNG KẾT:')
        self.stdout.write(f'   • Tổng số hợp đồng sắp hết hạn: {expiring_contracts.count()}')
        if not dry_run:
            self.stdout.write(f'   • Gửi email thành công: {success_count}')
            self.stdout.write(f'   • Gửi email thất bại: {error_count}')
            self.stdout.write(f'   • Bỏ qua (không có email): {skip_count}')
        else:
            self.stdout.write(self.style.WARNING(f'   • CHẾ ĐỘ DRY-RUN - Không gửi email'))
        self.stdout.write('=' * 60)
        self.stdout.write('')
