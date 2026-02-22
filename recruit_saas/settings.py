import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'getpillarpost.com',
    'www.getpillarpost.com',
    '.getpillarpost.com',
    'recruitmentsaas.herokuapp.com',
    '.herokuapp.com',
    'localhost',
    '.localhost',
    '127.0.0.1',
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
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
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

CSRF_TRUSTED_ORIGINS = [
    "https://*.getpillarpost.com",
    "https://getpillarpost.com",
    "https://*.herokuapp.com", #
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
# Security settings for local development
CSRF_COOKIE_HTTPONLY = False  
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# middleware settings for cookies
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = '.getpillarpost.com'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# --- DATABASE ---
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        engine="django_tenants.postgresql_backend",
        ssl_require=os.getenv('DATABASE_SSL', 'True') == 'True'
    )
}

DATABASES['default']['TEST'] = {
    'NAME': 'test_recruitment_v6',
}


DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
TENANT_MODEL = "customers.Client"
TENANT_DOMAIN_MODEL = "customers.Domain"
DEFAULT_SCHEMA_NAME = "public"
AUTO_CREATE_SCHEMA = True


# --- URL ROUTING ---
ROOT_URLCONF = 'recruit_saas.urls'
PUBLIC_SCHEMA_URLCONF = 'recruit_saas.urls_public'
TENANT_URLCONF = 'recruit_saas.urls_tenant'

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = 'https://getpillarpost.com/'

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'libraries': {
                'tenant_tags': 'marketing.templatetags.tenant_tags',
            },
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
STATICFILES_DIRS = []


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

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}


# fallback
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Stripe Settings
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


# Email Settings (zoho)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'hello@getpillarpost.com')