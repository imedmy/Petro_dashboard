"""
URLs for user authentication and management in accounts app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # يمكنك إضافة views مخصصة لاحقًا

app_name = 'Magasin_SITEP'  # مساحة أسماء لتجنب التعارض

urlpatterns = [
    # تسجيل الدخول
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True  # منع الدخول المكرر
        ),
        name='login'
    ),

    # تسجيل الخروج
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login'  # العودة لصفحة الدخول بعد الخروج
        ),
        name='logout'
    ),

    # إعادة تعيين كلمة المرور (اختياري - جاهز من Django)
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt'
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # ملفات تعريف المستخدم (يمكنك تفعيلها لاحقًا)
    # path('profile/', views.profile, name='profile'),
    # path('change-password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    # path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]


