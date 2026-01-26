import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = ['.localhost', '127.0.0.1', 'localhost']

# --- SHARED & TENANT APPS ---
SHARED_APPS = [
    'django_tenants',
    'customers',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'marketing',
    'crispy_forms',
    'crispy_bootstrap5',
]

TENANT_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cms',
]

INSTALLED_APPS = list(set(SHARED_APPS + TENANT_APPS))

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'recruit_saas.debug_middleware.CustomTenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- COOKIES & CSRF ---
# 1. This ensures the cookie is shared across vf.localhost and localhost
SESSION_COOKIE_DOMAIN = ".localhost"
CSRF_COOKIE_DOMAIN = ".localhost"

# 2. Recommended for multi-tenant redirects
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# 3. Security settings for local development
CSRF_COOKIE_HTTPONLY = True   # <--- CHANGE THIS TO TRUE
CSRF_COOKIE_SECURE = False     # Must be False for http://
SESSION_COOKIE_SECURE = False  # Must be False for http://

# 4. Origins (You have these right, but double check the port)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://*.localhost:8000",
    "http://127.0.0.1:8000",
]

# --- DATABASE ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        engine="django_tenants.postgresql_backend",
    )
}

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
TENANT_MODEL = "customers.Client"
TENANT_DOMAIN_MODEL = "customers.Domain"

# --- URL ROUTING ---
ROOT_URLCONF = 'recruit_saas.urls'
PUBLIC_SCHEMA_URLCONF = 'recruit_saas.urls'
TENANT_URLCONF = 'recruit_saas.urls_tenant'

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"

# --- TEMPLATES ---
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
                'cms.context_processors.tenant_profile',
            ],
        },
    },
]

# --- STATIC FILES ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "marketing" / "static",
]

# --- MEDIA FILES ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- CRISPY FORMS ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'