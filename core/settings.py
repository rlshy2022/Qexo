from pathlib import Path
import os
import sys
import json
import logging
import urllib3

urllib3.disable_warnings()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# 生产环境密钥（建议后续在 Vercel 环境变量里设置）
SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-mrf1flh+i8*!ao73h6)ne#%gowhtype!ld#+(j^r*!^11al2vz')

# 调试模式（先开着，确保你能看到具体情况）
DEBUG = True

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'hexoweb.apps.ConsoleConfig',
    'corsheaders',
    'passkeys',  # 上一把修好的库
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
# 👇 这里的逻辑是本次修复的核心！
# =========================================================

# 1. 优先尝试连接 MongoDB (如果你在 Vercel 填了环境变量)
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
# 2. 没有任何配置时，启动【临时演示模式】(Vercel 专用)
else:
    # ⚠️ 关键点：使用 /tmp 目录，因为 Vercel 只有这里能写文件
    sqlite_db_path = Path("/tmp") / "db.sqlite3"
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_db_path,
        }
    }
    
    # 自动执行迁移！(解决 500 报错的关键：自动建表)
    # 只有在 Serverless 环境下且数据库文件不存在时才执行，防止卡死
    if not sqlite_db_path.exists():
        try:
            from django.core.management import call_command
            print("🚀 [Vercel Demo] 正在初始化临时数据库...")
            # 这里的 migrate 会创建必须的 session 和 auth 表
            call_command('migrate', interactive=False)
            print("✅ [Vercel Demo] 数据库初始化完成！")
        except Exception as e:
            print(f"⚠️ [Vercel Demo] 初始化警告: {e}")

# =========================================================
# 👆 修复结束
# =========================================================

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']

# Password validation
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

# Passkeys Configuration
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
