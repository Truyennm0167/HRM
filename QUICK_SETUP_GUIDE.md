# 🎯 HƯỚNG DẪN NHANH: Setup PostgreSQL + Data Tiếng Việt

## ⚡ TÓM TẮT 5 PHÚT

Bạn đã cài PostgreSQL ✅. Bây giờ chỉ cần 5 bước:

### BƯỚC 1: Tạo Database trong PostgreSQL

**Cách 1 - Dùng pgAdmin (Dễ nhất)**:

```
1. Mở pgAdmin 4
2. Right-click "Databases" → Create → Database
3. Name: hrm_db
4. Click Save
```

**Cách 2 - Dùng Command Line**:

```powershell
psql -U postgres
CREATE DATABASE hrm_db;
\q
```

### BƯỚC 2: Edit File .env

Mở file `.env` (đã tạo sẵn) và sửa dòng:

```
POSTGRES_PASSWORD=YOUR_POSTGRESQL_PASSWORD_HERE
```

Thay bằng password PostgreSQL của bạn, ví dụ:

```
POSTGRES_PASSWORD=postgres123
```

### BƯỚC 3: Chạy Script Tự Động

```powershell
# Kích hoạt virtual environment
.\.venv\Scripts\Activate.ps1

# Chạy script setup tự động
python quick_setup_postgresql.py
```

Script sẽ tự động:

- ✅ Cài packages (psycopg2, python-dotenv)
- ✅ Test kết nối PostgreSQL
- ✅ Tạo tables (migrations)
- ✅ Kiểm tra superuser

### BƯỚC 4: Tạo Superuser (Nếu Chưa Có)

Nếu script báo chưa có superuser:

```powershell
python manage.py createsuperuser

# Nhập:
Username: admin
Email: admin@hrm.local
Password: (gõ password của bạn)
```

Sau đó chạy lại:

```powershell
python quick_setup_postgresql.py
```

### BƯỚC 5: Hoàn Thành!

Khi script hỏi xác nhận tạo data, gõ `yes`:

```
✋ Tiếp tục? (yes/no): yes
```

Data mẫu sẽ được tạo tự động (30-60 giây).

---

## 🚀 KHỞI ĐỘNG SERVER

```powershell
python manage.py runserver
```

Truy cập:

- **Admin**: http://localhost:8000/admin/
- **Login**: Dùng superuser hoặc nhân viên (password: 123456)

---

## 📊 DATA ĐÃ TẠO

- ✅ 8 Phòng ban
- ✅ 64 Nhân viên (tên tiếng Việt thực tế)
- ✅ 64 Hợp đồng
- ✅ 200+ Đơn nghỉ phép
- ✅ 190+ Bảng lương
- ✅ 5 Tin tuyển dụng
- ✅ 30 Đơn ứng tuyển

---

## 🐛 NẾU GẶP LỖI

### Lỗi: "could not connect to server"

```powershell
# Check service
Get-Service postgresql*

# Start service
Start-Service postgresql-x64-15
```

### Lỗi: "password authentication failed"

- Kiểm tra password trong `.env` có đúng không
- Thử đăng nhập psql xem password có work không

### Lỗi: "database does not exist"

```powershell
psql -U postgres -c "CREATE DATABASE hrm_db;"
```

---

## 📞 CẦN SETUP THỦ CÔNG?

Xem hướng dẫn chi tiết tại: `SETUP_POSTGRESQL_WITH_SAMPLE_DATA.md`

---

**Cập nhật**: November 16, 2024  
**Thời gian setup**: ~5 phút  
**Data**: Tiếng Việt 🇻🇳
