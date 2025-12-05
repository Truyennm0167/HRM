"""
Reset PostgreSQL Database
Drop và tạo lại database hrm_db từ đầu
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'hrm_db')

def reset_database():
    """Drop và tạo lại database"""
    print("=" * 70)
    print("  RESET DATABASE POSTGRESQL")
    print("=" * 70)
    print(f"\nDatabase: {POSTGRES_DB}")
    print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
    print(f"User: {POSTGRES_USER}")
    
    confirm = input("\n⚠️  Cảnh báo: Tất cả dữ liệu trong database sẽ bị XÓA!\nTiếp tục? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Đã hủy!")
        return False
    
    try:
        print("\n🔄 Đang kết nối đến PostgreSQL...")
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Kết nối thành công!")
        
        # Terminate all connections to the target database
        print(f"\n🔄 Đang ngắt kết nối đến database {POSTGRES_DB}...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{POSTGRES_DB}'
            AND pid <> pg_backend_pid();
        """)
        print("✅ Đã ngắt các kết nối!")
        
        # Drop database if exists
        print(f"\n🔄 Đang xóa database {POSTGRES_DB}...")
        cursor.execute(f'DROP DATABASE IF EXISTS "{POSTGRES_DB}"')
        print(f"✅ Đã xóa database {POSTGRES_DB}!")
        
        # Create new database
        print(f"\n🔄 Đang tạo database mới {POSTGRES_DB}...")
        cursor.execute(f'CREATE DATABASE "{POSTGRES_DB}" OWNER {POSTGRES_USER}')
        print(f"✅ Đã tạo database {POSTGRES_DB}!")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("🎉 RESET DATABASE THÀNH CÔNG!")
        print("=" * 70)
        print("\n✅ Bây giờ bạn có thể chạy:")
        print("   python quick_setup_postgresql.py")
        print()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Lỗi PostgreSQL: {e}")
        print("\n💡 Kiểm tra:")
        print("   1. PostgreSQL đang chạy")
        print("   2. Password trong file .env đúng")
        print("   3. User có quyền tạo/xóa database")
        return False
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        return False

if __name__ == '__main__':
    success = reset_database()
    if not success:
        exit(1)
