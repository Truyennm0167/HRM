"""
Test script for password validation
Tests various password scenarios against the security policy
"""

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

print("=" * 60)
print("TESTING PASSWORD POLICIES")
print("=" * 60)

# Test cases: (password, should_pass, reason)
test_cases = [
    ("weak", False, "Too short, no uppercase, no digit, no special char"),
    ("password123", False, "No uppercase, no special char, common pattern"),
    ("Password123", False, "No special character"),
    ("Pass1!", False, "Too short (minimum 10 chars)"),
    ("MyPassword1!", True, "Valid: meets all requirements"),
    ("Secure#HRM$2024", True, "Valid: meets all requirements"),
    ("admin Admin1!", False, "Contains username part"),
    ("123456789A!", False, "Common pattern (123456789)"),
    ("Pass word1!", False, "Contains space"),
    ("MyP@ssw0rd2024!", True, "Valid: strong password"),
    ("a" * 129 + "A1!", False, "Too long (>128 chars)"),
]

print("\n{:<25} {:<10} {:<40}".format("Password", "Result", "Reason"))
print("-" * 75)

for password, should_pass, reason in test_cases:
    # Create dummy user for testing
    test_user = User(username='testuser', email='test@example.com')
    
    try:
        validate_password(password, user=test_user)
        result = "✓ PASS"
        if not should_pass:
            result = "✗ FAIL (Expected to fail!)"
    except ValidationError as e:
        result = "✗ FAIL"
        if should_pass:
            result = f"✗ FAIL (Should pass!)"
            print(f"\n  Errors: {', '.join(e.messages)}")
    
    # Truncate long passwords for display
    display_pwd = password if len(password) <= 20 else password[:17] + "..."
    print(f"{display_pwd:<25} {result:<10} {reason}")

print("\n" + "=" * 60)
print("PASSWORD POLICY REQUIREMENTS:")
print("=" * 60)
print("""
✓ Minimum 10 characters
✓ At least 1 uppercase letter (A-Z)
✓ At least 1 lowercase letter (a-z)
✓ At least 1 digit (0-9)
✓ At least 1 special character (!@#$%^&*(),.?":{}<>)
✓ Maximum 128 characters
✓ No spaces allowed
✓ Cannot contain email parts
✓ Cannot contain common patterns (123456, password, qwerty)
""")

print("=" * 60)
print("RECOMMENDATION: Use passwords like 'MyP@ssw0rd2024!'")
print("=" * 60)
