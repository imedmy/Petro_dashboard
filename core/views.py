# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q, Max
from django.core.paginator import Paginator
import traceback
import sys
from decimal import Decimal, InvalidOperation
from django.db import connections
from django.db import transaction
import logging
import json
from django.template.loader import render_to_string
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import re  # ✅ تم الإضافة لدعم تقسيم النصوص
from django.views.decorators.http import require_http_methods, require_GET
from datetime import datetime, date, timedelta 
from django.utils.dateparse import parse_date
import pandas as pd
from django.db import IntegrityError
import io
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.utils import timezone
# --- النماذج ---
from .models import (
    Page, PermissionMatrix, ArticleFamily,
    Caracteristique, ArticleCaracteristique, ArticleImage, TypeMouvement, NatureStock, ValeurArticle, EtapeDossier, SuiviDossier,
    PieceJointeEtape, EtatB1View, AvisArrivee, DetailAvis, PieceJointeAvis, Personnel, Intervenant, Tache, Tiers, CustomUser,
    Citerne, Barremage, PlanningTache, Engin, LectureIndex, ConsommationCarburant, LectureJauge, LecturePompe, Equipement, service
)
from accounts.models import CustomUser
from .models_sql import ArticleSQL

# --- النماذج (نهاية) ---

# --- النماذج ---
from .forms import serviceForm, ArticleFamilyForm
from .forms import CaracteristiqueForm  # سيتم تعريفه لاحقًا إذا لزم
from .forms import NatureStockForm
from .forms import ValeurArticleForm
from .forms import EtapeDossierForm
from .forms import CiterneForm
from .forms import EnginForm, LectureIndexForm, ConsommationCarburantForm, EquipementForm
from .forms import LectureJaugeForm, LecturePompeForm

# --- النماذج (نهاية) ---

# --- أدوات مساعدة ---
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        {columns[i]: row[i] for i in range(len(row))}
        for row in cursor.fetchall()
    ]
# --- أدوات مساعدة (نهاية) ---


# ===========================
# 1. لوحة القيادة والصفحات العامة
# ===========================

from django.db.models import Max
from datetime import date

# @login_required
# def dashboard_view(request):
    # try:
        # === 1. تحميل قائمة القوائم الجانبية (كما في النسخة الأصلية) ===
        # menu_items = []
        # pages = Page.objects.filter(is_active=True).order_by('order')
        # for page in pages:
            # perm, created = PermissionMatrix.objects.get_or_create(
                # user=request.user,
                # page=page,
                # defaults={
                    # 'can_consulte': False,
                    # 'can_insert': False,
                    # 'can_update': False,
                    # 'can_delete': False
                # }
            # )
            # if perm.can_consulte:
                # menu_items.append({
                    # 'page': page,
                    # 'perm': perm
                # })

        # === 2. جلب الطلبات المتأخرة (Instance أو Litige) ===
        # last_dates = (
            # SuiviDossier.objects
            # .filter(influence_sur_dossier__in=['instance', 'litige'])
            # .values('numero_com')
            # .annotate(last_date=Max('date_etape'))
        # )

        # commandes_en_retard = []
        # for item in last_dates:
            # suivi = SuiviDossier.objects.filter(
                # numero_com=item['numero_com'],
                # date_etape=item['last_date'],
                # influence_sur_dossier__in=['instance', 'litige']
            # ).first()
            # if suivi:
                # today = date.today()
                # years = today.year - suivi.date_etape.year
                # months = today.month - suivi.date_etape.month
                # days = today.day - suivi.date_etape.day

                # if days < 0:
                    # months -= 1
                    # عدد أيام الشهر السابق
                    # if today.month == 1:
                        # prev_month_days = (date(today.year - 1, 12, 1) - date(today.year - 1, 11, 1)).days
                    # else:
                        # prev_month_days = (date(today.year, today.month - 1, 1) - date(today.year, today.month - 2, 1)).days
                    # days += prev_month_days
                # if months < 0:
                    # years -= 1
                    # months += 12

                # تحديد لون الحالة
                # if years > 0 or months >= 6:
                    # color_class = 'table-danger'      # أحمر (متأخر جدًّا)
                # elif months >= 2:
                    # color_class = 'table-warning'     # أصفر (متأخر)
                # else:
                    # color_class = 'table-info'        # أزرق (حديث نسبيًا)

                # commandes_en_retard.append({
                    # 'numero_com': suivi.numero_com,
                    # 'dat_com': suivi.dat_com,
                    # 'influence': suivi.get_influence_sur_dossier_display(),
                    # 'date_etape': suivi.date_etape,
                    # 'duree_texte': f"{years} ans, {months} mois, {days} jours" if years > 0 else f"{months} mois, {days} jours",
                    # 'color_class': color_class,
                # })

        # === 3. إعادة التحويل مع جميع المتغيرات ===
        # return render(request, 'core/dashboard.html', {
            # 'menu_items': menu_items,
            # 'title': _('Tableau de bord'),
            # 'commandes_en_retard': commandes_en_retard,  # ← مفتاح الإضافة
        # })

    # except Exception as e:
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        # return HttpResponseServerError(f"""
        # <h1>Erreur Interne</h1>
        # <p><strong>Type:</strong> {exc_type.__name__}</p>
        # <p><strong>Message:</strong> {str(e)}</p>
        # <pre>{trace}</pre>
        # """)

@login_required
def page_view(request, page_name):
    SPECIAL_PAGES = {
        'users': 'core:user_list',
        'permissions': 'core:permissions',
    }

    if page_name in SPECIAL_PAGES:
        return redirect(SPECIAL_PAGES[page_name])

    try:
        page = Page.objects.get(url_name=page_name, is_active=True)
        perm = PermissionMatrix.objects.get(user=request.user, page=page)

        if not perm.can_consulte:
            return redirect('core:forbidden')

        template_name = f'core/{page_name}.html'
        return render(request, template_name, {
            'page': page,
            'title': page.name_fr
        })

    except Page.DoesNotExist:
        return render(request, 'core/not_found.html', status=404)
    except PermissionMatrix.DoesNotExist:
        return redirect('core:forbidden')
    except Exception:
        return render(request, 'core/page_under_construction.html', {'page': page})


@login_required
def forbidden_view(request):
    return render(request, 'core/forbidden.html', {
        'title': _("Pas d'autorisation")
    }, status=403)


def _get_menu_items(request):
    items = []
    pages = Page.objects.filter(is_active=True).order_by('order')
    for page in pages:
        try:
            perm = PermissionMatrix.objects.get(user=request.user, page=page)
            if perm.can_consulte:
                items.append({'page': page, 'perm': perm})
        except PermissionMatrix.DoesNotExist:
            pass
    return items


# ===========================
# 2. إدارة المستخدمين
# ===========================

@login_required
def user_list_view(request):
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

    return render(request, 'core/users.html', {
        'page_obj': page_obj,
        'query': query,
        'perm': perm,
        'title': 'Gestion des utilisateurs'
    })


@login_required
def user_edit_view(request, user_id):
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
        return redirect('core:user_list')

    return render(request, 'core/user_form.html', {
        'edit_user': user,
        'title': f'Modifier l’utilisateur : {user.username}'
    })


@login_required
def user_delete_view(request, user_id):
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
        return redirect('core:user_list')

    return render(request, 'core/user_confirm_delete.html', {
        'user': user,
        'title': 'Confirmer la suppression'
    })


@login_required
def user_create_view(request):
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
            return render(request, 'core/user_form.html', {'title': 'Créer utilisateur'})

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
        return redirect('core:user_list')

    return render(request, 'core/user_form.html', {
        'title': 'Créer un nouvel utilisateur'
    })

# Service CRUD

def service_list(request):
    services = service.objects.all().order_by('nom')
    return render(request, 'core/service_list.html', {'services': services})

def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service ajouté avec succès.")
            return redirect('core:service_list')
    else:
        form = ServiceForm()
    return render(request, 'core/service_form.html', {'form': form, 'title': 'Ajouter un service'})

def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service mis à jour.")
            return redirect('core:service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'core/service_form.html', {'form': form, 'title': 'Modifier le service'})

def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service supprimé avec succès.")
        return redirect('core:service_list')
    return render(request, 'core/service_confirm_delete.html', {'service': service})
    
# Personnel CRUD
@login_required
def personnel_list_view(request):
    query = request.GET.get('q', '').strip()
    actif = request.GET.get('actif', '')
    personnel_list = Personnel.objects.all().order_by('nom', 'prenom')
    if query:
        personnel_list = personnel_list.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(matricule__icontains=query) |
            Q(email__icontains=query)
        )
    if actif == '1':
        personnel_list = personnel_list.filter(actif=True)
    elif actif == '0':
        personnel_list = personnel_list.filter(actif=False)
    return render(request, 'core/personnel_list.html', {
        'personnel_list': personnel_list,
        'q': query,
        'actif': actif,
    })

@login_required
def personnel_create_view(request):
    if request.method == 'POST':
        try:
            personnel = Personnel(
                matricule=request.POST['matricule'],
                nom=request.POST['nom'],
                prenom=request.POST['prenom'],
                email=request.POST['email'],
                telephone=request.POST.get('telephone', ''),
                poste=request.POST.get('poste', ''),
                username=request.POST['username'],
                actif='actif' in request.POST,
            )
            personnel.set_password(request.POST['password'])
            personnel.save()
            messages.success(request, "Personnel ajouté avec succès.")
            return redirect('core:personnel_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    return render(request, 'core/personnel_form.html', {'title': 'Ajouter un personnel'})

@login_required
def personnel_update_view(request, pk):
    personnel = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        try:
            personnel.matricule = request.POST['matricule']
            personnel.nom = request.POST['nom']
            personnel.prenom = request.POST['prenom']
            personnel.email = request.POST['email']
            personnel.telephone = request.POST.get('telephone', '')
            personnel.poste = request.POST.get('poste', '')
            personnel.username = request.POST['username']
            personnel.actif = 'actif' in request.POST
            if request.POST.get('password'):
                personnel.set_password(request.POST['password'])
            personnel.save()
            messages.success(request, "Personnel mis à jour.")
            return redirect('core:personnel_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    return render(request, 'core/personnel_form.html', {
        'personnel': personnel,
        'title': 'Modifier le personnel'
    })

@login_required
def personnel_delete_view(request, pk):
    personnel = get_object_or_404(Personnel, pk=pk)
    if request.method == 'POST':
        personnel.delete()
        messages.success(request, "Personnel supprimé.")
        return redirect('core:personnel_list')
    return render(request, 'core/personnel_confirm_delete.html', {'personnel': personnel})


#============================
# Tiers
#============================
# Tiers CRUD

@login_required
def tiers_list_view(request):
    query = request.GET.get('q', '').strip()
    type_tiers = request.GET.get('type_tiers', '')
    actif = request.GET.get('actif', '')
    tiers_list = Tiers.objects.all().order_by('raison_sociale')
    if query:
        tiers_list = tiers_list.filter(
            Q(raison_sociale__icontains=query) |
            Q(code_tiers__icontains=query) |
            Q(contact__icontains=query)
        )
    if type_tiers:
        tiers_list = tiers_list.filter(type_tiers=type_tiers)
    if actif == '1':
        tiers_list = tiers_list.filter(actif=True)
    elif actif == '0':
        tiers_list = tiers_list.filter(actif=False)
    return render(request, 'core/tiers_list.html', {
        'tiers_list': tiers_list,
        'q': query,
        'type_tiers': type_tiers,
        'actif': actif,
        'type_choices': Tiers.TYPE_CHOICES,
    })

@login_required
def tiers_create_view(request):
    if request.method == 'POST':
        try:
            tiers = Tiers.objects.create(
                code_tiers=request.POST['code_tiers'],
                raison_sociale=request.POST['raison_sociale'],
                contact=request.POST.get('contact', ''),
                telephone=request.POST.get('telephone', ''),
                email=request.POST.get('email', ''),
                type_tiers=request.POST['type_tiers'],
                actif='actif' in request.POST,
            )
            messages.success(request, "Tiers ajouté avec succès.")
            return redirect('core:tiers_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    return render(request, 'core/tiers_form.html', {'title': 'Ajouter un tiers'})

@login_required
def tiers_update_view(request, pk):
    tiers = get_object_or_404(Tiers, pk=pk)
    if request.method == 'POST':
        try:
            tiers.code_tiers = request.POST['code_tiers']
            tiers.raison_sociale = request.POST['raison_sociale']
            tiers.contact = request.POST.get('contact', '')
            tiers.telephone = request.POST.get('telephone', '')
            tiers.email = request.POST.get('email', '')
            tiers.type_tiers = request.POST['type_tiers']
            tiers.actif = 'actif' in request.POST
            tiers.save()
            messages.success(request, "Tiers mis à jour.")
            return redirect('core:tiers_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    return render(request, 'core/tiers_form.html', {
        'tiers': tiers,
        'title': 'Modifier le tiers'
    })

@login_required
def tiers_delete_view(request, pk):
    tiers = get_object_or_404(Tiers, pk=pk)
    if request.method == 'POST':
        tiers.delete()
        messages.success(request, "Tiers supprimé.")
        return redirect('core:tiers_list')
    return render(request, 'core/tiers_confirm_delete.html', {'tiers': tiers})
    
# ===========================
# 3. صلاحيات النظام
# ===========================

@login_required
def permission_management_view(request):
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

    return render(request, 'core/permissions.html', {
        'users': users,
        'selected_user': selected_user,
        'permissions': permissions,
        'query': query,
        'title': 'Gestion des permissions'
    })


def api_pages(request):
    query = request.GET.get('q', '')
    pages = Page.objects.filter(is_active=True)
    if query:
        pages = pages.filter(
            Q(name_fr__icontains=query) |
            Q(name_ar__icontains=query) |
            Q(url_name__icontains=query)
        )
    data = [
        {
            'id': page.id,
            'name_fr': page.name_fr,
            'name_ar': page.name_ar,
            'url_name': page.url_name
        }
        for page in pages
    ]
    return JsonResponse(data, safe=False)


def api_save_permission(request):
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
            'page_url': page.url_name,
            'can_consulte': perm.can_consulte,
            'can_insert': perm.can_insert,
            'can_update': perm.can_update,
            'can_delete': perm.can_delete
        })

    return JsonResponse({'success': False}, status=400)


def api_delete_permission(request, perm_id):
    if request.method == 'DELETE':
        perm = get_object_or_404(PermissionMatrix, id=perm_id)
        perm.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


# ===========================
# 4. إدارة السلع والمخزون
# ===========================

# @login_required
# def articles_view(request):
    # استقبال القيم من النموذج
    # cod_art = request.GET.get('cod_art', '').strip()
    # lib_art = request.GET.get('lib_art', '').strip()
    # class_cout = request.GET.get('class_cout', '').strip()
    # lib_um = request.GET.get('lib_um', '').strip()
    # empl = request.GET.get('empl', '').strip()
    # qte_min = request.GET.get('qte_min', '').strip()
    # qte_max = request.GET.get('qte_max', '').strip()
    # pu_min = request.GET.get('pu_min', '').strip()
    # pu_max = request.GET.get('pu_max', '').strip()
    # val_art = request.GET.get('val_art', '').strip()  # جديد: 1, 2, 3 أو 4 فقط

    # sql = """
    # SELECT 
        # a.COD_ART,
        # a.LIB_ART,
        # a.CLASS_COUT,
        # a.DATE_CREAT,
        # a.DERNIER_MV,
        # a.EMPL,
        # s.PUMP,
        # u.LIB_UM,
        # s.QTE_STOCK,
        # s.QTE_SURSTK,
        # s.VAL_ART,
        # s.QTE_SURSTK * s.PUMP / 1000 AS VALEUR,
        # a.DESIGNAT
    # FROM 
        # ARTICLE a
        # INNER JOIN STOCK s ON a.COD_ART = s.COD_ART
        # INNER JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
    # WHERE 1 = 1
    # """

    # conditions = []
    # values = []

    # 1. بحث متعدد في كود المقال
    # if cod_art:
        # for part in re.split(r'\s+', cod_art):
            # if part:
                # conditions.append("a.COD_ART LIKE %s")
                # values.append(f'%{part}%')

    # 2. بحث متعدد في اسم المقال
    # if lib_art:
        # for kw in re.split(r'\s+', lib_art.strip()):
            # if kw:
                # conditions.append("a.LIB_ART LIKE %s")
                # values.append(f'%{kw}%')

    # باقي الفلاتر
    # if class_cout:
        # conditions.append("a.CLASS_COUT = %s")
        # values.append(class_cout)

    # if lib_um:
        # conditions.append("u.LIB_UM = %s")
        # values.append(lib_um)

    # if empl:
        # conditions.append("a.EMPL LIKE %s")
        # values.append(f'%{empl}%')

    # if qte_min and qte_min.replace('.', '', 1).isdigit():
        # conditions.append("s.QTE_SURSTK >= %s")
        # values.append(qte_min)

    # if qte_max and qte_max.replace('.', '', 1).isdigit():
        # conditions.append("s.QTE_SURSTK <= %s")
        # values.append(qte_max)

    # if pu_min and pu_min.replace('.', '', 1).isdigit():
        # conditions.append("s.PUMP >= %s")
        # values.append(str(float(pu_min) * 1000))

    # if pu_max and pu_max.replace('.', '', 1).isdigit():
        # conditions.append("s.PUMP <= %s")
        # values.append(str(float(pu_max) * 1000))

    # 🔹 فلتر جديد: VAL_ART (1, 2, 3, أو 4 فقط)
    # if val_art in ['1', '2', '3', '4']:
        # conditions.append("s.VAL_ART = %s")
        # values.append(val_art)

    # if conditions:
        # sql += " AND " + " AND ".join(conditions)

    # sql += " ORDER BY a.CLASS_COUT, a.COD_ART"

    # rows = []
    # try:
        # with connections['sql_server'].cursor() as cursor:
            # cursor.execute(sql, values)
            # columns = [col[0] for col in cursor.description]
            # for row in cursor.fetchall():
                # data = dict(zip(columns, row))
                # data['PU'] = round(data['PUMP'] / 1000, 3) if data['PUMP'] else 0
                # rows.append(data)
    # except Exception as e:
        # print("❌ Erreur:", e)
        # print("SQL:", sql)
        # print("Values:", values)

    # paginator = Paginator(rows, 20)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    # return render(request, 'core/articles.html', {
        # 'page_obj': page_obj,
        # 'cod_art': cod_art,
        # 'lib_art': lib_art,
        # 'class_cout': class_cout,
        # 'lib_um': lib_um,
        # 'empl': empl,
        # 'qte_min': qte_min,
        # 'qte_max': qte_max,
        # 'pu_min': pu_min,
        # 'pu_max': pu_max,
        # 'val_art': val_art,  # تم تحديثه
    # })

def codification_view(request, codart):
    return render(request, 'core/codification.html', {'codart': codart})


def caracteristiques_view(request, codart):
    return render(request, 'core/caracteristiques.html', {'codart': codart})


def details_caracteristiques_view(request):
    return render(request, 'core/detailscaracteristiques.html')


# ===========================
# 5. إدارة الخصائص التقنية
# ===========================

# def gestion_caracteristiques(request):
    # query = request.GET.get('q', '')
    # all_caracts = Caracteristique.objects.all().select_related('parent')

    # if query:
        # all_caracts = all_caracts.filter(nom__icontains=query)

    # tree_map = {c.id: {'node': c, 'children': []} for c in all_caracts}
    # roots = []

    # for c in all_caracts:
        # if c.parent and c.parent.id in tree_map:
            # tree_map[c.parent.id]['children'].append(tree_map[c.id])
        # elif not c.parent:
            # roots.append(tree_map[c.id])

    # form = None
    # edit_id = request.GET.get('edit')
    
    # if edit_id:
        # instance = get_object_or_404(Caracteristique, id=edit_id)
        # if request.method == 'POST':
            # form = CaracteristiqueForm(request.POST, instance=instance)
            # if form.is_valid():
                # form.save()
                # messages.success(request, f"Caractéristique '{form.instance.nom}' mise à jour.")
                # return redirect('core:gestion_caracteristiques')
        # else:
            # form = CaracteristiqueForm(instance=instance)
    # else:
        # if request.method == 'POST':
            # form = CaracteristiqueForm(request.POST)
            # if form.is_valid():
                # form.save()
                # messages.success(request, f"Caractéristique '{form.instance.nom}' ajoutée.")
                # return redirect('core:gestion_caracteristiques')
        # else:
            # form = CaracteristiqueForm()

    # if request.method == 'POST' and 'delete_id' in request.POST:
        # delete_id = request.POST.get('delete_id')
        # carac = get_object_or_404(Caracteristique, id=delete_id)
        # carac.delete()
        # messages.success(request, f"Caractéristique '{carac.nom}' supprimée.")
        # return redirect('core:gestion_caracteristiques')

    # return render(request, 'core/caracteristiques.html', {
        # 'roots': roots,
        # 'form': form,
        # 'query': query,
    # })


# def api_caracteristiques(request):
    # query = request.GET.get('q', '').strip()
    # qs = Caracteristique.objects.all()
    # if query:
        # qs = qs.filter(nom__icontains=query)
    # data = [{'id': c.id, 'nom': c.nom, 'parent': c.parent.id if c.parent else None} for c in qs]
    # return JsonResponse(data, safe=False)


# ===========================
# 6. إدارة عائلات الترميز
# ===========================

