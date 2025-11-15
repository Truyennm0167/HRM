# EXPENSE MANAGEMENT MODULE - HƯỚNG DẪN SỬ DỤNG

## 📋 TỔNG QUAN

Module Quản Lý Chi Phí (Expense Management) cho phép nhân viên gửi yêu cầu hoàn ứng chi phí, quản lý duyệt và theo dõi thanh toán.

**Thời gian hoàn thành:** [Date]
**Phiên bản:** 1.0
**Trạng thái:** ✅ Hoàn thành và đã test

---

## 🏗️ CẤU TRÚC MODULE

### 1. Models (app/models.py)

#### ExpenseCategory - Danh Mục Chi Phí

```python
- name: Tên danh mục (VD: "Đi lại", "Ăn uống")
- code: Mã danh mục (VD: "TRAVEL", "MEAL")
- description: Mô tả chi tiết
- is_active: Trạng thái kích hoạt (Boolean)
```

**Danh mục mặc định:**

1. TRAVEL - Đi lại (taxi, xăng xe, vé máy bay)
2. MEAL - Ăn uống (ăn uống công tác, tiếp khách)
3. HOTEL - Khách sạn (thuê khách sạn công tác)
4. OFFICE - Văn phòng phẩm (văn phòng phẩm, thiết bị)
5. TRAINING - Đào tạo (khóa học, hội thảo)
6. PHONE - Điện thoại (cước điện thoại, data)
7. INTERNET - Internet (internet, cloud, domain)
8. MARKETING - Marketing (quảng cáo, PR)
9. EVENT - Sự kiện (tổ chức sự kiện, team building)
10. OTHER - Khác

#### Expense - Yêu Cầu Chi Phí

```python
- employee: Nhân viên tạo yêu cầu (ForeignKey)
- category: Danh mục chi phí (ForeignKey)
- amount: Số tiền (DecimalField, max 12 chữ số)
- date: Ngày phát sinh chi phí
- description: Mô tả chi tiết (TextField)
- receipt: Hóa đơn/biên lai (ImageField, upload to 'receipts/')
- status: Trạng thái
  * pending: Chờ duyệt (mặc định)
  * approved: Đã duyệt
  * rejected: Từ chối
  * paid: Đã thanh toán
  * cancelled: Đã hủy
- approved_by: Người duyệt (ForeignKey Employee, nullable)
- approved_at: Thời gian duyệt (DateTimeField, nullable)
- paid_by: Người thanh toán (ForeignKey Employee, nullable)
- paid_at: Thời gian thanh toán (DateTimeField, nullable)
- created_at: Thời gian tạo (auto_now_add)
- updated_at: Thời gian cập nhật (auto_now)
```

**Workflow trạng thái:**

```
pending → approved → paid
    ↓         ↓
cancelled  rejected
```

---

### 2. Forms (app/forms.py)

#### ExpenseCategoryForm

```python
Fields: name, code, description, is_active
Widgets: TextInput, Textarea, CheckboxInput
```

#### ExpenseForm

```python
Fields: category, amount, date, description, receipt
Validation:
- clean_amount(): Số tiền > 0
- clean_date(): Ngày không được trong tương lai
Widgets:
- category: Select (class='form-control')
- amount: NumberInput (class='form-control')
- date: DateInput (type='date', class='form-control')
- description: Textarea (rows=4, class='form-control')
- receipt: FileInput (class='form-control-file')
```

---

### 3. Views (app/HodViews.py)

#### 3.1. Quản Lý Danh Mục Chi Phí

**manage_expense_categories** - Trang quản lý danh mục

- URL: `/expense/categories/`
- Template: `manage_expense_categories.html`
- Permission: @login_required
- Context: categories (tất cả danh mục), form (ExpenseCategoryForm)

**add_expense_category_save** - Thêm danh mục mới

- URL: `/expense/category/add/`
- Method: POST
- Redirect: manage_expense_categories

**edit_expense_category_save** - Sửa danh mục

- URL: `/expense/category/edit/`
- Method: POST
- Redirect: manage_expense_categories

**delete_expense_category** - Xóa danh mục

