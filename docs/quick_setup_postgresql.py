"""
Quick Setup Script - PostgreSQL + Vietnamese Sample Data
Tự động setup PostgreSQL và tạo dữ liệu mẫu tiếng Việt
"""
import os
import sys
import subprocess
import time

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(step, text):
    print(f"\n{'='*5} BƯỚC {step} {'='*57}")
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def run_command(command, description, check_error=True):
    """Run command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print_success("Thành công!")
            if result.stdout and result.stdout.strip():
                print(result.stdout[:500])  # Show first 500 chars
            return True
        else:
            if check_error:
                print_error("Thất bại!")
                if result.stderr:
                    print(f"Lỗi: {result.stderr[:500]}")
            return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def check_env_file():
    """Check if .env file exists and is configured"""
    print_step(1, "KIỂM TRA FILE CẤU HÌNH (.env)")
    
    if not os.path.exists('.env'):
        print_error("File .env không tồn tại!")
        print_info("Cần tạo file .env với cấu hình PostgreSQL")
        return False
    
    # Use python-dotenv to properly read .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check required environment variables
        use_postgresql = os.getenv('USE_POSTGRESQL', '0')
        postgres_password = os.getenv('POSTGRES_PASSWORD', '')
        postgres_db = os.getenv('POSTGRES_DB', '')
        
        # Check if PostgreSQL is enabled
        if use_postgresql != '1':
            print_warning("PostgreSQL chưa được kích hoạt!")
            print_info("Trong file .env, đảm bảo có: USE_POSTGRESQL=1")
            return False
        
        # Check if password is configured
        if not postgres_password or postgres_password == 'YOUR_POSTGRESQL_PASSWORD_HERE':
            print_warning("POSTGRES_PASSWORD chưa được thiết lập!")
            print("\n" + "=" * 70)
            print("🛠️  CẦN CẤU HÌNH:")
            print("=" * 70)
            print("\n1. Mở file .env")
            print("2. Tìm dòng: POSTGRES_PASSWORD=...")
            print("3. Thay bằng password PostgreSQL của bạn")
            print("   Ví dụ: POSTGRES_PASSWORD=postgres123")
            print("4. Lưu file và chạy lại script này")
            print("\n" + "=" * 70)
            return False
        
        # Check database name
        if not postgres_db:
            print_warning("POSTGRES_DB chưa được thiết lập!")
            print_info("Thêm dòng: POSTGRES_DB=hrm_db")
            return False
        
        print_success(f"File .env đã được cấu hình đúng")
        print_info(f"Database: {postgres_db}")
        print_info(f"Password: {'*' * len(postgres_password)}")
        return True
        
    except ImportError:
        print_warning("Package python-dotenv chưa được cài đặt!")
        print_info("Đang cài đặt python-dotenv...")
        if run_command("pip install python-dotenv", "Cài đặt python-dotenv"):
            # Retry after installation
            from dotenv import load_dotenv
            load_dotenv()
            return check_env_file()  # Recursive call
        return False
    except Exception as e:
        print_error(f"Lỗi khi đọc file .env: {str(e)}")
        return False

def check_packages():
    """Check if required packages are installed"""
    print_step(2, "KIỂM TRA PACKAGES")
    
    packages = {
        'psycopg2': 'psycopg2-binary',
        'dotenv': 'python-dotenv',
    }
    
    all_installed = True
    
    for module, package in packages.items():
        try:
            __import__(module.replace('-', '_'))
            print_success(f"{package} đã cài đặt")
        except ImportError:
            print_warning(f"{package} chưa cài đặt")
            print_info(f"Đang cài đặt {package}...")
            if run_command(f"pip install {package}", f"Cài đặt {package}", check_error=False):
                print_success(f"Đã cài đặt {package}")
            else:
                all_installed = False
    
    return all_installed

def check_postgresql_connection():
    """Check PostgreSQL connection"""
    print_step(3, "KIỂM TRA KẾT NỐI POSTGRESQL")
    
    test_script = """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()