# def famille_codification_view(request):
    # query = request.GET.get('q', '')

    # if query:
        # families = ArticleFamily.objects.filter(
            # models.Q(name__icontains=query) |
            # models.Q(full_code__icontains=query)
        # ).select_related('parent')
    # else:
        # families = ArticleFamily.objects.select_related('parent').all()

    # tree = {}
    # roots = []

    # for family in families:
        # tree[family.id] = {
            # 'family': family,
            # 'children': []
        # }

    # for family in families:
        # if family.parent and family.parent.id in tree:
            # tree[family.parent.id]['children'].append(tree[family.id])
        # elif not family.parent:
            # roots.append(tree[family.id])

    # form = None
    # edit_id = request.GET.get('edit')
    
    # if edit_id:
        # family_obj = get_object_or_404(ArticleFamily, id=edit_id)
        # if request.method == 'POST':
            # form = ArticleFamilyForm(request.POST, instance=family_obj)
            # if form.is_valid():
                # form.save()
                # messages.success(request, f"Famille '{form.instance.name}' mise à jour.")
                # return redirect('core:gestion_famille_codification')
        # else:
            # form = ArticleFamilyForm(instance=family_obj)
    # else:
        # if request.method == 'POST':
            # form = ArticleFamilyForm(request.POST)
            # if form.is_valid():
                # form.save()
                # messages.success(request, f"Famille '{form.instance.name}' ajoutée.")
                # return redirect('core:gestion_famille_codification')
        # else:
            # form = ArticleFamilyForm()

    # if request.method == 'POST' and 'delete_id' in request.POST:
        # delete_id = request.POST.get('delete_id')
        # family = get_object_or_404(ArticleFamily, id=delete_id)
        # family_name = family.name
        # family.delete()
        # messages.success(request, f"Famille '{family_name}' supprimée.")
        # return redirect('core:gestion_famille_codification')

    # return render(request, 'core/famille_codification.html', {
        # 'families': families,
        # 'roots': roots,
        # 'form': form,
        # 'query': query,
        # 'title': 'Famille Codification des Articles'
    # })


# @login_required
# def api_article_families(request):
    # query = request.GET.get('q', '').strip()
    # all_families = ArticleFamily.objects.select_related('parent').all()

    # if query:
        # all_families = all_families.filter(
            # models.Q(name__icontains=query) |
            # models.Q(full_code__icontains=query)
        # )

    # data = []
    # for family in all_families.order_by('full_code')[:200]:
        # data.append({
            # 'id': family.id,
            # 'name': family.name,
            # 'code_segment': family.code_segment,
            # 'description': family.description or '',
            # 'full_code': family.full_code,
            # 'parent': {'id': family.parent.id} if family.parent else None
        # })

    # return JsonResponse(data, safe=False)


@login_required
def api_article_family_by_code(request):
    cod_art = request.GET.get('cod_art', '').strip()
    if not cod_art:
        return JsonResponse({'error': 'COD_ART manquant'}, status=400)

    try:
        article = ArticleSQL.objects.using('sql_server').get(COD_ART=cod_art)
        family_code = cod_art[:3]
        family = ArticleFamily.objects.get(full_code=family_code)

        def build_tree(fam):
            node = {
                'id': fam.id,
                'name': fam.name,
                'code_segment': fam.code_segment,
                'full_code': fam.full_code,
                'children': []
            }
            for child in fam.children.all():
                node['children'].append(build_tree(child))
            return node

        tree = build_tree(family)
        return JsonResponse({'family': tree})

    except ArticleSQL.DoesNotExist:
        return JsonResponse({'family': None, 'error': 'Article non trouvé'}, status=200)
    except ArticleFamily.DoesNotExist:
        return JsonResponse({'family': None, 'error': 'Famille non trouvée'}, status=200)
    except Exception as e:
        return JsonResponse({'family': None, 'error': 'Erreur interne', 'details': str(e)}, status=500)


# ===========================
# 7. إدارة خصائص السلع والصور
# ===========================

def article_caracteristiques(request, cod_art=None):
    selected_cod_art = cod_art or request.GET.get('cod_art')
    libelle = ""

    if selected_cod_art:
        try:
            article = ArticleSQL.objects.using('sql_server').get(COD_ART=selected_cod_art)
            libelle = article.LIB_ART
        except ArticleSQL.DoesNotExist:
            pass

    # جلب جميع الخصائص وبناء الشجرة
    all_caracts = Caracteristique.objects.all().select_related('parent')
    tree_map = {c.id: {'node': c, 'children': []} for c in all_caracts}
    roots = []

    for c in all_caracts:
        if c.parent and c.parent.id in tree_map:
            tree_map[c.parent.id]['children'].append(tree_map[c.id])
        elif not c.parent:
            roots.append(tree_map[c.id])

    # === تحويل الشجرة إلى قائمة مسطحة (tree_items) كما يتوقعها القالب ===
    def flatten_tree(nodes, level=0):
        items = []
        for node_data in nodes:
            items.append({
                'node': node_data['node'],
                'level': level
            })
            if node_data['children']:
                items.extend(flatten_tree(node_data['children'], level + 1))
        return items

    tree_items = flatten_tree(roots)

    # جلب القيم المسندة للسلعة
    values = {}
    if selected_cod_art:
        values_qs = ArticleCaracteristique.objects.filter(cod_art=selected_cod_art).values(
            'caracteristique_id', 'valeur'
        )
        values = {str(v['caracteristique_id']): v['valeur'] for v in values_qs}

    images = ArticleImage.objects.filter(cod_art=selected_cod_art) if selected_cod_art else []

    return render(request, 'core/article_caracteristiques.html', {
        'tree_items': tree_items,           # ✅ تم الإضافة
        'selected_cod_art': selected_cod_art,
        'libelle': libelle,
        'assigned_values': values,
        'images': images,
    })


# @login_required
# def api_articles(request):
    # query = request.GET.get('q', '').strip()
    
    # إذا لم يكن هناك بحث، لا تُرجع أي نتيجة
    # if not query:
        # return JsonResponse([], safe=False)
    
    # sql = "SELECT COD_ART, LIB_ART FROM ARTICLE WHERE COD_ART LIKE %s OR LIB_ART LIKE %s"
    
    # try:
        # with connections['sql_server'].cursor() as cursor:
            # search = f'%{query}%'
            # cursor.execute(sql, [search, search])
            # فقط استخدم LIB_ART في nom دون تكرار الكود
            # data = [
                # {
                    # 'id': row[0],
                    # 'nom': row[1]  # فقط الاسم (LIB_ART)
                # }
                # for row in cursor.fetchall()
            # ]
        # return JsonResponse(data, safe=False)
    # except Exception as e:
        # print("❌ Erreur dans api_articles:", str(e))  # لتسهيل التصحيح
        # return JsonResponse([], safe=False)


def api_article_caract_values(request, cod_art):
    values = ArticleCaracteristique.objects.filter(cod_art=cod_art).values(
        'caracteristique_id', 'valeur'
    )
    data = {str(v['caracteristique_id']): v['valeur'] for v in values}
    return JsonResponse(data, safe=False)


@csrf_exempt  # فقط إذا كنت تستقبل طلبات من خارج Django template (مثل API)
@require_http_methods(["POST"])  # يسمح فقط بـ POST
def api_add_article_caract(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    cod_art = data.get('cod_art')
    caract_id = data.get('caract_id')
    valeur = data.get('valeur', '')

    if not cod_art or not caract_id:
        return JsonResponse({
            'status': 'error',
            'message': 'Missing required fields: cod_art or caract_id'
        }, status=400)

    try:
        obj, created = ArticleCaracteristique.objects.update_or_create(
            cod_art=cod_art,
            caracteristique_id=caract_id,
            defaults={'valeur': valeur}
        )
        return JsonResponse({
            'status': 'ok',
            'created': created,
            'cod_art': obj.cod_art,
            'caract_id': obj.caracteristique_id,
            'valeur': obj.valeur
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def api_delete_article_caract(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cod_art = data['cod_art']
        caract_id = data['caract_id']
        ArticleCaracteristique.objects.filter(cod_art=cod_art, caracteristique_id=caract_id).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_upload_article_image(request, cod_art):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'articles'), exist_ok=True)
            img = ArticleImage.objects.create(cod_art=cod_art, image=image)
            return JsonResponse({
                'status': 'ok',
                'id': img.id,
                'url': img.image.url,
                'uploaded_at': img.uploaded_at.strftime('%Y-%m-%d %H:%M')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Aucune image reçue'}, status=400)

@csrf_exempt
def api_delete_article_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_id = data['image_id']
        try:
            img = ArticleImage.objects.get(id=image_id)
            if os.path.isfile(img.image.path):
                os.remove(img.image.path)
            img.delete()
            return JsonResponse({'status': 'ok'})
        except ArticleImage.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)


# ===========================
# 8. الإحصائيات
# ===========================
# @login_required
# def statistiques_view(request):
    # cod_art = request.GET.get('cod_art', '').strip()
    # nat_stock = request.GET.get('nat_stock', '').strip()  # ← جديد
    # val_art = request.GET.get('val_art', '').strip()      # ← جديد
    # date_min = request.GET.get('date_min', '')
    # date_max = request.GET.get('date_max', '')

    # context = {
        # 'cod_art': cod_art,
        # 'nat_stock': nat_stock,  # ← جديد
        # 'val_art': val_art,      # ← جديد
        # 'date_min': date_min,
        # 'date_max': date_max,
        # 'error': None,
        # 'libelle_article': '',
        # 'months_json': [],
        # 'quantities_json': [],
    # }

    # try:
        # التحقق من التواريخ (نفس منطق AJAX)
        # if not date_min:
            # date_min = (date.today() - timedelta(days=365)).isoformat()
        # if not date_max:
            # date_max = date.today().isoformat()

        # with connections['sql_server'].cursor() as cursor:
            # جلب libellé (لا يتأثر بـ nat_stock/val_art)
            # if cod_art:
                # try:
                    # cursor.execute("SELECT LIB_ART FROM ARTICLE WHERE COD_ART = %s", [cod_art])
                    # row = cursor.fetchone()
                    # context['libelle_article'] = row[0] if row else "Article inconnu"
                # except Exception as e:
                    # print("Erreur lecture LIB_ART:", str(e))
                    # context['libelle_article'] = "Article inconnu"

            # === CONSO MENSUELLE (يدعم المرشحات الجديدة) ===
            # if cod_art:
                # بناء شرط WHERE ديناميكي
                # where_clauses = ["e2.cod_art = %s", "e2.date_b >= %s", "e2.date_b <= %s"]
                # params = [cod_art, date_min, date_max]
                
                # if nat_stock:
                    # where_clauses.append("e2.nat_stock = %s")
                    # params.append(nat_stock)
                # if val_art:
                    # where_clauses.append("e2.val_art = %s")
                    # params.append(val_art)
                
                # where_sql = " AND ".join(where_clauses)

                # cursor.execute(f"""
                    # SELECT YEAR(e2.date_b), MONTH(e2.date_b), SUM(e2.qte_mvt)
                    # FROM Etat_b2 e2
                    # WHERE {where_sql}
                    # GROUP BY YEAR(e2.date_b), MONTH(e2.date_b)
                    # ORDER BY 1, 2;
                # """, params)
                
                # rows = cursor.fetchall()
                # ... باقي كود معالجة الأشهر والكميات كما هو ...
                # month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                             # 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                # حساب الأشهر بين date_min و date_max (ليس 12 شهرًا ثابتًا)
                # start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
                # end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
                # months = []
                # quantities = []
                # current = start_date.replace(day=1)
                # data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

                # while current <= end_date:
                    # year = current.year
                    # month = current.month
                    # months.append(f"{month_names[month-1]} {str(year)[-2:]}")
                    # quantities.append(data_dict.get((year, month), 0.0))
                    # if current.month == 12:
                        # current = current.replace(year=current.year + 1, month=1)
                    # else:
                        # current = current.replace(month=current.month + 1)

                # context['months_json'] = months
                # context['quantities_json'] = quantities

    # except Exception as e:
        # context['error'] = f"Erreur lors de l'exécution des requêtes : {str(e)}"
        # print("❌ Erreur SQL:", str(e))

    # return render(request, 'core/statistiques.html', context)

@login_required
def get_stock_info_view(request):
    """
    إرجاع معلومات المخزون لمادة معينة: 
    - Libellé, Class de coût, Empl, QTE_SURSTK, PUMP
    """
    cod_art = request.GET.get('cod_art', '').strip()
    nat_stock = request.GET.get('nat_stock', '').strip()
    val_art = request.GET.get('val_art', '').strip()
    date_min = request.GET.get('date_min', '')
    date_max = request.GET.get('date_max', '')
    
    context = {
        'cod_art': cod_art,
        'nat_stock': nat_stock,
        'val_art': val_art,
        'date_min': date_min,
        'date_max': date_max,
        'error': None,
        'libelle_article': '',
        'months_json': [],
        'quantities_json': [],
    }
    
    if not cod_art:
        return JsonResponse({'error': 'Code article requis'}, status=400)

    try:
        with connections['sql_server'].cursor() as cursor:
            # جلب المعلومات من ARTICLE
            cursor.execute("""
                SELECT LIB_ART, ISNULL(CLASS_COUT, ''), ISNULL(EMPL, '')
                FROM ARTICLE 
                WHERE COD_ART = %s
            """, [cod_art])
            art_row = cursor.fetchone()

            if not art_row:
                return JsonResponse({
                    'error': 'Article non trouvé',
                    'libelle_article': 'Inconnu',
                    'classe_cout': '—',
                    'emplacement': '—',
                    'qte_surstk': 0,
                    'pump': 0.0
                })

            libelle = art_row[0] or "Inconnu"
            classe_cout = art_row[1] or "Non défini"
            emplacement = art_row[2] or "Non défini"

            # جلب المخزون من STOCK (نفترض NAT_STOCK = '01' للمخزون الفعلي)
            cursor.execute("""
                SELECT 
                    ISNULL(SUM(QTE_SURSTK), 0),
                    ISNULL(AVG(PUMP/1000), 0)
                FROM STOCK 
                WHERE COD_ART = %s   -- عدّل حسب نظامك
            """, [cod_art])
            stock_row = cursor.fetchone()

            qte_surstk = float(stock_row[0]) if stock_row and stock_row[0] is not None else 0
            pump = float(stock_row[1]) if stock_row and stock_row[1] is not None else 0.0

            return JsonResponse({
                'libelle_article': libelle,
                'classe_cout': classe_cout,
                'emplacement': emplacement,
                'qte_surstk': qte_surstk,
                'pump': pump
            })

    except Exception as e:
        print("Erreur get_stock_info:", str(e))
        return JsonResponse({
            'error': 'Erreur serveur',
            'libelle_article': 'Erreur',
            'classe_cout': 'Erreur',
            'emplacement': 'Erreur',
            'qte_surstk': 0,
            'pump': 0.0
        }, status=500)

@login_required
@login_required
def statistiques_ajax_view(request):
    """
    نقطة الدخول العامة: تستقبل الطلب وتوجهه للدالة المناسبة.
    """
    tab = request.GET.get('tab')
    cod_art = request.GET.get('cod_art', '').strip()
    date_min = request.GET.get('date_min', '')
    date_max = request.GET.get('date_max', '')
    nat_stock = request.GET.get('nat_stock', '').strip()
    val_art = request.GET.get('val_art', '').strip()  

    # --- ⚠️ هذه المتغيرات مهمة جدًا ---
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 20))
    
    # --- الحصول على معلمات الفرز ---
    order_column_index = request.GET.get('order[0][column]')
    order_dir = request.GET.get('order[0][dir]', 'asc')
    
    # --- الحصول على نص البحث ---
    search_value = request.GET.get('search[value]', '').strip()

    # --- التحقق من التواريخ ---
    if not date_min:
        date_min = (date.today() - timedelta(days=365)).isoformat()
    if not date_max:
        date_max = date.today().isoformat()

    # --- تحديد الدالة حسب التبويب ---
    handler_map = {
        'consommation': get_consommation_data,
        'achat': get_achat_data,
        'entrees': get_entrees_data,
        'sorties': get_sorties_data,
        'retours': get_retours_data,
        'prestations': get_prestations_data,
        'mouvements': get_mouvements_data,
    }

    handler = handler_map.get(tab)
    if not handler:
        return JsonResponse({'error': 'Onglet invalide'}, status=400)

    try:
        with connections['sql_server'].cursor() as cursor:
            # تنفيذ الاستعلام والحصول على البيانات الكاملة
            # تمرير معلمات الفرز والبحث إلى الدالة
            result = handler(
                cursor, 
                cod_art, 
                nat_stock, 
                val_art, 
                date_min, 
                date_max,
                search_value=search_value,      # ← جديد
                order_column_index=order_column_index,  # ← جديد
                order_dir=order_dir             # ← جديد
            )

            data = result.get('data', [])
            total_records = result.get('total_records', len(data))
            filtered_records = result.get('filtered_records', total_records)

            # --- ✅ التقسيم الصحيح للبيانات ---
            paged_data = data[start:start + length]

            # --- ✅ الرد بالهيكل المطلوب من DataTables ---
            response_data = {
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': filtered_records,
                'data': paged_data,
            }
            
            # --- إضافة القيم الإجمالية إذا وُجدت ---
            if 'total_valeur' in result:
                response_data['total_valeur'] = result['total_valeur']
            if 'total_valeur_sorties' in result:
                response_data['total_valeur_sorties'] = result['total_valeur_sorties']
                
            # --- إرفاق بيانات الرسم البياني إن وُجدت (يدعم كلا النمطين) ---
            if 'months' in result:
                response_data['months'] = result['months']
                if 'quantities' in result:
                    response_data['quantities'] = result['quantities']
                if 'datasets' in result:
                    response_data['datasets'] = result['datasets']

            return JsonResponse(response_data)

    except Exception as e:
        print(f"Erreur dans statistiques_ajax_view: {e}")
        return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)

