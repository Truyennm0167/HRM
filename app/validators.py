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


# ============= PASSWORD VALIDATORS =============

class PasswordComplexityValidator:
    """
    Validates that password meets complexity requirements:
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    
    def validate(self, password, user=None):
        import re
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất 1 chữ cái viết hoa."),
                code='password_no_upper',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất 1 chữ cái viết thường."),
                code='password_no_lower',
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất 1 chữ số."),
                code='password_no_digit',
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        return _(
            "Mật khẩu phải chứa ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt."
        )


class MaximumLengthValidator:
    """
    Validates that password is not too long (prevent DoS attacks)
    """
    
    def __init__(self, max_length=128):
        self.max_length = max_length
    
    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _("Mật khẩu không được dài quá %(max_length)d ký tự."),
                code='password_too_long',
                params={'max_length': self.max_length},
            )
    
    def get_help_text(self):
        return _(
            "Mật khẩu không được dài quá %(max_length)d ký tự."
            % {'max_length': self.max_length}
        )


class NoSpaceValidator:
    """
    Validates that password contains no spaces
    """
    
    def validate(self, password, user=None):
        if ' ' in password:
            raise ValidationError(
                _("Mật khẩu không được chứa khoảng trắng."),
                code='password_contains_space',
            )
    
    def get_help_text(self):
        return _("Mật khẩu không được chứa khoảng trắng.")


class NoEmailInPasswordValidator:
    """
    Validates that password doesn't contain user's email
    """
    
    def validate(self, password, user=None):
        if not user:
            return
        
        email = getattr(user, 'email', None)
        if not email:
            return
        
        # Check if any part of email is in password (case insensitive)
        email_parts = email.lower().split('@')[0].split('.')
        password_lower = password.lower()
        
        for part in email_parts:
            if len(part) >= 4 and part in password_lower:
                raise ValidationError(
                    _("Mật khẩu không được chứa phần nào của email."),
                    code='password_contains_email',
                )
    
    def get_help_text(self):
        return _("Mật khẩu không được chứa phần nào của địa chỉ email.")


class CommonPatternValidator:
    """
    Validates against common patterns like '123456', 'password', 'qwerty', etc.
    """
    
    COMMON_PATTERNS = [
        '123456', '1234567', '12345678', '123456789',
        'password', 'password123', 'pass123',
        'qwerty', 'qwerty123',
        'abc123', 'abcd1234',
        '111111', '000000',
        '123123', '456456',
    ]
    
    def validate(self, password, user=None):
        password_lower = password.lower()
        
        for pattern in self.COMMON_PATTERNS:
            if pattern in password_lower:
                raise ValidationError(
                    _("Mật khẩu chứa mẫu phổ biến không an toàn ('%(pattern)s')."),
                    code='password_common_pattern',
                    params={'pattern': pattern},
                )
    
    def get_help_text(self):
        return _("Mật khẩu không được chứa các mẫu phổ biến như '123456', 'password', 'qwerty'.")
