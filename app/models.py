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

    class Meta:
        permissions = [
            ('view_team_employees', 'Can view team employees'),
            ('view_employee_salary', 'Can view employee salary information'),
            ('view_all_employees', 'Can view all employees across departments'),
            ('manage_employee_contracts', 'Can manage employee contracts'),
        ]

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
        permissions = [
            ('approve_leave_request', 'Can approve leave requests'),
            ('view_team_leave_requests', 'Can view team leave requests'),
        ]

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
        permissions = [
            ('approve_expense', 'Can approve expense claims'),
            ('pay_expense', 'Can pay approved expenses'),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.category.name} - {self.amount:,.0f} VNĐ ({self.get_status_display()})"

    def can_be_edited(self):
        """Chỉ cho phép sửa khi status = pending"""
        return self.status == 'pending'

    def can_be_cancelled(self):
        """Cho phép hủy khi status = pending hoặc approved"""
        return self.status in ['pending', 'approved']


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


# ============================================================================
# SALARY RULES ENGINE
# ============================================================================

class SalaryComponent(models.Model):
    """
    Các thành phần lương có thể cấu hình:
    - Allowances (Phụ cấp): position, transport, meal, housing
    - Bonuses (Thưởng): performance, attendance, project
    - Deductions (Khấu trừ): insurance, tax, late, absence
    """
    COMPONENT_TYPES = [
        ('allowance', 'Phụ cấp'),
        ('bonus', 'Thưởng'),
        ('deduction', 'Khấu trừ'),
        ('overtime', 'Làm thêm giờ'),
    ]
    
    CALCULATION_METHODS = [
        ('fixed', 'Cố định'),
        ('percentage', 'Phần trăm lương cơ bản'),
        ('formula', 'Công thức tùy chỉnh'),
        ('hourly', 'Theo giờ'),
        ('daily', 'Theo ngày'),
    ]
    
    code = models.CharField(max_length=50, unique=True, help_text="Mã thành phần (VD: PC_VITRI, TH_HIEUSUAT)")
    name = models.CharField(max_length=100, help_text="Tên thành phần")
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    calculation_method = models.CharField(max_length=20, choices=CALCULATION_METHODS)
    
    # For fixed amount
    default_amount = models.FloatField(default=0, help_text="Số tiền mặc định")
    
    # For percentage calculation
    percentage = models.FloatField(default=0, help_text="Phần trăm (0-100)")
    
    # For formula calculation
    formula = models.TextField(blank=True, help_text="Công thức Python (VD: base_salary * 0.1 + bonus)")
    
    # Settings
    is_taxable = models.BooleanField(default=True, help_text="Tính thuế TNCN")
    is_mandatory = models.BooleanField(default=False, help_text="Bắt buộc áp dụng cho tất cả")
    is_active = models.BooleanField(default=True)
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['component_type', 'name']
    
    def __str__(self):
        return f"{self.get_component_type_display()} - {self.name}"
    
    def calculate(self, base_salary=0, **kwargs):
        """Calculate component value based on method"""
        if self.calculation_method == 'fixed':
            return self.default_amount
        elif self.calculation_method == 'percentage':
            return base_salary * (self.percentage / 100)
        elif self.calculation_method == 'formula':
            if self.formula:
                try:
                    # Create safe evaluation context
                    context = {
                        'base_salary': base_salary,
                        **kwargs
                    }
                    return eval(self.formula, {"__builtins__": {}}, context)
                except:
                    return 0
            return 0
        elif self.calculation_method == 'hourly':
            hours = kwargs.get('hours', 0)
            return self.default_amount * hours
        elif self.calculation_method == 'daily':
            days = kwargs.get('days', 0)
            return self.default_amount * days
        return 0


