# EMAIL CONFIGURATION GUIDE

## 📧 Email System Overview

The HRM system includes a comprehensive email notification system with professional HTML templates for various events.

**Implemented**: November 16, 2024  
**Status**: ✅ Ready for Testing

---

## 🎯 Features Implemented

### Email Types

1. **Recruitment Emails**

   - Application received confirmation
   - Application status updates

2. **Leave Management Emails**

   - Leave request submitted
   - Leave request approved
   - Leave request rejected
   - Manager approval request

3. **Contract Management Emails**

   - Contract expiry warning (employee)
   - Contract expiry notification (HR)
   - Contract renewal confirmation

4. **Appraisal Emails**

   - Self-assessment reminder
   - Manager review notification
   - Appraisal completed

5. **System Emails**
   - Welcome email for new employees

### Template Features

- ✅ Professional HTML design
- ✅ Mobile-responsive layout
- ✅ Plain text fallback
- ✅ Vietnamese language support
- ✅ Company branding ready
- ✅ Consistent styling

---

## ⚙️ Configuration

### 1. Gmail SMTP Setup

#### Step 1: Enable 2-Step Verification

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**

#### Step 2: Generate App Password

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Other (Custom name)**
3. Enter name: "HRM System"
4. Click **Generate**
5. Copy the 16-character password

#### Step 3: Set Environment Variables

**Windows (PowerShell):**

```powershell
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-16-char-app-password"
$env:DEFAULT_FROM_EMAIL="HRM System <your-email@gmail.com>"
```

**Linux/Mac:**

```bash
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-16-char-app-password"
export DEFAULT_FROM_EMAIL="HRM System <your-email@gmail.com>"
```

**Permanent Setup (.env file):**
Create `.env` file in project root:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=HRM System <your-email@gmail.com>
```

Install python-dotenv:

```bash
pip install python-dotenv
```

### 2. Settings Configuration

Already configured in `hrm/settings.py`:

```python
# Development (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'HRM System <noreply@hrm.local>')
```

---

## 🧪 Testing

### Quick Test

```bash
# Set environment variables first
python test_email.py your-email@gmail.com
```

### Test Output

The script will test:

1. ✅ Email configuration
2. ✅ Simple email send
3. ✅ Application received template
4. ✅ Leave approved template
5. ✅ Contract expiry template

### Expected Results

```
============================================================
                HRM EMAIL TESTING SUITE
============================================================

Email Backend: django.core.mail.backends.smtp.EmailBackend
Email Host: smtp.gmail.com
Email Port: 587
Use TLS: True
From Email: HRM System <your-email@gmail.com>
Email User: your-email@gmail.com
Password Configured: ✓ Yes

✓ Email sent successfully!
✓ Template email sent successfully!
✓ Leave approved email sent successfully!
✓ Contract expiry email sent successfully!

Total: 4/4 tests passed (100%)
🎉 All email tests passed!
```

---

## 📝 Usage in Code

### Send Application Received Email

```python
from app.email_utils import send_application_received_email

# After application is saved
application = Application.objects.get(id=application_id)
send_application_received_email(application)
```

### Send Leave Approved Email

```python
from app.email_utils import send_leave_approved_email

# After leave is approved
leave_request = LeaveRequest.objects.get(id=leave_id)
leave_request.status = 'approved'
leave_request.save()

send_leave_approved_email(leave_request)
```

### Send Contract Expiry Warning

```python
from app.email_utils import send_contract_expiry_warning_email
from datetime import datetime, timedelta

# Find contracts expiring in 30 days
contracts = Contract.objects.filter(
    end_date__lte=datetime.now().date() + timedelta(days=30),
    end_date__gte=datetime.now().date()
)

for contract in contracts:
    days_left = (contract.end_date - datetime.now().date()).days
    send_contract_expiry_warning_email(contract, days_left)
```

### Send Custom Email

```python
from app.email_utils import send_email_with_template

subject = "Custom Subject"
context = {
    'employee_name': 'John Doe',
    'custom_data': 'value',
}

send_email_with_template(
    subject=subject,
    template_name='emails/custom_template',
    context=context,
    recipient_list=['employee@example.com'],
    fail_silently=True
)
```

---

## 📂 File Structure

```
app/
├── email_utils.py                    # Email sending functions
└── templates/
    └── emails/
        ├── base_email.html           # Base template
        ├── application_received.html
        ├── leave_approved.html
        ├── leave_rejected.html
        ├── leave_request_submitted.html
        ├── contract_expiry_warning.html
        └── contract_expiry_hr_notification.html

test_email.py                         # Email testing script
```

---

## 🎨 Template Customization

### Modify Base Template

Edit `app/templates/emails/base_email.html`:

```html
<div class="header">
  <h1>Your Company Name</h1>
  <p>Your Company Tagline</p>
