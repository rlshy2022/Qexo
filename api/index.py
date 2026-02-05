import os
import sys
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from pathlib import Path

# 1. 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. 初始化 Django (这步必须在 migrate 之前！)
app = get_wsgi_application()

# 3. 自动修复数据库 (Vercel 专用补丁)
# 只有当使用 SQLite 且文件不存在时才执行，避免重复运行
try:
    # 获取 settings 对象
    from django.conf import settings
    db_name = str(settings.DATABASES['default']['NAME'])
    
    # 检查是否是 /tmp 目录下的 sqlite 数据库，并且文件还不存在
    if db_name.startswith('/tmp') and not Path(db_name).exists():
        print("🚀 [Vercel] 正在初始化临时数据库...")
        call_command('migrate', interactive=False)
        print("✅ [Vercel] 数据库初始化完成！")
except Exception as e:
    # 打印错误但不要让程序崩溃
    print(f"⚠️ [Vercel] 数据库初始化跳过: {e}")
