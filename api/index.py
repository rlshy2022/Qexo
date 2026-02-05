import os
from django.core.wsgi import get_wsgi_application

# 必须指向你的 settings 文件位置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = get_wsgi_application()
