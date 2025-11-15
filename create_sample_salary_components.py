"""
Test script to create sample salary components
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from app.models import SalaryComponent

def create_sample_components():
    """Create sample salary components for testing"""
    
    components = [
        # Allowances
        {
            'code': 'PC_VITRI',
            'name': 'Phụ cấp vị trí',
            'component_type': 'allowance',
            'calculation_method': 'percentage',
            'percentage': 20,
            'is_taxable': True,
            'is_mandatory': True,
            'description': 'Phụ cấp theo vị trí công việc (20% lương cơ bản)'
        },
        {
            'code': 'PC_XANGXE',
            'name': 'Phụ cấp xăng xe',
            'component_type': 'allowance',
            'calculation_method': 'fixed',
            'default_amount': 1000000,
            'is_taxable': True,
            'is_mandatory': False,
            'description': 'Phụ cấp đi lại bằng xe máy/ô tô'
        },
        {
            'code': 'PC_COMAN',
            'name': 'Phụ cấp cơm trưa',
            'component_type': 'allowance',
            'calculation_method': 'daily',
            'default_amount': 50000,
            'is_taxable': False,
            'is_mandatory': True,
            'description': 'Tiền ăn trưa theo ngày làm việc (50k/ngày)'
        },
        {
            'code': 'PC_DIENTHOAI',
            'name': 'Phụ cấp điện thoại',
            'component_type': 'allowance',
            'calculation_method': 'fixed',
            'default_amount': 300000,
            'is_taxable': True,
            'is_mandatory': False,
            'description': 'Hỗ trợ chi phí điện thoại'
        },
        
        # Bonuses
        {
            'code': 'TH_HIEUSUAT',
            'name': 'Thưởng hiệu suất',
            'component_type': 'bonus',
            'calculation_method': 'percentage',
            'percentage': 10,
            'is_taxable': True,
            'is_mandatory': False,
            'description': 'Thưởng dựa trên đánh giá hiệu suất công việc'
        },
        {
            'code': 'TH_CHUYENCAN',
            'name': 'Thưởng chuyên cần',
            'component_type': 'bonus',
            'calculation_method': 'fixed',
            'default_amount': 500000,
            'is_taxable': True,
            'is_mandatory': False,
            'description': 'Thưởng cho nhân viên không vắng mặt'
        },
        
        # Deductions
        {
            'code': 'KT_DITRA',
            'name': 'Khấu trừ đi trễ',
            'component_type': 'deduction',
            'calculation_method': 'fixed',
            'default_amount': 100000,
            'is_taxable': False,
            'is_mandatory': False,
            'description': 'Phạt đi làm trễ'
        },
        {
            'code': 'KT_VANGMAT',
            'name': 'Khấu trừ vắng mặt',
            'component_type': 'deduction',
            'calculation_method': 'daily',
            'default_amount': 200000,
            'is_taxable': False,
            'is_mandatory': False,
            'description': 'Khấu trừ theo ngày vắng mặt không lý do'
        },
        
        # Overtime
        {
            'code': 'OT_GIONGAY',
            'name': 'Làm thêm giờ ngày thường',
            'component_type': 'overtime',
            'calculation_method': 'hourly',
            'default_amount': 100000,
            'is_taxable': True,
            'is_mandatory': False,
            'description': 'OT trong giờ hành chính (100k/giờ)'
        },
        {
            'code': 'OT_CUOITUAN',
            'name': 'Làm thêm cuối tuần',
            'component_type': 'overtime',
            'calculation_method': 'hourly',
            'default_amount': 150000,
            'is_taxable': True,
            'is_mandatory': False,
            'description': 'OT thứ 7, chủ nhật (150k/giờ)'
        },
    ]
    
    created_count = 0
    for comp_data in components:
        comp, created = SalaryComponent.objects.get_or_create(
            code=comp_data['code'],
            defaults=comp_data
        )
        if created:
            created_count += 1
            print(f"✅ Created: {comp.name}")
        else:
            print(f"⏭️  Already exists: {comp.name}")
    
    print(f"\n🎉 Summary: Created {created_count} new components")
    print(f"📊 Total components: {SalaryComponent.objects.count()}")

if __name__ == '__main__':
    create_sample_components()
