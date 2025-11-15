"""
Validators for HRM application
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os

# Constants
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image_file(file):
    """
    Validate uploaded image files.
    
    Args:
        file: UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
    """
    # Check file size
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            _(f'Kích thước file không được vượt quá {MAX_IMAGE_SIZE / (1024*1024):.0f}MB. '
              f'File của bạn: {file.size / (1024*1024):.2f}MB')
        )
    
    # Check file extension
    ext = os.path.splitext(file.name)[1][1:].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _(f'Định dạng file không được hỗ trợ. '
              f'Chỉ chấp nhận: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}')
        )
    
    return True


def validate_document_file(file):
    """
    Validate uploaded document files.
    
    Args:
        file: UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
    """
    # Check file size
    if file.size > MAX_DOCUMENT_SIZE:
        raise ValidationError(
            _(f'Kích thước file không được vượt quá {MAX_DOCUMENT_SIZE / (1024*1024):.0f}MB. '
              f'File của bạn: {file.size / (1024*1024):.2f}MB')
        )
    
    # Check file extension
    ext = os.path.splitext(file.name)[1][1:].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            _(f'Định dạng file không được hỗ trợ. '
              f'Chỉ chấp nhận: {", ".join(ALLOWED_DOCUMENT_EXTENSIONS)}')
        )
    
    return True


def validate_salary(value):
    """
    Validate salary value.
    
    Args:
        value: Salary amount
        
    Raises:
        ValidationError: If salary is invalid
    """
    try:
        salary = float(value)
        if salary < 0:
            raise ValidationError(_('Lương không thể là số âm'))
        if salary > 1000000000:  # 1 billion
            raise ValidationError(_('Lương không hợp lý'))
        return salary
    except (ValueError, TypeError):
        raise ValidationError(_('Lương phải là một số hợp lệ'))


def validate_phone_number(phone):
    """
    Validate Vietnamese phone number.
    
    Args:
        phone: Phone number string
        
    Raises:
        ValidationError: If phone number is invalid
    """
    import re
    # Vietnamese phone pattern: 10 digits, starts with 0
    pattern = r'^0\d{9}$'
    if not re.match(pattern, phone):
        raise ValidationError(
            _('Số điện thoại không hợp lệ. Phải có 10 chữ số và bắt đầu bằng 0')
        )
    return True


def validate_email(email):
    """
    Validate email address.
    
    Args:
        email: Email string
        
    Raises:
        ValidationError: If email is invalid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(_('Địa chỉ email không hợp lệ'))
    return True
