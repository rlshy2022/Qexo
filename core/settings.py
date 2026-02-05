from pathlib import Path
import os
import json
import random
import hexoweb.exceptions as exceptions
import logging
import urllib3

urllib3.disable_warnings()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-mrf1flh+i8*!ao73h6)ne#%gowhtype!ld#+(j^r*!^11al2vz'

# SECURITY WARNING: don't run with debug turned on in production!
# 为了方便调试，我先暂时设为 True，等你网站跑通了再改回 False
DEBUG = True 

LOCAL_CONFIG = False

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
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

# WebAuthn / Passkeys Configuration
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

WSGI_APPLICATION = 'core.wsgi.application' # 注意这里，配合我们之前改的 api/index.py 和 wsgi.py

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# =========================================================
# 👇 欢欢注意：这里是关键修改！强制使用 SQLite，暂时屏蔽其他数据库逻辑
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 原来的复杂逻辑先全部注释掉，防止报错
"""
errors = ""
if os.environ.get("MONGODB_HOST"):
    # ... (省略)
elif os.environ.get("MYSQL_HOST"):
    # ... (省略)
elif os.path.exists(BASE_DIR / "configs.py"):
    import configs
    DATABASES = configs.DATABASES
    LOCAL_CONFIG = True
else:
    errors = "数据库"

if errors:
    # 这一段必须注释掉，否则没有环境变量时会直接报错阻止启动
    logging.error(f"{errors}未设置...")
    raise exceptions.InitError(f"{errors}未设置...")
"""

# =========================================================
# 👆 修改结束
# =========================================================


def _load_allowed_hosts(local_config):
    # 这个函数暂时用不到，因为下面直接覆盖了 ALLOWED_HOSTS
    return ['*']


def _build_csrf_trusted_origins(hosts):
    origins = []
    for host in hosts:
        if (not host) or host == "*":
            continue
        host = host.rstrip("/")
        if "://" in host:
            origins.append(host)
        else:
            origins.append(f"https://{host}")
            origins.append(f"http://{host}")
    return origins

# 允许所有域名访问，防止 Vercel 动态域名被拦截
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True


USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = 'static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 86400

# Passkeys / WebAuthn Configuration
def get_fido_server_id(request=None):
    """动态获取FIDO Server ID（RP ID），与当前访问域名保持一致。"""
    host = None

    # 优先使用实际请求域名（包含端口时去掉端口）
    if request:
        try:
            host = request.get_host()
        except Exception:
            host = None

    # 回退到ALLOWED_HOSTS配置
    if not host:
        host = (ALLOWED_HOSTS[0] if ALLOWED_HOSTS else "localhost")

    # 清理协议和端口
    if "://" in host:
        host = host.split("://", 1)[1]
    host = host.split(":", 1)[0].strip()

    # FIDO要求RP ID是有效的注册域或localhost
    if not host:
        return "localhost"

    return host

FIDO_SERVER_ID = get_fido_server_id
FIDO_SERVER_NAME = "Qexo"
KEY_ATTACHMENT = None  # 允许任何类型的认证器（平台或跨平台）
