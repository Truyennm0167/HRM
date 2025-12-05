# Production Settings Template
# Copy this to settings.py or create settings_production.py

"""
PRODUCTION DEPLOYMENT CHECKLIST

Before deploying to production:
1. ✓ Set DEBUG = False
2. ✓ Generate new SECRET_KEY
3. ✓ Configure ALLOWED_HOSTS
4. ✓ Setup HTTPS/SSL
5. ✓ Configure database (PostgreSQL recommended)
6. ✓ Setup static files serving
7. ✓ Configure email backend
8. ✓ Setup error logging
9. ✓ Configure backup strategy
10. ✓ Review all security settings
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Generate new key: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = os.getenv('SECRET_KEY')  # MUST set in environment variable
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# IMPORTANT: Add your production domain/IP
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError("ALLOWED_HOSTS must be set in production")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'app',
    'ai_recruitment',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom security middleware
    'app.middleware.SecurityHeadersMiddleware',
    'app.middleware.UserGroupMiddleware',
    'app.middleware.LoginAttemptMiddleware',
]

ROOT_URLCONF = 'hrm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hrm.wsgi.application'

# Database - PostgreSQL recommended for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'hrm_production'),
        'USER': os.getenv('DB_USER', 'hrm_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Persistent connections
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Custom validators
    {
        'NAME': 'app.validators.PasswordComplexityValidator',
    },
    {
        'NAME': 'app.validators.MaximumLengthValidator',
        'OPTIONS': {
            'max_length': 128,
        }
    },
    {
        'NAME': 'app.validators.NoSpaceValidator',
    },
    {
        'NAME': 'app.validators.NoEmailInPasswordValidator',
    },
    {
        'NAME': 'app.validators.CommonPatternValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'  # Vietnam timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# SECURITY SETTINGS FOR PRODUCTION
# ============================================================

# HTTPS/SSL Configuration
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SESSION_COOKIE_SECURE = True  # Cookies only sent over HTTPS
CSRF_COOKIE_SECURE = True  # CSRF cookies only over HTTPS

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session Security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_NAME = 'hrm_sessionid'

# CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_NAME = 'hrm_csrftoken'

# Content Security Policy (optional, but recommended)
# Requires django-csp package
# CSP_DEFAULT_SRC = ("'self'",)
# CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
# CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ============================================================
# EMAIL CONFIGURATION
# ============================================================

# Email backend for production (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@yourcompany.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'admin@yourcompany.com')

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'hrm.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'hrm_errors.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'app': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'ai_recruitment': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'error_file', 'console'],
        'level': 'INFO',
    },
}

# ============================================================
# CACHING (Optional but recommended for production)
# ============================================================

# Redis cache (install django-redis)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# ============================================================
# ADMIN CONFIGURATION
# ============================================================

ADMINS = [
    ('Admin Name', os.getenv('ADMIN_EMAIL', 'admin@yourcompany.com')),
]

MANAGERS = ADMINS

# ============================================================
# FILE UPLOAD SETTINGS
# ============================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB

# ============================================================
# ENVIRONMENT VARIABLES REQUIRED
# ============================================================
"""
Required environment variables:

SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEBUG=False

# Database
DB_NAME=hrm_production
DB_USER=hrm_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@yourcompany.com

# Admin
ADMIN_EMAIL=admin@yourcompany.com

# Optional
REDIS_URL=redis://127.0.0.1:6379/1
"""

# ============================================================
# DEPLOYMENT COMMANDS
# ============================================================
"""
1. Setup environment variables
2. Install dependencies: pip install -r requirements.txt
3. Create logs directory: mkdir logs
4. Collect static files: python manage.py collectstatic --noinput
5. Run migrations: python manage.py migrate
6. Setup groups: python manage.py setup_groups_permissions
7. Assign users: python manage.py assign_user_groups
8. Create superuser: python manage.py createsuperuser
9. Test: python manage.py check --deploy
10. Start server with gunicorn: gunicorn hrm.wsgi:application --bind 0.0.0.0:8000
"""
