# Hướng dẫn sử dụng tính năng Login/Logout

## 🎯 Đã hoàn thành

### 1. Tạo trang đăng nhập

- ✅ Sử dụng template AdminLTE từ mẫu giao diện
- ✅ URL: `/login/`
- ✅ Template: `app/templates/login.html`
- ✅ Giao diện đẹp, responsive, chuẩn AdminLTE

### 2. Cấu hình Authentication

- ✅ `LOGIN_URL = '/login/'` - Redirect về trang login khi chưa đăng nhập
- ✅ `LOGIN_REDIRECT_URL = '/'` - Sau khi login xong sẽ về trang chủ
- ✅ `LOGOUT_REDIRECT_URL = '/login/'` - Sau khi logout sẽ về trang login

### 3. Thêm nút Logout vào navbar

- ✅ Dropdown user menu ở góc phải navbar
- ✅ Hiển thị username đang đăng nhập
- ✅ Menu "Hồ sơ" và "Đăng xuất"

### 4. Bảo vệ tất cả các trang

- ✅ 32 views đã có decorator `@login_required`
- ✅ Nếu chưa login sẽ tự động redirect về `/login/`

## 🚀 Cách sử dụng

### Đăng nhập:

1. Truy cập: http://127.0.0.1:8000/login/
2. Nhập username và password
3. Nhấn "Đăng nhập"

### Đăng xuất:

1. Click vào icon user ở góc phải navbar
2. Chọn "Đăng xuất"
3. Hoặc truy cập trực tiếp: http://127.0.0.1:8000/logout/

### Test trang login:

- Truy cập: http://127.0.0.1:8000/test-login/
- Trang này sẽ hiển thị thông tin user đang login
- Có nút logout để test

## 📝 Tài khoản mặc định

Nếu chưa có tài khoản, tạo superuser:

```bash
python manage.py createsuperuser
```

Hoặc sử dụng tài khoản admin có sẵn trong database.

## 🔒 Bảo mật

- ✅ Tất cả views quan trọng đã được bảo vệ bằng `@login_required`
- ✅ CSRF token được thêm vào form login
- ✅ Session-based authentication của Django
- ✅ Password được hash an toàn

## 🎨 Giao diện

- ✅ Sử dụng template AdminLTE từ thư mục `Template Front-End`
- ✅ Responsive, hiển thị đẹp trên mọi thiết bị
- ✅ Icon Font Awesome
- ✅ Bootstrap 4
- ✅ Checkbox "Ghi nhớ đăng nhập"

## ✨ Features

1. **Login Page:**

   - Form đăng nhập đẹp mắt
   - Validation input
   - Hiển thị lỗi khi sai username/password
   - Checkbox remember me

2. **Navbar User Menu:**

   - Hiển thị username
   - Link đến trang hồ sơ (có thể implement sau)
   - Nút đăng xuất

3. **Protected Views:**
   - Tất cả trang quan trọng yêu cầu login
   - Auto redirect về login nếu chưa đăng nhập
   - Sau khi login sẽ quay lại trang ban đầu

## 🔧 Files đã tạo/chỉnh sửa

1. `app/urls.py` - Routes cho login/logout/test
2. `app/templates/login.html` - Template trang login
3. `app/templates/test_login.html` - Trang test login
4. `app/templates/hod_template/notification_template.html` - Thêm user menu
5. `hrm/settings.py` - Cấu hình LOGIN_URL, LOGIN_REDIRECT_URL
6. `hrm/urls.py` - Include app.urls

## 🎉 Demo

### Khi chưa login:

1. Truy cập bất kỳ trang nào → Redirect về `/login/`
2. Ví dụ: http://127.0.0.1:8000/employee_list → http://127.0.0.1:8000/login/?next=/employee_list

### Khi đã login:

1. Thấy username ở navbar
2. Có thể truy cập tất cả các trang
3. Click "Đăng xuất" để logout

### Test:

1. Logout: http://127.0.0.1:8000/logout/
2. Login lại: http://127.0.0.1:8000/login/
3. Test page: http://127.0.0.1:8000/test-login/

---

**Hoàn thành!** Hệ thống login/logout đã sẵn sàng sử dụng với giao diện AdminLTE đẹp mắt! 🎊
