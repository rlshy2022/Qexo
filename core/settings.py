from pathlib import Path
import os
import sys
import urllib3
# 👇 【关键补丁】解决 Django 5.0 移除了 ugettext 导致报错的问题
import django.utils.translation
if not hasattr(django.utils.translation, "ugettext"):
    django.utils.translation.ugettext = django.utils.translation.gettext
    django.utils.translation.ugettext_lazy = django.utils.translation.gettext_lazy

urllib3.disable_warnings()

BASE_DIR = Path(__file__).resolve().parent.parent

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-mrf1flh+i8*!ao73h6)ne#%gowhtype!ld#+(j^r*!^11al2vz')
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'hexoweb.apps.ConsoleConfig',
    'corsheaders',
    'passkeys',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

AUTHENTICATION_BACKENDS = [
    'passkeys.backend.PasskeyModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# =========================================================
# 👇 数据库配置（兼容 Vercel）
# =========================================================
if os.environ.get("MONGODB_HOST"):
    DATABASES = {
        'default': {
            'ENGINE': 'django_mongodb_backend',
            'NAME': os.environ.get("MONGODB_DB") or 'django',
            'HOST': os.environ.get("MONGODB_HOST"),
            'PORT': int(os.environ.get("MONGODB_PORT", 27017)),
            'USER': os.environ.get("MONGODB_USER"),
            'PASSWORD': os.environ.get("MONGODB_PASSWORD"),
            'OPTIONS': {'authSource': 'admin'},
        }
    }
else:
    # Vercel 只读环境专用
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path("/tmp") / "db.sqlite3",
        }
    }
# =========================================================

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_COOKIE_AGE = 86400

def get_fido_server_id(request=None):
    host = None
    if request:
        try:
            host = request.get_host()
        except Exception:
            host = None
    if not host:
        host = (ALLOWED_HOSTS[0] if ALLOWED_HOSTS else "localhost")
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.split(":", 1)[0].strip()
    return host if host else "localhost"

FIDO_SERVER_ID = get_fido_server_id
FIDO_SERVER_NAME = "Qexo"
KEY_ATTACHMENT = None

# 强制指定自增字段类型，减少 Django 5.x 的验证冲突
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 忽略系统检查警告
SILENCED_SYSTEM_CHECKS = ["fields.W342"]

# 关键：确保 SESSION 序列化使用 JSON（Qexo默认通常是这个，确认一下）
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
