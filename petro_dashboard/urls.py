# petro_dashboard/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.conf.urls.static import static

# ✅ الاستيرادات الصحيحة
from accounts.views import login_view
from core import views as core_views  # ⬅️ تم الاستيراد

urlpatterns = [
    path('admin/', admin.site.urls),

    # تسجيل الدخول
    path('login/', login_view, name='login'),

    # لوحة التحكم
    path('', RedirectView.as_view(pattern_name='dashboard:index'), name='home'),
    
    # ✅ تطبيق Dashboard الجديد
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('articles/', include('apps.articles.urls', namespace='articles')),  
    path('users/', include('apps.users.urls', namespace='users')),
    # تضمين التطبيقات
    path('core/', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('projets/', include('apps.projets.urls', namespace='projets')),
    # تعدد اللغات
    path('i18n/', include('django.conf.urls.i18n'), name='set_language'),
]

# عرض الملفات الثابتة
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# تخصيص لوحة الإدارة
admin.site.site_header = _("إدارة منصة شركة البترول الوطنية")
admin.site.site_title = _("منصة البترول")
admin.site.index_title = _("مرحباً بك في النظام")