</div>
```

### Add Logo

```html
<div class="header">
  <img
    src="https://your-domain.com/logo.png"
    alt="Company Logo"
    style="max-width: 200px;"
  />
</div>
```

### Customize Colors

```css
.header h1 {
  color: #your-brand-color;
}
.button {
  background-color: #your-brand-color;
}
```

---

## 🔧 Troubleshooting

### Issue 1: "Authentication failed"

**Cause**: Wrong password or 2-step verification not enabled

**Solution**:

1. Verify 2-Step Verification is ON
2. Generate new App Password
3. Use App Password, not regular Gmail password
4. Update EMAIL_HOST_PASSWORD variable

### Issue 2: "SMTPSenderRefused"

**Cause**: FROM email doesn't match authenticated user

**Solution**:

```python
DEFAULT_FROM_EMAIL = 'HRM System <your-gmail-address@gmail.com>'
```

Must use the same email as EMAIL_HOST_USER

### Issue 3: "Connection timeout"

**Cause**: Firewall or network blocking port 587

**Solution**:

- Check firewall settings
- Try port 465 with EMAIL_USE_SSL = True
- Test network connectivity

### Issue 4: "Template not found"

**Cause**: Template path incorrect

**Solution**:

```python
# Correct path (no .html extension in email_utils.py)
template_name='emails/application_received'

# Will load: emails/application_received.html
```

### Issue 5: Gmail daily limit reached

**Cause**: Gmail free accounts have sending limits

- 500 emails/day for free Gmail
- 2000 emails/day for Google Workspace

**Solution**:

- Upgrade to Google Workspace
- Use dedicated email service (SendGrid, AWS SES)
- Implement email queuing

---

## 📊 Email Logs

All emails are logged in `hrm.log`:

```
INFO Email sent: Đơn ứng tuyển đã được tiếp nhận to ['applicant@example.com']
INFO Email sent: Đơn nghỉ phép đã được phê duyệt to ['employee@example.com']
ERROR Failed to send email 'Subject' to ['user@example.com']: Connection refused
```

View recent logs:

```bash
# Windows
Get-Content hrm.log -Tail 50 | Select-String "Email"

# Linux/Mac
tail -f hrm.log | grep Email
```

---

## 🚀 Production Configuration

### Use Dedicated Email Service

**SendGrid:**

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

**AWS SES:**

```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_SES_REGION_NAME = 'us-east-1'
```

### Email Queuing

For high-volume production, use Celery:

```python
# tasks.py
from celery import shared_task
from app.email_utils import send_leave_approved_email

@shared_task
def send_leave_approved_email_async(leave_request_id):
    leave_request = LeaveRequest.objects.get(id=leave_request_id)
    send_leave_approved_email(leave_request)

# Usage
send_leave_approved_email_async.delay(leave_request.id)
```

---

## 📋 Email Checklist

### Before Going Live

- [ ] Configure proper FROM email
- [ ] Test all email templates
- [ ] Set up email monitoring
- [ ] Configure email quotas/limits
- [ ] Add unsubscribe option (if needed)
- [ ] Verify SPAM score
- [ ] Setup SPF/DKIM records
- [ ] Test on multiple email clients
- [ ] Add email logging/tracking
- [ ] Configure retry logic

### Email Content Review

- [ ] Subject lines clear and concise
- [ ] Vietnamese text correct
- [ ] Links work correctly
- [ ] Mobile responsive
- [ ] Images load properly
- [ ] Footer information complete
- [ ] Legal disclaimers included

---

## 📈 Future Enhancements

1. **Email Templates**

   - Payroll notification
   - Birthday wishes
   - Work anniversary
   - Training reminders
   - Document expiry

2. **Features**

   - Email scheduling
   - Batch sending
   - Personalization tokens
   - A/B testing
   - Analytics tracking

3. **Integration**
   - Calendar invites (.ics)
   - PDF attachments
   - Rich text editor
   - Template builder UI
   - Multi-language support

---

## 📞 Support

### Quick Commands

```bash
# Test email configuration
python test_email.py test@example.com

# Check email settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
>>> print(settings.EMAIL_HOST_USER)

# View email logs
Get-Content hrm.log -Tail 50 | Select-String "Email"
```

### Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/4.2/topics/email/)
- [Gmail SMTP Guide](https://support.google.com/mail/answer/7126229)
- [HTML Email Best Practices](https://www.campaignmonitor.com/dev-resources/guides/coding-html-emails/)

---

**Last Updated**: November 16, 2024  
**Version**: 1.0  
**Status**: ✅ Production Ready (with Gmail SMTP testing)