def get_consommation_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                         search_value=None, order_column_index=None, order_dir='asc'):
    # بناء شرط WHERE ديناميكي
    where_clauses = ["e2.cod_art = %s"]
    params = [cod_art]
    
    if nat_stock:
        where_clauses.append("e2.nat_stock = %s")
        params.append(nat_stock)
    if val_art:
        where_clauses.append("e2.val_art = %s")
        params.append(val_art)
    
    where_clauses.extend(["e2.date_b >= %s", "e2.date_b <= %s"])
    params.extend([date_min, date_max])
    
    where_sql = " AND ".join(where_clauses)

    # --- بناء شرط البحث ---
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = [
            "e2.numero_bon LIKE %s",
            "e2.lib_art LIKE %s"
        ]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    # --- بناء شرط الفرز ---
    order_clause = "ORDER BY e2.date_b DESC"  # افتراضي
    if order_column_index and order_column_index.isdigit():
        # خريطة الأعمدة: index في DataTables -> اسم العمود في SQL
        columns_map = {
            '1': 'e2.date_b',      # Date
            '2': 'e2.numero_bon',  # N° Bon
            '3': 'e2.lib_art',     # Libellé
            '4': 'e2.qte_mvt',     # Quantité
            '5': 'VALEUR'          # Valeur
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            # ملاحظة: VALEUR عمود محسوب، لذا نستخدم التعبير الأصلي للفرز
            if col_name == 'VALEUR':
                order_clause = f"""
                    ORDER BY 
                    CASE 
                        WHEN e2.val_art = 1 THEN 1
                        WHEN e2.val_art = 2 THEN 2
                        WHEN e2.val_art = 3 THEN 3
                        WHEN e2.val_art = 4 THEN 4
                        ELSE 5 
                    END {'ASC' if order_dir == 'asc' else 'DESC'}
                """
            else:
                order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
                order_clause = f"ORDER BY {col_name} {order_dir_sql}"

    # --- البيانات الجدولية ---
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        
        cursor.execute(f"""
            SELECT 
                'Consommation' AS type,
                e2.date_b,
                e2.numero_bon,
                e2.lib_art,
                e2.qte_mvt,
                CASE 
                    WHEN e2.val_art = 1 THEN '100%%'
                    WHEN e2.val_art = 2 THEN '75%%'
                    WHEN e2.val_art = 3 THEN '25%%'
                    WHEN e2.val_art = 4 THEN '0%%'
                    ELSE 'Inconnu' 
                END AS VALEUR,
                'Sortie' AS sens
            FROM Etat_b2 e2
            WHERE {full_where}
            {order_clause};
        """, full_params)
        
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Erreur dans les données tabulaires de consommation:", str(e))
        data = []

    months_data = []
    quantities_data = []

    if cod_art and date_min and date_max:
        try:
            # --- الرسم البياني: حسب date_min و date_max ---
            # ملاحظة: الرسم البياني لا يتأثر بالبحث أو الفرز
            cursor.execute(f"""
                SELECT 
                    YEAR(e2.date_b) AS yr,
                    MONTH(e2.date_b) AS mth,
                    SUM(e2.qte_mvt) AS total
                FROM Etat_b2 e2
                WHERE {where_sql}
                GROUP BY YEAR(e2.date_b), MONTH(e2.date_b)
                ORDER BY yr, mth;
            """, params)
            
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

            while current <= end_date:
                year = current.year
                month = current.month
                key = (year, month)

                months_data.append(f"{month_names[month-1]} {str(year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))

                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            if not months_data:
                months_data = ['Période']
                quantities_data = [0]

        except Exception as e:
            print("Erreur dans le graphique de consommation:", str(e))
            months_data = ['Erreur']
            quantities_data = [0]
    else:
        months_data = []
        quantities_data = []

    # --- حساب العدد الإجمالي للسجلات ---
    try:
        # العدد الإجمالي (بدون تأثير البحث)
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b2 e2 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        
        # العدد بعد تطبيق البحث
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b2 e2 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except Exception as e:
        print("Erreur dans le calcul des enregistrements:", str(e))
        total_records = len(data)
        filtered_records = len(data)

    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'total_records': total_records,      # ← جديد
        'filtered_records': filtered_records  # ← جديد
    }


def get_achat_data(cursor, cod_art, nat_stock, val_art, date_min, date_max, 
                  search_value=None, order_column_index=None, order_dir='asc'):
    # ملاحظة: جدول Etat_b1 قد لا يحتوي على val_art، لذا نستخدم فقط nat_stock
    where_clauses = ["a.COD_ART = %s"]
    params = [cod_art]
    
    if nat_stock:
        where_clauses.append("e1.nat_stock = %s")
        params.append(nat_stock)
    # val_art غير مستخدم في جدول المشتريات (Etat_b1) عادةً
    
    where_clauses.extend(["e1.date_b >= %s", "e1.date_b <= %s"])
    params.extend([date_min, date_max])
    
    where_sql = " AND ".join(where_clauses)

    # --- بناء شرط البحث ---
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = [
            "e1.numero_bon LIKE %s",
            "a.LIB_ART LIKE %s",
            "e1.doc_ref LIKE %s"
        ]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    # --- بناء شرط الفرز ---
    order_clause = "ORDER BY e1.date_b DESC"  # افتراضي
    if order_column_index and order_column_index.isdigit():
        # خريطة الأعمدة: index في DataTables -> اسم العمود في SQL
        columns_map = {
            '1': 'e1.date_b',      # Date
            '2': 'e1.numero_bon',  # N° Bon
            '3': 'a.LIB_ART',      # Libellé
            '4': 'e1.qte_mvt',     # Quantité
            '5': 'PU',             # Prix Unitaire
            '6': 'e1.doc_ref'      # N° BC
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"

    # --- البيانات الجدولية ---
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        
        cursor.execute(f"""
            SELECT 
                'Achat' AS type,
                e1.date_b,
                e1.numero_bon,
                a.LIB_ART AS lib_art,
                e1.qte_mvt,
                CASE 
                    WHEN e1.qte_mvt > 0 THEN CAST(e1.valeur_tot AS FLOAT) / e1.qte_mvt 
                    ELSE 0 
                END AS PU,
                e1.doc_ref,
                e1.date_ref,
                'Entrée' AS sens
            FROM Etat_b1 e1
            INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART
            WHERE {full_where}
            {order_clause};
        """, full_params)
        
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Erreur dans les données tabulaires d'achat:", str(e))
        data = []

    months_data = []
    quantities_data = []

    if cod_art and date_min and date_max:
        try:
            # --- الرسم البياني: كمية الشراء الشهرية ---
            # ملاحظة: الرسم البياني لا يتأثر بالبحث أو الفرز
            cursor.execute(f"""
                SELECT 
                    YEAR(e1.date_b) AS yr,
                    MONTH(e1.date_b) AS mth,
                    SUM(e1.qte_mvt) AS total
                FROM Etat_b1 e1
                WHERE e1.cod_art = %s 
                  AND e1.date_b >= %s AND e1.date_b <= %s
                GROUP BY YEAR(e1.date_b), MONTH(e1.date_b)
                ORDER BY yr, mth;
            """, [cod_art, date_min, date_max])
            
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

            months_data = []
            quantities_data = []
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

            while current <= end_date:
                year = current.year
                month = current.month
                key = (year, month)

                months_data.append(f"{month_names[month-1]} {str(year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))

                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            if not months_data:
                months_data = ['Aucune donnée']
                quantities_data = [0]
                
        except Exception as e:
            print("Erreur dans le graphique d'achat:", str(e))
            months_data = ['Erreur']
            quantities_data = [0]
    else:
        months_data = []
        quantities_data = []

    # --- حساب العدد الإجمالي للسجلات ---
    try:
        # العدد الإجمالي (بدون تأثير البحث)
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM Etat_b1 e1
            INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART
            WHERE {where_sql}
        """, params)
        total_records = cursor.fetchone()[0]
        
        # العدد بعد تطبيق البحث
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM Etat_b1 e1
            INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART
            WHERE {full_where}
        """, full_params)
        filtered_records = cursor.fetchone()[0]
    except Exception as e:
        print("Erreur dans le calcul des enregistrements:", str(e))
        total_records = len(data)
        filtered_records = len(data)

    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'total_records': total_records,      # ← جديد
        'filtered_records': filtered_records  # ← جديد
    }

def get_entrees_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                    search_value=None, order_column_index=None, order_dir='asc'):
    # بناء شرط WHERE ديناميكي
    where_clauses = ["e1.date_b >= %s", "e1.date_b <= %s"]
    params = [date_min, date_max]
    
    # if cod_art:
        # where_clauses.append("e1.cod_art = %s")
        # params.append(cod_art)
    # if nat_stock:
        # where_clauses.append("e1.nat_stock = %s")
        # params.append(nat_stock)
    # ملاحظة: جدول Etat_b1 عادةً لا يحتوي على val_art
    
    where_sql = " AND ".join(where_clauses)

    # --- بناء شرط البحث ---
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = [
            "e1.numero_bon LIKE %s",
            "e1.lib_art LIKE %s",
            "e1.doc_ref LIKE %s"
        ]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    # --- بناء شرط الفرز ---
    order_clause = "ORDER BY e1.date_b DESC"  # افتراضي
    if order_column_index and order_column_index.isdigit():
        # خريطة الأعمدة: index في DataTables -> اسم العمود في SQL
        columns_map = {
            '0': 'e1.date_b',      # Date
            '1': 'e1.numero_bon',  # N° Bon
            '2': 'e1.lib_art',     # Libellé
            '3': 'e1.qte_mvt',     # Quantité
            '4': 'e1.valeur_tot',  # Valeur Totale
            '5': 'e1.doc_ref'      # N° BC
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"

    # --- البيانات الجدولية ---
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        
        cursor.execute(f"""
            SELECT 
                'Entrée' AS type,
                e1.date_b,
                e1.numero_bon,
                e1.lib_art,
                e1.qte_mvt,
                e1.valeur_tot,
                e1.doc_ref,
                e1.date_ref,
                'Entrée' AS sens
            FROM Etat_b1 e1
            WHERE {full_where}
            {order_clause};
        """, full_params)
        
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Erreur dans les données tabulaires des entrées:", str(e))
        data = []

    months_data = []
    quantities_data = []
    total_valeur = 0.0

    if cod_art and date_min and date_max:
        try:
            # --- حساب القيمة الإجمالية ---
            # ملاحظة: القيمة الإجمالية لا تتأثر بالبحث أو الفرز
            total_query = f"""
                SELECT COALESCE(SUM(e1.valeur_tot), 0)
                FROM Etat_b1 e1
                WHERE {where_sql}
            """
            cursor.execute(total_query, params)
            total_valeur = float(cursor.fetchone()[0] or 0)

            # --- الرسم البياني: القيمة الإجمالية للإدخالات ---
            # ملاحظة: الرسم البياني لا يتأثر بالبحث أو الفرز
            chart_where = ["e1.date_b >= %s", "e1.date_b <= %s"]
            chart_params = [date_min, date_max]
            
            # if cod_art:
                # chart_where.append("e1.cod_art = %s")
                # chart_params.append(cod_art)
            # if nat_stock:
                # chart_where.append("e1.nat_stock = %s")
                # chart_params.append(nat_stock)
                
            chart_where_sql = " AND ".join(chart_where)

            cursor.execute(f"""
                SELECT 
                    YEAR(e1.date_b) AS yr,
                    MONTH(e1.date_b) AS mth,
                    SUM(e1.valeur_tot) AS total
                FROM Etat_b1 e1
                WHERE {chart_where_sql}
                GROUP BY YEAR(e1.date_b), MONTH(e1.date_b)
                ORDER BY yr, mth;
            """, chart_params)
            
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

            while current <= end_date:
                year = current.year
                month = current.month
                key = (year, month)

                months_data.append(f"{month_names[month-1]} {str(year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))

                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            if not months_data:
                months_data = ['Période']
                quantities_data = [0]

        except Exception as e:
            print("Erreur dans le graphique des entrées:", str(e))
            months_data = ['Erreur']
            quantities_data = [0]
    else:
        months_data = []
        quantities_data = []

    # --- حساب العدد الإجمالي للسجلات ---
    try:
        # العدد الإجمالي (بدون تأثير البحث)
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b1 e1 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        
        # العدد بعد تطبيق البحث
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b1 e1 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except Exception as e:
        print("Erreur dans le calcul des enregistrements:", str(e))
        total_records = len(data)
        filtered_records = len(data)

    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'total_valeur': total_valeur,
        'total_records': total_records,      # ← جديد
        'filtered_records': filtered_records  # ← جديد
    }


def get_sorties_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                    search_value=None, order_column_index=None, order_dir='asc'):
    # بناء شرط WHERE ديناميكي
    where_clauses = [
        "f.date_b >= %s", 
        "f.date_b <= %s", 
        "f.nature_bon LIKE 'b2'"
    ]
    params = [date_min, date_max]
    
    # if cod_art:
        # where_clauses.append("f.cod_art = %s")
        # params.append(cod_art)
    # if nat_stock:
        # where_clauses.append("f.nat_stock = %s")
        # params.append(nat_stock)
    # if val_art:
        # where_clauses.append("f.val_art = %s")
        # params.append(val_art)
    
    where_sql = " AND ".join(where_clauses)

    # --- بناء شرط البحث ---
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = [
            "f.num LIKE %s",
            "a.LIB_ART LIKE %s",
            "u.LIB_UM LIKE %s",
            "ce.LIB_CENTRE LIKE %s"
        ]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    # --- بناء شرط الفرز ---
    order_clause = "ORDER BY f.date_b DESC"  # افتراضي
    if order_column_index and order_column_index.isdigit():
        # خريطة الأعمدة: index في DataTables -> اسم العمود في SQL
        columns_map = {
            '0': 'f.date_b',           # Date
            '1': 'f.num',              # N° Bon
            '2': 'a.LIB_ART',          # Libellé
            '3': 'f.qte_mvt',          # Quantité
            '4': 'u.LIB_UM',           # Unité
            '5': 'ce.LIB_CENTRE',      # Centre
            '6': 'PU',                 # P.U (TND)
            '7': 'MONTANT'             # Montant (TND)
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            # ملاحظة: PU و MONTANT أعمدة محسوبة، لذا نستخدم التعبير الأصلي للفرز
            if col_name == 'PU':
                order_clause = f"""
                    ORDER BY (COALESCE(s.PUMP, 0) / 1000.0) {'ASC' if order_dir == 'asc' else 'DESC'}
                """
            elif col_name == 'MONTANT':
                order_clause = f"""
                    ORDER BY ((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt) {'ASC' if order_dir == 'asc' else 'DESC'}
                """
            else:
                order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
                order_clause = f"ORDER BY {col_name} {order_dir_sql}"

    # --- البيانات الجدولية (محسّنة) ---
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        
        cursor.execute(f"""
            SELECT 
                'Sortie' AS type,
                f.date_b,
                f.num AS numero_bon,
                a.LIB_ART AS lib_art,
                f.qte_mvt,
                u.LIB_UM AS unite,
                ce.LIB_CENTRE AS centre,
                COALESCE(s.PUMP, 0) / 1000.0 AS PU,
                (COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt AS MONTANT,
                'Sortie' AS sens,
                b2.ref_doc AS ref_document
            FROM fiche_ebc f
            INNER JOIN ARTICLE a ON f.cod_art = a.COD_ART
            LEFT JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
            LEFT JOIN CENTRE ce ON f.centr_cout = ce.CENTR_COUT
            LEFT JOIN STOCK s ON f.cod_art = s.COD_ART 
                             AND f.val_art = s.VAL_ART
            LEFT JOIN Bon_b2_ebc b2 ON f.cod_art = b2.cod_art 
                                   AND f.num = b2.numero_bon 
                                   AND f.date_b = b2.date_b
            WHERE {full_where}
            {order_clause};
        """, full_params)
        
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Erreur dans les données tabulaires des sorties:", str(e))
        data = []

    months_data = []
    quantities_data = []
    total_valeur_sorties = 0.0

    if cod_art and date_min and date_max:
        try:
            # --- حساب القيمة الإجمالية للصادرات ---
            # ملاحظة: القيمة الإجمالية لا تتأثر بالبحث أو الفرز
            cursor.execute(f"""
                SELECT COALESCE(SUM((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt), 0)
                FROM fiche_ebc f
                LEFT JOIN STOCK s ON f.cod_art = s.COD_ART 
                                 AND f.val_art = s.VAL_ART
                WHERE {where_sql}
            """, params)
            
            total_valeur_sorties = float(cursor.fetchone()[0] or 0)

            # --- الرسم البياني: القيمة الإجمالية للصادرات ---
            # ملاحظة: الرسم البياني لا يتأثر بالبحث أو الفرز
            cursor.execute(f"""
                SELECT 
                    YEAR(f.date_b) AS yr,
                    MONTH(f.date_b) AS mth,
                    SUM((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt) AS total
                FROM fiche_ebc f
                LEFT JOIN STOCK s ON f.cod_art = s.COD_ART 
                                 AND f.val_art = s.VAL_ART
                WHERE {where_sql}
                GROUP BY YEAR(f.date_b), MONTH(f.date_b)
                ORDER BY yr, mth;
            """, params)
            
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

            while current <= end_date:
                year = current.year
                month = current.month
                key = (year, month)

                months_data.append(f"{month_names[month-1]} {str(year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))

                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            if not months_data:
                months_data = ['Période']
                quantities_data = [0]

        except Exception as e:
            print("Erreur dans le graphique des sorties:", str(e))
            months_data = ['Erreur']
            quantities_data = [0]
    else:
        months_data = []
        quantities_data = []

    # --- حساب العدد الإجمالي للسجلات ---
    try:
        # العدد الإجمالي (بدون تأثير البحث)
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM fiche_ebc f
            INNER JOIN ARTICLE a ON f.cod_art = a.COD_ART
            WHERE {where_sql}
        """, params)
        total_records = cursor.fetchone()[0]
        
        # العدد بعد تطبيق البحث
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM fiche_ebc f
            INNER JOIN ARTICLE a ON f.cod_art = a.COD_ART
            WHERE {full_where}
        """, full_params)
        filtered_records = cursor.fetchone()[0]
    except Exception as e:
        print("Erreur dans le calcul des enregistrements:", str(e))
        total_records = len(data)
        filtered_records = len(data)

    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'total_valeur_sorties': total_valeur_sorties,
        'total_records': total_records,      # ← جديد
        'filtered_records': filtered_records  # ← جديد
    }


def get_retours_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                    search_value=None, order_column_index=None, order_dir='asc'):
    # بناء شرط WHERE ديناميكي
    where_clauses = ["e3.date_b >= %s", "e3.date_b <= %s"]
    params = [date_min, date_max]
    
    # if cod_art:
        # where_clauses.append("e3.cod_art = %s")
        # params.append(cod_art)
    # if nat_stock:
        # where_clauses.append("e3.nat_stock = %s")
        # params.append(nat_stock)
    # if val_art:
        # where_clauses.append("e3.val_art = %s")
        # params.append(val_art)
    
    where_sql = " AND ".join(where_clauses)

    # --- بناء شرط البحث ---
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = [
            "e3.numero_bon LIKE %s",
            "e3.lib_art LIKE %s"
        ]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    # --- بناء شرط الفرز ---
    order_clause = "ORDER BY e3.date_b DESC"  # افتراضي
    if order_column_index and order_column_index.isdigit():
        # خريطة الأعمدة: index في DataTables -> اسم العمود في SQL
        columns_map = {
            '0': 'e3.date_b',       # Date
            '1': 'e3.numero_bon',   # N° Bon
            '2': 'e3.lib_art',      # Libellé
            '3': 'e3.qte_mvt'       # Quantité
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"

    # --- البيانات الجدولية ---
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        
        cursor.execute(f"""
            SELECT 
                'Retour' AS type,
                e3.date_b,
                e3.numero_bon,
                e3.lib_art,
                e3.qte_mvt,
                NULL AS extra,
                'Entrée' AS sens
            FROM Etat_b3 e3
            WHERE {full_where}
            {order_clause};
        """, full_params)
        
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Erreur dans les données tabulaires des retours:", str(e))
        data = []

    months_data = []
    quantities_data = []

    if cod_art and date_min and date_max:
        try:
            # --- الرسم البياني: كمية المرتجعات الشهرية ---
            # ملاحظة: الرسم البياني لا يتأثر بالبحث أو الفرز
            chart_where = ["e3.date_b >= %s", "e3.date_b <= %s"]
            chart_params = [date_min, date_max]
            
            # if cod_art:
                # chart_where.append("e3.cod_art = %s")
                # chart_params.append(cod_art)
            # if nat_stock:
                # chart_where.append("e3.nat_stock = %s")
                # chart_params.append(nat_stock)
            # if val_art:
                # chart_where.append("e3.val_art = %s")
                # chart_params.append(val_art)
                
            chart_where_sql = " AND ".join(chart_where)

            cursor.execute(f"""
                SELECT 
                    YEAR(e3.date_b) AS yr,
                    MONTH(e3.date_b) AS mth,
                    SUM(e3.qte_mvt) AS total
                FROM Etat_b3 e3
                WHERE {chart_where_sql}
                GROUP BY YEAR(e3.date_b), MONTH(e3.date_b)
                ORDER BY yr, mth;
            """, chart_params)
            
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

            while current <= end_date:
                year = current.year
                month = current.month
                key = (year, month)

                months_data.append(f"{month_names[month-1]} {str(year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))

                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            if not months_data:
                months_data = ['Période']
                quantities_data = [0]

        except Exception as e:
            print("Erreur dans le graphique des retours:", str(e))
            months_data = ['Erreur']
            quantities_data = [0]
    else:
        months_data = []
        quantities_data = []

    # --- حساب العدد الإجمالي للسجلات ---
    try:
        # العدد الإجمالي (بدون تأثير البحث)
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b3 e3 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        
        # العدد بعد تطبيق البحث
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b3 e3 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except Exception as e:
        print("Erreur dans le calcul des enregistrements:", str(e))
        total_records = len(data)
        filtered_records = len(data)

    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'total_records': total_records,      # ← جديد
        'filtered_records': filtered_records  # ← جديد
    }


def get_prestations_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                        search_value=None, order_column_index=None, order_dir='asc'):
    # بناء شرط WHERE ديناميكي
    where_clauses = ["e4.date_b >= %s", "e4.date_b <= %s"]
    params = [date_min, date_max]
    
    # if cod_art:
        # where_clauses.append("e4.cod_art = %s")
        # params.append(cod_art)
    # if nat_stock:
        # where_clauses.append("e4.nat_stock = %s")
        # params.append(nat_stock)
    # if val_art:
        # where_clauses.append("e4.val_art = %s")
        # params.append(val_art)
    
    where_sql = " AND ".join(where_clauses)

    # --- بناء شرط البحث ---
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = [
            "e4.numero_bon LIKE %s",
            "e4.lib_art LIKE %s"
        ]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    # --- بناء شرط الفرز ---
    order_clause = "ORDER BY e4.date_b DESC"  # افتراضي
    if order_column_index and order_column_index.isdigit():
        # خريطة الأعمدة: index في DataTables -> اسم العمود في SQL
        columns_map = {
            '0': 'e4.date_b',       # Date
            '1': 'e4.numero_bon',   # N° Bon
            '2': 'e4.lib_art',      # Libellé
            '3': 'e4.qte_mvt'       # Quantité
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"

    # --- البيانات الجدولية ---
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        
        cursor.execute(f"""
            SELECT 
                'Prestation' AS type,
                e4.date_b,
                e4.numero_bon,
                e4.lib_art,
                e4.qte_mvt,
                NULL AS extra,
                'Sortie' AS sens
            FROM Etat_b4 e4
            WHERE {full_where}
            {order_clause};
        """, full_params)
        
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        print("Erreur dans les données tabulaires des prestations:", str(e))
        data = []

    months_data = []
    quantities_data = []

    if cod_art and date_min and date_max:
        try:
            # --- الرسم البياني: كمية الخدمات الشهرية ---
            # ملاحظة: الرسم البياني لا يتأثر بالبحث أو الفرز
            chart_where = ["e4.date_b >= %s", "e4.date_b <= %s"]
            chart_params = [date_min, date_max]
            
            # if cod_art:
                # chart_where.append("e4.cod_art = %s")
                # chart_params.append(cod_art)
            # if nat_stock:
                # chart_where.append("e4.nat_stock = %s")
                # chart_params.append(nat_stock)
            # if val_art:
                # chart_where.append("e4.val_art = %s")
                # chart_params.append(val_art)
                
            chart_where_sql = " AND ".join(chart_where)

            cursor.execute(f"""
                SELECT 
                    YEAR(e4.date_b) AS yr,
                    MONTH(e4.date_b) AS mth,
                    SUM(e4.qte_mvt) AS total
                FROM Etat_b4 e4
                WHERE {chart_where_sql}
                GROUP BY YEAR(e4.date_b), MONTH(e4.date_b)
                ORDER BY yr, mth;
            """, chart_params)
            
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}

            while current <= end_date:
                year = current.year
                month = current.month
                key = (year, month)

                months_data.append(f"{month_names[month-1]} {str(year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))

                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)

            if not months_data:
                months_data = ['Période']
                quantities_data = [0]

        except Exception as e:
            print("Erreur dans le graphique des prestations:", str(e))
            months_data = ['Erreur']
            quantities_data = [0]
    else:
        months_data = []
        quantities_data = []

    # --- حساب العدد الإجمالي للسجلات ---
    try:
        # العدد الإجمالي (بدون تأثير البحث)
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b4 e4 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        
        # العدد بعد تطبيق البحث
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b4 e4 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except Exception as e:
        print("Erreur dans le calcul des enregistrements:", str(e))
        total_records = len(data)
        filtered_records = len(data)

    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'total_records': total_records,      # ← جديد
        'filtered_records': filtered_records  # ← جديد
    }