- URL: `/expense/category/delete/<category_id>/`
- Method: POST
- Validation: Không cho xóa danh mục đang được sử dụng
- Redirect: manage_expense_categories

#### 3.2. Yêu Cầu Chi Phí (Employee)

**create_expense** - Tạo yêu cầu chi phí

- URL: `/expense/create/`
- Methods: GET, POST
- Template: `create_expense.html`
- Features:
  - Form upload hóa đơn/biên lai
  - Preview ảnh trước khi upload
  - Validate số tiền và ngày
- Redirect: expense_history (sau khi tạo thành công)

**expense_history** - Lịch sử chi phí của nhân viên

- URL: `/expense/history/`
- Template: `expense_history.html`
- Features:
  - Hiển thị tất cả yêu cầu của nhân viên
  - Phân trang (10 items/page)
  - Thống kê: tổng chi phí, đã duyệt, đã thanh toán, chờ duyệt
  - Hủy yêu cầu đang chờ duyệt
- Context:
  - expenses: QuerySet phân trang
  - total_expenses, approved_expenses, paid_expenses, pending_expenses

**cancel_expense** - Hủy yêu cầu chi phí

- URL: `/expense/cancel/<expense_id>/`
- Method: POST
- Permission: Chỉ nhân viên tạo yêu cầu mới hủy được
- Validation: Chỉ hủy được yêu cầu status='pending'
- Redirect: expense_history

#### 3.3. Quản Lý Chi Phí (HR/Manager)

**manage_expenses** - Quản lý tất cả yêu cầu chi phí

- URL: `/expense/manage/`
- Template: `manage_expenses.html`
- Features:
  - Bộ lọc: status, employee, category, from_date, to_date
  - Phân trang (10 items/page)
  - Thống kê: tổng số tiền, số lượng theo trạng thái
  - Duyệt/từ chối/thanh toán
- Context:
  - expenses: QuerySet đã lọc và phân trang
  - employees, categories: danh sách để filter
  - total_amount, pending_count, approved_count, paid_count

**view_expense** - Xem chi tiết yêu cầu chi phí

- URL: `/expense/view/<expense_id>/`
- Template: `view_expense.html`
- Features:
  - Hiển thị đầy đủ thông tin
  - Timeline theo dõi workflow
  - Lightbox xem ảnh hóa đơn
  - Nút duyệt/từ chối/thanh toán

**approve_expense** - Duyệt yêu cầu chi phí

- URL: `/expense/approve/<expense_id>/`
- Method: POST
- Validation: Chỉ duyệt được yêu cầu status='pending'
- Updates:
  - status → 'approved'
  - approved_by → current employee
  - approved_at → now()
- Redirect: manage_expenses

**reject_expense** - Từ chối yêu cầu chi phí

- URL: `/expense/reject/<expense_id>/`
- Method: POST
- Validation: Chỉ từ chối được yêu cầu status='pending'
- Input: rejection_reason (textarea, required)
- Updates:
  - status → 'rejected'
  - approved_by → current employee
  - approved_at → now()
  - description += rejection_reason
- Redirect: manage_expenses

**mark_expense_as_paid** - Đánh dấu đã thanh toán (Accounting)

- URL: `/expense/mark-paid/<expense_id>/`
- Method: POST
- Validation: Chỉ thanh toán được yêu cầu status='approved'
- Updates:
  - status → 'paid'
  - paid_by → current employee
  - paid_at → now()
- Redirect: manage_expenses

---

### 4. Templates (app/templates/hod_template/)

#### 4.1. manage_expense_categories.html

**Layout:**

- Left Panel: Form thêm danh mục mới
- Right Panel: Bảng danh sách danh mục
- Modals: Edit category, Delete confirmation

**Features:**

- Inline editing với modal
- Status badge (Đang dùng/Vô hiệu)
- CRUD đầy đủ

#### 4.2. create_expense.html

**Layout:**

- Left Panel: Hướng dẫn và lưu ý
- Right Panel: Form tạo yêu cầu

**Features:**

- Upload ảnh hóa đơn với preview
- Format số tiền tự động
- DatePicker cho ngày phát sinh
- Validation client-side

#### 4.3. expense_history.html

