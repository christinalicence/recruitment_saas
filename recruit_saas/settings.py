import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = False

ALLOWED_HOSTS = [
            '.herokuapp.com',
            '.localhost',
            '127.0.0.1',
            'localhost',
        ]

# --- SHARED & TENANT APPS ---
SHARED_APPS = [
    'django_tenants',
    'customers',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'cloudinary',      
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
    'cloudinary',
]

INSTALLED_APPS = SHARED_APPS + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]


# --- MIDDLEWARE ---
MIDDLEWARE = [
    'recruit_saas.debug_middleware.CustomTenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'recruit_saas.debug_middleware.SubscriptionGuardMiddleware',
]

# Allow iframe embedding for tenant preview
X_FRAME_OPTIONS = 'SAMEORIGIN'

# --- COOKIES & CSRF ---
# We comment these out for localhost development to avoid 403 errors.
# SESSION_COOKIE_DOMAIN = ".localhost"
# CSRF_COOKIE_DOMAIN = ".localhost"

# Ensure Django trusts the subdomain origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://*.localhost:8000",
]

# Security settings for local development
CSRF_COOKIE_HTTPONLY = False  # Allows Django's CSRF middleware to see it
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# middleware settings for cookies
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

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
    BASE_DIR / "cms" / "static",
]


# --- CRISPY FORMS ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CLOUDINARY CONFIG ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET')
}

# Use the modern STORAGES dictionary (Django 4.2+)
# This forces Cloudinary for EVERYTHING uploaded via a model ImageField
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'

# Keep these local for your default/fallback images
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Stripe Settings
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
SITE_URL = 'http://localhost:8000'  # for local dev

# Email Settings (Console Backend for Development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'