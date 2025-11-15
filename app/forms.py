# employee_app/forms.py
from django import forms
from .models import Employee, LeaveType, LeaveRequest, ExpenseCategory, Expense

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
