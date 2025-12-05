# 📚 Hướng Dẫn Tạo Dữ Liệu Mẫu Tiếng Việt

## 🎯 Mục Đích

Script `create_vietnamese_sample_data.py` tạo dữ liệu mẫu hoàn chỉnh bằng tiếng Việt cho hệ thống HRM, bao gồm:

- ✅ **8 Phòng ban** với mô tả chi tiết
- ✅ **64 Nhân viên** với tên người Việt thực tế
- ✅ **64 Hợp đồng** lao động
- ✅ **200+ Đơn nghỉ phép** với lý do cụ thể
- ✅ **190+ Bảng lương** cho 3 tháng gần nhất
- ✅ **5 Tin tuyển dụng** đang mở
- ✅ **30 Đơn ứng tuyển** từ ứng viên
- ✅ **Đánh giá nhân viên** định kỳ

---

## 🚀 Cách Sử Dụng

### Bước 1: Backup Dữ Liệu Cũ (Nếu Cần)

```powershell
# Backup SQLite
python backup_sqlite_data.py

# Hoặc copy file
Copy-Item db.sqlite3 db.sqlite3.backup
```

### Bước 2: Chạy Script Tạo Dữ Liệu

```powershell
# Kích hoạt virtual environment
.\.venv\Scripts\Activate.ps1

# Chạy script
python create_vietnamese_sample_data.py
```

### Bước 3: Xác Nhận

Script sẽ hỏi xác nhận:

```
⚠️  CẢNH BÁO: Script này sẽ XÓA TẤT CẢ dữ liệu hiện có!
✋ Bạn có chắc chắn muốn tiếp tục? (yes/no):
```

Gõ `yes` và nhấn Enter.

### Bước 4: Chờ Hoàn Thành

Script sẽ tự động:

1. Xóa dữ liệu cũ (giữ lại superuser)
2. Tạo nhóm quyền
3. Tạo phòng ban
4. Tạo chức vụ
5. Tạo nhân viên với tên tiếng Việt
6. Tạo hợp đồng
7. Tạo đơn nghỉ phép
8. Tạo bảng lương
9. Tạo tin tuyển dụng
10. Tạo đơn ứng tuyển
11. Tạo đánh giá

**Thời gian**: ~30-60 giây

---

## 📊 Dữ Liệu Được Tạo

### 1. Phòng Ban (8 phòng)

| Tên Phòng Ban             | Mã  | Mô Tả                  |
| ------------------------- | --- | ---------------------- |
| Ban Giám Đốc              | BGD | Ban lãnh đạo công ty   |
| Phòng Nhân Sự             | HR  | Quản lý nguồn nhân lực |
| Phòng Kế Toán             | KT  | Quản lý tài chính      |
| Phòng Công Nghệ Thông Tin | IT  | Phát triển hệ thống    |
| Phòng Marketing           | MKT | Xây dựng thương hiệu   |
| Phòng Kinh Doanh          | KD  | Phát triển thị trường  |
| Phòng Hành Chính          | HC  | Quản lý hành chính     |
| Phòng Sản Xuất            | SX  | Điều hành sản xuất     |

### 2. Chức Vụ (8 chức vụ)

- Tổng Giám Đốc
- Phó Giám Đốc
- Trưởng Phòng
- Phó Phòng
- Trưởng Nhóm
- Nhân Viên Chính
- Nhân Viên
- Thực Tập Sinh

### 3. Nhân Viên (64 người)

**Phân bổ theo phòng ban**:

- Ban Giám Đốc: 3 người
- Phòng Nhân Sự: 6 người
- Phòng Kế Toán: 5 người
- Phòng IT: 12 người
- Phòng Marketing: 8 người
- Phòng Kinh Doanh: 10 người
- Phòng Hành Chính: 5 người
- Phòng Sản Xuất: 15 người

**Đặc điểm**:

