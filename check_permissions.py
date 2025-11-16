"""
Script kiểm tra phân quyền user
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Employee

print("\n" + "=" * 80)
print("DANH SÁCH PHÂN QUYỀN USER")
print("=" * 80)

print(f"\n{'USERNAME':<15} | {'IS_STAFF':<10} | {'IS_SUPERUSER':<13} | {'DEPARTMENT':<20} | {'JOB_TITLE'}")
print("-" * 90)

users = User.objects.all().exclude(username='admin').order_by('-is_superuser', '-is_staff', 'username')

for u in users:
    emp = Employee.objects.filter(email=u.email).first()
    dept_name = emp.department.name if emp and emp.department else "N/A"
    job_title = emp.job_title.name if emp and emp.job_title else "N/A"
    
    print(f"{u.username:<15} | {str(u.is_staff):<10} | {str(u.is_superuser):<13} | {dept_name:<20} | {job_title}")

print("\n" + "=" * 80)
print("TỔNG KẾT:")
print(f"  - Superuser (Giám Đốc): {User.objects.filter(is_superuser=True).exclude(username='admin').count()}")
print(f"  - Staff (Quản lý + HR): {User.objects.filter(is_staff=True, is_superuser=False).count()}")
print(f"  - Nhân viên thường: {User.objects.filter(is_staff=False, is_superuser=False).count()}")
print("=" * 80 + "\n")