class EmployeeSalaryRule(models.Model):
    """
    Quy tắc lương áp dụng cho từng nhân viên cụ thể.
    Override các giá trị mặc định từ SalaryComponent.
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_rules')
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    
    # Override values
    custom_amount = models.FloatField(null=True, blank=True, help_text="Số tiền tùy chỉnh (override default)")
    custom_percentage = models.FloatField(null=True, blank=True, help_text="Phần trăm tùy chỉnh")
    custom_formula = models.TextField(blank=True, help_text="Công thức tùy chỉnh")
    
    # Effective period
    effective_from = models.DateField(help_text="Có hiệu lực từ ngày")
    effective_to = models.DateField(null=True, blank=True, help_text="Hết hiệu lực (null = vô thời hạn)")
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, 
                                   related_name='created_salary_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_from']
        unique_together = ('employee', 'component', 'effective_from')
    
    def __str__(self):
        return f"{self.employee.name} - {self.component.name}"
    
    def get_amount(self):
        """Get the custom amount or default from component"""
        if self.custom_amount is not None:
            return self.custom_amount
        return self.component.default_amount
    
    def get_percentage(self):
        """Get custom percentage or default"""
        if self.custom_percentage is not None:
            return self.custom_percentage
        return self.component.percentage
    
    def calculate(self, base_salary=0, **kwargs):
        """Calculate with custom values"""
        if self.component.calculation_method == 'fixed':
            return self.get_amount()
        elif self.component.calculation_method == 'percentage':
            return base_salary * (self.get_percentage() / 100)
        elif self.component.calculation_method == 'formula':
            formula = self.custom_formula or self.component.formula
            if formula:
                try:
                    context = {'base_salary': base_salary, **kwargs}
                    return eval(formula, {"__builtins__": {}}, context)
                except:
                    return 0
            return 0
        elif self.component.calculation_method == 'hourly':
            hours = kwargs.get('hours', 0)
            return self.get_amount() * hours
        elif self.component.calculation_method == 'daily':
            days = kwargs.get('days', 0)
            return self.get_amount() * days
        return 0


class PayrollCalculationLog(models.Model):
    """
    Log chi tiết của việc tính lương, lưu breakdown của từng component
    """
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='calculation_logs')
    
    # Breakdown
    base_salary = models.FloatField()
    total_allowances = models.FloatField(default=0)
    total_bonuses = models.FloatField(default=0)
    total_deductions = models.FloatField(default=0)
    total_overtime = models.FloatField(default=0)
    
    # Tax
    taxable_income = models.FloatField(default=0)
    personal_income_tax = models.FloatField(default=0)
    
    # Insurance
    social_insurance = models.FloatField(default=0)
    health_insurance = models.FloatField(default=0)
    unemployment_insurance = models.FloatField(default=0)
    
    # Final
    gross_salary = models.FloatField(help_text="Tổng lương trước thuế và bảo hiểm")
    net_salary = models.FloatField(help_text="Lương thực nhận")
    
    calculation_details = models.JSONField(default=dict, help_text="Chi tiết từng component")
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-calculated_at']
    
    def __str__(self):
        return f"Calculation for {self.payroll}"


class SalaryRuleTemplate(models.Model):
    """
    Template cho việc gán rules mặc định theo chức vụ hoặc phòng ban
    """
    name = models.CharField(max_length=100, help_text="Tên template (VD: Template Giám đốc)")
    description = models.TextField(blank=True)
    
    # Apply to specific job title or department
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        target = self.job_title.name if self.job_title else (self.department.name if self.department else "General")
        return f"{self.name} ({target})"
    
    def apply_to_employee(self, employee, created_by=None, effective_from=None):
        """Apply this template's rules to an employee"""
        from datetime import date
        if not effective_from:
            effective_from = date.today()
        
        applied_count = 0
        for item in self.template_items.filter(is_active=True):
            # Check if rule already exists
            existing = EmployeeSalaryRule.objects.filter(
                employee=employee,
                component=item.component,
                is_active=True
            ).first()
            
            if not existing:
                EmployeeSalaryRule.objects.create(
                    employee=employee,
                    component=item.component,
                    custom_amount=item.custom_amount,
                    custom_percentage=item.custom_percentage,
                    custom_formula=item.custom_formula,
                    effective_from=effective_from,
                    notes=f"Auto-applied from template: {self.name}",
                    created_by=created_by
                )
                applied_count += 1
        
        return applied_count


class SalaryRuleTemplateItem(models.Model):
    """
    Các component trong template
    """
    template = models.ForeignKey(SalaryRuleTemplate, on_delete=models.CASCADE, related_name='template_items')
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    
    # Override values (null = use component defaults)
    custom_amount = models.FloatField(null=True, blank=True)
    custom_percentage = models.FloatField(null=True, blank=True)
    custom_formula = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'component__name']
        unique_together = ('template', 'component')
    
    def __str__(self):
        return f"{self.template.name} - {self.component.name}"


# ============================================================================
# CONTRACT MANAGEMENT
# ============================================================================