- ✅ Tên người Việt Nam thực tế (không có "Nguyễn Văn A")
- ✅ Email công ty theo tên
- ✅ Số điện thoại Việt Nam (090, 091, 093, 094...)
- ✅ Địa chỉ tại TP.HCM
- ✅ Ngày sinh (22-41 tuổi)
- ✅ Ngày vào làm (1 tháng - 5 năm)
- ✅ Lương (8-50 triệu)

**Ví dụ tên**:

- Nguyễn Đức Hùng
- Trần Thu Linh
- Lê Minh Tuấn
- Phạm Hồng Hà
- Hoàng Quang Khoa

### 4. Hợp Đồng (64 hợp đồng)

**Loại hợp đồng**:

- Thử việc (2 tháng) - cho thực tập sinh
- Xác định thời hạn (1-2 năm) - cho nhân viên mới
- Không xác định thời hạn - cho nhân viên lâu năm

**Trạng thái**:

- Active: Đang hiệu lực
- Expired: Đã hết hạn (cần gia hạn)

### 5. Đơn Nghỉ Phép (200+ đơn)

**Loại nghỉ**:

- Nghỉ phép năm
- Nghỉ ốm
- Nghỉ việc riêng
- Nghỉ không lương

**Trạng thái**:

- Pending: Chờ duyệt
- Approved: Đã duyệt
- Rejected: Từ chối

**Lý do cụ thể** (tiếng Việt):

- "Về quê thăm gia đình"
- "Bị cảm sốt, cần nghỉ ngơi"
- "Đưa con đi khám bác sĩ"
- "Tham dự đám cưới người thân"

### 6. Bảng Lương (190+ bảng)

**Thành phần lương**:

- Lương cơ bản: Theo hợp đồng
- Phụ cấp ăn trưa: 730,000 VNĐ
- Phụ cấp xăng xe: 500,000 VNĐ
- Phụ cấp điện thoại: 300,000 VNĐ (quản lý)
- Thưởng hiệu suất: 10-30% lương (ngẫu nhiên)
- Làm thêm giờ: x1.5 lương giờ

**Khấu trừ**:

- Bảo hiểm: 10.5% lương cơ bản
- Thuế TNCN: Theo bậc thuế
- Tạm ứng: Ngẫu nhiên

**3 tháng gần nhất**:

- Tháng hiện tại: Pending
- 2 tháng trước: Paid

### 7. Tin Tuyển Dụng (5 vị trí)

1. **Lập Trình Viên Backend Python/Django**

   - Phòng IT
   - Lương: 15-25 triệu
   - 2 vị trí

2. **Nhân Viên Marketing Digital**

   - Phòng Marketing
   - Lương: 10-15 triệu
   - 1 vị trí

3. **Kế Toán Tổng Hợp**

   - Phòng Kế Toán
   - Lương: 12-18 triệu
   - 1 vị trí

4. **Nhân Viên Kinh Doanh B2B**

   - Phòng Kinh Doanh
   - Lương: 8-12 triệu + hoa hồng
   - 3 vị trí

5. **Thực Tập Sinh Nhân Sự**
   - Phòng Nhân Sự
   - Trợ cấp: 3-4 triệu
   - 2 vị trí

### 8. Đơn Ứng Tuyển (30 đơn)

**Trạng thái**:

- Pending: Mới nộp
- Reviewed: Đã xem xét
- Interviewed: Đã phỏng vấn
- Approved: Đạt
- Rejected: Không đạt

**Thông tin ứng viên**:

- Tên người Việt thực tế
- Email và SĐT
- CV file path
- Thư xin việc bằng tiếng Việt

### 9. Đánh Giá Nhân Viên

**Chu kỳ**:

- 6 tháng (tháng 6)
- Cuối năm (tháng 12)

**Tiêu chí đánh giá** (thang điểm 1-5):

- Hiệu suất công việc
- Thái độ làm việc
- Làm việc nhóm

**Nhận xét bằng tiếng Việt**:

- "Xuất sắc, vượt kỳ vọng..."
- "Tốt, đáp ứng yêu cầu công việc..."
- "Cần cải thiện thái độ làm việc..."

