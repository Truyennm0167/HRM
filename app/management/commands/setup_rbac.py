"""
Management command to initialize RBAC groups and permissions for HRMS.

Creates 3 groups:
1. HR - Full access to employee management, contracts, payroll
2. Manager - Department-level access, team management, approvals
3. Employee - Self-service access only

Usage:
    python manage.py setup_rbac
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Employee, Contract, Department, LeaveRequest, Expense, Payroll


class Command(BaseCommand):
    help = 'Setup RBAC groups and permissions for HRMS'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting RBAC setup...'))
        
        # Create Groups
        hr_group, hr_created = Group.objects.get_or_create(name='HR')
        manager_group, mgr_created = Group.objects.get_or_create(name='Manager')
        employee_group, emp_created = Group.objects.get_or_create(name='Employee')
        
        if hr_created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created HR group'))
        else:
            self.stdout.write('  ⚪ HR group already exists')
            
        if mgr_created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created Manager group'))
        else:
            self.stdout.write('  ⚪ Manager group already exists')
            
        if emp_created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created Employee group'))
        else:
            self.stdout.write('  ⚪ Employee group already exists')
        
        # Get content types
        employee_ct = ContentType.objects.get_for_model(Employee)
        contract_ct = ContentType.objects.get_for_model(Contract)
        department_ct = ContentType.objects.get_for_model(Department)
        
        try:
            leave_ct = ContentType.objects.get_for_model(LeaveRequest)
        except:
            leave_ct = None
            
        try:
            expense_ct = ContentType.objects.get_for_model(Expense)
        except:
            expense_ct = None
            
        try:
            payroll_ct = ContentType.objects.get_for_model(Payroll)
        except:
            payroll_ct = None
        
        self.stdout.write(self.style.SUCCESS('\n📋 Setting up permissions...'))
        
        # === HR Group Permissions (Full Access) ===
        self.stdout.write('\n  🔐 HR Group:')
        hr_permissions = []
        
        # Employee permissions
        hr_permissions.extend([
            Permission.objects.get(codename='add_employee', content_type=employee_ct),
            Permission.objects.get(codename='change_employee', content_type=employee_ct),
            Permission.objects.get(codename='delete_employee', content_type=employee_ct),
            Permission.objects.get(codename='view_employee', content_type=employee_ct),
        ])
        
        # Contract permissions
        hr_permissions.extend([
            Permission.objects.get(codename='add_contract', content_type=contract_ct),
            Permission.objects.get(codename='change_contract', content_type=contract_ct),
            Permission.objects.get(codename='delete_contract', content_type=contract_ct),
            Permission.objects.get(codename='view_contract', content_type=contract_ct),
        ])
        
        # Department permissions
        hr_permissions.extend([
            Permission.objects.get(codename='add_department', content_type=department_ct),
            Permission.objects.get(codename='change_department', content_type=department_ct),
            Permission.objects.get(codename='delete_department', content_type=department_ct),
            Permission.objects.get(codename='view_department', content_type=department_ct),
        ])
        
        # Leave permissions (if available)
        if leave_ct:
            hr_permissions.extend([
                Permission.objects.get(codename='add_leaverequest', content_type=leave_ct),
                Permission.objects.get(codename='change_leaverequest', content_type=leave_ct),
                Permission.objects.get(codename='view_leaverequest', content_type=leave_ct),
            ])
        
        # Expense permissions (if available)
        if expense_ct:
            hr_permissions.extend([
                Permission.objects.get(codename='add_expense', content_type=expense_ct),
                Permission.objects.get(codename='change_expense', content_type=expense_ct),
                Permission.objects.get(codename='view_expense', content_type=expense_ct),
            ])
        
        # Payroll permissions (if available)
        if payroll_ct:
            hr_permissions.extend([
                Permission.objects.get(codename='add_payroll', content_type=payroll_ct),
                Permission.objects.get(codename='change_payroll', content_type=payroll_ct),
                Permission.objects.get(codename='view_payroll', content_type=payroll_ct),
            ])
        
        hr_group.permissions.set(hr_permissions)
        self.stdout.write(f'    ✅ Added {len(hr_permissions)} permissions')
        
        # === Manager Group Permissions (Department-level) ===
        self.stdout.write('\n  🔐 Manager Group:')
        manager_permissions = []
        
        # View employees (can view all in department)
        manager_permissions.append(
            Permission.objects.get(codename='view_employee', content_type=employee_ct)
        )
        
        # View contracts (department only)
        manager_permissions.append(
            Permission.objects.get(codename='view_contract', content_type=contract_ct)
        )
        
        # View departments
        manager_permissions.append(
            Permission.objects.get(codename='view_department', content_type=department_ct)
        )
        
        # Leave management
        if leave_ct:
            manager_permissions.extend([
                Permission.objects.get(codename='view_leaverequest', content_type=leave_ct),
                Permission.objects.get(codename='change_leaverequest', content_type=leave_ct),  # For approval
            ])
        
        # Expense approval
        if expense_ct:
            manager_permissions.extend([
                Permission.objects.get(codename='view_expense', content_type=expense_ct),
                Permission.objects.get(codename='change_expense', content_type=expense_ct),  # For approval
            ])
        
        # View payroll (department only)
        if payroll_ct:
            manager_permissions.append(
                Permission.objects.get(codename='view_payroll', content_type=payroll_ct)
            )
        
        manager_group.permissions.set(manager_permissions)
        self.stdout.write(f'    ✅ Added {len(manager_permissions)} permissions')
        
        # === Employee Group Permissions (Self-service) ===
        self.stdout.write('\n  🔐 Employee Group:')
        employee_permissions = []
        
        # View own employee record
        employee_permissions.append(
            Permission.objects.get(codename='view_employee', content_type=employee_ct)
        )
        
        # View own contracts
        employee_permissions.append(
            Permission.objects.get(codename='view_contract', content_type=contract_ct)
        )
        
        # Leave requests
        if leave_ct:
            employee_permissions.extend([
                Permission.objects.get(codename='add_leaverequest', content_type=leave_ct),
                Permission.objects.get(codename='view_leaverequest', content_type=leave_ct),
            ])
        
        # Expense claims
        if expense_ct:
            employee_permissions.extend([
                Permission.objects.get(codename='add_expense', content_type=expense_ct),
                Permission.objects.get(codename='view_expense', content_type=expense_ct),
            ])
        
        # View own payroll
        if payroll_ct:
            employee_permissions.append(
                Permission.objects.get(codename='view_payroll', content_type=payroll_ct)
            )
        
        employee_group.permissions.set(employee_permissions)
        self.stdout.write(f'    ✅ Added {len(employee_permissions)} permissions')
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ RBAC setup complete!'))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • HR Group: {hr_group.permissions.count()} permissions')
        self.stdout.write(f'  • Manager Group: {manager_group.permissions.count()} permissions')
        self.stdout.write(f'  • Employee Group: {employee_group.permissions.count()} permissions')
        
        self.stdout.write(f'\n💡 Next steps:')
        self.stdout.write(f'  1. Assign users to groups: user.groups.add(hr_group)')
        self.stdout.write(f'  2. Apply decorators to views: @permission_required("app.view_contract")')
        self.stdout.write(f'  3. Update templates with permission checks')
