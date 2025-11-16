"""
Complete Database Migration Script
Automates the entire migration process from SQLite to PostgreSQL
"""
import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(step, text):
    """Print step with number"""
    print(f"\n{'='*3} STEP {step} {'='*60}")
    print(f"  {text}")
    print("=" * 70)

def run_command(command, description):
    """Run shell command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Success!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ Failed!")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_requirements():
    """Check if all requirements are met"""
    print_step(1, "CHECKING REQUIREMENTS")
    
    checks = {
        'Python': 'python --version',
        'Django': 'python -c "import django; print(django.VERSION)"',
        'psycopg2': 'python -c "import psycopg2; print(psycopg2.__version__)"',
    }
    
    all_passed = True
    
    for name, command in checks.items():
        print(f"\nChecking {name}...", end=' ')
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
        else:
            print(f"❌ Not found!")
            all_passed = False
            
            if name == 'psycopg2':
                print("   Install with: pip install psycopg2-binary")
    
    return all_passed

def check_postgresql():
    """Check PostgreSQL connection"""
    print_step(2, "CHECKING POSTGRESQL CONNECTION")
    
    # Check if PostgreSQL is accessible
    print("\nTesting PostgreSQL connection...")
    
    # Try to import psycopg2 and connect
    try:
        import psycopg2
        
        db_config = {
            'dbname': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
        }
        
        print(f"   Host: {db_config['host']}:{db_config['port']}")
        print(f"   User: {db_config['user']}")
        print(f"   Database: {db_config['dbname']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        
        print(f"\n✅ PostgreSQL connection successful!")
        print(f"   Version: {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ PostgreSQL connection failed!")
        print(f"   Error: {str(e)}")
        print("\n💡 Make sure:")
        print("   1. PostgreSQL is installed and running")
        print("   2. Database exists (CREATE DATABASE hrm_db;)")
        print("   3. User has proper permissions")
        print("   4. Environment variables are set correctly")
        return False

def backup_sqlite():
    """Backup SQLite database"""
    print_step(3, "BACKING UP SQLITE DATABASE")
    
    if not os.path.exists('db.sqlite3'):
        print("❌ SQLite database not found (db.sqlite3)")
        return None
    
    # Check database size
    size = os.path.getsize('db.sqlite3')
    size_mb = size / (1024 * 1024)
    print(f"   Database size: {size_mb:.2f} MB")
    
    # Run backup script
    if run_command('python backup_sqlite_data.py', 'Running backup script'):
        # Find the latest backup directory
        backups_dir = 'backups'
        if os.path.exists(backups_dir):
            backups = [d for d in os.listdir(backups_dir) if d.startswith('sqlite_backup_')]
            if backups:
                latest_backup = max(backups)
                backup_path = os.path.join(backups_dir, latest_backup)
                print(f"\n✅ Backup created: {backup_path}")
                return backup_path
    
    return None

def update_env_file():
    """Update .env file to use PostgreSQL"""
    print_step(4, "UPDATING ENVIRONMENT CONFIGURATION")
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("⚠️  .env file not found. Creating from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', env_file)
        else:
            print("❌ .env.example not found!")
            return False
    
    # Read current .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update database settings
    new_lines = []
    for line in lines:
        if line.startswith('USE_SQLITE'):
            new_lines.append('USE_SQLITE=0\n')
            print("   ✓ Set USE_SQLITE=0")
        elif line.startswith('USE_POSTGRESQL'):
            new_lines.append('USE_POSTGRESQL=1\n')
            print("   ✓ Set USE_POSTGRESQL=1")
        else:
            new_lines.append(line)
    
    # Write updated .env
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print("\n✅ Environment configuration updated!")
    return True

def migrate_schema():
    """Run Django migrations to create PostgreSQL schema"""
    print_step(5, "CREATING POSTGRESQL SCHEMA")
    
    print("\n🗄️  Running Django migrations...")
    
    # Show migrations
    run_command('python manage.py showmigrations', 'Checking migrations')
    
    # Run migrations
    if run_command('python manage.py migrate', 'Creating database schema'):
        print("\n✅ Database schema created successfully!")
        return True
    else:
        print("\n❌ Migration failed!")
        return False

def restore_data(backup_dir):
    """Restore data from backup to PostgreSQL"""
    print_step(6, "RESTORING DATA TO POSTGRESQL")
    
    if not backup_dir or not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return False
    
    command = f'python restore_postgresql_data.py "{backup_dir}"'
    if run_command(command, 'Restoring data from backup'):
        print("\n✅ Data restored successfully!")
        return True
    else:
        print("\n❌ Data restoration failed!")
        return False

def verify_migration():
    """Verify that migration was successful"""
    print_step(7, "VERIFYING MIGRATION")
    
    print("\n🔍 Checking data integrity...")
    
    # Run verification script
    verify_script = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Employee, Department, LeaveRequest, Contract

print("\\nDatabase Statistics:")
print(f"  Users:          {User.objects.count()}")
print(f"  Employees:      {Employee.objects.count()}")
print(f"  Departments:    {Department.objects.count()}")
print(f"  Leave Requests: {LeaveRequest.objects.count()}")
print(f"  Contracts:      {Contract.objects.count()}")

# Check if superuser exists
superusers = User.objects.filter(is_superuser=True)
print(f"\\nSuperusers: {superusers.count()}")
for user in superusers:
    print(f"  - {user.username} ({user.email})")
"""
    
    with open('verify_migration.py', 'w') as f:
        f.write(verify_script)
    
    if run_command('python verify_migration.py', 'Verifying data'):
        print("\n✅ Verification passed!")
        return True
    else:
        print("\n❌ Verification failed!")
        return False