---

## 🔑 Thông Tin Đăng Nhập

### Mật Khẩu Mặc Định

**Tất cả tài khoản**: `123456`

### Tài Khoản Mẫu

Script sẽ hiển thị 5 tài khoản mẫu sau khi chạy xong:

```
👤 Nguyễn Đức Hùng
   Username: hungnguyen
   Email: hungnguyen@gmail.com
   Phòng ban: Phòng Công Nghệ Thông Tin
   Chức vụ: Trưởng Phòng

👤 Trần Thu Linh
   Username: linhtran
   Email: linh.tran@company.vn
   Phòng ban: Phòng Nhân Sự
   Chức vụ: Trưởng Phòng
```

### Đăng Nhập Admin

Nếu bạn đã có tài khoản superuser, nó sẽ được giữ lại:

```
Username: admin
Password: (mật khẩu bạn đã đặt)
```

---

## 📝 Lưu Ý Quan Trọng

### 1. Script Sẽ Xóa Dữ Liệu Cũ

⚠️ **CẢNH BÁO**: Script này xóa **TẤT CẢ** dữ liệu hiện có, ngoại trừ:

- Tài khoản superuser
- Groups và Permissions (sẽ được tạo lại)

### 2. Backup Trước Khi Chạy

```powershell
# Backup SQLite
Copy-Item db.sqlite3 db.sqlite3.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')

# Hoặc sử dụng script backup
python backup_sqlite_data.py
```

### 3. Chạy Trên Môi Trường Development

Chỉ chạy script này trên môi trường development, **KHÔNG BAO GIỜ** chạy trên production!

### 4. Dữ Liệu Ngẫu Nhiên

Mỗi lần chạy script sẽ tạo dữ liệu khác nhau vì:

- Tên nhân viên được random
- Số điện thoại random
- Email random
- Lương, thưởng, OT random
- Trạng thái đơn nghỉ phép random

---

## 🧪 Kiểm Tra Sau Khi Tạo Dữ Liệu

### 1. Khởi động server

```powershell
python manage.py runserver
```

### 2. Truy cập Admin Panel

URL: http://localhost:8000/admin/

Đăng nhập bằng:

- Superuser của bạn
- Hoặc tài khoản mẫu với password: `123456`

### 3. Kiểm tra các module

- ✅ Phòng ban: Xem danh sách 8 phòng
- ✅ Nhân viên: Xem 64 nhân viên với tên tiếng Việt
- ✅ Hợp đồng: Kiểm tra trạng thái active/expired
- ✅ Đơn nghỉ phép: Xem các đơn pending/approved/rejected
- ✅ Bảng lương: Kiểm tra lương tháng hiện tại
- ✅ Tuyển dụng: Xem 5 tin tuyển dụng
- ✅ Đơn ứng tuyển: Xem 30 đơn với các trạng thái khác nhau
- ✅ Đánh giá: Xem đánh giá của nhân viên

### 4. Test chức năng

- Login với các tài khoản khác nhau
- Xem thông tin cá nhân
- Tạo đơn nghỉ phép mới
- Duyệt đơn nghỉ phép (với tài khoản manager)
- Xem bảng lương
- Ứng tuyển công việc

---

## 🔧 Tùy Chỉnh Dữ Liệu

### Thay Đổi Số Lượng

Mở file `create_vietnamese_sample_data.py` và sửa:

```python
# Số nhân viên mỗi phòng
employee_distribution = {
    'Ban Giám Đốc': 3,        # Thay đổi số này
    'Phòng Nhân Sự': 6,
    'Phòng IT': 12,           # Thay đổi số này
    # ...
}

# Số đơn nghỉ phép mỗi nhân viên
num_requests = random.randint(2, 5)  # Thay đổi range

# Số đơn ứng tuyển
applications = create_applications(jobs, count=30)  # Thay đổi count
```

### Thêm Tên Mới