def get_mouvements_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                       search_value=None, order_column_index=None, order_dir='asc'):
    all_movements = []

    if not cod_art or not date_min or not date_max:
        return {'data': [], 'months': [], 'datasets': [], 'total_records': 0, 'filtered_records': 0}

    try:
        start_date = datetime.strptime(date_min, '%Y-%m-%d').date().replace(day=1)
        end_date = datetime.strptime(date_max, '%Y-%m-%d').date()

        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                       'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

        months_data = []
        current = start_date
        while current <= end_date:
            months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
            current = (current.replace(month=current.month + 1) 
                       if current.month < 12 else current.replace(year=current.year+1, month=1))

        achat_data = [0.0] * len(months_data)
        consommation_data = [0.0] * len(months_data)
        # sorties_data = [0.0] * len(months_data)  # ← معطلة كما طلبت
        retours_data = [0.0] * len(months_data)
        prestations_data = [0.0] * len(months_data)

        def get_month_index(date_b):
            if isinstance(date_b, str):
                date_b = datetime.strptime(date_b, '%Y-%m-%d').date()
            idx = ((date_b.year - start_date.year) * 12 + date_b.month - start_date.month)
            return idx if 0 <= idx < len(months_data) else None

        # --- بناء شروط WHERE بشكل آمن ---
        def build_params_and_conditions(base_table_alias, has_val_art=False):
            conditions = [
                f"{base_table_alias}.date_b >= %s",
                f"{base_table_alias}.date_b <= %s",
                f"{base_table_alias}.cod_art = %s"
            ]
            params = [date_min, date_max, cod_art]
            
            if nat_stock:
                conditions.append(f"{base_table_alias}.nat_stock = %s")
                params.append(nat_stock)
                
            if has_val_art and val_art:
                conditions.append(f"{base_table_alias}.val_art = %s")
                params.append(val_art)
                
            return " AND ".join(conditions), params

        # --- استعلامات الكميات الشهرية (بدون Sorties) ---
        queries = [
            # Achat (Etat_b1 - بدون val_art)
            (
                "SELECT e1.date_b, e1.qte_mvt FROM Etat_b1 e1 WHERE {}",
                build_params_and_conditions('e1', has_val_art=False),
                achat_data
            ),
            # Consommation (Etat_b2 - مع val_art)
            (
                "SELECT e2.date_b, e2.qte_mvt FROM Etat_b2 e2 WHERE {}",
                build_params_and_conditions('e2', has_val_art=True),
                consommation_data
            ),
            # Sorties (fiche_ebc - مع val_art) - معطلة
            # (
                # "SELECT f.date_b, f.qte_mvt FROM fiche_ebc f WHERE {} AND f.nature_bon LIKE 'b2'",
                # build_params_and_conditions('f', has_val_art=True),
                # sorties_data
            # ),
            # Retours (Etat_b3 - مع val_art)
            (
                "SELECT e3.date_b, e3.qte_mvt FROM Etat_b3 e3 WHERE {}",
                build_params_and_conditions('e3', has_val_art=True),
                retours_data
            ),
            # Prestations (Etat_b4 - مع val_art)
            (
                "SELECT e4.date_b, e4.qte_mvt FROM Etat_b4 e4 WHERE {}",
                build_params_and_conditions('e4', has_val_art=True),
                prestations_data
            ),
        ]

        for sql_template, (where_clause, params), target_list in queries:
            try:
                full_sql = sql_template.format(where_clause)
                cursor.execute(full_sql, params)
                for row in cursor.fetchall():
                    date_b = row[0]
                    qte = float(row[1]) if row[1] else 0.0
                    idx = get_month_index(date_b)
                    if idx is not None:
                        target_list[idx] += qte
            except Exception as e:
                print(f"Erreur dans la requête de mouvements: {str(e)}")
                continue

        # --- بناء شرط البحث ---
        search_filter = ""
        if search_value:
            search_conditions = []
            search_conditions.append(f"numero_bon LIKE '%{search_value}%'")
            search_conditions.append(f"lib_art LIKE '%{search_value}%'")
            search_conditions.append(f"type LIKE '%{search_value}%'")
            search_filter = " AND (" + " OR ".join(search_conditions) + ")"

        # --- استعلامات البيانات الجدولية (بدون Sorties) ---
        table_queries = [
            # Achat (بدون val_art)
            (
                """
                SELECT 'Achat' AS type, e1.date_b, e1.numero_bon, a.LIB_ART, e1.qte_mvt, 
                       CAST(e1.valeur_tot / NULLIF(e1.qte_mvt, 0) AS FLOAT) AS extra, 'Entrée' AS sens
                FROM Etat_b1 e1
                INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART
                WHERE {}
                """,
                build_params_and_conditions('e1', has_val_art=False)
            ),
            # Consommation (مع val_art)
            (
                """
                SELECT 'Consommation' AS type, e2.date_b, e2.numero_bon, e2.lib_art, e2.qte_mvt,
                       CASE 
                           WHEN e2.val_art = 1 THEN '100%%'
                           WHEN e2.val_art = 2 THEN '75%%'
                           WHEN e2.val_art = 3 THEN '25%%'
                           WHEN e2.val_art = 4 THEN '0%%'
                           ELSE 'Inconnu' 
                       END AS extra, 'Sortie' AS sens
                FROM Etat_b2 e2
                WHERE {}
                """,
                build_params_and_conditions('e2', has_val_art=True)
            ),
            # Sorties - معطلة
            # (
                # """
                # SELECT 'Sortie' AS type, f.date_b, f.num AS numero_bon, a.LIB_ART, f.qte_mvt, NULL AS extra, 'Sortie' AS sens
                # FROM fiche_ebc f
                # LEFT JOIN ARTICLE a ON f.cod_art = a.COD_ART
                # WHERE {} AND f.nature_bon LIKE 'b2'
                # """,
                # build_params_and_conditions('f', has_val_art=True)
            # ),
            # Retours
            (
                """
                SELECT 'Retour' AS type, e3.date_b, e3.numero_bon, e3.lib_art, e3.qte_mvt, NULL AS extra, 'Entrée' AS sens
                FROM Etat_b3 e3
                WHERE {}
                """,
                build_params_and_conditions('e3', has_val_art=True)
            ),
            # Prestations
            (
                """
                SELECT 'Prestation' AS type, e4.date_b, e4.numero_bon, e4.lib_art, e4.qte_mvt, NULL AS extra, 'Sortie' AS sens
                FROM Etat_b4 e4
                WHERE {}
                """,
                build_params_and_conditions('e4', has_val_art=True)
            ),
        ]

        columns = ['type', 'date_b', 'numero_bon', 'lib_art', 'qte_mvt', 'extra', 'sens']
        for sql_template, (where_clause, params) in table_queries:
            try:
                full_sql = sql_template.format(where_clause)
                cursor.execute(full_sql, params)
                for row in cursor.fetchall():
                    d = dict(zip(columns, row))
                    d['lib_art'] = d.get('lib_art') or "Inconnu"
                    all_movements.append(d)
            except Exception as e:
                print(f"Erreur dans la requête tabulaire: {str(e)}")
                continue

        # --- تطبيق البحث على النتائج النهائية ---
        if search_value:
            all_movements = [
                item for item in all_movements
                if (search_value.lower() in str(item.get('numero_bon', '')).lower() or
                    search_value.lower() in str(item.get('lib_art', '')).lower() or
                    search_value.lower() in str(item.get('type', '')).lower())
            ]

        # --- تطبيق الفرز ---
        if order_column_index and order_column_index.isdigit():
            columns_map = {
                '0': 'type',
                '1': 'date_b',
                '2': 'numero_bon',
                '3': 'lib_art',
                '4': 'qte_mvt',
                '5': 'extra',
                '6': 'sens'
            }
            if order_column_index in columns_map:
                sort_key = columns_map[order_column_index]
                reverse_order = order_dir != 'asc'
                try:
                    all_movements.sort(
                        key=lambda x: (x.get(sort_key) is None, x.get(sort_key)),
                        reverse=reverse_order
                    )
                except Exception as e:
                    print(f"Erreur de tri: {str(e)}")
                    all_movements.sort(key=lambda x: x['date_b'], reverse=True)
            else:
                all_movements.sort(key=lambda x: x['date_b'], reverse=True)
        else:
            all_movements.sort(key=lambda x: x['date_b'], reverse=True)

        datasets = [
            {'label': 'Achats', 'data': achat_data, 'borderColor': '#0d6efd', 'backgroundColor': 'rgba(13, 110, 253, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#0d6efd'},
            {'label': 'Consommation', 'data': consommation_data, 'borderColor': '#dc3545', 'backgroundColor': 'rgba(220, 53, 69, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#dc3545'},
            # {'label': 'Sorties', 'data': sorties_data, 'borderColor': '#fd7e14', 'backgroundColor': 'rgba(253, 126, 20, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#fd7e14'},
            {'label': 'Retours', 'data': retours_data, 'borderColor': '#198754', 'backgroundColor': 'rgba(25, 135, 84, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#198754'},
            {'label': 'Prestations', 'data': prestations_data, 'borderColor': '#6f42c1', 'backgroundColor': 'rgba(111, 66, 193, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#6f42c1'}
        ]

        total_records = len(all_movements)
        filtered_records = len(all_movements)  # البحث تم على مستوى Python

        return {
            'data': all_movements,
            'months': months_data,
            'datasets': datasets,
            'total_records': total_records,
            'filtered_records': filtered_records
        }

    except Exception as e:
        print("Erreur critique dans get_mouvements_", str(e))
        return {'data': [], 'months': [], 'datasets': [], 'total_records': 0, 'filtered_records': 0}

