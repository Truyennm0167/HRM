"""
Script kiểm tra các thay đổi bảo mật đã được áp dụng
Chạy script này để test xem các decorators đã hoạt động chưa
"""

import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:8000"

def test_authentication_required():
    """Test xem các endpoint có yêu cầu login không"""
    print("\n=== TEST 1: Authentication Required ===")
    
    endpoints = [
        "/add_employee",
        "/employee_list",
        "/department/",
        "/job_title",
        "/attendance/manage/",
        "/payroll/manage/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", allow_redirects=False)
            if response.status_code == 302:  # Redirect to login
                print(f"✅ {endpoint} - Yêu cầu login (redirect)")
            elif response.status_code == 200:
                print(f"⚠️  {endpoint} - Truy cập được (có thể đã login)")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Lỗi: {e}")

def test_method_restrictions():
    """Test xem các endpoint POST-only có chặn GET không"""
    print("\n=== TEST 2: Method Restrictions (POST-only endpoints) ===")
    
    post_only_endpoints = [
        "/add_employee_save",
        "/add_department_save/",
        "/add_job_title_save",
        "/update_employee_save/",
        "/attendance/add/save/",
        "/payroll/save/",
        "/payroll/delete/",
        "/payroll/confirm/",
    ]
    
    for endpoint in post_only_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", allow_redirects=False)
            if response.status_code == 405:  # Method Not Allowed
                print(f"✅ {endpoint} - Chặn GET đúng (405)")
            elif response.status_code == 302:  # Redirect to login first
                print(f"✅ {endpoint} - Redirect to login (302)")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Lỗi: {e}")

def test_validation_exists():
    """Kiểm tra xem file validators.py có tồn tại không"""
    print("\n=== TEST 3: Validator File ===")
    
    import os
    validator_path = "app/validators.py"
    
    if os.path.exists(validator_path):
        print(f"✅ {validator_path} - Tồn tại")
        
        # Đọc và kiểm tra các function
        with open(validator_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        validators = [
            'validate_image_file',
            'validate_document_file', 
            'validate_salary',
            'validate_phone_number',
            'validate_email'
        ]
        
        for validator in validators:
            if f"def {validator}" in content:
                print(f"  ✅ {validator}() - Có")
            else:
                print(f"  ❌ {validator}() - Không tìm thấy")
    else:
        print(f"❌ {validator_path} - Không tồn tại")

def test_logging_configured():
    """Kiểm tra logging configuration"""
    print("\n=== TEST 4: Logging Configuration ===")
    
    import os
    settings_path = "hrm/settings.py"
    
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'LOGGING = {' in content:
            print("✅ LOGGING configuration - Có")
            
            if "'file':" in content:
                print("  ✅ File handler - Có")
            if "'console':" in content:
                print("  ✅ Console handler - Có")
            if "hrm.log" in content:
                print("  ✅ Log file path - hrm.log")
        else:
            print("❌ LOGGING configuration - Không tìm thấy")
    else:
        print(f"❌ {settings_path} - Không tồn tại")

def test_env_example():
    """Kiểm tra .env.example"""
    print("\n=== TEST 5: Environment Configuration ===")
    
    import os
    env_path = ".env.example"
    
    if os.path.exists(env_path):
        print(f"✅ {env_path} - Tồn tại")
        
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_vars = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'GEMINI_API_KEY']
        
        for var in required_vars:
            if var in content:
                print(f"  ✅ {var} - Có")
            else:
                print(f"  ❌ {var} - Không tìm thấy")
    else:
        print(f"❌ {env_path} - Không tồn tại")

def check_decorators_in_code():
    """Kiểm tra decorators trong HodViews.py"""
    print("\n=== TEST 6: Decorators in HodViews.py ===")
    
    import os
    views_path = "app/HodViews.py"
    
    if os.path.exists(views_path):
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        login_count = content.count('@login_required')
        post_count = content.count('@require_POST')
        http_methods_count = content.count('@require_http_methods')
        logger_count = content.count('logger.')
        
        print(f"✅ @login_required: {login_count} lần")
        print(f"✅ @require_POST: {post_count} lần")
        print(f"✅ @require_http_methods: {http_methods_count} lần")
        print(f"✅ logger calls: {logger_count} lần")
        
        # Check specific functions
        critical_functions = [
            'def delete_payroll',
            'def confirm_payroll',
            'def export_payroll',
            'def delete_employee',
            'def delete_department'
        ]
        
        print("\nKiểm tra các functions quan trọng:")
        for func in critical_functions:
            if func in content:
                # Find decorator before this function
                func_index = content.find(func)
                before_func = content[max(0, func_index-200):func_index]
                
                has_login = '@login_required' in before_func
                has_post = '@require_POST' in before_func
                
                status = "✅" if (has_login or has_post) else "⚠️"
                decorators = []
                if has_login: decorators.append("@login_required")
                if has_post: decorators.append("@require_POST")
                
                print(f"  {status} {func} - {', '.join(decorators) if decorators else 'Không có decorator'}")
    else:
        print(f"❌ {views_path} - Không tồn tại")

if __name__ == "__main__":
    print("=" * 60)
    print("KIỂM TRA CÁC THAY ĐỔI BẢO MẬT")
    print("=" * 60)
    
    # File-based tests (không cần server running)
    test_validation_exists()
    test_logging_configured()
    test_env_example()
    check_decorators_in_code()
    
    # Server-based tests (cần server đang chạy)
    print("\n" + "=" * 60)
    print("Đang kiểm tra server (cần server đang chạy ở http://127.0.0.1:8000)...")
    print("=" * 60)
    
    try:
        test_authentication_required()
        test_method_restrictions()
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Server không chạy. Hãy chạy: python manage.py runserver")
    
    print("\n" + "=" * 60)
    print("HOÀN THÀNH!")
    print("=" * 60)
