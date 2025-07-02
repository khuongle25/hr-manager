# Phase 1: Thiết lập môi trường và cấu trúc cơ bản

## Mục tiêu học tập

- Hiểu cấu trúc dự án Django chuẩn doanh nghiệp
- Thiết lập môi trường development với PostgreSQL và Redis
- Cấu hình Django settings cho development/production
- Thiết lập authentication và authorization cơ bản

## Bước 1: Cài đặt môi trường

### 1.1 Cài đặt Python và PostgreSQL

#### Ubuntu/Debian:

```bash
# Cài đặt Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Cài đặt PostgreSQL
sudo apt install postgresql postgresql-contrib

# Cài đặt Redis
sudo apt install redis-server
```

#### macOS:

```bash
# Sử dụng Homebrew
brew install python@3.11
brew install postgresql
brew install redis
```

### 1.2 Thiết lập PostgreSQL

```bash
# Khởi động PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Tạo database và user
sudo -u postgres psql
CREATE DATABASE hr_management;
CREATE USER hr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE hr_management TO hr_user;
\q
```

### 1.3 Thiết lập Redis

```bash
# Khởi động Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Kết quả: PONG
```

## Bước 2: Tạo dự án Django

### 2.1 Tạo virtual environment

```bash
# Tạo virtual environment
python3.11 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate  # Linux/macOS
# hoặc venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2.2 Tạo cấu trúc dự án

```bash
# Tạo Django project
django-admin startproject hr_management .

# Tạo thư mục apps
mkdir apps
cd apps
django-admin startapp users
django-admin startapp leave_management
django-admin startapp departments
django-admin startapp ai_agents
cd ..

# Tạo các thư mục cần thiết
mkdir static templates media tests docs
```

## Bước 3: Cấu hình Django Settings

### 3.1 Tạo file settings phân tách

Tạo cấu trúc settings như sau:

```python
# hr_management/settings/base.py
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'crispy_bootstrap5',
    'debug_toolbar',
]

LOCAL_APPS = [
    'apps.users',
    'apps.leave_management',
    'apps.departments',
    'apps.ai_agents',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'hr_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'hr_management.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Django Allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 3.2 Tạo file settings cho development

```python
# hr_management/settings/development.py
from .base import *

DEBUG = True

# Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 3.3 Tạo file settings cho production

```python
# hr_management/settings/production.py
from .base import *

DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

## Bước 4: Tạo Custom User Model

### 4.1 Tạo User model trong apps/users/models.py

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('hr', 'HR'),
        ('team_lead', 'Team Lead'),
        ('employee', 'Employee'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
```

### 4.2 Tạo admin cho User model

```python
# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('HR Information', {'fields': ('role', 'employee_id', 'phone', 'address', 'date_of_birth', 'hire_date')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('HR Information', {'fields': ('role', 'employee_id', 'phone', 'address', 'date_of_birth', 'hire_date')}),
    )
```

## Bước 5: Chạy migrations và tạo superuser

```bash
# Tạo migrations
python manage.py makemigrations

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy development server
python manage.py runserver
```

## Bước 6: Test cấu hình

### 6.1 Test database connection

```python
# Trong Django shell
python manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT version();")
>>> cursor.fetchone()
```

### 6.2 Test Redis connection

```python
# Trong Django shell
>>> from django.core.cache import cache
>>> cache.set('test_key', 'test_value', 30)
>>> cache.get('test_key')
'test_value'
```

## Bài tập thực hành

### Bài tập 1: Tạo User với role khác nhau

1. Tạo 3 user với role khác nhau (HR, Team Lead, Employee)
2. Test login với từng user
3. Tạo custom permission cho từng role

### Bài tập 2: Cấu hình Email

1. Cấu hình email backend cho development
2. Test gửi email thông báo
3. Tạo email template

### Bài tập 3: Redis Caching

1. Cache user session
2. Cache database queries
3. Implement cache invalidation

## Kiểm tra kiến thức

Sau khi hoàn thành Phase 1, bạn cần hiểu:

- [ ] Cấu trúc dự án Django chuẩn doanh nghiệp
- [ ] Cấu hình PostgreSQL và Redis
- [ ] Custom User model và authentication
- [ ] Django settings cho development/production
- [ ] Basic logging và monitoring

## Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
