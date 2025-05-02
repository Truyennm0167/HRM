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
