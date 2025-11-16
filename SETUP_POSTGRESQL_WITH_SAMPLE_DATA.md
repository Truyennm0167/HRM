# 🚀 Hướng Dẫn Setup PostgreSQL + Data Mẫu Tiếng Việt

## 📋 Quy Trình Tổng Thể

```
PostgreSQL ✅ → Create Database → Configure Django → Migrate Schema → Create Sample Data ✅
```

---

## BƯỚC 1: Tạo Database trong PostgreSQL

### Option A: Sử dụng pgAdmin 4 (GUI - Dễ nhất)

1. **Mở pgAdmin 4** (đã cài cùng PostgreSQL)

2. **Kết nối đến PostgreSQL Server**:

   - Expand "Servers" → "PostgreSQL 15"
   - Nhập password bạn đã đặt khi cài đặt

3. **Tạo Database**:

   - Right-click vào "Databases"
   - Chọn "Create" → "Database..."
   - Điền thông tin:
     ```
     Database: hrm_db
     Owner: postgres
     Encoding: UTF8
     ```
   - Click "Save"

4. **✅ Xong!** Database `hrm_db` đã được tạo.

### Option B: Sử dụng Command Line (psql)

```powershell
# Mở PowerShell và chạy:
psql -U postgres

# Trong psql, gõ:
CREATE DATABASE hrm_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

# Kiểm tra database đã tạo:
\l

# Thoát psql:
\q
```

---

## BƯỚC 2: Cài Đặt PostgreSQL Driver cho Python

```powershell
# 1. Kích hoạt virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Cài psycopg2
pip install psycopg2-binary

# 3. Cài python-dotenv (để đọc .env)
pip install python-dotenv

# 4. Verify đã cài thành công
python -c "import psycopg2; print('✅ psycopg2 installed successfully')"
```

---

## BƯỚC 3: Cấu Hình Environment Variables

### Tạo file `.env` trong thư mục gốc project:

```powershell
# Tạo file .env
New-Item -Path .env -ItemType File -Force
```

### Mở file `.env` và thêm nội dung:

```env
# Database Configuration - PostgreSQL
USE_SQLITE=0
USE_POSTGRESQL=1
USE_MYSQL=0

# PostgreSQL Settings
POSTGRES_DB=hrm_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_PASSWORD_HERE
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Django Settings
SECRET_KEY=django-insecure-41_t=2g08yel_j%ind5p@v0xaq7wkhsdjq^$xliwhy06d_x6ly
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (optional - để sau)
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

**⚠️ LÀM QUAN TRỌNG:**

- Thay `YOUR_PASSWORD_HERE` bằng password PostgreSQL bạn đã đặt khi cài đặt
- Ví dụ: nếu password là `postgres123` thì ghi `POSTGRES_PASSWORD=postgres123`

---

## BƯỚC 4: Test Kết Nối PostgreSQL

```powershell
# Chạy lệnh này để test connection
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings'); import django; django.setup(); from django.db import connection; connection.ensure_connection(); print('✅ PostgreSQL connection successful!')"
```

**Nếu thành công**, bạn sẽ thấy:

```
✅ PostgreSQL connection successful!
```

**Nếu lỗi**, kiểm tra:

- Password trong `.env` có đúng không?
- PostgreSQL service có đang chạy không?
- Database `hrm_db` đã tạo chưa?

---

## BƯỚC 5: Tạo Schema Database (Migrations)

```powershell
# 1. Xóa file SQLite cũ (nếu muốn)
# Remove-Item db.sqlite3 -ErrorAction SilentlyContinue

# 2. Xóa cache migrations cũ (optional - nếu có vấn đề)
# Remove-Item -Recurse -Force app\migrations\__pycache__ -ErrorAction SilentlyContinue

# 3. Chạy migrations để tạo tables trong PostgreSQL
python manage.py migrate

# Bạn sẽ thấy output:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying app.0001_initial... OK
#   ...
```

**✅ Sau bước này**: PostgreSQL đã có đầy đủ tables nhưng chưa có dữ liệu.

---

## BƯỚC 6: Tạo Superuser (Admin)

```powershell
# Tạo tài khoản admin để đăng nhập
python manage.py createsuperuser

# Nhập thông tin:
# Username: admin
# Email: admin@hrm.local
# Password: (gõ password, ví dụ: admin123)
# Password (again): (gõ lại password)
```

---

## BƯỚC 7: Tạo Data Mẫu Tiếng Việt 🇻🇳

```powershell
# Chạy script tạo dữ liệu mẫu
python create_vietnamese_sample_data.py

# Khi hỏi xác nhận, gõ: yes
```

**Script sẽ tạo**:

- ✅ 8 Phòng ban (Ban Giám Đốc, HR, IT, Marketing...)
- ✅ 64 Nhân viên với tên người Việt thực tế
- ✅ 64 Hợp đồng lao động
- ✅ 200+ Đơn nghỉ phép
- ✅ 190+ Bảng lương
- ✅ 5 Tin tuyển dụng
- ✅ 30 Đơn ứng tuyển
- ✅ 50+ Đánh giá nhân viên

**Thời gian**: 30-60 giây

---

## BƯỚC 8: Khởi Động Server và Test

```powershell
# 1. Chạy server
python manage.py runserver