@csrf_exempt
@login_required
def export_tab_excel(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
        tab = data.get('tab')
        cod_art = data.get('cod_art', '').strip()
        date_min = data.get('date_min', '')
        date_max = data.get('date_max', '')
        nat_stock = data.get('nat_stock', '').strip()
        val_art = data.get('val_art', '').strip()

        if not date_min:
            date_min = (date.today() - timedelta(days=365)).isoformat()
        if not date_max:
            date_max = date.today().isoformat()

        # --- المتغيرات الأساسية ---
        table_data = []
        columns = []
        chart_data = []
        chart_months = []
        query_params = []
        where_sql = ""

        with connections['sql_server'].cursor() as cursor:
            # --- بناء الاستعلام حسب التبويب ---
            if tab == 'achat' and cod_art:
                query = """
                    SELECT e1.doc_ref, e1.date_b, e1.numero_bon, a.LIB_ART, e1.qte_mvt,
                           CASE WHEN e1.qte_mvt > 0 THEN CAST(e1.valeur_tot AS FLOAT) / e1.qte_mvt ELSE 0 END AS PU
                    FROM Etat_b1 e1
                    INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART
                    WHERE a.COD_ART = %s
                    ORDER BY e1.date_b DESC
                """
                query_params = [cod_art]
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

                # بيانات الرسم البياني
                chart_query = """
                    SELECT 
                        FORMAT(e1.date_b, 'MMM yyyy') AS month_label,
                        SUM(e1.qte_mvt) AS total
                    FROM Etat_b1 e1
                    WHERE e1.cod_art = %s
                    GROUP BY YEAR(e1.date_b), MONTH(e1.date_b), FORMAT(e1.date_b, 'MMM yyyy')
                    ORDER BY YEAR(e1.date_b), MONTH(e1.date_b)
                """
                cursor.execute(chart_query, [cod_art])
                chart_rows = cursor.fetchall()
                chart_months = [row[0] for row in chart_rows]
                chart_data = [float(row[1]) for row in chart_rows]

            elif tab == 'entrees':
                where_clauses = ["e1.date_b >= %s", "e1.date_b <= %s"]
                query_params = [date_min, date_max]
                # if cod_art:
                    # where_clauses.append("e1.cod_art = %s")
                    # query_params.append(cod_art)
                # if nat_stock:
                    # where_clauses.append("e1.nat_stock = %s")
                    # query_params.append(nat_stock)
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                    SELECT e1.date_b, e1.numero_bon, e1.lib_art, e1.qte_mvt, e1.valeur_tot
                    FROM Etat_b1 e1
                    WHERE {where_sql}
                    ORDER BY e1.date_b DESC
                """
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

                # بيانات الرسم البياني
                chart_query = f"""
                    SELECT 
                        FORMAT(e1.date_b, 'MMM yyyy') AS month_label,
                        SUM(e1.valeur_tot) AS total
                    FROM Etat_b1 e1
                    WHERE {where_sql}
                    GROUP BY YEAR(e1.date_b), MONTH(e1.date_b), FORMAT(e1.date_b, 'MMM yyyy')
                    ORDER BY YEAR(e1.date_b), MONTH(e1.date_b)
                """
                cursor.execute(chart_query, query_params)
                chart_rows = cursor.fetchall()
                chart_months = [row[0] for row in chart_rows]
                chart_data = [float(row[1]) for row in chart_rows]

            elif tab == 'sorties':
                where_clauses = ["f.date_b >= %s", "f.date_b <= %s", "f.nature_bon LIKE 'b2'"]
                query_params = [date_min, date_max]
                # if cod_art:
                    # where_clauses.append("f.cod_art = %s")
                    # query_params.append(cod_art)
                # if nat_stock:
                    # where_clauses.append("f.nat_stock = %s")
                    # query_params.append(nat_stock)
                # if val_art:
                    # where_clauses.append("f.val_art = %s")
                    # query_params.append(val_art)
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                    SELECT f.date_b, f.num AS numero_bon, a.LIB_ART, f.qte_mvt,
                           (COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt AS MONTANT
                    FROM fiche_ebc f
                    LEFT JOIN ARTICLE a ON f.cod_art = a.COD_ART
                    LEFT JOIN STOCK s ON f.cod_art = s.COD_ART AND f.val_art = s.VAL_ART
                    WHERE {where_sql}
                    ORDER BY f.date_b DESC
                """
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

                # بيانات الرسم البياني
                chart_query = f"""
                    SELECT 
                        FORMAT(f.date_b, 'MMM yyyy') AS month_label,
                        SUM((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt) AS total
                    FROM fiche_ebc f
                    LEFT JOIN STOCK s ON f.cod_art = s.COD_ART AND f.val_art = s.VAL_ART
                    WHERE {where_sql}
                    GROUP BY YEAR(f.date_b), MONTH(f.date_b), FORMAT(f.date_b, 'MMM yyyy')
                    ORDER BY YEAR(f.date_b), MONTH(f.date_b)
                """
                cursor.execute(chart_query, query_params)
                chart_rows = cursor.fetchall()
                chart_months = [row[0] for row in chart_rows]
                chart_data = [float(row[1]) for row in chart_rows]

            elif tab == 'retours':
                where_clauses = ["e3.date_b >= %s", "e3.date_b <= %s"]
                query_params = [date_min, date_max]
                # if cod_art:
                    # where_clauses.append("e3.cod_art = %s")
                    # query_params.append(cod_art)
                # if nat_stock:
                    # where_clauses.append("e3.nat_stock = %s")
                    # query_params.append(nat_stock)
                # if val_art:
                    # where_clauses.append("e3.val_art = %s")
                    # query_params.append(val_art)
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                    SELECT e3.date_b, e3.numero_bon, e3.lib_art, e3.qte_mvt
                    FROM Etat_b3 e3
                    WHERE {where_sql}
                    ORDER BY e3.date_b DESC
                """
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

                # بيانات الرسم البياني
                chart_query = f"""
                    SELECT 
                        FORMAT(e3.date_b, 'MMM yyyy') AS month_label,
                        SUM(e3.qte_mvt) AS total
                    FROM Etat_b3 e3
                    WHERE {where_sql}
                    GROUP BY YEAR(e3.date_b), MONTH(e3.date_b), FORMAT(e3.date_b, 'MMM yyyy')
                    ORDER BY YEAR(e3.date_b), MONTH(e3.date_b)
                """
                cursor.execute(chart_query, query_params)
                chart_rows = cursor.fetchall()
                chart_months = [row[0] for row in chart_rows]
                chart_data = [float(row[1]) for row in chart_rows]

            elif tab == 'prestations':
                where_clauses = ["e4.date_b >= %s", "e4.date_b <= %s"]
                query_params = [date_min, date_max]
                # if cod_art:
                    # where_clauses.append("e4.cod_art = %s")
                    # query_params.append(cod_art)
                # if nat_stock:
                    # where_clauses.append("e4.nat_stock = %s")
                    # query_params.append(nat_stock)
                # if val_art:
                    # where_clauses.append("e4.val_art = %s")
                    # query_params.append(val_art)
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                    SELECT e4.date_b, e4.numero_bon, e4.lib_art, e4.qte_mvt
                    FROM Etat_b4 e4
                    WHERE {where_sql}
                    ORDER BY e4.date_b DESC
                """
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

                # بيانات الرسم البياني
                chart_query = f"""
                    SELECT 
                        FORMAT(e4.date_b, 'MMM yyyy') AS month_label,
                        SUM(e4.qte_mvt) AS total
                    FROM Etat_b4 e4
                    WHERE {where_sql}
                    GROUP BY YEAR(e4.date_b), MONTH(e4.date_b), FORMAT(e4.date_b, 'MMM yyyy')
                    ORDER BY YEAR(e4.date_b), MONTH(e4.date_b)
                """
                cursor.execute(chart_query, query_params)
                chart_rows = cursor.fetchall()
                chart_months = [row[0] for row in chart_rows]
                chart_data = [float(row[1]) for row in chart_rows]

            elif tab == 'consommation' and cod_art:
                where_clauses = ["e2.cod_art = %s"]
                query_params = [cod_art]
                if nat_stock:
                    where_clauses.append("e2.nat_stock = %s")
                    query_params.append(nat_stock)
                if val_art:
                    where_clauses.append("e2.val_art = %s")
                    query_params.append(val_art)
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                    SELECT e2.date_b, e2.numero_bon, e2.lib_art, e2.qte_mvt,
                           CASE WHEN e2.val_art = 1 THEN '100%'
                                WHEN e2.val_art = 2 THEN '75%'
                                WHEN e2.val_art = 3 THEN '25%'
                                WHEN e2.val_art = 4 THEN '0%'
                                ELSE 'Inconnu' END AS VALEUR
                    FROM Etat_b2 e2
                    WHERE {where_sql}
                    ORDER BY e2.date_b DESC
                """
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

                # بيانات الرسم البياني
                chart_query = f"""
                    SELECT 
                        FORMAT(e2.date_b, 'MMM yyyy') AS month_label,
                        SUM(e2.qte_mvt) AS total
                    FROM Etat_b2 e2
                    WHERE {where_sql}
                    GROUP BY YEAR(e2.date_b), MONTH(e2.date_b), FORMAT(e2.date_b, 'MMM yyyy')
                    ORDER BY YEAR(e2.date_b), MONTH(e2.date_b)
                """
                cursor.execute(chart_query, query_params)
                chart_rows = cursor.fetchall()
                chart_months = [row[0] for row in chart_rows]
                chart_data = [float(row[1]) for row in chart_rows]

            elif tab == 'mouvements' and cod_art:
                query = """
                    SELECT type, date_b, numero_bon, lib_art, qte_mvt, sens
                    FROM (
                        SELECT 'Entrée' as type, e1.date_b, e1.numero_bon, e1.lib_art, e1.qte_mvt, 'Entrée' as sens
                        FROM Etat_b1 e1 WHERE e1.cod_art = %s AND e1.date_b >= %s AND e1.date_b <= %s
                        UNION ALL
                        SELECT 'Sortie' as type, f.date_b, f.num, a.LIB_ART, f.qte_mvt, 'Sortie' as sens
                        FROM fiche_ebc f LEFT JOIN ARTICLE a ON f.cod_art = a.COD_ART
                        WHERE f.cod_art = %s AND f.date_b >= %s AND f.date_b <= %s AND f.nature_bon LIKE 'b2'
                        UNION ALL
                        SELECT 'Retour' as type, e3.date_b, e3.numero_bon, e3.lib_art, e3.qte_mvt, 'Entrée' as sens
                        FROM Etat_b3 e3 WHERE e3.cod_art = %s AND e3.date_b >= %s AND e3.date_b <= %s
                        UNION ALL
                        SELECT 'Prestation' as type, e4.date_b, e4.numero_bon, e4.lib_art, e4.qte_mvt, 'Sortie' as sens
                        FROM Etat_b4 e4 WHERE e4.cod_art = %s AND e4.date_b >= %s AND e4.date_b <= %s
                    ) AS all_movements
                    ORDER BY date_b DESC
                """
                cursor.execute(query, [cod_art, date_min, date_max, cod_art, date_min, date_max, cod_art, date_min, date_max,cod_art, date_min, date_max])
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()

            else:
                return HttpResponse(status=400)

        # --- إنشاء ملف Excel ---
        wb = Workbook()
        ws = wb.active
        ws.title = tab.capitalize()

        # --- إضافة العنوان الرئيسي ---
        ws.merge_cells('A1:F1')
        ws['A1'] = f"Statistiques - {tab.capitalize()} ({date_min} au {date_max})"
        ws['A1'].font = Font(size=16, bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")

        # --- إضافة البيانات الجدولية ---
        if columns and table_data:
            # ترجمة أسماء الأعمدة
            column_mapping = {
                'date_b': 'Date', 'numero_bon': 'N° Bon', 'lib_art': 'Libellé Article',
                'qte_mvt': 'Quantité', 'MONTANT': 'Montant (TND)', 'unite': 'Unité',
                'centre': 'Centre', 'PU': 'Prix Unitaire (TND)', 'doc_ref': 'N° BC',
                'VALEUR': 'Valeur (%)', 'valeur_tot': 'Valeur Totale (TND)',
                'type': 'Type', 'sens': 'Sens'
            }
            headers = [column_mapping.get(col, col) for col in columns]
            
            # كتابة العناوين
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=3, column=col_num, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style='thin'), 
                    right=Side(style='thin'), 
                    top=Side(style='thin'), 
                    bottom=Side(style='thin')
                )
            
            # كتابة البيانات
            for row_num, row_data in enumerate(table_data, 4):
                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    cell.border = Border(
                        left=Side(style='thin'), 
                        right=Side(style='thin'), 
                        top=Side(style='thin'), 
                        bottom=Side(style='thin')
                    )
                    # تنسيق التواريخ
                    if columns[col_num-1] == 'date_b' and value:
                        cell.number_format = 'dd/mm/yyyy'

        # --- إضافة الرسم البياني (للتبويبات المدعومة) ---
        if chart_months and chart_data and tab != 'mouvements':
            # إضافة بيانات الرسم البياني في أعمدة منفصلة
            chart_start_col = len(columns) + 2
            ws.cell(row=3, column=chart_start_col, value="Mois")
            ws.cell(row=3, column=chart_start_col+1, value="Valeur")
            
            for i, (month, value) in enumerate(zip(chart_months, chart_data), 4):
                ws.cell(row=i, column=chart_start_col, value=month)
                ws.cell(row=i, column=chart_start_col+1, value=value)

            # إنشاء الرسم البياني
            chart = LineChart()
            chart.title = f"Évolution des {tab.capitalize()}"
            chart.style = 13
            chart.height = 10  # ارتفاع الرسم البياني (بوحدات Excel)
            chart.width = 20   # عرض الرسم البياني (بوحدات Excel)
            chart.x_axis.title = "Mois"
            chart.y_axis.title = "Valeur" if tab in ['achat', 'consommation', 'retours', 'prestations'] else "Valeur (TND)"
            
            # تحديد البيانات
            data = Reference(ws, min_col=chart_start_col+1, min_row=3, max_row=3+len(chart_data))
            cats = Reference(ws, min_col=chart_start_col, min_row=4, max_row=3+len(chart_data))
            
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            
            # إضافة الرسم البياني إلى الورقة
            ws.add_chart(chart, f"{get_column_letter(chart_start_col)}10")

        # --- ضبط عرض الأعمدة تلقائيًا ---
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        # --- حفظ الملف ---
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=Statistiques_{tab}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        return response

    except Exception as e:
        print("Erreur export Excel:", str(e))
        return HttpResponse(status=500)
    
    
    
# ===========================

# def recherche_par_caracteristiques(request):
    # """
    # عرض صفحة البحث عن السلع باستخدام الخصائص التقنية.
    # """
    # return render(request, 'core/recherche_par_caracteristiques.html')

@csrf_exempt
def api_search_articles_by_caracts(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        filters = data.get('filters', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données invalides'}, status=400)

    if not filters:
        return JsonResponse({'results': []})

    # ✅ التصحيح: استيراد من الملف الصحيح
    from core.models_sql import ArticleSQL
    from core.models import ArticleCaracteristique

    # جلب جميع المواد من قاعدة SQL Server
    articles = ArticleSQL.objects.using('sql_server').all()

    # جلب كل القيم المسندة من قاعدة البيانات المحلية
    all_assignments = ArticleCaracteristique.objects.select_related('caracteristique')

    results = []
    for art in articles:
        # تحديد القيم المسندة لهذه السلعة فقط
        assignments = all_assignments.filter(cod_art=art.COD_ART)
        match_count = 0
        total_caracts = len(filters)

        for f in filters:
            caract_id = f['id']
            expected_value = f.get('value', None)

            # البحث عن تطابق بالخاصية
            assignment = assignments.filter(caracteristique_id=caract_id).first()
            if not assignment:
                continue  # لا توجد هذه الخاصية للسلعة

            # إذا طُلب تطابق بالقيمة، نتحقق منها
            if expected_value:
                if not assignment.valeur or assignment.valeur.lower() != expected_value.lower():
                    continue

            match_count += 1

        # إضافة النتيجة إذا كان هناك تطابق واحد على الأقل
        if match_count > 0:
            results.append({
                'cod_art': art.COD_ART,
                'libelle': art.LIB_ART,
                'match_count': match_count,
                'total_caracts': total_caracts
            })

    # ترتيب النتائج من الأكثر تطابقًا إلى الأقل
    results.sort(key=lambda x: x['match_count'], reverse=True)

    return JsonResponse({'results': results})

@login_required
def types_mouvement_view(request):
    types = TypeMouvement.objects.all().order_by('code')
    return render(request, 'core/types_mouvement.html', {'types': types})


@csrf_exempt
@login_required
def api_create_type_mouvement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            type_mvt = TypeMouvement.objects.create(
                code=data['code'].strip().upper(),
                libelle=data['libelle'].strip(),
                description=data.get('description', '').strip(),
                sens=data['sens'],
                actif=data.get('actif', True)
            )
            return JsonResponse({
                'status': 'ok',
                'type': {
                    'id': type_mvt.id,
                    'code': type_mvt.code,
                    'libelle': type_mvt.libelle,
                    'description': type_mvt.description or '',
                    'sens': type_mvt.sens,
                    'actif': type_mvt.actif
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@csrf_exempt
@login_required
def api_update_type_mouvement(request, pk):
    try:
        type_mvt = TypeMouvement.objects.get(pk=pk)
    except TypeMouvement.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Non trouvé'}, status=404)

    if request.method == 'POST':
        data = json.loads(request.body)
        type_mvt.code = data['code'].strip().upper()
        type_mvt.libelle = data['libelle'].strip()
        type_mvt.description = data.get('description', '').strip()
        type_mvt.sens = data['sens']
        type_mvt.actif = data.get('actif', True)
        type_mvt.save()

        return JsonResponse({
            'status': 'ok',
            'type': {
                'id': type_mvt.id,
                'code': type_mvt.code,
                'libelle': type_mvt.libelle,
                'description': type_mvt.description or '',
                'sens': type_mvt.sens,
                'actif': type_mvt.actif
            }
        })
    return JsonResponse({'status': 'error'}, status=405)


@csrf_exempt
@login_required
def api_delete_type_mouvement(request, pk):
    try:
        type_mvt = TypeMouvement.objects.get(pk=pk)
        type_mvt.delete()
        return JsonResponse({'status': 'ok'})
    except TypeMouvement.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Non trouvé'}, status=404)

# naature stock
def nature_stock_list(request):
    """
    عرض قائمة طبيعة المخزون.
    يدعم تنسيق JSON عند وجود ?format=json في الطلب.
    """
    query = request.GET.get('q', '')
    if query:
        natures = NatureStock.objects.filter(
            libelle_nature__icontains=query
        ).order_by('code_nature')
    else:
        natures = NatureStock.objects.all().order_by('code_nature')
    
    # دعم تنسيق JSON للقوائم المنسدلة
    if request.GET.get('format') == 'json':
        return JsonResponse(
            list(natures.values('code_nature', 'libelle_nature')),
            safe=False
        )
    
    # العرض العادي
    form = NatureStockForm()
    return render(request, 'core/nature_stock_list.html', {
        'natures': natures,
        'form': form,
        'query': query
    })    

def nature_stock_create(request):
    if request.method == 'POST':
        form = NatureStockForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # طلب AJAX: نعيد JSON بنجاح
                    return JsonResponse({'success': True})
                else:
                    # طلب عادي: نعيد توجيه
                    messages.success(request, 'Nature de stock ajoutée avec succès!')
                    return redirect('core:nature_stock_list')
            except IntegrityError:
                form.add_error('code_nature', 'Ce code existe déjà.')
        
        # في حالة وجود أخطاء
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field.name: field.errors for field in form if field.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    # طلب GET
    form = NatureStockForm()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # لا نستخدم هذا عادةً، لكن نعيده للاستقرار
        return JsonResponse({'success': False, 'error': 'Méthode non supportée'}, status=405)
    
    return render(request, 'core/nature_stock_form.html', {
        'form': form,
        'title': 'Ajouter une nature de stock'
    })

def nature_stock_update(request, pk):
    nature = get_object_or_404(NatureStock, pk=pk)
    if request.method == 'POST':
        form = NatureStockForm(request.POST, instance=nature)
        if form.is_valid():
            try:
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, 'Nature de stock mise à jour avec succès!')
                    return redirect('core:nature_stock_list')
            except IntegrityError:
                form.add_error('code_nature', 'Ce code existe déjà.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field.name: field.errors for field in form if field.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    form = NatureStockForm(instance=nature)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Méthode non supportée'}, status=405)
    
    return render(request, 'core/nature_stock_form.html', {
        'form': form,
        'title': 'Modifier la nature de stock'
    })

def nature_stock_delete(request, pk):
    """حذف طبيعة مخزون"""
    nature = get_object_or_404(NatureStock, pk=pk)
    if request.method == 'POST':
        nature.delete()
        messages.success(request, 'Nature de stock supprimée avec succès!')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})        

def valeur_article_list(request):
    """
    عرض قائمة قيم المادة.
    يدعم تنسيق JSON عند وجود ?format=json في الطلب.
    """
    query = request.GET.get('q', '')
    if query:
        valeurs = ValeurArticle.objects.filter(
            libelle_valeur__icontains=query
        ).order_by('code_valeur')
    else:
        valeurs = ValeurArticle.objects.all().order_by('code_valeur')
    
    # دعم تنسيق JSON للقوائم المنسدلة
    if request.GET.get('format') == 'json':
        return JsonResponse(
            list(valeurs.values('code_valeur', 'libelle_valeur')),
            safe=False
        )
    
    # العرض العادي
    form = ValeurArticleForm()
    return render(request, 'core/valeur_article_list.html', {
        'valeurs': valeurs,
        'form': form,
        'query': query
    })

def valeur_article_create(request):
    if request.method == 'POST':
        form = ValeurArticleForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, 'Valeur d\'article ajoutée avec succès!')
                    return redirect('core:valeur_article_list')
            except IntegrityError:
                form.add_error('code_valeur', 'Ce code existe déjà.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field.name: field.errors for field in form if field.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    form = ValeurArticleForm()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Méthode non supportée'}, status=405)
    
    return render(request, 'core/valeur_article_form.html', {
        'form': form,
        'title': 'Ajouter une valeur d\'article'
    })

def valeur_article_update(request, pk):
    valeur = get_object_or_404(ValeurArticle, pk=pk)
    if request.method == 'POST':
        form = ValeurArticleForm(request.POST, instance=valeur)
        if form.is_valid():
            try:
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, 'Valeur d\'article mise à jour avec succès!')
                    return redirect('core:valeur_article_list')
            except IntegrityError:
                form.add_error('code_valeur', 'Ce code existe déjà.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field.name: field.errors for field in form if field.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    form = ValeurArticleForm(instance=valeur)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Méthode non supportée'}, status=405)
    
    return render(request, 'core/valeur_article_form.html', {
        'form': form,
        'title': 'Modifier la valeur d\'article'
    })

def valeur_article_delete(request, pk):
    valeur = get_object_or_404(ValeurArticle, pk=pk)
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            valeur.delete()
            return JsonResponse({'success': True})
        else:
            valeur.delete()
            messages.success(request, 'Valeur d\'article supprimée avec succès!')
            return redirect('core:valeur_article_list')
    return JsonResponse({'success': False})    

# ===========================

def etape_dossier_list(request):
    query = request.GET.get('q', '')
    if query:
        etapes = EtapeDossier.objects.filter(
            libelle_etape__icontains=query
        ).order_by('code_etape')
    else:
        etapes = EtapeDossier.objects.all().order_by('code_etape')
    
    return render(request, 'core/etape_dossier_list.html', {
        'etapes': etapes,
        'query': query
    })

def etape_dossier_create(request):
    if request.method == 'POST':
        form = EtapeDossierForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, 'Étape de dossier ajoutée avec succès!')
                    return redirect('core:etape_dossier_list')
            except IntegrityError:
                form.add_error('code_etape', 'Ce code existe déjà.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field.name: field.errors for field in form if field.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    form = EtapeDossierForm()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Méthode non supportée'}, status=405)
    
    return render(request, 'core/etape_dossier_form.html', {
        'form': form,
        'title': 'Ajouter une étape de dossier'
    })

def etape_dossier_update(request, pk):
    etape = get_object_or_404(EtapeDossier, pk=pk)
    if request.method == 'POST':
        form = EtapeDossierForm(request.POST, instance=etape)
        if form.is_valid():
            try:
                form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, 'Étape de dossier mise à jour avec succès!')
                    return redirect('core:etape_dossier_list')
            except IntegrityError:
                form.add_error('code_etape', 'Ce code existe déjà.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field.name: field.errors for field in form if field.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    form = EtapeDossierForm(instance=etape)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Méthode non supportée'}, status=405)
    
    return render(request, 'core/etape_dossier_form.html', {
        'form': form,
        'title': 'Modifier l\'étape de dossier'
    })

def etape_dossier_delete(request, pk):
    etape = get_object_or_404(EtapeDossier, pk=pk)
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            etape.delete()
            return JsonResponse({'success': True})
        else:
            etape.delete()
            messages.success(request, 'Étape de dossier supprimée avec succès!')
            return redirect('core:etape_dossier_list')
    return JsonResponse({'success': False})    

# ==================================================أنشئ view لمراقبة الاستعلامات النشطة
@login_required
def db_monitor_view(request):
    with connections['sql_server'].cursor() as cursor:
        cursor.execute("""
            SELECT 
                session_id,
                blocking_session_id,
                wait_time,
                wait_type,
                SUBSTRING(text, statement_start_offset/2+1, 
                    (CASE WHEN statement_end_offset = -1 
                        THEN LEN(CONVERT(NVARCHAR(MAX), text)) * 2 
                        ELSE statement_end_offset END - statement_start_offset)/2+1) AS query_text
            FROM sys.dm_exec_requests
            CROSS APPLY sys.dm_exec_sql_text(sql_handle)
            WHERE blocking_session_id != 0
        """)
        blocking_queries = cursor.fetchall()
    
    return render(request, 'core/db_monitor.html', {'queries': blocking_queries})    

@login_required
def kill_session_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'success': False, 'error': 'ID de session requis'})
        
        # التحقق من أن session_id رقم صحيح
        try:
            session_id = int(session_id)
            if session_id <= 0:
                raise ValueError("ID invalide")
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'ID de session invalide'})
        
        # منع قتل الجلسات النظامية (اختياري)
        if session_id < 50:
            return JsonResponse({'success': False, 'error': 'Impossible de tuer les sessions système'})
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("KILL %s", [session_id])
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Erreur kill_session: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})    

#===============================================================================================
#==================Bon de Commande==============================================================
#===============================================================================================

@login_required
def bons_commande_view(request):
    """عرض صفحة استعلام بطاقات الأوامر"""
    context = {
        'error': None,
        'fournisseurs': [],
        'natures': [],
        'etats': [],
        'mode_pays': [],
        'devise': [],
        'centres': []
    }
    
    try:
        with connections['sql_server'].cursor() as cursor:
            # جلب قائمة الموردين (لـ Lookup)
            cursor.execute("SELECT CODE_FOURN, LIB_FOURN FROM fourniss ORDER BY LIB_FOURN")
            context['fournisseurs'] = cursor.fetchall()
            
            # جلب القيم الفريدة للـ Nature
            cursor.execute("SELECT DISTINCT NATURE_MAT FROM COMMANDE WHERE NATURE_MAT IS NOT NULL ORDER BY NATURE_MAT")
            context['natures'] = [row[0] for row in cursor.fetchall()]
            
            # جلب القيم الفريدة للـ Etat
            cursor.execute("SELECT DISTINCT FLAG_ANNUL FROM COMMANDE WHERE FLAG_ANNUL IS NOT NULL ORDER BY FLAG_ANNUL")
            context['etats'] = [row[0] for row in cursor.fetchall()]
            
            # جلب القيم الفريدة لـ Mode de paiement
            cursor.execute("SELECT DISTINCT MODE_PAIEM FROM COMMANDE WHERE MODE_PAIEM IS NOT NULL ORDER BY MODE_PAIEM")
            context['mode_pays'] = [row[0] for row in cursor.fetchall()]
            
            # جلب العملات
            cursor.execute("SELECT COD_DEVISE, LIB_DEVISE FROM DEVISE ORDER BY LIB_DEVISE")
            context['devise'] = cursor.fetchall()
            
            # جلب مراكز المسؤولية
            cursor.execute("SELECT CENTR_RESP, LIB_CENT_R FROM CENTRESP ORDER BY LIB_CENT_R")
            context['centres'] = cursor.fetchall()
            
    except Exception as e:
        context['error'] = f"Erreur lors du chargement des filtres: {str(e)}"
        print("Erreur chargement filtres:", str(e))
    
    return render(request, 'core/bons_commande.html', context)

@login_required
def bons_commande_ajax_view(request):
    """AJAX endpoint to fetch purchase orders with human-readable labels."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # === 1. جلب معلمات الفلترة ===
        num_com = request.GET.get('num_com', '').strip()
        code_fourn = request.GET.get('code_fourn', '').strip()
        date_com_min = request.GET.get('date_com_min', '').strip()
        date_com_max = request.GET.get('date_com_max', '').strip()
        
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 20))
        search_value = request.GET.get('search[value]', '').strip()
        
        # === 2. جلب القيم المفهومة من قواعد البيانات المناسبة ===
        nature_map = {}
        mode_paiem_map = {}
        
        # 2.1. جلب nature_stock من MySQL (default)
        try:
            with connections['default'].cursor() as mysql_cursor:
                mysql_cursor.execute("SELECT code_nature, libelle_Nature FROM nature_stock")
                nature_map = {row[0]: row[1] for row in mysql_cursor.fetchall()}
        except Exception as e:
            print(f"⚠️ تحذير: فشل تحميل nature_stock من MySQL: {e}")
            nature_map = {}
        
        # 2.2. جلب modePaiem من SQL Server (sql_server)
        try:
            with connections['sql_server'].cursor() as mssql_cursor:
                mssql_cursor.execute("SELECT CODE_PAIEM, MODE_PAIEM FROM modePaiem")
                mode_paiem_map = {row[0]: row[1] for row in mssql_cursor.fetchall()}
        except Exception as e:
            print(f"⚠️ تحذير: فشل تحميل modePaiem من SQL Server: {e}")
            mode_paiem_map = {}
        
        # === 3. استعلام بيانات بطاقات الأوامر من SQL Server ===
        with connections['sql_server'].cursor() as cursor:
            where_clauses = ["1=1"]
            params = []
            
            if num_com:
                where_clauses.append("c.NUMERO_COM LIKE %s")
                params.append(f"%{num_com}%")
            if code_fourn:
                where_clauses.append("c.CODE_FOURN = %s")
                params.append(code_fourn)
            if date_com_min:
                where_clauses.append("c.DAT_COM >= %s")
                params.append(date_com_min)
            if date_com_max:
                where_clauses.append("c.DAT_COM <= %s")
                params.append(date_com_max)
                
            if search_value:
                search_conditions = [
                    "c.NUMERO_COM LIKE %s",
                    "f.LIB_FOURN LIKE %s"
                ]
                where_clauses.append("(" + " OR ".join(search_conditions) + ")")
                params.extend([f"%{search_value}%"] * len(search_conditions))
            
            where_sql = " AND ".join(where_clauses)
            
            # العدد الإجمالي
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM COMMANDE c
                LEFT JOIN fourniss f ON c.CODE_FOURN = f.CODE_FOURN
                WHERE {where_sql}
            """, params)
            total_records = cursor.fetchone()[0]
            
            # الترتيب
            order_column = request.GET.get('order[0][column]', '0')
            order_dir = request.GET.get('order[0][dir]', 'desc')
            columns = ['c.NUMERO_COM', 'c.DAT_COM', 'f.LIB_FOURN', 'c.NATURE_MAT', 
                      'c.FLAG_ANNUL', 'c.MODE_PAIEM', 'c.LIV_COM', 'c.TTC']
            order_col_index = int(order_column) if order_column.isdigit() else 0
            order_col = columns[order_col_index] if 0 <= order_col_index < len(columns) else 'c.DAT_COM'
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            
            # جلب البيانات
            cursor.execute(f"""
                SELECT 
                    c.NUMERO_COM,
                    c.DAT_COM,
                    f.LIB_FOURN,
                    c.CODE_FOURN,
                    c.NATURE_MAT,
                    c.FLAG_ANNUL,
                    c.MODE_PAIEM,
                    c.LIV_COM,
                    c.TTC,
                    d.LIB_DEVISE,
                    cr.LIB_CENT_R
                FROM COMMANDE c
                LEFT JOIN fourniss f ON c.CODE_FOURN = f.CODE_FOURN
                LEFT JOIN DEVISE d ON c.COD_DEVISE = d.COD_DEVISE
                LEFT JOIN CENTRESP cr ON c.CENTR_RESP = cr.CENTR_RESP
                WHERE {where_sql}
                ORDER BY {order_col} {order_dir_sql}
                OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
            """, params + [start, length])
            
            columns_desc = [col[0] for col in cursor.description]
            raw_data = [dict(zip(columns_desc, row)) for row in cursor.fetchall()]
        
        # === 4. إثراء البيانات بالقيم المفهومة ===
        enriched_data = []
        for row in raw_data:
            # Nature من MySQL
            nature_code = row.get('NATURE_MAT')
            nature_lib = nature_map.get(nature_code, nature_code or 'Inconnu')
            
            # État (مدمج)
            etat_code = row.get('FLAG_ANNUL')
            etat_lib = 'Actif' if etat_code == '0' else 'Annulé' if etat_code == '1' else 'Inconnu'
            
            # Mode de paiement من SQL Server
            mode_code = row.get('MODE_PAIEM')
            mode_lib = mode_paiem_map.get(mode_code, mode_code or 'Inconnu')
            
            enriched_row = {
                'NUMERO_COM': row.get('NUMERO_COM'),
                'DAT_COM': row.get('DAT_COM'),
                'LIB_FOURN': row.get('LIB_FOURN'),
                'CODE_FOURN': row.get('CODE_FOURN'),
                'NATURE_LIB': nature_lib,
                'ETAT_LIB': etat_lib,
                'MODE_PAIEM_LIB': mode_lib,
                'LIV_COM': row.get('LIV_COM'),
                'TTC': row.get('TTC'),
                'LIB_DEVISE': row.get('LIB_DEVISE'),
                'LIB_CENT_R': row.get('LIB_CENT_R'),
            }
            enriched_data.append(enriched_row)
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,  # يمكنك تحسينه لاحقًا إذا لزم الأمر
            'data': enriched_data
        })
        
    except Exception as e:
        import traceback
        print("=== ERREUR AJAX VIEW ===")
        print("Paramètres:", dict(request.GET))
        print("Erreur:", str(e))
        traceback.print_exc()
        return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)

