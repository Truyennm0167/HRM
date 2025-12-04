# HRM Seed Data

Thư mục này chứa các script tạo dữ liệu mẫu cho hệ thống HRM.

## Cấu trúc files

| File                                 | Mô tả                               | Phụ thuộc        |
| ------------------------------------ | ----------------------------------- | ---------------- |
| `base.py`                            | Cấu hình chung, helper functions    | -                |
| `seed_01_departments.py`             | Chức danh, Phòng ban                | -                |
| `seed_02_employees.py`               | Nhân viên (40 người)                | seed_01          |
| `seed_03_leaves.py`                  | Loại nghỉ phép, Số dư, Đơn xin nghỉ | seed_02          |
| `seed_04_expenses.py`                | Danh mục chi phí, Yêu cầu hoàn tiền | seed_02          |
| `seed_05_attendance_payroll.py`      | Chấm công, Bảng lương (3 tháng)     | seed_02          |
| `seed_06_rewards_disciplines.py`     | Khen thưởng, Kỷ luật, Đánh giá      | seed_02          |
| `seed_07_recruitment.py`             | Tin tuyển dụng, Đơn ứng tuyển       | seed_01, seed_02 |
| `seed_08_contracts_settings.py`      | Hợp đồng, System Settings           | seed_02          |
| `seed_09_appraisals.py`              | Kỳ đánh giá, Tiêu chí, Đánh giá     | seed_02          |
| `seed_10_documents_announcements.py` | Tài liệu, Thông báo                 | seed_02          |

## Cách chạy

### Chạy từng file riêng lẻ

```bash
# Cách 1: Dùng Django shell
python manage.py shell < seed/seed_01_departments.py

# Cách 2: Chạy trực tiếp
python seed/seed_01_departments.py
```

### Chạy tất cả

```bash
python seed/run_all.py
```

## Thứ tự chạy

**BẮT BUỘC** chạy theo thứ tự từ 01 đến 10, vì các file sau phụ thuộc vào dữ liệu của file trước.

```
seed_01 → seed_02 → seed_03 → seed_04 → seed_05 → seed_06 → seed_07 → seed_08 → seed_09 → seed_10
```

## Dữ liệu tạo ra

Sau khi chạy đầy đủ, hệ thống sẽ có:

- **8 Chức danh**: Từ Giám đốc đến Thực tập sinh
- **8 Phòng ban**: Ban GĐ, HR, Kế toán, IT, Kinh doanh, Marketing, Hành chính, CSKH
- **40 Nhân viên**: Đầy đủ thông tin cá nhân, hợp đồng
- **6 Loại nghỉ phép**: Phép năm, Nghỉ ốm, Thai sản, v.v.
- **~100+ Đơn xin nghỉ**: Các trạng thái khác nhau
- **6 Danh mục chi phí**: Đi lại, Ăn uống, Khách sạn, v.v.
- **~150+ Yêu cầu hoàn tiền**: Các trạng thái khác nhau
- **~4000+ Bản ghi chấm công**: 3 tháng gần nhất
- **~120 Bảng lương**: 3 tháng cho tất cả nhân viên
- **15+ Khen thưởng**: Với mô tả chi tiết
- **5 Kỷ luật**: Các vi phạm thực tế
- **6 Tin tuyển dụng**: Các vị trí khác nhau
- **20+ Đơn ứng tuyển**: Các trạng thái khác nhau
- **40 Hợp đồng lao động**: Cho tất cả nhân viên
- **2 Kỳ đánh giá**: Giữa năm và cuối năm
- **16 Tiêu chí đánh giá**: 8 tiêu chí x 2 kỳ
- **~60+ Đánh giá nhân viên**: Với điểm chi tiết
- **5 Danh mục tài liệu**: Chính sách, Biểu mẫu, Hướng dẫn, v.v.
- **14 Tài liệu**: Các loại khác nhau
- **6 Thông báo**: Team building, Nghỉ lễ, Chính sách, v.v.
- **System Settings**: Cấu hình đầy đủ

## Lưu ý

1. **Xóa dữ liệu cũ**: Mỗi seed file sẽ xóa dữ liệu cũ của model tương ứng trước khi tạo mới
2. **Dữ liệu ngẫu nhiên**: Tên, CCCD, SĐT được tạo ngẫu nhiên nhưng đảm bảo duy nhất
3. **Thời gian**: Dữ liệu được tạo dựa trên năm 2025
4. **Encoding**: Hỗ trợ đầy đủ tiếng Việt Unicode
