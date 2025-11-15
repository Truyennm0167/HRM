# employee_app/forms.py
from django import forms
from .models import Employee, LeaveType, LeaveRequest, ExpenseCategory, Expense, Contract, JobPosting, Application

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'


class LeaveTypeForm(forms.ModelForm):
    """Form để tạo/sửa loại nghỉ phép"""
    class Meta:
        model = LeaveType
        fields = ['name', 'code', 'description', 'max_days_per_year', 'requires_approval', 'is_paid', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Phép năm'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: AL'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_days_per_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LeaveRequestForm(forms.ModelForm):
    """Form để nhân viên tạo đơn xin nghỉ phép"""
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Nhập lý do xin nghỉ phép...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu")
        
        return cleaned_data


class ExpenseCategoryForm(forms.ModelForm):
    """Form để tạo/sửa danh mục chi phí"""
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Đi lại'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: TRAVEL'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExpenseForm(forms.ModelForm):
    """Form để nhân viên tạo đơn yêu cầu hoàn tiền"""
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'description', 'receipt']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '1000',
                'placeholder': 'Nhập số tiền (VNĐ)'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mô tả chi tiết chi phí...'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Số tiền phải lớn hơn 0")
        return amount
    
    def clean_date(self):
        from datetime import date
        expense_date = self.cleaned_data.get('date')
        if expense_date and expense_date > date.today():
            raise forms.ValidationError("Ngày chi phí không thể trong tương lai")
        return expense_date


class ContractForm(forms.ModelForm):
    """Form để tạo/sửa hợp đồng lao động"""
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'employee', 'contract_type', 'start_date', 'end_date',
            'signed_date', 'salary', 'salary_coefficient', 'allowances', 'job_title',
            'job_description', 'workplace', 'working_hours', 'terms', 'benefits',
            'insurance_info', 'notes', 'contract_file', 'status'
        ]
        widgets = {
            'contract_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: HD001/2025'
            }),
            'employee': forms.Select(attrs={'class': 'form-control select2'}),
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '100000',
                'placeholder': 'Nhập mức lương (VNĐ)'
            }),
            'salary_coefficient': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.1',
                'value': 1.0
            }),
            'allowances': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '100000',
                'value': 0
            }),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Mô tả công việc...'
            }),
            'workplace': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Địa điểm làm việc'
            }),
            'working_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'value': '8 giờ/ngày, 5 ngày/tuần'
            }),
            'terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Các điều khoản hợp đồng...'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Các quyền lợi...'
            }),
            'insurance_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Thông tin bảo hiểm...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ghi chú...'
            }),
            'contract_file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': '.pdf,.doc,.docx'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        signed_date = cleaned_data.get('signed_date')
        contract_type = cleaned_data.get('contract_type')
        
        # Validate dates
        if start_date and signed_date and start_date < signed_date:
            raise forms.ValidationError("Ngày bắt đầu không thể trước ngày ký hợp đồng")
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu")
        
        # Hợp đồng không xác định thời hạn không cần ngày kết thúc
        if contract_type == 'indefinite' and end_date:
            raise forms.ValidationError("Hợp đồng không xác định thời hạn không nên có ngày kết thúc")
        
        # Các loại hợp đồng khác cần ngày kết thúc
        if contract_type != 'indefinite' and not end_date:
            raise forms.ValidationError("Loại hợp đồng này cần có ngày kết thúc")
        
        return cleaned_data
    
    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary and salary <= 0:
            raise forms.ValidationError("Mức lương phải lớn hơn 0")
        return salary
    
    def clean_contract_number(self):
        contract_number = self.cleaned_data.get('contract_number')
        # Check uniqueness only for new contracts
        if self.instance.pk is None:  # New contract
            if Contract.objects.filter(contract_number=contract_number).exists():
                raise forms.ValidationError("Số hợp đồng này đã tồn tại")
        else:  # Editing existing contract
            if Contract.objects.filter(contract_number=contract_number).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Số hợp đồng này đã tồn tại")
        return contract_number


# ============= Recruitment Forms =============

class JobPostingForm(forms.ModelForm):
    """Form để tạo/sửa tin tuyển dụng (Admin)"""
    class Meta:
        model = JobPosting
        exclude = ['created_by', 'created_at', 'updated_at', 'views_count', 'applications_count']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Software Developer'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: JOB2025001'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Mô tả chi tiết công việc...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Yêu cầu ứng viên...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Trách nhiệm công việc...'}),
            'benefits': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Quyền lợi được hưởng...'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Select(attrs={'class': 'form-control'}),
            'number_of_positions': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa điểm làm việc'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1000000}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1000000}),
            'salary_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get('deadline')
        start_date = cleaned_data.get('start_date')
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        # Validate deadline
        from django.utils import timezone
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Hạn nộp hồ sơ không thể là ngày trong quá khứ")
        
        # Validate start date
        if start_date and deadline and start_date < deadline:
            raise forms.ValidationError("Ngày nhận việc không thể trước hạn nộp hồ sơ")
        
        # Validate salary range
        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Mức lương tối thiểu không thể lớn hơn mức lương tối đa")
        
        return cleaned_data
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        # Check uniqueness
        if self.instance.pk is None:  # New job
            if JobPosting.objects.filter(code=code).exists():
                raise forms.ValidationError("Mã tin tuyển dụng này đã tồn tại")
        else:  # Editing
            if JobPosting.objects.filter(code=code).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Mã tin tuyển dụng này đã tồn tại")
        return code


class ApplicationForm(forms.ModelForm):
    """Form ứng tuyển public (không cần login)"""
    class Meta:
        model = Application
        fields = [
            'full_name', 'email', 'phone', 'date_of_birth', 'gender', 'address',
            'current_position', 'current_company', 'years_of_experience',
            'education_level', 'school', 'major',
            'resume', 'cover_letter', 'portfolio_url', 'linkedin_url',
            'expected_salary', 'available_start_date', 'notice_period_days',
            'source'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên *', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email *', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại *', 'required': True}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa chỉ hiện tại'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vị trí hiện tại'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Công ty hiện tại'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trường học'}),
            'major': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chuyên ngành'}),
            'resume': forms.FileInput(attrs={'class': 'form-control-file', 'accept': '.pdf,.doc,.docx', 'required': True}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Giới thiệu bản thân và lý do ứng tuyển...'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1000000, 'placeholder': 'VNĐ'}),
            'available_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notice_period_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 180, 'placeholder': 'Số ngày'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Basic phone validation
        import re
        if phone and not re.match(r'^[\d\s\-\+\(\)]+$', phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ")
        return phone
    
    def clean_available_start_date(self):
        date = self.cleaned_data.get('available_start_date')
        from django.utils import timezone
        if date and date < timezone.now().date():
            raise forms.ValidationError("Ngày có thể bắt đầu không thể là ngày trong quá khứ")
        return date


class ApplicationReviewForm(forms.ModelForm):
    """Form để HR review và update trạng thái application"""
    class Meta:
        model = Application
        fields = ['status', 'rating', 'notes', 'assigned_to', 'interviewer', 
                  'interview_date', 'interview_location', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ghi chú đánh giá...'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'interviewer': forms.Select(attrs={'class': 'form-control'}),
            'interview_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'interview_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Địa điểm phỏng vấn'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Lý do từ chối...'}),
        }