**Layout:**

- Top: 4 statistic boxes (Tổng, Chờ duyệt, Đã duyệt, Đã thanh toán)
- Main: Bảng danh sách chi phí
- Modal: Xác nhận hủy

**Features:**

- Phân trang
- Status badges với màu sắc
- Nút "Tạo yêu cầu mới" nổi bật
- Nút hủy cho yêu cầu pending

#### 4.4. manage_expenses.html

**Layout:**

- Top: 4 statistic boxes
- Filter Panel: Bộ lọc có thể collapse
- Main: Bảng danh sách với actions
- Modals: Approve, Reject (với input lý do), Mark as Paid

**Features:**

- Filter theo: status, employee, category, date range
- Phân trang với query string preservation
- 3 loại action button theo status:
  - pending: Approve + Reject
  - approved: Mark as Paid
- Icon xem hóa đơn

#### 4.5. view_expense.html

**Layout:**

- Left Panel: Thông tin chi tiết (bảng)
- Right Panel:
  - Receipt image với lightbox
  - Timeline workflow

**Features:**

- Timeline hiển thị lịch sử duyệt/thanh toán
- Lightbox (ekko-lightbox) để xem ảnh phóng to
- Action buttons theo status
- Download hóa đơn

---

### 5. URLs (hrm/urls.py)

```python
# Expense Management URLs (12 routes)
path('expense/categories/', HodViews.manage_expense_categories, name='manage_expense_categories'),
path('expense/category/add/', HodViews.add_expense_category_save, name='add_expense_category_save'),
path('expense/category/edit/', HodViews.edit_expense_category_save, name='edit_expense_category_save'),
path('expense/category/delete/<int:category_id>/', HodViews.delete_expense_category, name='delete_expense_category'),
path('expense/create/', HodViews.create_expense, name='create_expense'),
path('expense/history/', HodViews.expense_history, name='expense_history'),
path('expense/manage/', HodViews.manage_expenses, name='manage_expenses'),
path('expense/view/<int:expense_id>/', HodViews.view_expense, name='view_expense'),
path('expense/approve/<int:expense_id>/', HodViews.approve_expense, name='approve_expense'),
path('expense/reject/<int:expense_id>/', HodViews.reject_expense, name='reject_expense'),
path('expense/mark-paid/<int:expense_id>/', HodViews.mark_expense_as_paid, name='mark_expense_as_paid'),
path('expense/cancel/<int:expense_id>/', HodViews.cancel_expense, name='cancel_expense'),
```

---

### 6. Sidebar Navigation (sidebar_template.html)

```html
<!-- Chi phí -->
<li class="nav-item has-treeview">
  <a href="#" class="nav-link">
    <i class="nav-icon fas fa-wallet"></i>
    <p>Quản lý chi phí <i class="right fas fa-angle-left"></i></p>
  </a>
  <ul class="nav nav-treeview">
    <li class="nav-item">
      <a href="{% url 'create_expense' %}" class="nav-link">
        <i class="nav-icon fas fa-receipt"></i>
        <p>Tạo yêu cầu chi phí</p>
      </a>
    </li>
    <li class="nav-item">
      <a href="{% url 'expense_history' %}" class="nav-link">
        <i class="nav-icon fas fa-history"></i>
        <p>Lịch sử chi phí</p>
      </a>
    </li>
    <li class="nav-item">
      <a href="{% url 'manage_expenses' %}" class="nav-link">
        <i class="nav-icon fas fa-clipboard-check"></i>
        <p>Duyệt chi phí</p>
      </a>
    </li>
    <li class="nav-item">
      <a href="{% url 'manage_expense_categories' %}" class="nav-link">
        <i class="nav-icon fas fa-tags"></i>
        <p>Danh mục chi phí</p>
      </a>
    </li>
  </ul>
</li>
```

---

### 7. Management Command

**init_expense_categories**

```bash
python manage.py init_expense_categories
```

**Kết quả:**

- Tạo 10 danh mục chi phí mặc định
- Không duplicate nếu chạy lại
- Cập nhật thông tin nếu đã tồn tại

---

### 8. Django Admin