class Contract(models.Model):
    """
    Hợp đồng lao động của nhân viên
    Một nhân viên có thể có nhiều hợp đồng (gia hạn, ký mới)
    """
    CONTRACT_TYPE_CHOICES = [
        ('probation', 'Thử việc'),
        ('fixed_term', 'Xác định thời hạn'),
        ('indefinite', 'Không xác định thời hạn'),
        ('seasonal', 'Thời vụ'),
        ('part_time', 'Bán thời gian'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('active', 'Đang hiệu lực'),
        ('expired', 'Hết hạn'),
        ('terminated', 'Chấm dứt'),
        ('renewed', 'Đã gia hạn'),
    ]
    
    # Basic Information
    contract_code = models.CharField(max_length=20, unique=True, default='TEMP', help_text="Mã hợp đồng")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    
    # Dates
    start_date = models.DateField(help_text="Ngày bắt đầu hiệu lực")
    end_date = models.DateField(null=True, blank=True, help_text="Ngày kết thúc (null nếu không xác định thời hạn)")
    signed_date = models.DateField(null=True, blank=True, help_text="Ngày ký")
    
    # Salary Information
    base_salary = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Lương cơ bản")
    allowances = models.JSONField(default=dict, blank=True, help_text="Phụ cấp dạng JSON")
    
    # Work Information
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    work_location = models.CharField(max_length=255, blank=True)
    working_hours = models.CharField(max_length=100, default="8:00-17:00", help_text="Giờ làm việc")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Additional Information
    terms = models.TextField(blank=True, help_text="Điều khoản hợp đồng")
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='contracts/', blank=True, help_text="File hợp đồng PDF")
    
    # Tracking
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='contracts_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Renewal tracking
    renewed_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='renewals', help_text="Hợp đồng cũ được gia hạn")
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['end_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.contract_code} - {self.employee.name} ({self.get_contract_type_display()})"
    
    def is_active(self):
        """Check if contract is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'active' and
            self.start_date <= today and
            (self.end_date is None or self.end_date >= today)
        )
    
    def days_until_expiry(self):
        """Calculate days until contract expires"""
        if not self.end_date:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        delta = self.end_date - today
        return delta.days
    
    def is_expiring_soon(self, days=30):
        """Check if contract is expiring within specified days"""
        days_left = self.days_until_expiry()
        if days_left is None:
            return False
        return 0 < days_left <= days
    
    def save(self, *args, **kwargs):
        """Auto-generate contract code if not set"""
        if not self.contract_code or self.contract_code == 'TEMP':
            from django.utils import timezone
            import uuid
            date_str = timezone.now().strftime('%Y%m%d')
            unique_str = uuid.uuid4().hex[:6].upper()
            self.contract_code = f"HD{date_str}{unique_str}"
        super().save(*args, **kwargs)


class ContractHistory(models.Model):
    """
    Lịch sử thay đổi hợp đồng (gia hạn, điều chỉnh lương, chấm dứt)
    """
    ACTION_CHOICES = [
        ('created', 'Tạo mới'),
        ('renewed', 'Gia hạn'),
        ('salary_adjusted', 'Điều chỉnh lương'),
        ('terminated', 'Chấm dứt'),
        ('status_changed', 'Thay đổi trạng thái'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(help_text="Mô tả chi tiết thay đổi")
    old_value = models.JSONField(null=True, blank=True, help_text="Giá trị cũ (nếu có)")
    new_value = models.JSONField(null=True, blank=True, help_text="Giá trị mới")
    
    performed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-performed_at']
        verbose_name_plural = "Contract histories"
    
    def __str__(self):
        return f"{self.contract.contract_code} - {self.get_action_display()} ({self.performed_at.strftime('%d/%m/%Y')})"


class PermissionAuditLog(models.Model):
    """
    Audit log for permission denials and access attempts
    Tracks security events for compliance and monitoring
    """
    ACTION_CHOICES = [
        ('denied', 'Access Denied'),
        ('granted', 'Access Granted'),
        ('attempted', 'Access Attempted'),
    ]
    
    # Who
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    username = models.CharField(max_length=150, help_text="Username at time of action")
    user_groups = models.JSONField(default=list, help_text="User's groups at time of action")
    
    # What
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='denied')
    resource_type = models.CharField(max_length=50, help_text="Contract, LeaveRequest, Expense, Payroll, etc.")
    resource_id = models.IntegerField(null=True, blank=True, help_text="ID of the resource accessed")
    permission_required = models.CharField(max_length=100, help_text="Permission that was checked")
    
    # When & Where
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Why
    reason = models.TextField(help_text="Reason for denial or additional context")
    view_name = models.CharField(max_length=100, blank=True, help_text="Django view name")
    url_path = models.CharField(max_length=500, blank=True)
    
    # Additional Context
    extra_data = models.JSONField(default=dict, blank=True, help_text="Additional context (department, etc.)")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Permission Audit Log"
        verbose_name_plural = "Permission Audit Logs"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()}: {self.username} -> {self.resource_type} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


# ============================================================================
# PERFORMANCE APPRAISAL MANAGEMENT
# ============================================================================

class AppraisalPeriod(models.Model):
    """
    Kỳ đánh giá nhân viên (ví dụ: Đánh giá cuối năm 2025, Đánh giá thử việc Q1)
    HR tạo các kỳ đánh giá và định nghĩa tiêu chí
    """
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('active', 'Đang diễn ra'),
        ('closed', 'Đã kết thúc'),
        ('archived', 'Lưu trữ'),
    ]
    
    name = models.CharField(max_length=200, help_text="Tên kỳ đánh giá (VD: Đánh giá năm 2025)")
    description = models.TextField(blank=True, help_text="Mô tả mục đích, phạm vi đánh giá")
    
    # Timeline
    start_date = models.DateField(help_text="Ngày bắt đầu kỳ đánh giá")
    end_date = models.DateField(help_text="Ngày kết thúc kỳ đánh giá")
    self_assessment_deadline = models.DateField(help_text="Deadline nhân viên tự đánh giá")
    manager_review_deadline = models.DateField(help_text="Deadline quản lý hoàn thành đánh giá")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Scope
    applicable_departments = models.ManyToManyField(Department, blank=True, 
                                                    help_text="Phòng ban áp dụng (để trống = tất cả)")
    applicable_job_titles = models.ManyToManyField(JobTitle, blank=True,
                                                   help_text="Chức danh áp dụng (để trống = tất cả)")
    
    # Metadata
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, 
                                   related_name='created_appraisal_periods')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', '-start_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    def is_active(self):
        """Kiểm tra kỳ đánh giá có đang diễn ra không"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    def can_self_assess(self):
        """Kiểm tra còn nhận tự đánh giá không"""
        from django.utils import timezone
        return self.status == 'active' and timezone.now().date() <= self.self_assessment_deadline


class AppraisalCriteria(models.Model):
    """
    Tiêu chí đánh giá (KPI) cho từng kỳ
    Ví dụ: Chất lượng công việc, Kỹ năng làm việc nhóm, Tuân thủ quy định
    """
    CATEGORY_CHOICES = [
        ('performance', 'Hiệu suất công việc'),
        ('behavior', 'Hành vi & Thái độ'),
        ('skill', 'Kỹ năng chuyên môn'),
        ('leadership', 'Năng lực lãnh đạo'),
        ('development', 'Phát triển bản thân'),
    ]
    
    period = models.ForeignKey(AppraisalPeriod, on_delete=models.CASCADE, related_name='criteria')
    name = models.CharField(max_length=200, help_text="Tên tiêu chí (VD: Chất lượng công việc)")
    description = models.TextField(help_text="Mô tả chi tiết tiêu chí")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Weight
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0,
                                 help_text="Trọng số (%) - tổng các tiêu chí = 100%")
    max_score = models.IntegerField(default=5, help_text="Điểm tối đa (thường là 5 hoặc 10)")
    
    # Order
    order = models.IntegerField(default=0, help_text="Thứ tự hiển thị")
    
    class Meta:
        ordering = ['period', 'order', 'name']
        verbose_name = "Appraisal Criterion"
        verbose_name_plural = "Appraisal Criteria"
    
    def __str__(self):
        return f"{self.period.name} - {self.name} ({self.weight}%)"


