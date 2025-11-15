from django.db import models

class JobTitle(models.Model):
    name = models.CharField(max_length=100)
    salary_coefficient = models.FloatField()
    description = models.TextField(blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    date_establishment = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    GENDER_CHOICES = [(0, 'Nam'), (1, 'Nữ'), (2, 'Khác')]
    MARITAL_STATUS_CHOICES = [(0, 'Độc thân'), (1, 'Đã kết hôn'), (2, 'Đã ly hôn')]
    STATUS_CHOICES = [(0, 'Onboarding'), (1, 'Thử việc'), (2, 'Nhân viên chính thức'), (3, 'Đã nghỉ việc'), (4, 'Bị sa thải')]
    EDUCATION_LEVEL_CHOICES = [(0, 'Phổ thông'), (1, 'Trung cấp'), (2, 'Cao Đẳng'), (3, 'Đại học'), (4, 'Thạc sĩ'), (5, 'Tiến sĩ'), (6, 'Khác')]

    employee_code = models.CharField(max_length=20, unique=True, null=False, blank=False)
    name = models.CharField(max_length=50)
    gender = models.IntegerField(choices=GENDER_CHOICES)
    birthday = models.DateField()
    place_of_birth = models.CharField(max_length=300)
    place_of_origin = models.CharField(max_length=300)
    place_of_residence = models.CharField(max_length=300)
    identification = models.CharField(max_length=50, unique=True)
    date_of_issue = models.DateField()
    place_of_issue = models.CharField(max_length=300)
    nationality = models.CharField(max_length=50)
    nation = models.CharField(max_length=50)
    religion = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=300)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    marital_status = models.IntegerField(choices=MARITAL_STATUS_CHOICES)
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True)
    job_position = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    is_manager = models.BooleanField(default=False)
    salary = models.FloatField()
    contract_start_date = models.DateField()
    contract_duration = models.FloatField(help_text="Đơn vị tháng")
    status = models.IntegerField(choices=STATUS_CHOICES)
    education_level = models.IntegerField(choices=EDUCATION_LEVEL_CHOICES)
    major = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    certificate = models.TextField(blank=True)  # nhập cách nhau bởi dấu ","
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Reward(models.Model):
    number = models.IntegerField(unique=True)
    description = models.TextField()
    date = models.DateTimeField()
    amount = models.FloatField()
    cash_payment = models.BooleanField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reward {self.number} - {self.employee.name}"


class Discipline(models.Model):
    number = models.IntegerField(unique=True)
    description = models.TextField()
    date = models.DateTimeField()
    amount = models.FloatField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discipline {self.number} - {self.employee.name}"


class Evaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    period = models.CharField(max_length=50)  # Tháng / quý / năm / dự án
    score = models.FloatField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation - {self.employee.name} - {self.period}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Có làm việc', 'Có làm việc'),
        ('Nghỉ phép', 'Nghỉ phép'),
        ('Nghỉ không phép', 'Nghỉ không phép')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    working_hours = models.FloatField(default=0)
    notes = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.date.date()} - {self.employee.name}"


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chưa xác nhận'),
        ('confirmed', 'Đã xác nhận')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.IntegerField()  # Tháng (1-12)
    year = models.IntegerField()
    base_salary = models.FloatField()  # Lương cơ bản
    salary_coefficient = models.FloatField()  # Hệ số lương
    standard_working_days = models.IntegerField()  # Số ngày làm việc chuẩn
    hourly_rate = models.FloatField()  # Lương theo giờ
    total_working_hours = models.FloatField()  # Tổng số giờ làm việc
    bonus = models.FloatField(default=0)  # Thưởng
    penalty = models.FloatField(default=0)  # Phạt
    total_salary = models.FloatField()  # Tổng lương
    notes = models.TextField(blank=True)  # Ghi chú
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"Bảng lương - {self.employee.name} - {self.month}/{self.year}"