**ExpenseCategoryAdmin:**

- list_display: name, code, is_active
- list_filter: is_active
- search_fields: name, code
- ordering: name

**ExpenseAdmin:**

- list_display: employee, category, amount, date, status, created_at
- list_filter: status, category, date
- search_fields: employee\_\_name, description
- date_hierarchy: date
- readonly_fields: created_at, updated_at

---

## 🔄 WORKFLOW SỬ DỤNG

### A. Thiết Lập Ban Đầu (HR/Admin)

1. **Khởi tạo danh mục chi phí:**

   ```bash
   python manage.py init_expense_categories
   ```

2. **Quản lý danh mục:**
   - Truy cập: Quản lý chi phí → Danh mục chi phí
   - Thêm/sửa/xóa danh mục theo nhu cầu doanh nghiệp
   - Vô hiệu hóa danh mục không còn dùng

### B. Quy Trình Nhân Viên

1. **Tạo yêu cầu chi phí:**

   - Click: Quản lý chi phí → Tạo yêu cầu chi phí
   - Chọn danh mục chi phí
   - Nhập số tiền (VND)
   - Chọn ngày phát sinh
   - Mô tả chi tiết mục đích chi phí
   - Upload hóa đơn/biên lai (nếu có)
   - Click "Gửi Yêu Cầu"

2. **Theo dõi yêu cầu:**
   - Click: Quản lý chi phí → Lịch sử chi phí
   - Xem trạng thái: Chờ duyệt / Đã duyệt / Từ chối / Đã thanh toán
   - Hủy yêu cầu đang chờ duyệt (nếu cần)

### C. Quy Trình Manager/HR (Duyệt)

1. **Xem danh sách yêu cầu:**

   - Click: Quản lý chi phí → Duyệt chi phí
   - Sử dụng bộ lọc: status, nhân viên, danh mục, ngày

2. **Duyệt yêu cầu:**
   - Click vào yêu cầu để xem chi tiết
   - Xem hóa đơn đính kèm
   - Click "Duyệt" hoặc "Từ chối"
   - Nếu từ chối: nhập lý do

### D. Quy Trình Kế Toán (Thanh Toán)

1. **Xem chi phí đã duyệt:**

   - Click: Quản lý chi phí → Duyệt chi phí
   - Filter: Trạng thái = "Đã duyệt"

2. **Thanh toán:**
   - Sau khi chuyển tiền cho nhân viên
   - Click "Đánh Dấu Đã Thanh Toán"
   - Xác nhận

---

## 📊 BÁO CÁO VÀ THỐNG KÊ

### Employee Dashboard

- Tổng chi phí (all time)
- Chi phí đang chờ duyệt
- Chi phí đã duyệt (chưa thanh toán)
- Chi phí đã thanh toán

### Manager Dashboard

- Tổng số tiền tất cả yêu cầu
- Số lượng yêu cầu chờ duyệt
- Số lượng đã duyệt
- Số lượng đã thanh toán

### Bộ Lọc

- Theo trạng thái
- Theo nhân viên
- Theo danh mục
- Theo khoảng thời gian

---

## 🔒 PHÂN QUYỀN

### Nhân Viên (Employee)

✅ Tạo yêu cầu chi phí
✅ Xem lịch sử chi phí của mình
✅ Hủy yêu cầu đang chờ duyệt
❌ Xem chi phí của người khác
❌ Duyệt chi phí
❌ Thanh toán

### Quản Lý (Manager/HR)

✅ Tất cả quyền của Nhân viên
✅ Xem tất cả yêu cầu chi phí
✅ Duyệt/từ chối yêu cầu
✅ Quản lý danh mục chi phí
✅ Đánh dấu đã thanh toán (nếu có quyền)

### Kế Toán (Accounting)

✅ Xem tất cả yêu cầu
✅ Đánh dấu đã thanh toán
❌ Duyệt/từ chối (phải do Manager)

---

## 🎨 UI/UX FEATURES

### AdminLTE Components

- Card với header màu sắc theo chức năng
- Small boxes (info boxes) cho statistics
- Badge status với màu:
  - warning: Chờ duyệt (yellow)
  - success: Đã duyệt (green)
  - danger: Từ chối (red)
  - primary: Đã thanh toán (blue)
  - secondary: Đã hủy (gray)