class Appraisal(models.Model):
    """
    Đánh giá của một nhân viên trong một kỳ
    Mỗi nhân viên có một Appraisal record cho mỗi period
    """
    STATUS_CHOICES = [
        ('pending_self', 'Chờ nhân viên tự đánh giá'),
        ('pending_manager', 'Chờ quản lý đánh giá'),
        ('pending_hr', 'Chờ HR phê duyệt'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]
    
    OVERALL_RATING_CHOICES = [
        ('outstanding', 'Xuất sắc'),
        ('exceeds', 'Vượt mong đợi'),
        ('meets', 'Đạt yêu cầu'),
        ('needs_improvement', 'Cần cải thiện'),
        ('unsatisfactory', 'Không đạt'),
    ]
    
    # Core Relationships
    period = models.ForeignKey(AppraisalPeriod, on_delete=models.CASCADE, related_name='appraisals')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='appraisals')
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, 
                                related_name='managed_appraisals',
                                help_text="Người quản lý trực tiếp đánh giá")
    
    # Status & Timeline
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_self')
    self_assessment_date = models.DateTimeField(null=True, blank=True)
    manager_review_date = models.DateTimeField(null=True, blank=True)
    final_review_date = models.DateTimeField(null=True, blank=True)
    
    # Self Assessment
    self_overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            help_text="Tổng điểm tự đánh giá")
    self_comments = models.TextField(blank=True, help_text="Nhận xét của nhân viên")
    self_achievements = models.TextField(blank=True, help_text="Thành tích nổi bật")
    self_challenges = models.TextField(blank=True, help_text="Khó khăn gặp phải")
    self_development_plan = models.TextField(blank=True, help_text="Kế hoạch phát triển")
    
    # Manager Review
    manager_overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                                help_text="Tổng điểm đánh giá của quản lý")
    manager_comments = models.TextField(blank=True, help_text="Nhận xét của quản lý")
    manager_strengths = models.TextField(blank=True, help_text="Điểm mạnh")
    manager_weaknesses = models.TextField(blank=True, help_text="Điểm cần cải thiện")
    manager_recommendations = models.TextField(blank=True, help_text="Đề xuất (thăng chức, tăng lương, đào tạo...)")
    
    # Final Result
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                      help_text="Điểm cuối cùng (sau khi HR review)")
    overall_rating = models.CharField(max_length=20, choices=OVERALL_RATING_CHOICES, null=True, blank=True)
    hr_comments = models.TextField(blank=True, help_text="Nhận xét của HR")
    
    # Actions
    salary_adjustment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                           help_text="Điều chỉnh lương (nếu có)")
    promotion_recommended = models.BooleanField(default=False)
    training_recommended = models.TextField(blank=True, help_text="Khóa đào tạo đề xuất")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('period', 'employee')
        indexes = [
            models.Index(fields=['period', 'status']),
            models.Index(fields=['employee', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.period.name}"
    
    def calculate_final_score(self):
        """Tính điểm tổng kết dựa trên các AppraisalScore"""
        scores = self.scores.all()
        if not scores:
            return None
        
        total_weighted_score = 0
        total_weight = 0
        
        for score in scores:
            if score.final_score is not None and score.criteria.weight:
                total_weighted_score += float(score.final_score) * float(score.criteria.weight)
                total_weight += float(score.criteria.weight)
        
        if total_weight > 0:
            return round(total_weighted_score / total_weight, 2)
        return None
    
    def can_self_assess(self, user_employee):
        """Kiểm tra nhân viên có thể tự đánh giá không"""
        return (self.employee == user_employee and 
                self.status == 'pending_self' and
                self.period.can_self_assess())
    
    def can_manager_review(self, user_employee):
        """Kiểm tra quản lý có thể đánh giá không"""
        return (self.manager == user_employee and 
                self.status == 'pending_manager')


class AppraisalScore(models.Model):
    """
    Điểm số cho từng tiêu chí trong đánh giá
    Có cả điểm tự đánh giá và điểm quản lý đánh giá
    """
    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name='scores')
    criteria = models.ForeignKey(AppraisalCriteria, on_delete=models.CASCADE)
    
    # Self Assessment
    self_score = models.IntegerField(null=True, blank=True, help_text="Điểm tự đánh giá")
    self_comment = models.TextField(blank=True, help_text="Giải thích điểm tự đánh giá")
    
    # Manager Review
    manager_score = models.IntegerField(null=True, blank=True, help_text="Điểm quản lý đánh giá")
    manager_comment = models.TextField(blank=True, help_text="Giải thích điểm quản lý")
    
    # Final Score (có thể khác với manager_score nếu HR điều chỉnh)
    final_score = models.IntegerField(null=True, blank=True, help_text="Điểm cuối cùng")
    
    class Meta:
        ordering = ['criteria__order', 'criteria__name']
        unique_together = ('appraisal', 'criteria')
    
    def __str__(self):
        return f"{self.appraisal.employee.name} - {self.criteria.name}: Self={self.self_score}, Manager={self.manager_score}"


class AppraisalComment(models.Model):
    """
    Comments và feedback trong quá trình đánh giá
    Cho phép trao đổi giữa nhân viên - quản lý - HR
    """
    AUTHOR_TYPE_CHOICES = [
        ('employee', 'Nhân viên'),
        ('manager', 'Quản lý'),
        ('hr', 'HR'),
    ]
    
    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Employee, on_delete=models.CASCADE)
    author_type = models.CharField(max_length=20, choices=AUTHOR_TYPE_CHOICES)
    
    content = models.TextField(help_text="Nội dung góp ý")
    is_private = models.BooleanField(default=False, help_text="Chỉ HR và quản lý thấy")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.name} ({self.get_author_type_display()}) - {self.created_at.strftime('%Y-%m-%d')}"
