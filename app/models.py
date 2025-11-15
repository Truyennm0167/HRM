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


# ============= Recruitment Models =============

class JobPosting(models.Model):
    """Job posting for recruitment"""
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('open', 'Đang mở'),
        ('closed', 'Đã đóng'),
        ('cancelled', 'Đã hủy'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('fulltime', 'Toàn thời gian'),
        ('parttime', 'Bán thời gian'),
        ('contract', 'Hợp đồng'),
        ('internship', 'Thực tập'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Mới tốt nghiệp'),
        ('junior', 'Junior (1-2 năm)'),
        ('mid', 'Middle (3-5 năm)'),
        ('senior', 'Senior (5+ năm)'),
        ('expert', 'Expert (10+ năm)'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Tiêu đề công việc")
    code = models.CharField(max_length=50, unique=True, help_text="Mã tin tuyển dụng")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Job Details
    description = models.TextField(help_text="Mô tả công việc")
    requirements = models.TextField(help_text="Yêu cầu công việc")
    responsibilities = models.TextField(help_text="Trách nhiệm công việc")
    benefits = models.TextField(help_text="Quyền lợi")
    
    # Employment Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='fulltime')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='junior')
    number_of_positions = models.IntegerField(default=1, help_text="Số lượng cần tuyển")
    
    # Location and Salary
    location = models.CharField(max_length=300, help_text="Địa điểm làm việc")
    salary_min = models.FloatField(null=True, blank=True, help_text="Lương tối thiểu")
    salary_max = models.FloatField(null=True, blank=True, help_text="Lương tối đa")
    salary_negotiable = models.BooleanField(default=False, help_text="Lương thỏa thuận")
    
    # Dates
    deadline = models.DateField(help_text="Hạn nộp hồ sơ")
    start_date = models.DateField(null=True, blank=True, help_text="Ngày dự kiến nhận việc")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Contact
    contact_person = models.CharField(max_length=100, blank=True, help_text="Người liên hệ")
    contact_email = models.EmailField(blank=True, help_text="Email liên hệ")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Điện thoại liên hệ")
    
    # Metadata
    views_count = models.IntegerField(default=0, help_text="Số lượt xem")
    applications_count = models.IntegerField(default=0, help_text="Số lượt ứng tuyển")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def is_active(self):
        """Kiểm tra tin tuyển dụng còn hiệu lực"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'open' and self.deadline >= today
    
    def days_until_deadline(self):
        """Số ngày còn lại đến deadline"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.deadline < today:
            return 0
        delta = self.deadline - today
        return delta.days
    
    def get_salary_display(self):
        """Hiển thị mức lương"""
        if self.salary_negotiable:
            return "Thỏa thuận"
        elif self.salary_min and self.salary_max:
            return f"{self.salary_min:,.0f} - {self.salary_max:,.0f} VNĐ"
        elif self.salary_min:
            return f"Từ {self.salary_min:,.0f} VNĐ"
        elif self.salary_max:
            return f"Đến {self.salary_max:,.0f} VNĐ"
        return "Không nêu rõ"
    
    def increment_views(self):
        """Tăng số lượt xem"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_applications(self):
        """Tăng số lượt ứng tuyển"""
        self.applications_count += 1
        self.save(update_fields=['applications_count'])


class Application(models.Model):
    """Job application from candidates"""
    STATUS_CHOICES = [
        ('new', 'Mới'),
        ('screening', 'Sơ tuyển'),
        ('phone_interview', 'Phỏng vấn điện thoại'),
        ('interview', 'Phỏng vấn'),
        ('test', 'Làm bài test'),
        ('offer', 'Đề nghị'),
        ('accepted', 'Chấp nhận'),
        ('rejected', 'Từ chối'),
        ('withdrawn', 'Rút lui'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website công ty'),
        ('referral', 'Giới thiệu'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('indeed', 'Indeed'),
        ('vietnamworks', 'VietnamWorks'),
        ('other', 'Khác'),
    ]
    
    # Job and Candidate Info
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    application_code = models.CharField(max_length=50, unique=True, help_text="Mã đơn ứng tuyển")
    
    # Personal Information
    full_name = models.CharField(max_length=100, help_text="Họ và tên")
    email = models.EmailField(help_text="Email")
    phone = models.CharField(max_length=20, help_text="Số điện thoại")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Ngày sinh")
    gender = models.IntegerField(choices=Employee.GENDER_CHOICES, null=True, blank=True)
    address = models.CharField(max_length=300, blank=True, help_text="Địa chỉ")
    
    # Professional Information
    current_position = models.CharField(max_length=100, blank=True, help_text="Vị trí hiện tại")
    current_company = models.CharField(max_length=200, blank=True, help_text="Công ty hiện tại")
    years_of_experience = models.IntegerField(default=0, help_text="Số năm kinh nghiệm")
    education_level = models.IntegerField(choices=Employee.EDUCATION_LEVEL_CHOICES, null=True, blank=True)
    school = models.CharField(max_length=200, blank=True, help_text="Trường học")
    major = models.CharField(max_length=100, blank=True, help_text="Chuyên ngành")
    
    # Application Details
    resume = models.FileField(upload_to='resumes/', help_text="CV ứng viên")
    cover_letter = models.TextField(blank=True, help_text="Thư xin việc")
    portfolio_url = models.URLField(blank=True, help_text="Link portfolio")
    linkedin_url = models.URLField(blank=True, help_text="Link LinkedIn")
    
    # Availability
    expected_salary = models.FloatField(null=True, blank=True, help_text="Mức lương mong muốn")
    available_start_date = models.DateField(null=True, blank=True, help_text="Ngày có thể bắt đầu")
    notice_period_days = models.IntegerField(default=0, help_text="Thời gian báo trước (ngày)")
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    rating = models.IntegerField(null=True, blank=True, help_text="Đánh giá (1-5)")
    notes = models.TextField(blank=True, help_text="Ghi chú nội bộ")
    
    # Interview Information
    interview_date = models.DateTimeField(null=True, blank=True, help_text="Ngày giờ phỏng vấn")
    interview_location = models.CharField(max_length=300, blank=True, help_text="Địa điểm phỏng vấn")
    interviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='interviews_conducted')
    
    # Decision
    offer_made_date = models.DateField(null=True, blank=True, help_text="Ngày đề nghị")
    offer_accepted_date = models.DateField(null=True, blank=True, help_text="Ngày chấp nhận")
    rejection_reason = models.TextField(blank=True, help_text="Lý do từ chối")
    
    # Conversion to Employee
    converted_to_employee = models.BooleanField(default=False)
    employee = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='application')
    
    # Metadata
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_applications', help_text="Người phụ trách")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
    
    def __str__(self):
        return f"{self.application_code} - {self.full_name} ({self.job.title})"
    
    def can_convert_to_employee(self):
        """Kiểm tra có thể chuyển thành nhân viên không"""
        return self.status == 'accepted' and not self.converted_to_employee
    
    def get_age(self):
        """Tính tuổi từ ngày sinh"""
        if not self.date_of_birth:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        return age
    
    def days_since_applied(self):
        """Số ngày kể từ khi ứng tuyển"""
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.days


class ApplicationNote(models.Model):
    """Notes and comments on applications"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='application_notes')
    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    note = models.TextField(help_text="Ghi chú")
    is_important = models.BooleanField(default=False, help_text="Đánh dấu quan trọng")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.author} on {self.application.application_code}"