from django.db import connection
from django.conf import settings

# Check database engine
db_engine = settings.DATABASES['default']['ENGINE']
if 'postgresql' not in db_engine:
    print("ERROR: Database engine is not PostgreSQL:", db_engine)
    exit(1)

# Test connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"PostgreSQL version: {version.split(',')[0]}")
        print("Connection successful!")
except Exception as e:
    print(f"ERROR: {str(e)}")
    exit(1)
"""
    
    with open('_test_connection.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    success = run_command('python _test_connection.py', 'Test kết nối PostgreSQL')
    
    # Clean up
    if os.path.exists('_test_connection.py'):
        os.remove('_test_connection.py')
    
    if not success:
        print("\n" + "=" * 70)
        print("🔧 HƯỚNG DẪN SỬA LỖI:")
        print("=" * 70)
        print("\n1. Kiểm tra PostgreSQL service đang chạy:")
        print("   Get-Service postgresql*")
        print("\n2. Nếu stopped, start service:")
        print("   Start-Service postgresql-x64-15")
        print("\n3. Kiểm tra password trong .env có đúng không")
        print("\n4. Đảm bảo database 'hrm_db' đã được tạo:")
        print("   psql -U postgres -c \"CREATE DATABASE hrm_db;\"")
        print("\n" + "=" * 70)
        return False
    
    return True

def run_migrations():
    """Run Django migrations"""
    print_step(4, "TẠO SCHEMA DATABASE")
    
    return run_command(
        'python manage.py migrate',
        'Chạy migrations (tạo tables trong PostgreSQL)'
    )

def check_superuser():
    """Check if superuser exists"""
    print_step(5, "KIỂM TRA SUPERUSER")
    
    check_script = """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()

from django.contrib.auth.models import User

superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    print(f"Found {superusers.count()} superuser(s)")
    for user in superusers:
        print(f"  - {user.username} ({user.email})")
    exit(0)
else:
    print("No superuser found")
    exit(1)
"""
    
    with open('_check_superuser.py', 'w', encoding='utf-8') as f:
        f.write(check_script)
    
    success = run_command('python _check_superuser.py', 'Kiểm tra superuser', check_error=False)
    
    # Clean up
    if os.path.exists('_check_superuser.py'):
        os.remove('_check_superuser.py')
    
    if not success:
        print_warning("Chưa có superuser")
        print_info("Bạn cần tạo superuser để đăng nhập admin panel")
        print("\nChạy lệnh sau để tạo:")
        print("  python manage.py createsuperuser")
        print("\nSau đó chạy lại script này để tạo data mẫu")
        return False
    
    return True

def create_sample_data():
    """Create Vietnamese sample data"""
    print_step(6, "TẠO DỮ LIỆU MẪU TIẾNG VIỆT")
    
    # Check if data already exists
    check_script = """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()

from app.models import Employee, Department

emp_count = Employee.objects.count()
dept_count = Department.objects.count()

if emp_count > 0 or dept_count > 0:
    print(f"Found existing data: {emp_count} employees, {dept_count} departments")
    exit(1)
else:
    print("No existing data found")
    exit(0)
"""
    
    with open('_check_data.py', 'w', encoding='utf-8') as f:
        f.write(check_script)
    
    has_data = not run_command('python _check_data.py', 'Kiểm tra dữ liệu hiện tại', check_error=False)
    
    # Clean up
    if os.path.exists('_check_data.py'):
        os.remove('_check_data.py')
    
    if has_data:
        print_warning("Database đã có dữ liệu!")
        print("\nBạn muốn:")
        print("  1. Giữ nguyên dữ liệu cũ")
        print("  2. Xóa và tạo dữ liệu mới")
        
        choice = input("\nChọn (1/2): ").strip()
        
        if choice == '2':
            print_info("Đang xóa dữ liệu cũ...")
            # Data sẽ được xóa bởi script tạo data
        else:
            print_info("Giữ nguyên dữ liệu cũ")
            return True
    
    # Run sample data script
    print_info("Chạy script tạo dữ liệu mẫu...")
    print_warning("Khi script hỏi xác nhận, gõ 'yes' và nhấn Enter")
    
    time.sleep(2)
    
    # Run interactively
    subprocess.run('python create_vietnamese_sample_data.py', shell=True)
    
    return True

def verify_setup():
    """Verify everything is setup correctly"""
    print_step(7, "KIỂM TRA TỔNG THỂ")
    
    verify_script = """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
