# apps/users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from core.models import Page, PermissionMatrix


# ===========================
# 1. إدارة المستخدمين
# ===========================
@login_required
def user_list_view(request):
    """عرض قائمة المستخدمين"""
    try:
        page_obj = Page.objects.get(url_name='users')
        perm = PermissionMatrix.objects.get(user=request.user, page=page_obj)
        if not perm.can_consulte:
            return redirect('core:forbidden')
    except (Page.DoesNotExist, PermissionMatrix.DoesNotExist):
        return redirect('core:forbidden')
    
    query = request.GET.get('q')
    users = CustomUser.objects.all().order_by('username')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/user_list.html', {
        'page_obj': page_obj,
        'query': query,
        'perm': perm,
    })


@login_required
def user_create_view(request):
    """إنشاء مستخدم جديد"""
    try:
        page = Page.objects.get(url_name='users')
        perm = PermissionMatrix.objects.get(user=request.user, page=page)
        if not perm.can_insert:
            return redirect('core:forbidden')
    except (Page.DoesNotExist, PermissionMatrix.DoesNotExist):
        return redirect('core:forbidden')
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        address = request.POST['address']
        is_active = 'is_active' in request.POST
        is_staff = 'is_staff' in request.POST
        password = 'TempPass123!'
        
        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, f"Mdp non sécurisé : {' '.join(e.messages)}")
            return render(request, 'users/user_form.html')
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            is_active=is_active,
            is_staff=is_staff
        )
        messages.success(request, f"Utilisateur {username} créé.")
        return redirect('users:user_list')
    
    return render(request, 'users/user_form.html')


@login_required
def user_edit_view(request, user_id):
    """تعديل مستخدم"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    try:
        page = Page.objects.get(url_name='users')
        perm = PermissionMatrix.objects.get(user=request.user, page=page)
        if not perm.can_update:
            return redirect('core:forbidden')
    except (Page.DoesNotExist, PermissionMatrix.DoesNotExist):
        return redirect('core:forbidden')
    
    if request.method == 'POST':
        user.username = request.POST['username']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.phone = request.POST['phone']
        user.address = request.POST['address']
        user.is_active = 'is_active' in request.POST
        user.is_staff = 'is_staff' in request.POST
        user.save()
        messages.success(request, f"Utilisateur {user.username} mis à jour.")
        return redirect('users:user_list')
    
    return render(request, 'users/user_form.html', {'edit_user': user})


@login_required
def user_delete_view(request, user_id):
    """حذف مستخدم"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    try:
        page = Page.objects.get(url_name='users')
        perm = PermissionMatrix.objects.get(user=request.user, page=page)
        if not perm.can_delete:
            return redirect('core:forbidden')
    except (Page.DoesNotExist, PermissionMatrix.DoesNotExist):
        return redirect('core:forbidden')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Utilisateur {username} supprimé.")
        return redirect('users:user_list')
    
    return render(request, 'users/user_confirm_delete.html', {'user': user})


# ===========================
# 2. الصلاحيات
# ===========================
@login_required
def permission_management_view(request):
    """إدارة مصفوفة الصلاحيات"""
    query = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('username')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    selected_user_id = request.GET.get('user_id')
    selected_user = None
    permissions = []
    
    if selected_user_id:
        selected_user = get_object_or_404(CustomUser, id=selected_user_id)
        permissions = PermissionMatrix.objects.filter(user=selected_user).select_related('page')
    
    return render(request, 'users/permissions.html', {
        'users': users,
        'selected_user': selected_user,
        'permissions': permissions,
        'query': query,
    })


def api_pages(request):
    """API لجلب الصفحات"""
    query = request.GET.get('q', '')
    pages = Page.objects.filter(is_active=True)
    
    if query:
        pages = pages.filter(
            Q(name_fr__icontains=query) |
            Q(name_ar__icontains=query) |
            Q(url_name__icontains=query)
        )
    
    data = [{
        'id': page.id,
        'name_fr': page.name_fr,
        'name_ar': page.name_ar,
        'url_name': page.url_name
    } for page in pages]
    
    return JsonResponse(data, safe=False)


def api_save_permission(request):
    """API لحفظ صلاحية"""
    if request.method == 'POST':
        user_id = request.POST['user_id']
        page_id = request.POST['page_id']
        can_consulte = 'can_consulte' in request.POST
        can_insert = 'can_insert' in request.POST
        can_update = 'can_update' in request.POST
        can_delete = 'can_delete' in request.POST
        
        user = get_object_or_404(CustomUser, id=user_id)
        page = get_object_or_404(Page, id=page_id)
        
        perm, created = PermissionMatrix.objects.update_or_create(
            user=user,
            page=page,
            defaults={
                'can_consulte': can_consulte,
                'can_insert': can_insert,
                'can_update': can_update,
                'can_delete': can_delete
            }
        )
        
        return JsonResponse({
            'success': True,
            'id': perm.id,
            'page_name': page.name_fr,
        })
    
    return JsonResponse({'success': False}, status=400)


def api_delete_permission(request, perm_id):
    """API لحذف صلاحية"""
    if request.method == 'DELETE':
        perm = get_object_or_404(PermissionMatrix, id=perm_id)
        perm.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)