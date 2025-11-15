from django import forms
from .models import Resume, JobDescription

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file', 'accept': '.pdf,.doc,.docx'})
        }

class JobDescriptionForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Python Developer'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 
                                    'placeholder': 'Mô tả chi tiết về công việc...'})
    )
    required_skills = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                    'placeholder': 'Mỗi kỹ năng một dòng\nVí dụ:\nPython\nDjango\nMySQL'}),
        help_text='Nhập mỗi kỹ năng trên một dòng'
    )
    nice_to_have_skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                    'placeholder': 'Mỗi kỹ năng một dòng\nVí dụ:\nDocker\nAWS'}),
        help_text='Nhập mỗi kỹ năng trên một dòng (không bắt buộc)'
    )
    required_years_experience = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 2'})
    )
    required_degrees = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                    'placeholder': 'Mỗi bằng cấp một dòng\nVí dụ:\nCử nhân Công nghệ thông tin\nThạc sĩ Khoa học máy tính'}),
        help_text='Nhập mỗi bằng cấp trên một dòng (không bắt buộc)'
    )

    def save(self):
        data = self.cleaned_data
        # Convert text to JSON arrays
        data['required_skills'] = [s.strip() for s in data['required_skills'].split('\n') if s.strip()]
        data['nice_to_have_skills'] = [s.strip() for s in data['nice_to_have_skills'].split('\n') if s.strip()] if data.get('nice_to_have_skills') else []
        data['required_degrees'] = [d.strip() for d in data['required_degrees'].split('\n') if d.strip()] if data.get('required_degrees') else []
        
        return JobDescription.objects.create(**data)