# Bạn sẽ thấy:
# Starting development server at http://127.0.0.1:8000/
```

### Test Admin Panel:

1. Mở browser: http://localhost:8000/admin/

2. Đăng nhập bằng:

   - Username: `admin`
   - Password: (password bạn vừa tạo ở bước 6)

3. Kiểm tra data:
   - Click "Employees" → Xem 64 nhân viên
   - Click "Departments" → Xem 8 phòng ban
   - Click "Leave requests" → Xem đơn nghỉ phép
   - Click "Payrolls" → Xem bảng lương

### Test User Login:

1. Mở: http://localhost:8000/

2. Đăng nhập bằng tài khoản nhân viên mẫu:
   - Username: (xem trong admin hoặc console output)
   - Password: `123456` (tất cả nhân viên mẫu đều dùng password này)

---

## ✅ CHECKLIST HOÀN THÀNH

Đánh dấu các bước đã làm:

- [ ] **Bước 1**: Tạo database `hrm_db` trong PostgreSQL
- [ ] **Bước 2**: Cài `psycopg2-binary` và `python-dotenv`
- [ ] **Bước 3**: Tạo file `.env` với PostgreSQL config
- [ ] **Bước 4**: Test connection thành công
- [ ] **Bước 5**: Chạy `python manage.py migrate` thành công
- [ ] **Bước 6**: Tạo superuser `admin`
- [ ] **Bước 7**: Chạy `python create_vietnamese_sample_data.py` thành công
- [ ] **Bước 8**: Login admin panel thành công
- [ ] **Bước 9**: Xem được data tiếng Việt trong admin

---

## 🎯 TÓM TẮT CÁC LỆNH (Copy & Paste)

```powershell
# ===== SETUP =====
# 1. Kích hoạt venv
.\.venv\Scripts\Activate.ps1

# 2. Cài packages
pip install psycopg2-binary python-dotenv

# 3. Tạo .env (sau đó edit file này thủ công)
New-Item -Path .env -ItemType File -Force

# ===== SAU KHI ĐÃ EDIT .env =====
# 4. Tạo database trong PostgreSQL (dùng pgAdmin hoặc psql)

# 5. Chạy migrations
python manage.py migrate

# 6. Tạo superuser
python manage.py createsuperuser

# 7. Tạo data mẫu
python create_vietnamese_sample_data.py

# 8. Chạy server
python manage.py runserver
```

---

## 🐛 TROUBLESHOOTING

### Lỗi 1: "psycopg2 not installed"

```powershell
pip install psycopg2-binary
```

### Lỗi 2: "could not connect to server"

```powershell
# Kiểm tra PostgreSQL service đang chạy
Get-Service postgresql*

# Nếu stopped, start nó:
Start-Service postgresql-x64-15
```

### Lỗi 3: "password authentication failed"

- Kiểm tra password trong `.env` có đúng không
- Thử reset password PostgreSQL:

```powershell
psql -U postgres
\password postgres
# Nhập password mới
```

### Lỗi 4: "database does not exist"

```powershell
# Tạo database:
psql -U postgres -c "CREATE DATABASE hrm_db;"
```

### Lỗi 5: "relation does not exist"

```powershell
# Chạy lại migrations:
python manage.py migrate --run-syncdb
```

### Lỗi 6: Script tạo data bị lỗi

```powershell
# Xóa data và chạy lại:
python manage.py flush --no-input
python create_vietnamese_sample_data.py
```

---

## 📊 SAU KHI HOÀN THÀNH

### Dữ liệu trong PostgreSQL:

```
┌─────────────────────────────────────────┐
│         DATABASE: hrm_db                │
├─────────────────────────────────────────┤
│  📁 Phòng ban:           8              │
│  👥 Nhân viên:          64              │
│  📄 Hợp đồng:           64              │
│  📅 Đơn nghỉ phép:     200+             │
│  💰 Bảng lương:        190+             │
│  📢 Tin tuyển dụng:      5              │
│  📝 Đơn ứng tuyển:      30              │
│  ⭐ Đánh giá:          50+              │
└─────────────────────────────────────────┘
```

### Tài khoản đăng nhập:

**Admin (superuser)**:

- Username: `admin`
- Password: (của bạn)
- URL: http://localhost:8000/admin/

**Nhân viên mẫu** (tất cả đều có):

- Password: `123456`
- Ví dụ username: xem trong admin panel hoặc output console

---

## 🎉 CHÚC MỪNG!

Bạn đã:

- ✅ Cài đặt PostgreSQL thành công
- ✅ Cấu hình Django với PostgreSQL
- ✅ Tạo database schema
- ✅ Tạo 800+ records dữ liệu mẫu tiếng Việt
- ✅ Hệ thống đã sẵn sàng sử dụng!

---

## 📞 CẦN HỖ TRỢ?

Nếu gặp vấn đề, check:

1. **PostgreSQL logs**: `C:\Program Files\PostgreSQL\15\data\log\`
2. **Django errors**: Terminal output
3. **File .env**: Password có đúng không?

---

**Tạo bởi**: HRM System  
**Ngày**: November 16, 2024  
**Phiên bản**: 1.0
