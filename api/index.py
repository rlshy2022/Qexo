import os
import sys
# 👇 【关键】把补丁放在所有代码的最前面，防止加载报错
import django.utils.translation
if not hasattr(django.utils.translation, "ugettext"):
    django.utils.translation.ugettext = django.utils.translation.gettext
    django.utils.translation.ugettext_lazy = django.utils.translation.gettext_lazy

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from pathlib import Path

# 1. 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. 初始化 Django
app = get_wsgi_application()

# 3. 自动修复数据库 (Vercel 专用)
try:
    from django.conf import settings
    # 确保 DATABASES 配置存在且有 NAME 字段
    if 'default' in settings.DATABASES and 'NAME' in settings.DATABASES['default']:
        db_name = str(settings.DATABASES['default']['NAME'])
        
        # 检查是否是 /tmp 目录下的 sqlite 数据库，并且文件还不存在
        if db_name.startswith('/tmp') and not Path(db_name).exists():
            print("🚀 [Vercel] 正在初始化临时数据库...")
            call_command('migrate', interactive=False)
            print("✅ [Vercel] 数据库初始化完成！")
except Exception as e:
    # 打印错误但不要让程序崩溃
    print(f"⚠️ [Vercel] 数据库初始化跳过: {e}")