import django
django.setup()

from django.contrib.auth.models import User
from app.models import Employee, Department, Contract, LeaveRequest, Payroll

print("\\n📊 Thống kê dữ liệu:")
print(f"  👥 Nhân viên:       {Employee.objects.count()}")
print(f"  📁 Phòng ban:       {Department.objects.count()}")
print(f"  📄 Hợp đồng:        {Contract.objects.count()}")
print(f"  📅 Đơn nghỉ phép:   {LeaveRequest.objects.count()}")
print(f"  💰 Bảng lương:      {Payroll.objects.count()}")
print(f"  👤 Users:           {User.objects.count()}")

superusers = User.objects.filter(is_superuser=True)
print(f"\\n🔑 Superusers: {superusers.count()}")
for user in superusers:
    print(f"  - {user.username}")
"""
    
    with open('_verify.py', 'w', encoding='utf-8') as f:
        f.write(verify_script)
    
    run_command('python _verify.py', 'Kiểm tra dữ liệu')
    
    # Clean up
    if os.path.exists('_verify.py'):
        os.remove('_verify.py')

def main():
    """Main function"""
    print_header("SETUP POSTGRESQL + DỮ LIỆU MẪU TIẾNG VIỆT")
    
    print("Script này sẽ tự động:")
    print("  1. Kiểm tra cấu hình .env")
    print("  2. Cài đặt packages cần thiết")
    print("  3. Kiểm tra kết nối PostgreSQL")
    print("  4. Chạy migrations (tạo tables)")
    print("  5. Kiểm tra superuser")
    print("  6. Tạo dữ liệu mẫu tiếng Việt")
    print("  7. Verify kết quả")
    
    print("\n⚠️  YÊU CẦU TRƯỚC KHI CHẠY:")
    print("  - PostgreSQL đã được cài đặt")
    print("  - Database 'hrm_db' đã được tạo")
    print("  - File .env đã được cấu hình password")
    
    response = input("\n✋ Tiếp tục? (yes/no): ")
    if response.lower() != 'yes':
        print_error("Đã hủy!")
        return
    
    try:
        # Step 1: Check .env
        if not check_env_file():
            return
        
        # Step 2: Check packages
        if not check_packages():
            print_error("Không thể cài đặt packages cần thiết")
            return
        
        # Step 3: Check PostgreSQL connection
        if not check_postgresql_connection():
            return
        
        # Step 4: Run migrations
        if not run_migrations():
            print_error("Migrations thất bại")
            return
        
        # Step 5: Check superuser
        if not check_superuser():
            return
        
        # Step 6: Create sample data
        create_sample_data()
        
        # Step 7: Verify
        verify_setup()
        
        # Success!
        print_header("🎉 HOÀN THÀNH!")
        
        print("\n✅ PostgreSQL đã được setup")
        print("✅ Dữ liệu mẫu tiếng Việt đã được tạo")
        print("✅ Hệ thống sẵn sàng sử dụng!")
        
        print("\n" + "=" * 70)
        print("📱 BƯỚC TIẾP THEO:")
        print("=" * 70)
        print("\n1. Chạy server:")
        print("   python manage.py runserver")
        print("\n2. Mở browser:")
        print("   http://localhost:8000/admin/")
        print("\n3. Đăng nhập:")
        print("   - Admin: (username/password bạn đã tạo)")
        print("   - Nhân viên: password = 123456")
        print("\n" + "=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n❌ Đã bị hủy bởi người dùng (Ctrl+C)")
    except Exception as e:
        print_error(f"Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
