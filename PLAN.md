# Kế hoạch Phát triển Chức năng Chấm Công

## 1. Trang Thêm Bảng Chấm Công Mới

### 1.1. Mô tả chức năng
- Cán bộ Nhân sự thực hiện chấm công hàng ngày cho toàn bộ nhân viên của ngày hôm trước
- Hệ thống tự động điền thông tin mặc định cho bảng chấm công mới
- Cho phép cập nhật bảng chấm công nếu ngày được chọn đã tồn tại

### 1.2. Giao diện người dùng
#### a. Form chọn ngày
- Trường chọn ngày (Date Picker)
- Nút "Kiểm tra" để xác định tồn tại bảng chấm công

#### b. Bảng chấm công
- Hiển thị dạng bảng (table) với các cột:
  1. STT
  2. Mã nhân viên (tự động từ Employee)
  3. Tên nhân viên (tự động từ Employee)
  4. Trạng thái (dropdown: Có làm việc/Nghỉ phép/Nghỉ không phép)
  5. Số giờ công
  6. Ghi chú
- Giá trị mặc định:
  - Trạng thái: "Có làm việc"
  - Số giờ công: 8
  - Ghi chú: để trống

#### c. Các nút chức năng
- Lưu bảng chấm công
- Hủy bỏ
- Trở về trang Quản lý bảng chấm công

### 1.3. Xử lý dữ liệu
#### a. Kiểm tra ngày chấm công
- Kiểm tra xem ngày được chọn đã có bảng chấm công chưa
- Nếu có: Hiển thị dữ liệu có sẵn và cho phép cập nhật
- Nếu không: Tạo bảng mới với dữ liệu mặc định

#### b. Validate dữ liệu
- Kiểm tra ngày chấm công không được trong tương lai
- Số giờ công phải là số dương và ≤ 24
- Trạng thái phải được chọn từ danh sách có sẵn

## 2. Trang Quản Lý Bảng Chấm Công

### 2.1. Mô tả chức năng
- Xem tất cả dữ liệu chấm công
- Cập nhật, xóa bảng chấm công
- Thêm bảng chấm công mới

### 2.2. Giao diện người dùng
#### a. Bộ lọc và tìm kiếm
- Lọc theo ngày (từ ngày - đến ngày)
- Lọc theo phòng ban
- Tìm kiếm theo mã/tên nhân viên
- Lọc theo trạng thái chấm công

#### b. Bảng hiển thị dữ liệu
- Hiển thị dạng bảng với các cột:
  1. STT
  2. Ngày chấm công
  3. Mã nhân viên
  4. Tên nhân viên
  5. Phòng ban
  6. Trạng thái
  7. Số giờ công
  8. Ghi chú
  9. Thao tác (Cập nhật/Xóa)

#### c. Các nút chức năng
- Thêm bảng chấm công mới
- Xuất báo cáo (Excel)
- Phân trang

### 2.3. Xử lý dữ liệu
#### a. Hiển thị dữ liệu
- Phân trang (10 bản ghi/trang)
- Sắp xếp theo ngày giảm dần
- Tổng hợp số liệu (tổng số bản ghi, tổng giờ công)

#### b. Cập nhật bảng chấm công
- Chuyển đến giao diện Thêm bảng chấm công
- Hiển thị dữ liệu của ngày được chọn
- Cho phép cập nhật thông tin

#### c. Xóa bảng chấm công
- Hiển thị dialog xác nhận trước khi xóa
- Xóa toàn bộ dữ liệu chấm công của ngày được chọn

### 2.4. Báo cáo
- Xuất file Excel với định dạng:
  - Thông tin công ty
  - Tiêu đề báo cáo
  - Thời gian báo cáo
  - Bảng dữ liệu chấm công
  - Tổng hợp số liệu