```python
# Thêm họ
VIETNAMESE_SURNAMES.append('Cao')

# Thêm tên nam
MALE_FIRST_NAMES.append('Đạt')

# Thêm tên nữ
FEMALE_FIRST_NAMES.append('Ngân')
```

### Thêm Địa Chỉ

```python
VIETNAM_ADDRESSES.append(
    'Số 999, Đường Lê Văn Việt, Quận 9, TP.HCM'
)
```

---

## 🆘 Xử Lý Lỗi

### Lỗi: "No module named 'django'"

```powershell
# Kích hoạt virtual environment
.\.venv\Scripts\Activate.ps1

# Cài Django
pip install -r requirements.txt
```

### Lỗi: "DJANGO_SETTINGS_MODULE not set"

```powershell
# Chạy từ thư mục gốc project (có manage.py)
cd D:\Study\CT201\Project\hrm
python create_vietnamese_sample_data.py
```

### Lỗi: "Database is locked"

```powershell
# Đóng tất cả connection đến database
# Tắt server Django nếu đang chạy
# Chạy lại script
```

### Lỗi: Foreign Key Constraint

Script đã xử lý đúng thứ tự tạo dữ liệu. Nếu vẫn lỗi:

1. Xóa hoàn toàn database: `del db.sqlite3`
2. Chạy migrations: `python manage.py migrate`
3. Tạo superuser: `python manage.py createsuperuser`
4. Chạy lại script

---

## 📊 Thống Kê Dữ Liệu

Sau khi chạy xong, script sẽ hiển thị:

```
==================================================================
              HOÀN THÀNH TẠO DỮ LIỆU MẪU
==================================================================

✅ Phòng ban:           8
✅ Chức vụ:            8
✅ Nhân viên:          64
✅ Hợp đồng:           64
✅ Đơn nghỉ phép:      200+
✅ Thành phần lương:   12
✅ Bảng lương:         190+
✅ Tin tuyển dụng:     5
✅ Đơn ứng tuyển:      30
✅ Đánh giá:           50+
```

---

## 🎯 Kịch Bản Sử Dụng

### 1. Demo cho khách hàng

- Tạo dữ liệu mẫu tiếng Việt chuyên nghiệp
- Khách hàng dễ hiểu và liên tưởng

### 2. Testing

- Test các chức năng với dữ liệu thực tế
- Test performance với 64 nhân viên
- Test reports và analytics

### 3. Development

- Phát triển tính năng mới với dữ liệu có sẵn
- Không cần tạo dữ liệu thủ công

### 4. Training

- Đào tạo nhân viên sử dụng hệ thống
- Dữ liệu mẫu dễ hiểu, gần gũi

---

## 💡 Tips & Tricks

### 1. Backup Trước Khi Test

```powershell
# Tạo backup nhanh
Copy-Item db.sqlite3 db_backup.sqlite3

# Test tính năng mới...

# Khôi phục nếu cần
Copy-Item db_backup.sqlite3 db.sqlite3
```

### 2. Tạo Dữ Liệu Nhiều Lần

Script có thể chạy nhiều lần:

```powershell
# Lần 1: Development
python create_vietnamese_sample_data.py

# Lần 2: Demo
python create_vietnamese_sample_data.py

# Mỗi lần sẽ có dữ liệu khác nhau
```

### 3. Kết Hợp Với Migration

```powershell
# 1. Reset database
del db.sqlite3

# 2. Chạy migrations
python manage.py migrate

# 3. Tạo superuser
python manage.py createsuperuser

# 4. Tạo dữ liệu mẫu
python create_vietnamese_sample_data.py

# 5. Chạy server
python manage.py runserver
```

---

## 📚 Tài Nguyên Liên Quan

- **Script chính**: `create_vietnamese_sample_data.py`
- **Backup script**: `backup_sqlite_data.py`
- **Migration guide**: `POSTGRESQL_QUICK_START.md`

---

**Tạo bởi**: HRM System Development Team  
**Cập nhật**: November 16, 2024  
**Phiên bản**: 1.0  
**Trạng thái**: ✅ Sẵn sàng sử dụng
