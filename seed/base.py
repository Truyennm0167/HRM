"""
Base configuration for seed scripts
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

django.setup()

# Common imports
from datetime import date, datetime, timedelta
from decimal import Decimal
import random
from django.utils import timezone

# Vietnamese data
HO_LIST = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", 
           "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Lương", "Mai", "Trịnh"]
DEM_LIST = ["Văn", "Thị", "Hoàng", "Hữu", "Minh", "Quốc", "Đức", "Thanh", "Xuân", "Ngọc", 
            "Kim", "Anh", "Thành", "Phương", "Bảo", "Quang", "Hải", "Tuấn", "Công", "Mạnh"]
TEN_NAM = ["Hùng", "Dũng", "Mạnh", "Cường", "Tuấn", "Đức", "Thắng", "Quân", "Bình", "Phong",
           "Long", "Khang", "Kiệt", "Vinh", "Tùng", "Nam", "Trung", "Hải", "Sơn", "Đạt"]
TEN_NU = ["Hương", "Lan", "Hoa", "Thảo", "Linh", "Hạnh", "Ngọc", "Mai", "Trang", "Yến",
          "Nhung", "Chi", "Vy", "Trinh", "Oanh", "Hà", "Như", "Phương", "Thùy", "Diệu"]

TINH_THANH = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", 
              "Nghệ An", "Thanh Hóa", "Bình Dương", "Đồng Nai", "Quảng Ninh",
              "Bắc Ninh", "Thái Nguyên", "Nam Định", "Hải Dương", "Vĩnh Phúc"]

TRUONG_DAI_HOC = ["Đại học Bách khoa Hà Nội", "Đại học Kinh tế Quốc dân", 
                 "Đại học Ngoại thương", "Đại học FPT", "Đại học Công nghệ - ĐHQGHN",
                 "Đại học Kinh tế TP.HCM", "Đại học Bách khoa TP.HCM",
                 "Học viện Ngân hàng", "Đại học Thương mại", "Đại học Công nghiệp Hà Nội"]


def remove_vietnamese_accents(text):
    """Remove Vietnamese accents for email generation"""
    replacements = [
        ("ă", "a"), ("â", "a"), ("đ", "d"), ("ê", "e"), ("ô", "o"), ("ơ", "o"), ("ư", "u"),
        ("á", "a"), ("à", "a"), ("ả", "a"), ("ã", "a"), ("ạ", "a"),
        ("ắ", "a"), ("ằ", "a"), ("ẳ", "a"), ("ẵ", "a"), ("ặ", "a"),
        ("ấ", "a"), ("ầ", "a"), ("ẩ", "a"), ("ẫ", "a"), ("ậ", "a"),
        ("é", "e"), ("è", "e"), ("ẻ", "e"), ("ẽ", "e"), ("ẹ", "e"),
        ("ế", "e"), ("ề", "e"), ("ể", "e"), ("ễ", "e"), ("ệ", "e"),
        ("í", "i"), ("ì", "i"), ("ỉ", "i"), ("ĩ", "i"), ("ị", "i"),
        ("ó", "o"), ("ò", "o"), ("ỏ", "o"), ("õ", "o"), ("ọ", "o"),
        ("ố", "o"), ("ồ", "o"), ("ổ", "o"), ("ỗ", "o"), ("ộ", "o"),
        ("ớ", "o"), ("ờ", "o"), ("ở", "o"), ("ỡ", "o"), ("ợ", "o"),
        ("ú", "u"), ("ù", "u"), ("ủ", "u"), ("ũ", "u"), ("ụ", "u"),
        ("ứ", "u"), ("ừ", "u"), ("ử", "u"), ("ữ", "u"), ("ự", "u"),
        ("ý", "y"), ("ỳ", "y"), ("ỷ", "y"), ("ỹ", "y"), ("ỵ", "y"),
    ]
    result = text.lower()
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def generate_random_name(gender, used_names):
    """Generate unique Vietnamese name"""
    while True:
        ho = random.choice(HO_LIST)
        dem = random.choice(DEM_LIST)
        ten = random.choice(TEN_NAM if gender == 0 else TEN_NU)
        full_name = f"{ho} {dem} {ten}"
        if full_name not in used_names:
            used_names.add(full_name)
            return full_name


def generate_cccd(used_cccd):
    """Generate unique CCCD"""
    while True:
        cccd = f"0{random.randint(10, 99)}{random.randint(100000000, 999999999)}"
        if cccd not in used_cccd:
            used_cccd.add(cccd)
            return cccd


def generate_phone(used_phones):
    """Generate unique phone number"""
    while True:
        phone = f"0{random.choice(['9', '8', '7', '3', '5'])}{random.randint(10000000, 99999999)}"
        if phone not in used_phones:
            used_phones.add(phone)
            return phone


def print_success(message):
    """Print success message"""
    print(f"✓ {message}")


def print_header(message):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f" {message}")
    print(f"{'='*60}")