# إعداد التسجيل للتصحيح
logger = logging.getLogger(__name__)

@login_required
def bons_commande_details_view(request):
    """
    جلب تفاصيل بطاقة الأمر وبنودها بناءً على رقم الأمر أو كود المورد.
    يدعم الخصم الفعلي من جدول LIGNECOM (حقل 'remise').
    """
    try:
        num_com = request.GET.get('num_com', '').strip()
        code_fourn = request.GET.get('code_fourn', '').strip()
        
        if not num_com and not code_fourn:
            return JsonResponse({
                'error': 'Veuillez fournir au moins un critère de recherche (N° bon ou code fournisseur)'
            }, status=400)
        
        logger.info(f"Recherche bon: num_com='{num_com}', code_fourn='{code_fourn}'")
        
        # === جلب الخرائط لعرض القيم المفهومة ===
        nature_map = {}
        mode_paiem_map = {}

        # Nature من MySQL
        try:
            with connections['default'].cursor() as mysql_cursor:
                mysql_cursor.execute("SELECT code_nature, libelle_Nature FROM nature_stock")
                nature_map = {row[0]: row[1] for row in mysql_cursor.fetchall()}
        except Exception as e:
            logger.warning(f"⚠️ فشل تحميل nature_stock من MySQL: {e}")

        # Mode de paiement من SQL Server
        try:
            with connections['sql_server'].cursor() as mssql_cursor:
                mssql_cursor.execute("SELECT CODE_PAIEM, MODE_PAIEM FROM modePaiem")
                mode_paiem_map = {row[0]: row[1] for row in mssql_cursor.fetchall()}
        except Exception as e:
            logger.warning(f"⚠️ فشل تحميل modePaiem من SQL Server: {e}")

        with connections['sql_server'].cursor() as cursor:
            # بناء شرط WHERE ديناميكي
            where_clauses = []
            params = []
            if num_com:
                where_clauses.append("c.NUMERO_COM = %s")
                params.append(num_com)
            if code_fourn:
                where_clauses.append("c.CODE_FOURN = %s")
                params.append(code_fourn)
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # جلب رأس الأمر مع JOIN للعملة ومركز المسؤولية
            cursor.execute(f"""
                SELECT 
                    c.NUMERO_COM, c.DAT_COM, c.CODE_FOURN, c.NATURE_MAT, c.FLAG_ANNUL, 
                    c.MODE_PAIEM, c.LIV_COM, c.TTC, c.FOB, c.FRET, c.COD_DEVISE, c.CENTR_RESP,
                    d.LIB_DEVISE, d.LIB_S_DEVISE,
                    cr.LIB_CENT_R
                FROM COMMANDE c
                LEFT JOIN DEVISE d ON c.COD_DEVISE = d.COD_DEVISE
                LEFT JOIN CENTRESP cr ON c.CENTR_RESP = cr.CENTR_RESP
                WHERE {where_sql}
            """, params)
            
            bon_row = cursor.fetchone()
            if not bon_row:
                error_msg = f"Aucun bon trouvé pour: num_com='{num_com}', code_fourn='{code_fourn}'"
                logger.warning(error_msg)
                return JsonResponse({'error': error_msg}, status=404)
            
            columns = [col[0] for col in cursor.description]
            bon = dict(zip(columns, bon_row))
            
            # جلب بيانات المورد
            fournisseur = {'LIB_FOURN': 'Inconnu'}
            if bon.get('CODE_FOURN'):
                cursor.execute("SELECT LIB_FOURN FROM fourniss WHERE CODE_FOURN = %s", [bon['CODE_FOURN']])
                fourn_row = cursor.fetchone()
                if fourn_row:
                    fournisseur['LIB_FOURN'] = fourn_row[0]
            
            # جلب البنود مع حقل remise (نفترض أن اسم الحقل هو 'remise')
            cursor.execute("""
                SELECT ITEM, LIB_ART, UNITE_MES, QTE, PRIX_UNIT, ISNULL(remise, 0) AS remise
                FROM LIGNECOM 
                WHERE NUMERO_COM = %s
                ORDER BY RANG
            """, [bon['NUMERO_COM']])
            
            ligne_columns = [col[0] for col in cursor.description]
            lignes = []
            total_ht = 0.0
            total_remise = 0.0

            for row in cursor.fetchall():
                ligne = dict(zip(ligne_columns, row))
                qte = float(ligne.get('QTE', 0))
                prix_unit = float(ligne.get('PRIX_UNIT', 0))
                remise_ligne = float(ligne.get('remise', 0))

                ht_ligne = qte * prix_unit
                total_ht += ht_ligne
                total_remise += remise_ligne

                # اختياري: حفظ القيم المؤقتة لكل بند
                ligne['_ht_ligne'] = ht_ligne
                ligne['_remise_ligne'] = remise_ligne
                lignes.append(ligne)
            
            # الحسابات النهائية
            ht_apres_remise = total_ht - total_remise
            tva = ht_apres_remise * 0.19  # TVA = 19% — عدّله حسب نظامك
            total_ttc = bon['TTC']

            # === إثراء bon بالقيم المفهومة ===
            bon['NATURE_LIB'] = nature_map.get(bon.get('NATURE_MAT'), bon.get('NATURE_MAT') or 'Inconnu')
            bon['ETAT_LIB'] = 'Actif' if bon.get('FLAG_ANNUL') == '0' else 'Annulé' if bon.get('FLAG_ANNUL') == '1' else 'Inconnu'
            bon['MODE_PAIEM_LIB'] = mode_paiem_map.get(bon.get('MODE_PAIEM'), bon.get('MODE_PAIEM') or 'Inconnu')

            return JsonResponse({
                'bon': bon,
                'fournisseur': fournisseur,
                'lignes': lignes,
                'calculs': {
                    'total_ht': total_ht,
                    'total_remise': total_remise,
                    'ht_apres_remise': ht_apres_remise,
                    'total_ttc': total_ttc
                }
            })
            
    except Exception as e:
        import traceback
        logger.error("=== ERREUR DÉTAILLÉE DANS bons_commande_details_view ===")
        logger.error(f"Paramètres: num_com={num_com}, code_fourn={code_fourn}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'error': 'Erreur interne du serveur. Veuillez contacter l\'administrateur.'
        }, status=500)

def build_where_clause(params, num_com=None, code_fourn=None, date_com_min=None, date_com_max=None, search_value=None):
    where_clauses = ["1=1"]
    
    if num_com:
        where_clauses.append("c.NUMERO_COM LIKE %s")
        params.append(f"%{num_com}%")
    if code_fourn:
        where_clauses.append("c.CODE_FOURN = %s")
        params.append(code_fourn)
    if date_com_min:
        where_clauses.append("c.DAT_COM >= %s")
        params.append(date_com_min)
    if date_com_max:
        where_clauses.append("c.DAT_COM <= %s")
        params.append(date_com_max)
    if search_value:
        where_clauses.append("(c.NUMERO_COM LIKE %s OR f.LIB_FOURN LIKE %s)")
        params.extend([f"%{search_value}%"] * 2)
    
    return " AND ".join(where_clauses)
    
@login_required
def api_fournisseurs(request):
    """API للبحث عن الموردين"""
    q = request.GET.get('q', '').strip()
    results = []
    
    try:
        with connections['sql_server'].cursor() as cursor:
            if q:
                cursor.execute("SELECT CODE_FOURN, LIB_FOURN FROM fourniss WHERE LIB_FOURN LIKE %s ORDER BY LIB_FOURN", [f"%{q}%"])
            else:
                cursor.execute("SELECT CODE_FOURN, LIB_FOURN FROM fourniss ORDER BY LIB_FOURN LIMIT 50")
            
            for row in cursor.fetchall():
                results.append({
                    'CODE_FOURN': row[0],
                    'LIB_FOURN': row[1]
                })
    except Exception as e:
        print("Erreur dans api_fournisseurs:", str(e))
        results = []
    
    return JsonResponse(results, safe=False)        

#===============================================================================================
#==================Suivie BonCommande===========================================================
#===============================================================================================   

@login_required
def suivi_etapes_view(request):
    num_com = request.GET.get('num_com')
    dat_com_str = request.GET.get('dat_com')
    code_fourn = request.GET.get('code_fourn')
    
    if not all([num_com, dat_com_str, code_fourn]):
        return JsonResponse({'error': 'Paramètres manquants'}, status=400)
    
    try:
        # تحويل النص إلى تاريخ
        if 'T' in dat_com_str:
            # "2025-08-01T00:00:00" → date(2025, 8, 1)
            dat_com = datetime.fromisoformat(dat_com_str.replace('Z', '+00:00')).date()
        else:
            # "2025-08-01"
            dat_com = datetime.strptime(dat_com_str, '%Y-%m-%d').date()
        
        etapes = SuiviDossier.objects.filter(
            numero_com=num_com,
            #dat_com=dat_com,  # ← أعد تفعيل هذا السطر!
            code_fourn=code_fourn
        ).order_by('-date_etape').values()
        
        return JsonResponse(list(etapes), safe=False)
    except Exception as e:
        print("Erreur suivi_etapes:", str(e))
        logger.error(f"Erreur suivi_etapes: {e}")
        return JsonResponse({'error': 'Erreur serveur'}, status=500)

@login_required
def api_etapes_view(request):
    """API: جلب قائمة المراحل المرجعية من etape_dossier"""
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT code_etape, libelle_etape, influence FROM etape_dossier ORDER BY code_etape")
        etapes = [{'code_etape': row[0], 'libelle_etape': row[1], 'influence': row[2]} for row in cursor.fetchall()]
    return JsonResponse(etapes, safe=False)


@login_required
def suivi_etapes_detail_view(request):
    """GET: جلب تفاصيل مرحلة واحدة حسب ID"""
    etape_id = request.GET.get('id')
    try:
        etape = SuiviDossier.objects.get(id=etape_id)
        return JsonResponse({
            'id': etape.id,
            'numero_com': etape.numero_com,
            'dat_com': etape.dat_com.isoformat(),
            'code_fourn': etape.code_fourn,
            'id_etape': etape.id_etape,
            'libelle_etape': etape.libelle_etape,
            'influence_sur_dossier': etape.influence_sur_dossier,
            'observation': etape.observation,
            'numero_bordereau': etape.numero_bordereau,
            'numero_avis': etape.numero_avis,
            'numero_ci': etape.numero_ci,
            'numero_facture': etape.numero_facture,
            'date_facture': etape.date_facture.isoformat() if etape.date_facture else None,
            'numero_bl': etape.numero_bl,
            'date_bl': etape.date_bl.isoformat() if etape.date_bl else None,
            # 'email': etape.email,
            'email_data': etape.email_data or {},
            # --- الحقول الجديدة ---
            'date_etape': etape.date_etape.isoformat() if etape.date_etape else None,
            'date_avis': etape.date_avis.isoformat() if etape.date_avis else None,
            'bct': etape.bct,
            'date_bct': etape.date_bct.isoformat() if etape.date_bct else None,
            'date_bordereau': etape.date_bordereau.isoformat() if etape.date_bordereau else None,
            'date_email': etape.date_email.isoformat() if etape.date_email else None,
        })
    except SuiviDossier.DoesNotExist:
        return JsonResponse({'error': 'Étape non trouvée'}, status=404)

def parse_date_safe(date_str):
    if not date_str or date_str.strip() == '':
        return None
    try:
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        else:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None  # أو يمكنك رفع خطأ إذا أردت
        
@csrf_exempt
@login_required
def suivi_etapes_create_view(request):
    print("Python version:", sys.version)
    print("Executable:", sys.executable)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # قراءة الحقول الأساسية من POST
        numero_com = request.POST.get('numero_com')
        dat_com_str = request.POST.get('dat_com')
        code_fourn = request.POST.get('code_fourn')
        id_etape = request.POST.get('id_etape')
        email_body = request.POST.get('email_body', '')

        # تحويل date_etape (من datetime-local)
        date_etape_str = request.POST.get('date_etape')
        if date_etape_str:
            # دعم التنسيق: "YYYY-MM-DDTHH:mm"
            date_etape = datetime.fromisoformat(date_etape_str.replace('Z', '+00:00'))
            if timezone.is_naive(date_etape):
                date_etape = timezone.make_aware(date_etape)
        else:
            date_etape = timezone.now()

        # التحقق من الحقول الأساسية
        if not all([numero_com, dat_com_str, code_fourn, id_etape]):
            return JsonResponse({
                'error': 'Champs manquants: numero_com, dat_com, code_fourn, id_etape'
            }, status=400)

        # تحويل dat_com إلى كائن date
        if 'T' in dat_com_str:
            dat_com = datetime.fromisoformat(dat_com_str.replace('Z', '+00:00')).date()
        else:
            dat_com = datetime.strptime(dat_com_str, '%Y-%m-%d').date()

        # جلب libelle_etape و influence من etape_dossier
        with connections['default'].cursor() as cursor:
            cursor.execute(
                "SELECT libelle_etape, influence FROM etape_dossier WHERE code_etape = %s",
                [id_etape]
            )
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'error': 'Étape non valide'}, status=400)
            libelle_etape, influence = row

        # إنشاء الكائن مرة واحدة مع كل الحقول
        etape = SuiviDossier.objects.create(
            numero_com=numero_com,
            dat_com=dat_com,
            code_fourn=code_fourn,
            id_etape=id_etape,
            libelle_etape=libelle_etape,
            influence_sur_dossier=influence,
            date_etape=date_etape,
            date_avis=parse_date_safe(request.POST.get('date_avis')),
            bct=request.POST.get('bct'),
            date_bct=parse_date_safe(request.POST.get('date_bct')),
            date_bordereau=parse_date_safe(request.POST.get('date_bordereau')),
            date_email=parse_date_safe(request.POST.get('date_email')),
            observation=request.POST.get('observation', ''),
            numero_bordereau=request.POST.get('numero_bordereau'),
            numero_avis=request.POST.get('numero_avis'),
            numero_ci=request.POST.get('numero_ci'),
            numero_facture=request.POST.get('numero_facture'),
            date_facture=parse_date_safe(request.POST.get('date_facture')),
            numero_bl=request.POST.get('numero_bl'),
            date_bl=parse_date_safe(request.POST.get('date_bl')),
            email_data={
                'corps': email_body,
                'date_import': timezone.now().isoformat(),
            }
        )

        # رفع المرفقات
        for f in request.FILES.getlist('email_attachments'):
            PieceJointeEtape.objects.create(
                etape=etape,
                fichier=f,
                nom_original=f.name,
                description="Pièce jointe de l'email"
            )

        return JsonResponse({'id': etape.id, 'status': 'created'})

    except Exception as e:
        print("Erreur création étape:", str(e))
        return JsonResponse({'error': 'Erreur serveur'}, status=500)
        
@csrf_exempt
@login_required
def suivi_etapes_update_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        etape_id = request.POST.get('id')  # ← تغيير هنا: من request.POST بدل json
        if not etape_id:
            return JsonResponse({'error': 'ID manquant'}, status=400)
        
        etape = SuiviDossier.objects.get(id=etape_id)
        
        # تحديث id_etape إذا تغيّر
        new_id_etape = request.POST.get('id_etape')
        if new_id_etape and new_id_etape != etape.id_etape:
            with connections['default'].cursor() as cursor:
                cursor.execute(
                    "SELECT libelle_etape, influence FROM etape_dossier WHERE code_etape = %s",
                    [new_id_etape]
                )
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'error': 'Étape non valide'}, status=400)
                etape.libelle_etape = row[0]
                etape.influence_sur_dossier = row[1]
                etape.id_etape = new_id_etape

        # تحديث الحقول الأخرى
        # تحويل date_etape (من datetime-local)
        date_etape_str = request.POST.get('date_etape')
        if date_etape_str:
            date_etape = datetime.fromisoformat(date_etape_str)
        else:
            date_etape = timezone.now()  # احتياطي

        # الحقول الجديدة
        etape.date_etape = date_etape
        etape.date_avis = parse_date_safe(request.POST.get('date_avis'))
        etape.bct = request.POST.get('bct')
        etape.date_bct = parse_date_safe(request.POST.get('date_bct'))
        etape.date_bordereau = parse_date_safe(request.POST.get('date_bordereau'))
        etape.date_email = parse_date_safe(request.POST.get('date_email'))
        
        etape.observation = request.POST.get('observation', '')
        etape.numero_bordereau = request.POST.get('numero_bordereau', '')
        etape.numero_avis = request.POST.get('numero_avis', '')
        etape.numero_ci = request.POST.get('numero_ci', '')
        etape.numero_facture = request.POST.get('numero_facture', '')
        etape.date_facture = parse_date_safe(request.POST.get('date_facture'))
        etape.numero_bl = request.POST.get('numero_bl', '')
        etape.date_bl = parse_date_safe(request.POST.get('date_bl'))

        # تحديث email_data إذا وُجد
        email_body = request.POST.get('email_body', '')
        if email_body:
            etape.email_data = {
                'corps': email_body,
                'date_import': timezone.now().isoformat(),
            }

        etape.save()

        # رفع المرفقات الجديدة (اختياري)
        for f in request.FILES.getlist('email_attachments'):
            PieceJointeEtape.objects.create(
                etape=etape,
                fichier=f,
                nom_original=f.name,
                description="Pièce jointe de l'email"
            )

        return JsonResponse({'status': 'updated'})

    except SuiviDossier.DoesNotExist:
        return JsonResponse({'error': 'Étape non trouvée'}, status=404)
    except Exception as e:
        logger.error(f"Erreur mise à jour étape: {e}")
        return JsonResponse({'error': 'Erreur serveur'}, status=500)
        
