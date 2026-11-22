# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse, NoReverseMatch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ✅ تسجيل الدخول - بدون @login_required
# =============================================================================
def login_view(request):
    """
    عرض صفحة تسجيل الدخول
    ✅ بدون @login_required لأن المستخدم ليس مسجّل الدخول بعد
    """
    # إذا كان المستخدم مسجّل الدخول بالفعل، وجّه للوحة التحكم
    if request.user.is_authenticated:
        try:
            return redirect('dashboard:index')  # ✅ الهيكل الجديد: apps/dashboard
        except NoReverseMatch:
            return redirect('articles:list')  # احتياطي
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # حفظ اسم المستخدم إذا كان "تذكرني" مفعلًا
            if request.POST.get('remember'):
                request.session['remember_username'] = user.username
            
            # إعادة التوجيه
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                try:
                    return redirect('dashboard:index')  # ✅ لوحة التحكم الجديدة
                except NoReverseMatch:
                    return redirect('articles:list')  # احتياطي
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            logger.warning(f"Login failed for: {request.POST.get('username')}")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


# =============================================================================
# ✅ تسجيل الخروج - يحتاج @login_required
# =============================================================================
@login_required
def logout_view(request):
    """
    عرض صفحة تسجيل الخروج
    ✅ مع @login_required لأن المستخدم يجب أن يكون مسجّل الدخول ليخرج
    """
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accounts:login')


# =============================================================================
# ✅ استعادة كلمة المرور - بدون @login_required
# =============================================================================
@require_http_methods(["POST"])
def password_reset_api(request):
    """
    API: طلب استعادة كلمة المرور
    ✅ بدون @login_required لأن المستخدم نسي كلمة المرور
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email requis'}, status=400)
        
        # هنا يتم إرسال البريد الإلكتروني الفعلي
        # من الدالة Django المدمجة: password_reset
        # أو من خدمة خارجية مثل SendGrid
        
        return JsonResponse({'status': 'ok', 'message': 'Lien envoyé'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Données invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)