### Interactive Features

- Modal confirmations
- Image preview before upload
- Lightbox for receipt viewing
- Timeline for workflow tracking
- Collapsible filter panel
- Pagination với page info

### Icons (Font Awesome)

- fa-wallet: Module icon
- fa-receipt: Tạo yêu cầu
- fa-history: Lịch sử
- fa-clipboard-check: Duyệt
- fa-tags: Danh mục
- fa-eye: Xem chi tiết
- fa-check: Duyệt
- fa-times: Từ chối/Hủy
- fa-dollar-sign: Thanh toán

---

## 🧪 TESTING CHECKLIST

### ✅ Unit Tests (Models)

- [x] ExpenseCategory: CRUD operations
- [x] Expense: Create với tất cả fields
- [x] Expense: Status workflow transitions
- [x] Expense: ForeignKey relationships

### ✅ Integration Tests (Views)

- [x] create_expense: Tạo yêu cầu thành công
- [x] expense_history: Hiển thị đúng dữ liệu
- [x] manage_expenses: Filter hoạt động
- [x] approve_expense: Chuyển status thành công
- [x] reject_expense: Lưu lý do từ chối
- [x] mark_expense_as_paid: Cập nhật paid_at
- [x] cancel_expense: Chỉ cancel được pending

### ✅ UI Tests

- [x] Upload receipt: Preview hiển thị
- [x] Filter form: Submit giữ nguyên query params
- [x] Pagination: Chuyển trang bình thường
- [x] Modals: Mở/đóng không lỗi
- [x] Timeline: Hiển thị đúng sự kiện

### ✅ Permission Tests

- [x] Employee chỉ xem được chi phí của mình
- [x] Không thể cancel chi phí đã duyệt
- [x] Không thể approve chi phí đã approve
- [x] Không thể mark paid chi phí chưa approve

---

## 🚀 DEPLOYMENT NOTES

### Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files

- Receipt uploads → `media/receipts/`
- Đảm bảo `MEDIA_ROOT` và `MEDIA_URL` đã cấu hình

### Initial Data

```bash
python manage.py init_expense_categories
```

### Permissions Setup

- Tất cả views đã có `@login_required`
- Kiểm tra employee ownership trong views

---

## 📝 MAINTENANCE

### Backup

- Database: Bảng `app_expensecategory`, `app_expense`
- Media files: Folder `media/receipts/`

### Cleanup

- Xóa receipt files của expense đã xóa
- Archive expense cũ hơn 1 năm (optional)

### Monitoring

- Log all approve/reject/payment actions
- Track expense amount trends
- Alert khi có expense lớn

---

## 🔮 FUTURE ENHANCEMENTS

### Phase 2 (Khuyến nghị)

1. **Email Notifications:**

   - Thông báo khi yêu cầu được duyệt/từ chối
   - Nhắc nhở manager về yêu cầu chờ duyệt

2. **Expense Reports:**

   - Export Excel báo cáo chi phí theo tháng
   - Chart thống kê chi phí theo danh mục

3. **Approval Workflow:**

   - Multi-level approval (Manager → Director)
   - Auto-approve cho expense nhỏ hơn threshold

4. **Budget Management:**

   - Thiết lập ngân sách theo phòng ban
   - Cảnh báo vượt ngân sách

5. **Mobile Upload:**
   - API cho mobile app
   - Upload receipt từ điện thoại

---

## 📞 SUPPORT

**Vấn đề thường gặp:**

1. **Upload receipt lỗi:**

   - Kiểm tra file size < 5MB
   - Chỉ chấp nhận JPG, PNG
   - Kiểm tra permission folder `media/receipts/`

2. **Không thấy menu Quản lý chi phí:**

   - Kiểm tra đã login
   - Kiểm tra permission của user

3. **Lỗi khi duyệt chi phí:**
   - Kiểm tra expense status = 'pending'
   - Kiểm tra approved_by không null

**Contact:** [Your Support Email]

---

**© 2024 HR Management System - Expense Management Module**