@csrf_exempt
@login_required
def suivi_etapes_delete_view(request):
    """POST: حذف مرحلة"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        etape_id = data.get('id')
        if not etape_id:
            return JsonResponse({'error': 'ID manquant'}, status=400)
        
        SuiviDossier.objects.filter(id=etape_id).delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        logger.error(f"Erreur suppression étape: {e}")
        return JsonResponse({'error': 'Erreur serveur'}, status=500)
        
# عرض تفاصيل مرحلة واحدة
@login_required
def etape_details_view(request):
    etape_id = request.GET.get('id')
    try:
        etape = SuiviDossier.objects.get(id=etape_id)
        return JsonResponse({
            'id': etape.id,
            'numero_com': etape.numero_com,
            'date_etape': etape.date_etape,
            'libelle_etape': etape.libelle_etape,
            'influence_sur_dossier': etape.influence_sur_dossier,
            'observation': etape.observation,
            'numero_bordereau': etape.numero_bordereau, 
            'numero_avis': etape.numero_avis, 
            'numero_facture': etape.numero_facture,
            'date_facture': etape.date_facture,
            'numero_bl': etape.numero_bl,
            'date_bl': etape.date_bl,
            'email_data': etape.email_data,
        })
    except SuiviDossier.DoesNotExist:
        return JsonResponse({'error': 'Étape non trouvée'}, status=404)

# رفع ملف
@csrf_exempt
@login_required
def upload_piece_jointe_view(request):
    if request.method == 'POST':
        etape_id = request.POST.get('etape_id')
        fichier = request.FILES.get('fichier')
        description = request.POST.get('description', '')
        try:
            etape = SuiviDossier.objects.get(id=etape_id)
            piece = PieceJointeEtape.objects.create(
                etape=etape,
                fichier=fichier,
                nom_original=fichier.name,
                description=description
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# قائمة الملفات المرفقة
@login_required
def liste_pieces_jointes_view(request):
    etape_id = request.GET.get('etape_id')
    pieces = PieceJointeEtape.objects.filter(etape_id=etape_id).values('id', 'fichier', 'nom_original', 'description')
    for p in pieces:
        p['url'] = f"{settings.MEDIA_URL}{p['fichier']}"  # ← settings مستورد
    return JsonResponse(list(pieces), safe=False)

#===============================================================================================
#==================B1 BonCommande===========================================================
#===============================================================================================

@login_required
def etat_b1_view(request):
    num_bc = request.GET.get('num_com')
    if not num_bc:
        return JsonResponse({'error': 'N° BC manquant'}, status=400)

    # جلب البيانات من الجدول المحلي فقط (بدون مزامنة)
    data = list(EtatB1View.objects.filter(doc_ref=num_bc).values())
    return JsonResponse(data, safe=False)

@login_required
def etat_b1_sync_view(request):
    num_bc = request.GET.get('num_com')
    if not num_bc:
        return JsonResponse({'error': 'N° BC manquant'}, status=400)
    sync_etat_b1_to_local(num_bc)  # الدالة التي كتبتها سابقًا
    return JsonResponse({'status': 'synced'})
    
def sync_etat_b1_to_local(num_bc):
    with connections['sql_server'].cursor() as cursor:
        cursor.execute("""
            SELECT  
                b1.doc_ref, 
                b1.date_ref, 
                L.ITEM, 
                A.COD_ART, 
                CAST(A.LIB_ART AS VARCHAR(MAX)) AS LIB_ART,
                L.QTE AS QTE_COMMANDE, 
                b1.nature_bon, 
                b1.date_b, 
                b1.numero_bon, 
                b1.qte_mvt AS QTE_RECEPT, 
                b1.lib_um,
                L.UNITE_MES AS lib_um_com,                
                b1.valeur_tot, 
                b1.class_cout, 
                A.EMPL, 
                (S.QTE_SURSTK - b1.qte_mvt) AS old_QTE, 
                S.VAL_ART, 
                b1_ebc.ref_doc AS num_facture
            FROM (((Etat_b1 AS b1 
                LEFT JOIN ARTICLE AS A ON b1.cod_art = A.COD_ART) 
                LEFT JOIN LIGNECOM AS L ON b1.cod_art = L.COD_ART AND b1.doc_ref = L.NUMERO_COM) 
                LEFT JOIN STOCK AS S ON b1.cod_art = S.COD_ART) 
                LEFT JOIN Bon_b1_ebc AS b1_ebc ON b1.numero_bon = b1_ebc.numero_bon
            WHERE b1.doc_ref = %s
            ORDER BY L.ITEM, b1.numero_bon
        """, [num_bc])

        columns = [col[0] for col in cursor.description]
        source_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

    with transaction.atomic():
        for row in source_data:
            EtatB1View.objects.update_or_create(
                date_b=row['date_b'],
                numero_bon=row['numero_bon'],
                defaults={
                    'doc_ref': row.get('doc_ref'),
                    'date_ref': row.get('date_ref'),
                    'item': row.get('ITEM'),
                    'cod_art': row.get('COD_ART'),
                    'lib_art': row.get('LIB_ART'),
                    'qte_commande': row.get('QTE_COMMANDE'),
                    'nature_bon': row.get('nature_bon'),
                    'qte_recept': row.get('QTE_RECEPT'),
                    'lib_um': row.get('lib_um'),
                    'lib_um_com': row.get('lib_um_com'),  # ← إضافة هذا السطر
                    'valeur_tot': row.get('valeur_tot'),
                    'class_cout': row.get('class_cout'),
                    'empl': row.get('EMPL'),
                    'old_qte': row.get('old_QTE'),
                    'val_art': row.get('VAL_ART'),
                    'num_facture': row.get('num_facture'),
                    # ملاحظة: لا نلمس numero_bp و taux_change هنا
                }
            )
        # 3. (اختياري) حذف السجلات المحلية غير الموجودة في المصدر
        # EtatB1View.objects.filter(doc_ref=num_bc).exclude(
        #     date_b__in=[r['date_b'] for r in source_data],
        #     numero_bon__in=[r['numero_bon'] for r in source_data]
        # ).delete()
        
@csrf_exempt
@login_required
def etat_b1_update(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        date_b = request.POST.get('date_b')
        numero_bon = request.POST.get('numero_bon')
        if not date_b or not numero_bon:
            return JsonResponse({'error': 'date_b ou numero_bon manquant'}, status=400)

        etape = EtatB1View.objects.get(date_b=date_b, numero_bon=numero_bon)
        
        # تحديث الحقول النصية
        etape.item = request.POST.get('item', etape.item)
        etape.lib_um_com = request.POST.get('lib_um_com', etape.lib_um_com)
        etape.lib_um = request.POST.get('lib_um', etape.lib_um)
        etape.numero_bp = request.POST.get('numero_bp', etape.numero_bp)
        
        # دالة مساعدة لتحويل القيمة إلى Decimal بأمان
        def safe_decimal(value):
            if value is None or value == '' or value.lower() == 'null':
                return None
            # إزالة المسافات الزائدة
            value = str(value).strip()
            # استبدال الفاصلة بال نقطة (إذا لزم)
            value = value.replace(',', '.')
            try:
                return Decimal(value)
            except (InvalidOperation, ValueError):
                return None

        # تحديث الحقول العددية
        etape.qte_commande = safe_decimal(request.POST.get('qte_commande'))
        etape.taux_change = safe_decimal(request.POST.get('taux_change'))
        
        etape.save()
        return JsonResponse({'status': 'updated'})

    except EtatB1View.DoesNotExist:
        return JsonResponse({'error': 'Enregistrement non trouvé'}, status=404)
    except Exception as e:
        print("Erreur dans etat_b1_update:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def etat_b1_delete(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        date_b = request.POST.get('date_b')
        numero_bon = request.POST.get('numero_bon')
        if not date_b or not numero_bon:
            return JsonResponse({'error': 'date_b ou numero_bon manquant'}, status=400)

        EtatB1View.objects.filter(date_b=date_b, numero_bon=numero_bon).delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)        
        
# جلب قائمة ITEMS
@login_required
def api_items_view(request):
    num_com = request.GET.get('num_com')
    if not num_com:
        return JsonResponse([], safe=False)
    with connections['sql_server'].cursor() as cursor:
        cursor.execute("SELECT DISTINCT ITEM FROM lignecom WHERE TYPE_ITEM = 'M' AND NUMERO_COM = %s", [num_com])
        items = [row[0] for row in cursor.fetchall()]
    return JsonResponse(items, safe=False)

# جلب تفاصيل ITEM (QTE و UNITE_MES)
@login_required
def api_item_details_view(request):
    num_com = request.GET.get('num_com')
    item = request.GET.get('item')
    if not num_com or not item:
        return JsonResponse({'qte': None, 'unite_mes': None})
    with connections['sql_server'].cursor() as cursor:
        cursor.execute("""
            SELECT QTE, UNITE_MES 
            FROM lignecom 
            WHERE NUMERO_COM = %s AND ITEM = %s
            LIMIT 1
        """, [num_com, item])
        row = cursor.fetchone()
        if row:
            return JsonResponse({'qte': float(row[0]) if row[0] else None, 'unite_mes': row[1] or ''})
        else:
            return JsonResponse({'qte': None, 'unite_mes': None})
            
# في views.py
@require_GET
@login_required
def api_item_qte_um(request):
    num_com = request.GET.get('num_com')
    item = request.GET.get('item')
    if not num_com or not item:
        return JsonResponse({'error': 'num_com et item requis'}, status=400)

    try:
        with connections['sql_server'].cursor() as cursor:
            # جلب التفاصيل من LIGNECOM
            cursor.execute("""
                SELECT TOP 1 COD_ART, LIB_ART, QTE, UNITE_MES
                FROM LIGNECOM
                WHERE NUMERO_COM = %s AND ITEM = %s
            """, [num_com, item])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'error': 'Article non trouvé'}, status=404)

            cod_art = row[0] or ''
            lib_art = row[1] or ''
            qte = str(row[2]) if row[2] is not None else None
            um_code = row[3] or ''

            # ⬇️ جلب الاسم من T_UNITES
            lib_um = um_code
            if um_code:
                cursor.execute("SELECT LIB_UM FROM T_UNITES WHERE UNITE_MES = %s", [um_code])
                um_row = cursor.fetchone()
                if um_row and um_row[0]:
                    lib_um = um_row[0]

            return JsonResponse({
                'cod_art': cod_art,
                'lib_art': lib_art,
                'qte': qte,
                'lib_um': lib_um,  # ← هذا الآن اسم حقيقي
            })
    except Exception as e:
        import logging
        logging.error("api_item_qte_um error: %s", str(e))
        return JsonResponse({'error': 'Erreur interne'}, status=500)
            
#===============================================================================================
#==================Comparaison B1 BonCommande===================================================
#===============================================================================================            

@login_required
def comparaison_commande_reception(request):
    num_com = request.GET.get('num_com')
    if not num_com:
        return JsonResponse({'error': 'N° BC manquant'}, status=400)

    # 1. جلب البيانات من SQL Server (المصدر الأصلي)
    source_data = {}
    with connections['sql_server'].cursor() as cursor:
        cursor.execute("""
            SELECT  
                L.ITEM, 
                A.COD_ART, 
                CAST(A.LIB_ART AS VARCHAR(MAX)) AS LIB_ART,
                L.QTE AS QTE_COMMANDE, 
                L.UNITE_MES AS lib_um_com
            FROM LIGNECOM AS L
            LEFT JOIN ARTICLE AS A ON L.COD_ART = A.COD_ART
            WHERE type_item = 'M' and L.NUMERO_COM = %s
            ORDER BY L.ITEM
        """, [num_com])
        for row in cursor.fetchall():
            item = row[0]
            if item:
                source_data[item] = {
                    'cod_art': row[1],
                    'lib_art': row[2],
                    'qte_commande': float(row[3]) if row[3] not in (None, '') else 0.0,
                    'lib_um_com': row[4] or '',
                }

    # 2. جلب البيانات من الجدول المحلي (EtatB1View) مع تجميع الكميات حسب ITEM
    local_aggregated = (
        EtatB1View.objects
        .filter(doc_ref=num_com)
        .filter(~Q(item='') & Q(item__isnull=False))  # فقط العناصر غير فارغة
        .values('item')
        .annotate(
            total_qte_recept=Sum('qte_recept'),
            total_qte_commande=Sum('qte_commande')
        )
        .values('item', 'total_qte_recept', 'total_qte_commande', 'lib_um_com', 'lib_um')
    )

    local_data = {}
    for rec in local_aggregated:
        item = rec['item']
        local_data[item] = {
            'qte_commande_locale': float(rec['total_qte_commande']) if rec['total_qte_commande'] not in (None, '') else 0.0,
            'qte_reception': float(rec['total_qte_recept']) if rec['total_qte_recept'] not in (None, '') else 0.0,
            'lib_um_com': rec.get('lib_um_com') or '',
            'lib_um': rec.get('lib_um') or '',
        }

    # 3. دمج البيانات (جميع العناصر من المصدر + المحلي)
    all_items = set(source_data.keys()) | set(local_data.keys())
    result = []

    for item in sorted(all_items, key=lambda x: (x.isdigit(), x)):  # فرز ذكي: رقمي ثم نصي
        src = source_data.get(item, {})
        loc = local_data.get(item, {})

        qte_src = src.get('qte_commande', 0.0)
        qte_loc = loc.get('qte_commande_locale', 0.0)
        qte_rec = loc.get('qte_reception', 0.0)
        ecart = qte_rec - qte_src

        # تحديد حالة الاستلام
        if qte_src == 0:
            statut = 'non_recu'  # لا يوجد طلب أصلاً
        elif qte_rec >= qte_src:
            statut = 'complet'
        elif qte_rec > 0:
            statut = 'partiel'
        else:
            statut = 'non_recu'

        result.append({
            'item': item,
            'cod_art': src.get('cod_art', '-'),
            'lib_art': src.get('lib_art', '-'),
            'qte_commande_source': qte_src,
            'qte_commande_locale': qte_loc,
            'qte_reception': qte_rec,
            'ecart': ecart,
            'lib_um_com': loc.get('lib_um_com', src.get('lib_um_com', '')),
            'lib_um': loc.get('lib_um', ''),
            'statut_reception': statut,
        })

    return JsonResponse(result, safe=False)
  
#===============================================================================================
#==================Avis arrivee BonCommande  عرض قائمة إشعارات الاستلام لطلبية معينة==============
#===============================================================================================  

@login_required
def avis_arrivee_list(request):
    num_com = request.GET.get('num_com')
    if not num_com:
        return JsonResponse({'error': 'N° Bon manquant'}, status=400)
    
    avis_list = AvisArrivee.objects.filter(numero_com=num_com).values(
        'id', 'numero_avis', 'date_avis', 'numero_bordereau', 'bct',
        'numero_facture', 'numero_bl', 'observation'
    )
    return JsonResponse(list(avis_list), safe=False)


# عرض تفاصيل إشعار استلام (السلع المستلمة)
@login_required
def avis_arrivee_details(request):
    avis_id = request.GET.get('id')
    if not avis_id:
        return JsonResponse({'error': 'ID manquant'}, status=400)
    
    details = DetailAvis.objects.filter(avis_id=avis_id).values(
         'id', 'item', 'cod_art', 'lib_art', 'qte_commande', 'qte_receptionnee',
        'um_commande', 'um_reception', 'conformite', 'observation'  # ← أضف هذه
    )
    return JsonResponse(list(details), safe=False)


# إنشاء إشعار استلام جديد
@csrf_exempt
@login_required
def avis_arrivee_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        numero_avis = request.POST.get('numero_avis')
        date_avis = request.POST.get('date_avis')
        numero_com = request.POST.get('numero_com')
        dat_com_str = request.POST.get('dat_com')

        # ✅ التحقق من وجود الحقول الأربعة المطلوبة
        if not all([numero_avis, date_avis, numero_com, dat_com_str]):
            return JsonResponse({
                'error': 'Tous les champs suivants sont obligatoires : N° Avis, Date Avis, N° Bon, Date Bon'
            }, status=400)

        # ✅ التحقق من صحة تاريخ الطلبية
        try:
            dat_com = datetime.strptime(dat_com_str.strip(), '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'error': 'Format de la date du bon invalide. Utilisez YYYY-MM-DD.'
            }, status=400)

        avis = AvisArrivee.objects.create(
            numero_com=numero_com,
            dat_com=dat_com,
            numero_avis=numero_avis,
            date_avis=date_avis,
            numero_bordereau=request.POST.get('numero_bordereau', ''),
            bct=request.POST.get('bct', ''),
            numero_facture=request.POST.get('numero_facture', ''),
            numero_bl=request.POST.get('numero_bl', ''),
            observation=request.POST.get('observation', ''),
        )
        return JsonResponse({'id': avis.id, 'status': 'created'})
    except Exception as e:
        print("Erreur dans avis_arrivee_create:", str(e))
        return JsonResponse({'error': str(e)}, status=500)


# تعديل إشعار استلام
@csrf_exempt
@login_required
def avis_arrivee_update(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        avis_id = request.POST.get('id')
        if not avis_id:
            return JsonResponse({'error': 'ID manquant'}, status=400)
        
        avis = AvisArrivee.objects.get(id=avis_id)
        avis.numero_avis = request.POST.get('numero_avis', avis.numero_avis)
        avis.date_avis = request.POST.get('date_avis', avis.date_avis)
        avis.numero_bordereau = request.POST.get('numero_bordereau', avis.numero_bordereau)
        avis.bct = request.POST.get('bct', avis.bct)
        avis.numero_facture = request.POST.get('numero_facture', avis.numero_facture)
        avis.numero_bl = request.POST.get('numero_bl', avis.numero_bl)
        avis.observation = request.POST.get('observation', avis.observation)
        avis.save()
        return JsonResponse({'status': 'updated'})
    except AvisArrivee.DoesNotExist:
        return JsonResponse({'error': 'Avis non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# حذف إشعار استلام
@csrf_exempt
@login_required
def avis_arrivee_delete(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        avis_id = request.POST.get('id')
        if not avis_id:
            return JsonResponse({'error': 'ID manquant'}, status=400)
        
        AvisArrivee.objects.filter(id=avis_id).delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# إنشاء تفاصيل إشعار استلام (سطر سلعة مستلمة)
@csrf_exempt
@login_required
def detail_avis_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        avis_id = request.POST.get('avis_id')
        if not avis_id:
            return JsonResponse({'error': 'ID avis manquant'}, status=400)
        
        detail = DetailAvis.objects.create(
            avis_id=avis_id,
            item=request.POST.get('item', ''),
            cod_art=request.POST.get('cod_art', ''),
            lib_art=request.POST.get('lib_art', ''),
            qte_commande=request.POST.get('qte_commande') or None,
            qte_receptionnee=request.POST.get('qte_receptionnee'),
            um_commande=request.POST.get('um_commande', ''),
            um_reception=request.POST.get('um_reception', ''),
            conformite=request.POST.get('conformite', 'conforme'),  # ← جديد
            observation=request.POST.get('observation', ''),        # ← جديد
        )
        return JsonResponse({'id': detail.id, 'status': 'created'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# تعديل تفاصيل إشعار استلام
@csrf_exempt
@login_required
def detail_avis_update(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        detail_id = request.POST.get('id')
        if not detail_id:
            return JsonResponse({'error': 'ID détail manquant'}, status=400)
        
        detail = DetailAvis.objects.get(id=detail_id)
        detail.item = request.POST.get('item', detail.item)
        detail.cod_art = request.POST.get('cod_art', detail.cod_art)
        detail.lib_art = request.POST.get('lib_art', detail.lib_art)
        detail.qte_commande = request.POST.get('qte_commande') or detail.qte_commande
        detail.qte_receptionnee = request.POST.get('qte_receptionnee', detail.qte_receptionnee)
        detail.um_commande = request.POST.get('um_commande', detail.um_commande)
        detail.um_reception = request.POST.get('um_reception', detail.um_reception)
        conformite=request.POST.get('conformite', 'conforme'),  # ← جديد
        detail.observation = request.POST.get('observation', detail.observation)
        detail.save()
        return JsonResponse({'status': 'updated'})
    except DetailAvis.DoesNotExist:
        return JsonResponse({'error': 'Détail non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# حذف تفاصيل إشعار استلام
@csrf_exempt
@login_required
def detail_avis_delete(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        detail_id = request.POST.get('id')
        if not detail_id:
            return JsonResponse({'error': 'ID détail manquant'}, status=400)
        
        DetailAvis.objects.filter(id=detail_id).delete()
        return JsonResponse({'status': 'deleted'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#===============================================================================================
#==================Avis DETAILS arrivee BonCommande  +++++++++++++++++++++++++++++==============
#===============================================================================================

@require_GET
@login_required
def api_ligne_commande_by_item(request):
    num_com = request.GET.get('num_com')
    item = request.GET.get('item')
    
    if not num_com or not item:
        return JsonResponse({'error': 'num_com et item sont requis'}, status=400)

    try:
        # استخدام قاعدة البيانات sqlserver
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 1 COD_ART, LIB_ART, QTE, UNITE_MES
                FROM LIGNECOM
                WHERE NUMERO_COM = %s AND ITEM = %s
            """, [num_com, item])
            row = cursor.fetchone()
            
            if row:
                return JsonResponse({
                    'cod_art': row[0] or '',
                    'lib_art': row[1] or '',
                    'qte_commande': str(row[2]) if row[2] is not None else None,
                    'um_commande': row[3] or '',
                })
            else:
                return JsonResponse({'error': 'Article non trouvé'}, status=404)
    except Exception as e:
        # سجّل الخطأ لمزيد من التفاصيل
        import logging
        logging.error("Erreur dans api_ligne_commande_by_item: %s", str(e))
        return JsonResponse({'error': 'Erreur interne'}, status=500)        

@require_GET
@login_required
def api_unite_libelle(request):
    um_code = request.GET.get('um_code')
    if not um_code:
        return JsonResponse({'error': 'um_code requis'}, status=400)

    try:
        # ✅ استخدام الاتصال الصحيح (sqlserver وليس الافتراضي)
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("SELECT LIB_UM FROM T_UNITES WHERE UM_CODE = %s", [um_code])
            row = cursor.fetchone()
            libelle = row[0] if row else um_code  # إذا لم يُوجد، أعد الرمز نفسه
        return JsonResponse({'libelle': libelle})
    except Exception as e:
        import logging
        logging.error("Erreur dans api_unite_libelle: %s", str(e))
        return JsonResponse({'error': 'Erreur interne'}, status=500)        
        

