"""
Restore data from JSON fixtures to PostgreSQL
Run this AFTER setting up PostgreSQL and running migrations
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def restore_database(backup_dir):
    """Restore data from JSON backup to PostgreSQL"""
    print("=" * 70)
    print("            PostgreSQL DATABASE RESTORE")
    print("=" * 70)
    
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return False
    
    print(f"\n📁 Restoring from: {backup_dir}\n")
    
    # Check database engine
    db_engine = connection.settings_dict['ENGINE']
    print(f"Database engine: {db_engine}")
    
    if 'postgresql' not in db_engine:
        print(f"⚠️  Warning: Expected PostgreSQL but got {db_engine}")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            return False
    
    # Files to restore in order (to handle foreign key dependencies)
    restore_order = [
        'auth_data.json',              # Users, Groups first
        'contenttypes_data.json',      # Content types
        'app_data.json',               # Main app data
        'ai_recruitment_data.json',    # Recruitment data
    ]
    
    # Track statistics
    stats = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
    }
    
    print("\n🔄 Restoring data...\n")
    
    for filename in restore_order:
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠ Skipping {filename} (not found)")
            stats['skipped'] += 1
            continue
        
        # Check if file has data
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data:
                    print(f"⚠ Skipping {filename} (empty)")
                    stats['skipped'] += 1
                    continue
                record_count = len(data)
        except Exception as e:
            print(f"✗ Error reading {filename}: {str(e)}")
            stats['failed'] += 1
            continue
        
        print(f"Loading {filename} ({record_count} records)...", end=' ')
        
        try:
            # Load data using loaddata command
            call_command('loaddata', filepath, verbosity=0)
            print(f"✓")
            stats['success'] += 1
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            stats['failed'] += 1
            
            # Show detailed error for important failures
            if 'auth_data' in filename or 'app_data' in filename:
                print(f"   Details: {str(e)[:200]}")
    
    # Show summary
    print("\n" + "=" * 70)
    print("RESTORE SUMMARY")
    print("=" * 70)
    print(f"  ✓ Success: {stats['success']}")
    print(f"  ✗ Failed:  {stats['failed']}")
    print(f"  ⚠ Skipped: {stats['skipped']}")
    print("=" * 70)
    
    if stats['failed'] > 0:
        print("\n⚠️  Some data could not be restored. Check errors above.")
        print("💡 Common issues:")
        print("   - Foreign key constraints")
        print("   - Duplicate primary keys")
        print("   - Missing migrations")
        return False
    else:
        print("\n✅ Data restored successfully!")
        print("\n💡 Verify your data:")
        print("   - Check admin panel")
        print("   - Test login with existing users")
        print("   - Verify employee records")
        return True

def verify_data():
    """Quick verification of restored data"""
    from django.contrib.auth.models import User
    from app.models import Employee, Department
    
    print("\n" + "=" * 70)
    print("DATA VERIFICATION")
    print("=" * 70)
    
    user_count = User.objects.count()
    employee_count = Employee.objects.count()
    department_count = Department.objects.count()
    
    print(f"  Users:       {user_count}")
    print(f"  Employees:   {employee_count}")
    print(f"  Departments: {department_count}")
    print("=" * 70)
    
    if user_count == 0:
        print("⚠️  No users found! You may need to create a superuser.")
    
    if employee_count == 0:
        print("⚠️  No employees found! Check if data was imported correctly.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python restore_postgresql_data.py <backup_directory>")
        print("\nExample:")
        print("  python restore_postgresql_data.py backups/sqlite_backup_20241116_123456")
        sys.exit(1)
    
    backup_dir = sys.argv[1]
    
    try:
        success = restore_database(backup_dir)
        if success:
            verify_data()
    except Exception as e:
        print(f"\n❌ Restore failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
