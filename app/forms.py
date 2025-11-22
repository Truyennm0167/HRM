# employee_app/forms.py
from django import forms
from .models import (Employee, LeaveType, LeaveRequest, ExpenseCategory, Expense, 
                     Contract, JobPosting, Application, AppraisalPeriod, 
                     AppraisalCriteria, Appraisal, AppraisalScore)

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


class EmployeeProfileForm(forms.ModelForm):
    """Form để nhân viên tự chỉnh sửa thông tin cá nhân (giới hạn)"""
    class Meta:
        model = Employee
        fields = ['phone', 'address', 'email', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Số điện thoại'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Địa chỉ hiện tại'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Check if phone already exists (excluding current employee)
            existing = Employee.objects.filter(phone=phone).exclude(id=self.instance.id)
            if existing.exists():
                raise forms.ValidationError("Số điện thoại này đã được sử dụng")
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists (excluding current employee)
            existing = Employee.objects.filter(email=email).exclude(id=self.instance.id)
            if existing.exists():
                raise forms.ValidationError("Email này đã được sử dụng")
        return email


class PasswordChangeForm(forms.Form):
    """Form để nhân viên đổi mật khẩu"""
    old_password = forms.CharField(
        label="Mật khẩu hiện tại",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu hiện tại'
        })
    )
    new_password = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới'
        })
    )
    confirm_password = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu mới'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Mật khẩu hiện tại không đúng")
        return old_password
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        
        # Validate password strength
        if len(new_password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự")
        
        if new_password.isdigit():
            raise forms.ValidationError("Mật khẩu không thể chỉ chứa số")
        
        if new_password.isalpha():
            raise forms.ValidationError("Mật khẩu phải chứa cả chữ và số")
        
        return new_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        old_password = cleaned_data.get('old_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Mật khẩu mới và xác nhận không khớp")
        
        if old_password and new_password:
            if old_password == new_password:
                raise forms.ValidationError("Mật khẩu mới phải khác mật khẩu hiện tại")
        
        return cleaned_data


class ContractForm(forms.ModelForm):
    """Form để tạo/sửa hợp đồng lao động"""
    class Meta:
        model = Contract
        fields = [
            'employee', 'contract_type', 'start_date', 'end_date', 'signed_date',
            'base_salary', 'job_title', 'department', 'work_location', 
            'working_hours', 'terms', 'notes', 'attachment', 'status'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control select2'}),
            'contract_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'signed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '100000',
                'placeholder': 'Nhập mức lương cơ bản (VNĐ)'
            }),
            'job_title': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'work_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Địa điểm làm việc'
            }),
            'working_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 8:00-17:00'
            }),
            'terms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Các điều khoản hợp đồng...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ghi chú...'
            }),
            'attachment': forms.FileInput(attrs={
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
    
    def clean_base_salary(self):
        salary = self.cleaned_data.get('base_salary')
        if salary and salary <= 0:
            raise forms.ValidationError("Mức lương phải lớn hơn 0")
        return salary


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


# ============================================================================
# APPRAISAL FORMS
# ============================================================================

class AppraisalPeriodForm(forms.ModelForm):
    """Form cho HR tạo/sửa kỳ đánh giá"""
    class Meta:
        model = AppraisalPeriod
        fields = ['name', 'description', 'start_date', 'end_date', 
                  'self_assessment_deadline', 'manager_review_deadline',
                  'status', 'applicable_departments', 'applicable_job_titles']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Đánh giá năm 2025'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'self_assessment_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manager_review_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'applicable_departments': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
            'applicable_job_titles': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        }


class AppraisalCriteriaForm(forms.ModelForm):
    """Form để thêm tiêu chí đánh giá vào kỳ"""
    class Meta:
        model = AppraisalCriteria
        fields = ['name', 'description', 'category', 'weight', 'max_score', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Chất lượng công việc'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'value': '5', 'min': '1'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'value': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make order field optional with default value
        self.fields['order'].required = False
        self.fields['order'].initial = 0


class SelfAssessmentForm(forms.ModelForm):
    """Form cho nhân viên tự đánh giá"""
    class Meta:
        model = Appraisal
        fields = ['self_comments', 'self_achievements', 'self_challenges', 'self_development_plan']
        widgets = {
            'self_comments': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Nhận xét chung về công việc của bạn trong kỳ...'
            }),
            'self_achievements': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Liệt kê các thành tích nổi bật...'
            }),
            'self_challenges': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Những khó khăn bạn gặp phải...'
            }),
            'self_development_plan': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Kế hoạch phát triển bản thân trong năm tới...'
            }),
        }


class ManagerReviewForm(forms.ModelForm):
    """Form cho quản lý đánh giá nhân viên"""
    class Meta:
        model = Appraisal
        fields = ['manager_comments', 'manager_strengths', 'manager_weaknesses', 
                  'manager_recommendations', 'promotion_recommended', 'training_recommended']
        widgets = {
            'manager_comments': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Nhận xét chung về nhân viên...'
            }),
            'manager_strengths': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Điểm mạnh của nhân viên...'
            }),
            'manager_weaknesses': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Điểm cần cải thiện...'
            }),
            'manager_recommendations': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Đề xuất về thăng chức, tăng lương, đào tạo...'
            }),
            'promotion_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'training_recommended': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Các khóa đào tạo đề xuất...'
            }),
        }


class AppraisalScoreForm(forms.ModelForm):
    """Form để nhập điểm cho từng tiêu chí"""
    class Meta:
        model = AppraisalScore
        fields = ['self_score', 'self_comment', 'manager_score', 'manager_comment']
        widgets = {
            'self_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'self_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'manager_score': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'manager_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class HRFinalReviewForm(forms.ModelForm):
    """Form cho HR hoàn tất đánh giá"""
    class Meta:
        model = Appraisal
        fields = ['overall_rating', 'hr_comments', 'salary_adjustment']
        widgets = {
            'overall_rating': forms.Select(attrs={'class': 'form-control'}),
            'hr_comments': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Nhận xét cuối cùng của HR...'
            }),
            'salary_adjustment': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '100000', 
                'placeholder': 'Điều chỉnh lương (VD: 1000000 = tăng 1 triệu)'
            }),
        }