# 1. عرض صفحة مستقلة
@login_required
def avis_arrivee_list_view(request):
    query = request.GET.get('q', '').strip()
    numero_avis = request.GET.get('numero_avis', '').strip()
    date_avis_min = request.GET.get('date_avis_min')
    date_avis_max = request.GET.get('date_avis_max')
    numero_com = request.GET.get('numero_com', '').strip()

    avis_list = AvisArrivee.objects.select_related().order_by('-date_avis', 'numero_avis')

    if query:
        avis_list = avis_list.filter(
            Q(numero_avis__icontains=query) |
            Q(numero_com__icontains=query) |
            Q(numero_bordereau__icontains=query)
        )
    if numero_avis:
        avis_list = avis_list.filter(numero_avis__icontains=numero_avis)
    if numero_com:
        avis_list = avis_list.filter(numero_com__icontains=numero_com)
    if date_avis_min:
        avis_list = avis_list.filter(date_avis__gte=date_avis_min)
    if date_avis_max:
        avis_list = avis_list.filter(date_avis__lte=date_avis_max)

    paginator = Paginator(avis_list, 10)  # 10 إشعارات في الصفحة
    page_number = request.GET.get('page')
    avis_page = paginator.get_page(page_number)

    return render(request, 'core/avis_arrivee_list.html', {
        'avis_list': avis_page,
        'q': request.GET.get('q', ''),
        'numero_avis': numero_avis,
        'numero_com': numero_com,
        'date_avis_min': date_avis_min,
        'date_avis_max': date_avis_max,
    })
    
from django.utils.dateparse import parse_date

@login_required
def avis_arrivee_create_view(request):
    if request.method == 'POST':
        try:
            numero_com = request.POST.get('numero_com') or None
            dat_com_str = request.POST.get('dat_com')
            dat_com = parse_date(dat_com_str) if dat_com_str else None

            avis = AvisArrivee.objects.create(
                numero_com=numero_com,
                dat_com=dat_com,
                numero_avis=request.POST['numero_avis'],
                date_avis=parse_date(request.POST['date_avis']),
                numero_bordereau=request.POST.get('numero_bordereau') or None,
                bct=request.POST.get('bct') or None,
                numero_facture=request.POST.get('numero_facture') or None,
                numero_bl=request.POST.get('numero_bl') or None,
                observation=request.POST.get('observation') or None,
            )
            return redirect('core:avis_arrivee_detail_page', pk=avis.pk)
        except Exception as e:
            return render(request, 'core/avis_arrivee_form.html', {
                'error': str(e),
                'form_data': request.POST,
            })
    else:
        return render(request, 'core/avis_arrivee_form.html')
        
@login_required
def avis_arrivee_update_view(request, pk):
    avis = get_object_or_404(AvisArrivee, pk=pk)
    if request.method == 'POST':
        avis.numero_com = request.POST.get('numero_com') or None
        avis.dat_com = parse_date(request.POST.get('dat_com')) if request.POST.get('dat_com') else None
        avis.numero_avis = request.POST['numero_avis']
        avis.date_avis = parse_date(request.POST['date_avis'])
        avis.numero_bordereau = request.POST.get('numero_bordereau') or None
        avis.bct = request.POST.get('bct') or None
        avis.numero_facture = request.POST.get('numero_facture') or None
        avis.numero_bl = request.POST.get('numero_bl') or None
        avis.observation = request.POST.get('observation') or None
        avis.save()
        return redirect('core:avis_arrivee_detail_page', pk=avis.pk)
    return render(request, 'core/avis_arrivee_form.html', {'avis': avis})

@login_required
def avis_arrivee_delete_view(request, pk):
    if request.method == 'POST':
        avis = get_object_or_404(AvisArrivee, pk=pk)
        avis.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@login_required
def avis_arrivee_detail_view(request, pk):
    avis = get_object_or_404(AvisArrivee, pk=pk)
    details = avis.details.all()
    return render(request, 'core/avis_arrivee_detail.html', {
        'avis': avis,
        'details': details,
    })

@login_required
def upload_piece_jointe_avis(request, avis_id):
    if request.method == 'POST' and request.FILES.get('fichier'):
        avis = get_object_or_404(AvisArrivee, pk=avis_id)
        f = request.FILES['fichier']
        PieceJointeAvis.objects.create(
            avis=avis,
            fichier=f,
            nom_original=f.name,
            description=request.POST.get('description', '')
        )
        return redirect('core:avis_arrivee_detail_page', pk=avis_id)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@login_required
def delete_piece_jointe_avis(request, avis_id, piece_id):
    piece = get_object_or_404(PieceJointeAvis, pk=piece_id, avis_id=avis_id)
    piece.delete()
    return redirect('core:avis_arrivee_detail_page', pk=avis_id)

@login_required
def avis_arrivee_detail_view(request, pk):
    avis = get_object_or_404(AvisArrivee, pk=pk)
    details = avis.details.all()
    return render(request, 'core/avis_arrivee_detail.html', {
        'avis': avis,
        'details': details,
    })    
    
@login_required
def api_items(request):
    """
    إرجاع قائمة ITEM من LIGNECOM لطلبية معينة (لـ type_item = 'M' فقط)
    """
    num_com = request.GET.get('num_com')
    if not num_com:
        return JsonResponse({'error': 'N° BC manquant'}, status=400)

    items = []
    try:
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("""
                SELECT L.ITEM
                FROM LIGNECOM AS L
                WHERE L.NUMERO_COM = %s
                  AND L.type_item = 'M'
                  AND L.ITEM IS NOT NULL
                ORDER BY L.ITEM
            """, [num_com])
            items = [row[0] for row in cursor.fetchall() if row[0]]
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(items, safe=False)    

@login_required
def api_commandes(request):
    """
    API: جلب قائمة الأوامر مع دعم البحث (q)
    """
    q = request.GET.get('q', '').strip()
    try:
        with connections['sql_server'].cursor() as cursor:
            if q:
                cursor.execute("""
                    SELECT c.NUMERO_COM, c.DAT_COM, f.LIB_FOURN
                    FROM COMMANDE c
                    LEFT JOIN fourniss f ON c.CODE_FOURN = f.CODE_FOURN
                    WHERE c.NUMERO_COM IS NOT NULL
                      AND (c.NUMERO_COM LIKE %s OR f.LIB_FOURN LIKE %s)
                    ORDER BY c.DAT_COM DESC
                    OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY
                """, [f"%{q}%", f"%{q}%"])
            else:
                cursor.execute("""
                    SELECT c.NUMERO_COM, c.DAT_COM, f.LIB_FOURN
                    FROM COMMANDE c
                    LEFT JOIN fourniss f ON c.CODE_FOURN = f.CODE_FOURN
                    WHERE c.NUMERO_COM IS NOT NULL
                    ORDER BY c.DAT_COM DESC
                    OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY
                """)
            commandes = [
                {
                    'numero_com': row[0],
                    'dat_com': row[1].strftime('%Y-%m-%d') if row[1] else '',
                    'lib_fourn': row[2] or 'Inconnu'
                }
                for row in cursor.fetchall()
            ]
        return JsonResponse(commandes, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)    

#===============================================================================================
#================== Tache =========================  +++++++++++++++++++++++++++++==============
#===============================================================================================        

@login_required
def tache_list_view(request):
    query = request.GET.get('q', '').strip()
    etat = request.GET.get('etat', '')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    taches = Tache.objects.all().order_by('-date_prevue')

    if query:
        taches = taches.filter(
            Q(libelle__icontains=query) |
            Q(description__icontains=query) |
            Q(observation__icontains=query)
        )
    if etat:
        taches = taches.filter(etat=etat)
    if date_min:
        taches = taches.filter(date_prevue__gte=date_min)
    if date_max:
        taches = taches.filter(date_prevue__lte=date_max)

    paginator = Paginator(taches, 10)
    page_number = request.GET.get('page')
    taches_page = paginator.get_page(page_number)

    return render(request, 'core/tache_list.html', {
        'taches': taches_page,
        'q': query,
        'etat': etat,
        'date_min': date_min,
        'date_max': date_max,
        'etat_choices': Tache.ETAT_CHOICES,
    })
    
@login_required
def tache_create_view(request):
    if request.method == 'POST':
        try:
            tache = Tache.objects.create(
                libelle=request.POST['libelle'],
                description=request.POST.get('description', ''),
                date_prevue=request.POST['date_prevue'],
                observation=request.POST.get('observation', ''),
                delai_repetition=request.POST.get('delai_repetition') or 0,
                etat=request.POST.get('etat', 'a_faire'),
            )
            # حفظ المتدخلين
            for personnel_id in request.POST.getlist('intervenants'):
                if personnel_id:  # تأكد من أن القيمة ليست فارغة
                    Intervenant.objects.create(
                        tache=tache,
                        personnel_id=personnel_id,
                        role=request.POST.get(f'role_{personnel_id}', '')
                    )
            # حفظ المعدات
            for engin_lib in request.POST.getlist('engins'):
                if engin_lib.strip():
                    Engin.objects.create(tache=tache, libelle=engin_lib)

            # رفع المرفقات
            for f in request.FILES.getlist('pieces_jointes'):
                PieceJointeTache.objects.create(
                    tache=tache,
                    fichier=f,
                    nom_original=f.name,
                    description=request.POST.get('description_piece', '')
                )

            messages.success(request, "Tâche créée avec succès.")
            return redirect('core:tache_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    return render(request, 'core/tache_form.html', {
        'Tache': Tache,
        'personnels': Personnel.objects.all(),
        'plannings_referentiel': PlanningTache.objects.all(),
        'users': CustomUser.objects.all(),  # ← استخدام CustomUser
    })  

@login_required
def tache_update_view(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    if request.method == 'POST':
        try:
            tache.libelle = request.POST['libelle']
            tache.description = request.POST.get('description', '')
            tache.date_prevue = request.POST['date_prevue']
            tache.observation = request.POST.get('observation', '')
            tache.delai_repetition = request.POST.get('delai_repetition') or 0
            tache.etat = request.POST.get('etat', 'a_faire')
            tache.save()

            # تحديث المتدخلين
            tache.intervenants.all().delete()
            for personnel_id in request.POST.getlist('intervenants'):
                if personnel_id:  # تأكد من أن القيمة ليست فارغة
                    Intervenant.objects.create(
                        tache=tache,
                        personnel_id=personnel_id,
                        role=request.POST.get(f'role_{personnel_id}', '')
                    )

            # تحديث المعدات
            tache.engins.all().delete()
            for engin_lib in request.POST.getlist('engins'):
                if engin_lib.strip():
                    Engin.objects.create(tache=tache, libelle=engin_lib)

            # رفع مرفقات جديدة
            for f in request.FILES.getlist('pieces_jointes'):
                PieceJointeTache.objects.create(
                    tache=tache,
                    fichier=f,
                    nom_original=f.name,
                    description=request.POST.get('description_piece', '')
                )

            messages.success(request, "Tâche mise à jour.")
            return redirect('core:tache_list')
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    return render(request, 'core/tache_form.html', {
        'tache': tache,
        'personnels': Personnel.objects.all(),
        'plannings_referentiel': PlanningTache.objects.all(),
        'users': CustomUser.objects.all(),  # ← استخدام CustomUser
    })

@login_required
def tache_delete_view(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    if request.method == 'POST':
        tache.delete()
        messages.success(request, "Tâche supprimée.")
        return redirect('core:tache_list')
    return render(request, 'core/tache_confirm_delete.html', {'tache': tache})

@login_required
def tache_detail_view(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    return render(request, 'core/tache_detail.html', {'tache': tache})

@login_required
def planning_referentiel_list_view(request):
    plannings = PlanningTache.objects.all().order_by('-created_at')
    return render(request, 'core/planning_referentiel_list.html', {'plannings': plannings})

@login_required
def planning_referentiel_create_view(request):
    if request.method == 'POST':
        libelle = request.POST.get('libelle', '').strip()
        nature = request.POST.get('nature')
        delai = request.POST.get('delai_repetition') or 0
        observation = request.POST.get('observation', '')
        PlanningTache.objects.create(
            libelle=libelle,
            nature=nature,
            delai_repetition=delai,
            observation=observation
        )
        messages.success(request, "Planning référentiel créé.")
        return redirect('core:planning_referentiel_list')
    return render(request, 'core/planning_referentiel_form.html', {'title': 'Nouveau Planning Référentiel'})

@login_required
def planning_referentiel_update_view(request, pk):
    planning = get_object_or_404(PlanningTache, pk=pk)
    if request.method == 'POST':
        planning.libelle = request.POST.get('libelle', '').strip()
        planning.nature = request.POST.get('nature')
        planning.delai_repetition = request.POST.get('delai_repetition') or 0
        planning.observation = request.POST.get('observation', '')
        planning.save()
        messages.success(request, "Planning mis à jour.")
        return redirect('core:planning_referentiel_list')
    return render(request, 'core/planning_referentiel_form.html', {
        'planning': planning,
        'title': 'Modifier le Planning Référentiel'
    })

@login_required
def planning_referentiel_delete_view(request, pk):
    planning = get_object_or_404(PlanningTache, pk=pk)
    if request.method == 'POST':
        planning.delete()
        messages.success(request, "Planning supprimé.")
        return redirect('core:planning_referentiel_list')
    return render(request, 'core/planning_referentiel_confirm_delete.html', {'planning': planning})
# ===========================
# citerne
# ===========================

def citerne_list(request):
    citernes = Citerne.objects.all().order_by('code_citerne')
    return render(request, 'core/citerne_list.html', {'citernes': citernes})

def citerne_create(request):
    if request.method == 'POST':
        form = CiterneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Citerne créée avec succès.")
            return redirect('core:citerne_list')
    else:
        form = CiterneForm()
    return render(request, 'core/citerne_form.html', {'form': form, 'title': 'Créer une nouvelle Citerne'})

def citerne_update(request, pk):
    citerne = get_object_or_404(Citerne, pk=pk)
    if request.method == 'POST':
        form = CiterneForm(request.POST, instance=citerne)
        if form.is_valid():
            form.save()
            messages.success(request, "Citerne mise à jour avec succès.")
            return redirect('core:citerne_list')
    else:
        form = CiterneForm(instance=citerne)
    return render(request, 'core/citerne_form.html', {'form': form, 'title': 'Modifier la Citerne'})

def barremage_list_for_citerne(request, citerne_id):
    citerne = get_object_or_404(Citerne, pk=citerne_id)
    barremages = citerne.barremages.all().order_by('hauteur_cm')

    if request.method == 'POST':
        # إضافة نقطة جديدة
        hauteur = request.POST.get('hauteur_cm')
        volume = request.POST.get('volume_litres')
        if hauteur and volume:
            try:
                Barremage.objects.create(
                    citerne=citerne,
                    hauteur_cm=hauteur,
                    volume_litres=volume
                )
                messages.success(request, "Point de barremage ajouté avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur: {e}")
        return redirect('core:barremage_list_for_citerne', citerne_id=citerne_id)

    return render(request, 'core/barremage_list.html', {
        'citerne': citerne,
        'barremages': barremages
    })

# API للبحث عن السوائل (موجودة بالفعل، لكن يمكن تحسينها)
@login_required
def api_articles(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    sql = "SELECT COD_ART, LIB_ART FROM ARTICLE WHERE COD_ART LIKE %s OR LIB_ART LIKE %s"

    try:
        with connections['sql_server'].cursor() as cursor:
            search = f'%{query}%'
            cursor.execute(sql, [search, search])
            data = [
                {
                    'id': row[0],
                    'nom': row[1]
                }
                for row in cursor.fetchall()
            ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        print("❌ Erreur dans api_articles:", str(e))
        return JsonResponse([], safe=False)   

# === Engin ===
def engin_list(request):
    engins = Engin.objects.all().order_by('libelle')
    return render(request, 'core/engin_list.html', {'engins': engins})

def engin_create(request):
    if request.method == 'POST':
        form = EnginForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Engin ajouté avec succès.")
            return redirect('core:engin_list')
    else:
        form = EnginForm()
    return render(request, 'core/engin_form.html', {'form': form, 'title': 'Ajouter un engin'})

def engin_update(request, pk):
    engin = get_object_or_404(Engin, pk=pk)
    if request.method == 'POST':
        form = EnginForm(request.POST, instance=engin)
        if form.is_valid():
            form.save()
            messages.success(request, "Engin mis à jour.")
            return redirect('core:engin_list')
    else:
        form = EnginForm(instance=engin)
    return render(request, 'core/engin_form.html', {'form': form, 'title': 'Modifier l\'engin'})

def engin_delete(request, pk):
    engin = get_object_or_404(Engin, pk=pk)
    if request.method == 'POST':
        engin.delete()
        messages.success(request, "Engin supprimé avec succès.")
        return redirect('core:engin_list')
    return render(request, 'core/engin_confirm_delete.html', {'engin': engin})
    
# === Equipement (Statique) ===
def equipement_list(request):
    equipements = Equipement.objects.all().order_by('libelle')
    return render(request, 'core/equipement_list.html', {'equipements': equipements})

def equipement_create(request):
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement ajouté avec succès.")
            return redirect('core:equipement_list')
    else:
        form = EquipementForm()
    return render(request, 'core/equipement_form.html', {'form': form, 'title': 'Ajouter un équipement'})

def equipement_update(request, pk):
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, "Équipement mis à jour.")
            return redirect('core:equipement_list')
    else:
        form = EquipementForm(instance=equipement)
    return render(request, 'core/equipement_form.html', {'form': form, 'title': 'Modifier l\'équipement'})

def equipement_delete(request, pk):
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        equipement.delete()
        messages.success(request, "Équipement supprimé avec succès.")
        return redirect('core:equipement_list')
    return render(request, 'core/equipement_confirm_delete.html', {'equipement': equipement})
# === Lecture Index ===
def lecture_index_list(request):
    lectures = LectureIndex.objects.select_related('engin').all()
    return render(request, 'core/lecture_index_list.html', {'lectures': lectures})

def lecture_index_create(request):
    if request.method == 'POST':
        form = LectureIndexForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecture d'index enregistrée.")
            return redirect('core:lecture_index_list')
    else:
        form = LectureIndexForm()
    return render(request, 'core/lecture_index_form.html', {'form': form, 'title': 'Nouvelle lecture'})

# === Consommation ===
def consommation_list(request):
    consommations = ConsommationCarburant.objects.select_related('engin').all()
    return render(request, 'core/consommation_list.html', {'consommations': consommations})

def consommation_create(request):
    if request.method == 'POST':
        form = ConsommationCarburantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ravitaillement enregistré.")
            return redirect('core:consommation_list')
    else:
        form = ConsommationCarburantForm()
    return render(request, 'core/consommation_form.html', {'form': form, 'title': 'Nouveau ravitaillement'})        

# === Lecture Jauge ===
def lecture_jauge_list(request):
    lectures = LectureJauge.objects.select_related('citerne').all()
    return render(request, 'core/lecture_jauge_list.html', {'lectures': lectures})

def lecture_jauge_create(request):
    if request.method == 'POST':
        form = LectureJaugeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecture de jauge enregistrée.")
            return redirect('core:lecture_jauge_list')
    else:
        form = LectureJaugeForm()  # 👈 هنا يتم إنشاء نموذج فارغ
    return render(request, 'core/lecture_jauge_form.html', {
        'form': form,
        'title': 'Nouvelle lecture de jauge'
    })
    
# === Lecture Pompe ===
def lecture_pompe_list(request):
    lectures = LecturePompe.objects.select_related('pompe').all()
    return render(request, 'core/lecture_pompe_list.html', {'lectures': lectures})

def lecture_pompe_create(request):
    if request.method == 'POST':
        form = LecturePompeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecture de pompe enregistrée.")
            return redirect('core:lecture_pompe_list')
    else:
        form = LecturePompeForm()
    return render(request, 'core/lecture_pompe_form.html', {'form': form, 'title': 'Nouvelle lecture de pompe'})    

def lectures_consommations_view(request):
    # معالجة الطلبات POST من أي نموذج
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'jauge':
            form = LectureJaugeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Lecture de jauge enregistrée.")
                return redirect('core:lectures_consommations')
        elif form_type == 'pompe':
            form = LecturePompeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Lecture de pompe enregistrée.")
                return redirect('core:lectures_consommations')
        elif form_type == 'index':
            form = LectureIndexForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Lecture d'index enregistrée.")
                return redirect('core:lectures_consommations')
        elif form_type == 'consommation':
            form = ConsommationCarburantForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Consommation enregistrée.")
                return redirect('core:lectures_consommations')
    
    # جلب جميع البيانات للعرض
    lectures_jauge = LectureJauge.objects.select_related('citerne').all().order_by('-date_lecture')
    lectures_pompe = LecturePompe.objects.select_related('pompe').all().order_by('-date_lecture')
    lectures_index = LectureIndex.objects.select_related('engin').all().order_by('-date_lecture')
    consommations = ConsommationCarburant.objects.select_related('engin').all().order_by('-date_ravitaillement')

    # إنشاء نماذج فارغة
    jauge_form = LectureJaugeForm()
    pompe_form = LecturePompeForm()
    index_form = LectureIndexForm()
    consommation_form = ConsommationCarburantForm()

    context = {
        'jauge_form': jauge_form,
        'pompe_form': pompe_form,
        'index_form': index_form,
        'consommation_form': consommation_form,
        'lectures_jauge': lectures_jauge,
        'lectures_pompe': lectures_pompe,
        'lectures_index': lectures_index,
        'consommations': consommations,
    }
    return render(request, 'core/lectures_consommations.html', context)    
    
# ===========================
# citerne
# ===========================

@login_required
def get_notifications(request):
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:10]
    data = [{
        'id': n.id,
        'message': n.message,
        'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
        'type': n.get_type_display(),
        'is_read': n.is_read
    } for n in notifications]
    return JsonResponse({'notifications': data, 'count': notifications.count()})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})    