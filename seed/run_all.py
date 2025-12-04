"""
Run All Seeds - Chạy tất cả các seed files theo thứ tự
Run: python seed/run_all.py
"""
import os
import sys

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

# Add project root and seed folder to path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

seed_dir = os.path.join(project_root, 'seed')
if seed_dir not in sys.path:
    sys.path.insert(0, seed_dir)

# Setup Django BEFORE importing seed files
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()

# Import base module and create shared context
from seed import base
import seed.base as seed_base

# Create execution context with all base exports
exec_globals = {
    '__builtins__': __builtins__,
    'seed': type(sys)('seed'),  # Create fake seed module
}
# Copy all from base to exec_globals and to fake seed.base
for name in dir(base):
    if not name.startswith('_'):
        exec_globals[name] = getattr(base, name)

# Make seed.base available
exec_globals['seed'].base = seed_base

# List of seed files in order
seed_files = [
    "seed/seed_01_departments.py",
    "seed/seed_02_employees.py",
    "seed/seed_03_leaves.py",
    "seed/seed_04_expenses.py",
    "seed/seed_05_attendance_payroll.py",
    "seed/seed_06_rewards_disciplines.py",
    "seed/seed_07_recruitment.py",
    "seed/seed_08_contracts_settings.py",
    "seed/seed_09_appraisals.py",
    "seed/seed_10_documents_announcements.py",
    "seed/seed_11_users_permissions.py",
]

print("="*60)
print(" HRM SEED DATA - Run All")
print("="*60)
print(f"\nSẽ chạy {len(seed_files)} seed files theo thứ tự.\n")

# Ask for confirmation
response = input("Bạn có muốn tiếp tục? (y/n): ").strip().lower()
if response != 'y':
    print("Đã hủy.")
    sys.exit(0)

print("\n" + "-"*60)

# Run each seed file
for i, seed_file in enumerate(seed_files, 1):
    print(f"\n[{i}/{len(seed_files)}] Đang chạy: {seed_file}")
    print("-"*40)
    
    try:
        # Read and execute the seed file
        with open(seed_file, 'r', encoding='utf-8') as f:
            seed_code = f.read()
        
        exec(seed_code, exec_globals)
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy {seed_file}: {e}")
        import traceback
        traceback.print_exc()
        response = input("Tiếp tục với file tiếp theo? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)

print("\n" + "="*60)
print(" HOÀN TẤT TẤT CẢ SEED DATA!")
print("="*60)