def main():
    """Main migration workflow"""
    print_header("DATABASE MIGRATION: SQLite → PostgreSQL")
    print("This script will migrate your data from SQLite to PostgreSQL")
    print("\n⚠️  WARNING: This is a critical operation!")
    print("   - Make sure you have a backup of your data")
    print("   - PostgreSQL must be installed and running")
    print("   - Database credentials must be configured in .env")
    
    response = input("\n✋ Continue with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled by user")
        return
    
    # Track overall status
    start_time = time.time()
    backup_dir = None
    
    try:
        # Step 1: Check requirements
        if not check_requirements():
            print("\n❌ Requirements not met. Please install missing packages.")
            return
        
        # Step 2: Check PostgreSQL
        if not check_postgresql():
            print("\n❌ PostgreSQL not accessible. Please check configuration.")
            return
        
        # Step 3: Backup SQLite
        backup_dir = backup_sqlite()
        if not backup_dir:
            print("\n❌ Backup failed. Migration cancelled.")
            return
        
        # Step 4: Update .env
        if not update_env_file():
            print("\n❌ Failed to update environment configuration.")
            return
        
        # Step 5: Create schema
        if not migrate_schema():
            print("\n❌ Schema migration failed.")
            print("💡 Reverting to SQLite...")
            # Revert .env changes
            update_env_file()  # This will set SQLite back
            return
        
        # Step 6: Restore data
        if not restore_data(backup_dir):
            print("\n❌ Data restoration failed.")
            print("⚠️  Database schema exists but no data was imported.")
            print("💡 You can try restoring manually:")
            print(f"   python restore_postgresql_data.py {backup_dir}")
            return
        
        # Step 7: Verify
        if not verify_migration():
            print("\n⚠️  Verification failed but data may have been imported.")
            print("💡 Check manually using Django admin panel")
        
        # Success!
        elapsed = time.time() - start_time
        print_header("MIGRATION COMPLETED SUCCESSFULLY! 🎉")
        print(f"⏱️  Total time: {elapsed:.1f} seconds")
        print(f"📁 Backup location: {backup_dir}")
        print("\n✅ Your database has been migrated to PostgreSQL!")
        
        print("\n📋 Next steps:")
        print("   1. Test your application: python manage.py runserver")
        print("   2. Login to admin panel: http://localhost:8000/admin/")
        print("   3. Verify all data is accessible")
        print("   4. Keep the SQLite backup for safety")
        print(f"   5. Backup location: {backup_dir}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user (Ctrl+C)")
        if backup_dir:
            print(f"💡 Your backup is safe at: {backup_dir}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        if backup_dir:
            print(f"💡 Your backup is safe at: {backup_dir}")

if __name__ == '__main__':
    main()