class LeaveType(models.Model):
    """Loại nghỉ phép: Phép năm, Nghỉ ốm, Nghỉ cưới, v.v."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)  # AL (Annual Leave), SL (Sick Leave)
    description = models.TextField(blank=True)
    max_days_per_year = models.IntegerField(help_text="Số ngày tối đa trong năm")
    requires_approval = models.BooleanField(default=True, help_text="Có cần duyệt không?")
    is_paid = models.BooleanField(default=True, help_text="Có hưởng lương không?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class LeaveBalance(models.Model):
    """Số ngày phép còn lại của từng nhân viên theo từng loại"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    total_days = models.FloatField(help_text="Tổng số ngày phép được cấp")
    used_days = models.FloatField(default=0, help_text="Số ngày đã sử dụng")
    remaining_days = models.FloatField(help_text="Số ngày còn lại")
    
    class Meta:
        unique_together = ('employee', 'leave_type', 'year')
        ordering = ['-year', 'leave_type']

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.name} - {self.year}: {self.remaining_days} ngày"

    def save(self, *args, **kwargs):
        """Auto-calculate remaining days"""
        self.remaining_days = self.total_days - self.used_days
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    """Đơn xin nghỉ phép"""
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.FloatField(help_text="Số ngày nghỉ (có thể là 0.5 cho nửa ngày)")
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval workflow
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_leaves',
        help_text="Người duyệt (Manager hoặc HR)"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

    def calculate_working_days(self):
        """Tính số ngày làm việc (không tính thứ 7, CN)"""
        from datetime import timedelta
        current_date = self.start_date
        working_days = 0
        
        while current_date <= self.end_date:
            # 0 = Monday, 6 = Sunday
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days

    def save(self, *args, **kwargs):
        """Auto-calculate total_days if not set"""
        if not self.total_days:
            self.total_days = self.calculate_working_days()
        super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
    """Danh mục chi phí: Đi lại, Ăn uống, Khách sạn, v.v."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'


class Expense(models.Model):
    """Đơn yêu cầu hoàn tiền chi phí"""
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Số tiền yêu cầu hoàn")
    date = models.DateField(help_text="Ngày phát sinh chi phí")
    description = models.TextField(help_text="Mô tả chi tiết chi phí")
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True, help_text="Ảnh hóa đơn")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Approval workflow
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_expenses',
        help_text="Người duyệt (Manager hoặc HR)"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Payment tracking
    paid_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_expenses',
        help_text="Người thanh toán (Kế toán)"
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('cash', 'Tiền mặt'),
            ('bank_transfer', 'Chuyển khoản'),
            ('check', 'Séc')
        ]
    )
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Mã giao dịch/Số séc")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f"{self.employee.name} - {self.category.name} - {self.amount:,.0f} VNĐ ({self.get_status_display()})"

    def can_be_edited(self):
        """Chỉ cho phép sửa khi status = pending"""
        return self.status == 'pending'

    def can_be_cancelled(self):
        """Cho phép hủy khi status = pending hoặc approved"""
        return self.status in ['pending', 'approved']


class Contract(models.Model):
    """Model quản lý hợp đồng lao động"""
    CONTRACT_TYPE_CHOICES = [
        ('probation', 'Hợp đồng thử việc'),
        ('definite', 'Hợp đồng xác định thời hạn'),
        ('indefinite', 'Hợp đồng không xác định thời hạn'),
        ('seasonal', 'Hợp đồng theo mùa vụ'),
        ('project', 'Hợp đồng theo dự án'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('active', 'Đang hiệu lực'),
        ('expired', 'Hết hạn'),
        ('terminated', 'Đã chấm dứt'),
        ('renewed', 'Đã gia hạn'),
    ]
    
    # Basic Information
    contract_number = models.CharField(max_length=50, unique=True, help_text="Số hợp đồng")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    
    # Dates
    start_date = models.DateField(help_text="Ngày bắt đầu")
    end_date = models.DateField(null=True, blank=True, help_text="Ngày kết thúc (null nếu vô thời hạn)")
    signed_date = models.DateField(help_text="Ngày ký")
    
    # Financial
    salary = models.FloatField(help_text="Mức lương theo hợp đồng")
    salary_coefficient = models.FloatField(default=1.0, help_text="Hệ số lương")
    allowances = models.FloatField(default=0, help_text="Phụ cấp")
    
    # Contract Details
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True)
    job_description = models.TextField(blank=True, help_text="Mô tả công việc")
    workplace = models.CharField(max_length=300, help_text="Địa điểm làm việc")
    working_hours = models.CharField(max_length=100, default="8 giờ/ngày, 5 ngày/tuần", help_text="Thời gian làm việc")
    
    # Terms and Conditions
    terms = models.TextField(help_text="Các điều khoản hợp đồng")
    benefits = models.TextField(blank=True, help_text="Các quyền lợi")
    insurance_info = models.TextField(blank=True, help_text="Thông tin bảo hiểm")
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    termination_reason = models.TextField(blank=True, help_text="Lý do chấm dứt")
    termination_date = models.DateField(null=True, blank=True, help_text="Ngày chấm dứt")
    notes = models.TextField(blank=True, help_text="Ghi chú")
    
    # File Attachment
    contract_file = models.FileField(upload_to='contracts/', blank=True, help_text="File hợp đồng scan")
    
    # Renewal Reference
    renewed_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='renewals', help_text="Hợp đồng được gia hạn từ")
    
    # Metadata
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, 
                                   related_name='created_contracts', help_text="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
    
    def __str__(self):
        return f"{self.contract_number} - {self.employee.name} ({self.get_contract_type_display()})"
    
    def is_active(self):
        """Kiểm tra hợp đồng còn hiệu lực"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status != 'active':
            return False
        
        if self.start_date > today:
            return False
        
        if self.end_date and self.end_date < today:
            return False
        
        return True
    
    def days_until_expiration(self):
        """Số ngày còn lại đến khi hết hạn"""
        if not self.end_date or self.status != 'active':
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        delta = self.end_date - today
        return delta.days if delta.days > 0 else 0
    
    def is_expiring_soon(self, days=30):
        """Kiểm tra hợp đồng sắp hết hạn (mặc định 30 ngày)"""
        days_left = self.days_until_expiration()
        return days_left is not None and 0 < days_left <= days
    
    def can_be_renewed(self):
        """Kiểm tra có thể gia hạn hay không"""
        return self.status == 'active' and self.contract_type in ['probation', 'definite', 'seasonal', 'project']
    
    def can_be_terminated(self):
        """Kiểm tra có thể chấm dứt hay không"""
        return self.status == 'active'
