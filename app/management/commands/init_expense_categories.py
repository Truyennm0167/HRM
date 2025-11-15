from django.core.management.base import BaseCommand
from app.models import ExpenseCategory

class Command(BaseCommand):
    help = 'Khởi tạo các danh mục chi phí mẫu'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Đi lại',
                'code': 'TRAVEL',
                'description': 'Chi phí đi lại công tác, xăng xe, taxi, vé máy bay',
            },
            {
                'name': 'Ăn uống',
                'code': 'MEAL',
                'description': 'Chi phí ăn uống trong công tác, tiếp khách',
            },
            {
                'name': 'Khách sạn',
                'code': 'HOTEL',
                'description': 'Chi phí thuê khách sạn khi đi công tác',
            },
            {
                'name': 'Văn phòng phẩm',
                'code': 'OFFICE',
                'description': 'Chi phí mua sắm văn phòng phẩm, thiết bị văn phòng',
            },
            {
                'name': 'Đào tạo',
                'code': 'TRAINING',
                'description': 'Chi phí khóa học, đào tạo, hội thảo',
            },
            {
                'name': 'Điện thoại',
                'code': 'PHONE',
                'description': 'Chi phí điện thoại, data di động phục vụ công việc',
            },
            {
                'name': 'Internet',
                'code': 'INTERNET',
                'description': 'Chi phí internet, dịch vụ cloud, domain',
            },
            {
                'name': 'Marketing',
                'code': 'MARKETING',
                'description': 'Chi phí quảng cáo, marketing, PR',
            },
            {
                'name': 'Sự kiện',
                'code': 'EVENT',
                'description': 'Chi phí tổ chức sự kiện, hội nghị, team building',
            },
            {
                'name': 'Khác',
                'code': 'OTHER',
                'description': 'Các chi phí khác',
            },
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categories:
            category, created = ExpenseCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Đã tạo danh mục: {category.name}')
                )
            else:
                # Cập nhật nếu đã tồn tại
                category.name = cat_data['name']
                category.description = cat_data['description']
                category.is_active = True
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Đã cập nhật danh mục: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Hoàn thành! Tạo mới: {created_count}, Cập nhật: {updated_count}'
            )
        )
