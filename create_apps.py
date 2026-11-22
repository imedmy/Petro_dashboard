# create_apps.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APPS = [
    'dashboard',
    'articles',
    'commandes',
    'avis_arrivee',
    'stock',
    'tasks',
    'station',
    'parametrage',
    'users',
]

def create_app_structure(app_name):
    """إنشاء هيكل تطبيق Django كامل"""
    app_dir = BASE_DIR / 'apps' / app_name
    
    # إنشاء المجلدات
    dirs = [
        app_dir,
        app_dir / 'templates' / app_name,
        app_dir / 'static' / app_name,
        app_dir / 'migrations',
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    # الملفات الأساسية
    files = {
        '__init__.py': f"# apps/{app_name}/__init__.py\ndefault_app_config = 'apps.{app_name}.apps.{app_name.title().replace('_', '')}Config'\n",
        'apps.py': f"""# apps/{app_name}/apps.py
from django.apps import AppConfig

class {app_name.title().replace('_', '')}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{app_name.title()}'
""",
        'models.py': f'# apps/{app_name}/models.py\nfrom django.db import models\n\n# أضف النماذج هنا\n',
        'views.py': f'# apps/{app_name}/views.py\nfrom django.shortcuts import render\n\n# أضف الـ views هنا\n',
        'urls.py': f'# apps/{app_name}/urls.py\nfrom django.urls import path\nfrom . import views\n\napp_name = \'{app_name}\'\n\nurlpatterns = [\n    # path(\'\', views.index_view, name=\'index\'),\n]\n',
        'admin.py': f'# apps/{app_name}/admin.py\nfrom django.contrib import admin\n\n# سجل النماذج هنا\n',
        'tests.py': f'# apps/{app_name}/tests.py\nfrom django.test import TestCase\n\n# أضف الاختبارات هنا\n',
        'migrations/__init__.py': '',
    }
    
    for filename, content in files.items():
        filepath = app_dir / filename
        if not filepath.exists():
            filepath.write_text(content, encoding='utf-8')
    
    print(f'✅ تم إنشاء التطبيق: {app_name}')

if __name__ == '__main__':
    # إنشاء مجلد apps
    apps_dir = BASE_DIR / 'apps'
    apps_dir.mkdir(exist_ok=True)
    (apps_dir / '__init__.py').write_text('"""\nحزمة تحتوي على جميع تطبيقات المشروع\n"""\n')
    
    for app in APPS:
        create_app_structure(app)
    
    print('\n🎉 اكتمل إنشاء جميع التطبيقات!')
    print('الخطوة التالية: تحديث settings.py')