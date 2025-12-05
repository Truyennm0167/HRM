"""
Backup SQLite database to JSON fixtures
Run this BEFORE migrating to PostgreSQL
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.core.management import call_command

def backup_database():
    """Backup all data from SQLite to JSON files"""
    print("=" * 70)
    print("            SQLite DATABASE BACKUP")
    print("=" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backups/sqlite_backup_{timestamp}'
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Apps to backup
    apps = [
        'auth',           # Users, Groups, Permissions
        'contenttypes',   # Content types
        'app',            # Main HRM app
        'ai_recruitment', # Recruitment module
    ]
    
    print(f"\n📦 Creating backup directory: {backup_dir}\n")
    
    # Backup each app
    for app in apps:
        output_file = os.path.join(backup_dir, f'{app}_data.json')
        
        try:
            print(f"Backing up {app}...", end=' ')
            
            # Use dumpdata to export
            with open(output_file, 'w', encoding='utf-8') as f:
                call_command('dumpdata', app, 
                           indent=2, 
                           format='json',
                           stdout=f,
                           verbosity=0)
            
            # Check file size
            size = os.path.getsize(output_file)
            size_kb = size / 1024
            
            if size_kb > 0:
                print(f"✓ {size_kb:.1f} KB")
            else:
                print(f"⚠ Empty (0 KB)")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    # Create full backup (all data)
    full_backup_file = os.path.join(backup_dir, 'full_backup.json')
    
    print(f"\nCreating full backup...", end=' ')
    try:
        with open(full_backup_file, 'w', encoding='utf-8') as f:
            call_command('dumpdata', 
                       exclude=['contenttypes', 'auth.permission'],
                       indent=2,
                       format='json',
                       stdout=f,
                       verbosity=0)
        
        size = os.path.getsize(full_backup_file)
        size_kb = size / 1024
        print(f"✓ {size_kb:.1f} KB")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Show summary
    print("\n" + "=" * 70)
    print("BACKUP SUMMARY")
    print("=" * 70)
    
    total_size = 0
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            total_size += size
            size_kb = size / 1024
            print(f"  {file:<30} {size_kb:>8.1f} KB")
    
    print("-" * 70)
    print(f"  {'TOTAL':<30} {total_size/1024:>8.1f} KB")
    print("=" * 70)
    
    print(f"\n✅ Backup completed successfully!")
    print(f"📁 Location: {backup_dir}")
    print(f"\n💡 Next steps:")
    print(f"   1. Setup PostgreSQL database")
    print(f"   2. Update settings.py with PostgreSQL config")
    print(f"   3. Run: python manage.py migrate")
    print(f"   4. Run: python restore_postgresql_data.py {backup_dir}")
    
    return backup_dir

if __name__ == '__main__':
    try:
        backup_dir = backup_database()
    except Exception as e:
        print(f"\n❌ Backup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
