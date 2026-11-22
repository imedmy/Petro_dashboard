# apps/articles/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connections
from django.db.models import Q, Sum
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.utils.dateparse import parse_date
import json
import os
import re
import traceback
from datetime import date, timedelta, datetime
from decimal import Decimal, InvalidOperation
import io
import logging
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from django.utils import timezone
import sys
from django.views.decorators.http import require_http_methods, require_GET

from core.models import (
    ArticleFamily, Caracteristique, ArticleCaracteristique, ArticleImage,
    NatureStock, ValeurArticle, TypeMouvement, ArticleCorrelation, NatureBon
)
from core.models_sql import ArticleSQL
from core.forms import ArticleFamilyForm, CaracteristiqueForm, NatureStockForm, ValeurArticleForm
from .services import (
    create_analysis_workflow,
    get_or_start_analysis,
    cleanup_expired_workflows
)
from core.models import ArticleAnalysisWorkflow

logger = logging.getLogger(__name__)

# =============================================================================
# ✅ دالة مساعدة: بناء شرط LIKE حسب المشغل
# =============================================================================
def build_like_simple(value, operator):
    """بناء شرط LIKE بسيط - يزيل الأحرف الخاصة أولاً"""
    if not value:
        return None
    clean_value = value.replace('%', '').replace('_', '').replace('[', '').replace(']', '')
    if operator == 'starts':
        return clean_value + '%'
    elif operator == 'ends':
        return '%' + clean_value
    elif operator == 'exact':
        return clean_value
    else:  # contains
        return '%' + clean_value + '%'

# =============================================================================
# ✅ القسم 1: عرض السلع (النسخة التقليدية مع Pagination)
# =============================================================================
@login_required
def articles_view(request):
    """عرض قائمة السلع من SQL Server مع فلاتر متعددة"""
    cod_art = request.GET.get('cod_art', '').strip()
    lib_art = request.GET.get('lib_art', '').strip()
    class_cout = request.GET.get('class_cout', '').strip()
    lib_um = request.GET.get('lib_um', '').strip()
    empl = request.GET.get('empl', '').strip()
    qte_min = request.GET.get('qte_min', '').strip()
    qte_max = request.GET.get('qte_max', '').strip()
    pu_min = request.GET.get('pu_min', '').strip()
    pu_max = request.GET.get('pu_max', '').strip()
    val_art = request.GET.get('val_art', '').strip()

    sql = """
    SELECT
        a.COD_ART, a.LIB_ART, a.CLASS_COUT, a.DATE_CREAT, a.DERNIER_MV,
        a.EMPL, s.PUMP, u.LIB_UM, s.QTE_STOCK, s.QTE_SURSTK, s.VAL_ART,
        s.QTE_SURSTK * s.PUMP / 1000 AS VALEUR, a.DESIGNAT
    FROM ARTICLE a
    INNER JOIN STOCK s ON a.COD_ART = s.COD_ART
    INNER JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
    WHERE 1 = 1
    """
    conditions = []
    values = []

    if cod_art:
        for part in re.split(r'\s+', cod_art):
            if part:
                conditions.append("a.COD_ART LIKE %s")
                values.append(f'%{part}%')
    if lib_art:
        for kw in re.split(r'\s+', lib_art.strip()):
            if kw:
                conditions.append("a.LIB_ART LIKE %s")
                values.append(f'%{kw}%')
    if class_cout:
        conditions.append("a.CLASS_COUT = %s")
        values.append(class_cout)
    if lib_um:
        conditions.append("u.LIB_UM = %s")
        values.append(lib_um)
    if empl:
        conditions.append("a.EMPL LIKE %s")
        values.append(f'%{empl}%')
    if qte_min and qte_min.replace('.', '', 1).isdigit():
        conditions.append("s.QTE_SURSTK >= %s")
        values.append(qte_min)
    if qte_max and qte_max.replace('.', '', 1).isdigit():
        conditions.append("s.QTE_SURSTK <= %s")
        values.append(qte_max)
    if pu_min and pu_min.replace('.', '', 1).isdigit():
        conditions.append("s.PUMP >= %s")
        values.append(str(float(pu_min) * 1000))
    if pu_max and pu_max.replace('.', '', 1).isdigit():
        conditions.append("s.PUMP <= %s")
        values.append(str(float(pu_max) * 1000))
    if val_art in ['1', '2', '3', '4']:
        conditions.append("s.VAL_ART = %s")
        values.append(val_art)

    if conditions:
        sql += " AND " + " AND ".join(conditions)
    sql += " ORDER BY a.CLASS_COUT, a.COD_ART"

    rows = []
    try:
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql, values)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                data['PU'] = round(data['PUMP'] / 1000, 3) if data['PUMP'] else 0
                rows.append(data)
    except Exception as e:
        logger.error(f"Erreur articles_view: {e}")

    paginator = Paginator(rows, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'articles/articles.html', {
        'page_obj': page_obj,
        'cod_art': cod_art,
        'lib_art': lib_art,
        'class_cout': class_cout,
        'lib_um': lib_um,
        'empl': empl,
        'qte_min': qte_min,
        'qte_max': qte_max,
        'pu_min': pu_min,
        'pu_max': pu_max,
        'val_art': val_art,
    })

# =============================================================================
# ✅ القسم 2: DataTables Server-Side API (نسخة نهائية - معاملات %s)
# =============================================================================
@login_required
def api_articles_data(request):
    """
    API لـ DataTables Server-Side Processing
    نسخة نهائية: مؤشر واحد لكل الاستعلامات + معاملات %s آمنة
    """
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 20))
        
        cod_art = request.GET.get('cod_art', '').strip()
        lib_art = request.GET.get('lib_art', '').strip()
        class_cout = request.GET.get('class_cout', '').strip()
        lib_um = request.GET.get('lib_um', '').strip()
        empl = request.GET.get('empl', '').strip()
        qte_min = request.GET.get('qte_min', '').strip()
        qte_max = request.GET.get('qte_max', '').strip()
        pu_min = request.GET.get('pu_min', '').strip()
        pu_max = request.GET.get('pu_max', '').strip()
        val_art = request.GET.get('val_art', '').strip()
        nat_stock = request.GET.get('nat_stock', '').strip()
        
        search_value = request.GET.get('search[value]', '').strip()
        order_column_index = request.GET.get('order[0][column]', '0')
        order_dir = request.GET.get('order[0][dir]', 'asc')
        
        def clean_like(value, prefix=True, suffix=True):
            if not value:
                return None
            clean = value.replace('%', '').replace('_', '').replace('[', '').replace(']', '')
            result = ''
            if prefix: result += '%'
            result += clean
            if suffix: result += '%'
            return result
        
        conditions = []
        values = []
        
        if cod_art:
            like_val = clean_like(cod_art)
            if like_val:
                conditions.append("a.COD_ART LIKE %s")
                values.append(like_val)
        
        if lib_art:
            for kw in re.split(r'\s+', lib_art.strip()):
                if kw:
                    like_val = clean_like(kw)
                    if like_val:
                        conditions.append("a.LIB_ART LIKE %s")
                        values.append(like_val)
        
        if class_cout:
            conditions.append("a.CLASS_COUT = %s")
            values.append(class_cout)
        if lib_um:
            conditions.append("u.LIB_UM = %s")
            values.append(lib_um)
        if empl:
            conditions.append("a.EMPL LIKE %s")
            values.append(clean_like(empl))
        
        for field, sql_field, multiplier in [
            ('qte_min', 's.QTE_SURSTK >= %s', 1),
            ('qte_max', 's.QTE_SURSTK <= %s', 1),
            ('pu_min', 's.PUMP >= %s', 1000),
            ('pu_max', 's.PUMP <= %s', 1000),
        ]:
            val = request.GET.get(field, '').strip()
            if val:
                try:
                    conditions.append(sql_field)
                    values.append(float(val) * multiplier)
                except (ValueError, TypeError):
                    pass
        
        if val_art in ['1', '2', '3', '4']:
            conditions.append("s.VAL_ART = %s")
            values.append(val_art)
        if nat_stock:
            conditions.append("s.NAT_STOCK = %s")
            values.append(nat_stock)
        
        if search_value:
            clean = clean_like(search_value)
            conditions.append("(a.COD_ART LIKE %s OR a.LIB_ART LIKE %s)")
            values.extend([clean, clean])
        
        where_sql = " AND ".join(conditions) if conditions else "1 = 1"
        
        with connections['sql_server'].cursor() as cursor:
            count_sql = "SELECT COUNT(*) FROM ARTICLE a INNER JOIN STOCK s ON a.COD_ART = s.COD_ART"
            cursor.execute(count_sql)
            total_records = cursor.fetchone()[0]
            
            if conditions:
                count_filtered_sql = f"""
                SELECT COUNT(*) FROM ARTICLE a 
                INNER JOIN STOCK s ON a.COD_ART = s.COD_ART 
                INNER JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
                WHERE {where_sql}
                """
                cursor.execute(count_filtered_sql, values)
                filtered_records = cursor.fetchone()[0]
            else:
                filtered_records = total_records
            
            columns = ['a.COD_ART', 'a.LIB_ART', 'a.CLASS_COUT', 'a.DATE_CREAT', 
                       'a.DERNIER_MV', 'a.EMPL', 's.PUMP', 's.QTE_SURSTK', 
                       'u.LIB_UM', 's.VAL_ART', 's.NAT_STOCK', 'a.DESIGNAT']
            try:
                col_idx = int(order_column_index) if order_column_index.isdigit() else 0
                order_col = columns[col_idx] if 0 <= col_idx < len(columns) else 'a.COD_ART'
            except:
                order_col = 'a.COD_ART'
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            
            sql = f"""
            SELECT
                a.COD_ART, a.LIB_ART, a.CLASS_COUT, a.DATE_CREAT, a.DERNIER_MV,
                a.EMPL, s.PUMP, u.LIB_UM, s.QTE_STOCK, s.QTE_SURSTK, s.VAL_ART, s.NAT_STOCK,
                s.QTE_SURSTK * s.PUMP / 1000 AS VALEUR, a.DESIGNAT
            FROM ARTICLE a
            INNER JOIN STOCK s ON a.COD_ART = s.COD_ART
            INNER JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
            WHERE {where_sql}
            ORDER BY {order_col} {order_dir_sql}
            OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
            """
            
            final_values = values + [start, length]
            cursor.execute(sql, final_values)
            columns_desc = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            data = []
            for row in rows:
                item = dict(zip(columns_desc, row))
                item['PU'] = round(item['PUMP'] / 1000, 3) if item['PUMP'] else 0
                data.append(item)
            
            # ✅ إثراء البيانات بـ libelle_nature من جدول nature_stock (MySQL)
            nat_codes = list(set(item.get('NAT_STOCK') for item in data if item.get('NAT_STOCK')))
            nature_labels = {}
            if nat_codes:
                try:
                    nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                    nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
                except Exception as e:
                    logger.warning(f"Erreur chargement nature_stock depuis MySQL: {e}")
            
            for item in data:
                nat_code = item.get('NAT_STOCK')
                item['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        })
    
    except Exception as e:
        logger.error(f"CRITICAL ERROR api_articles_data: {str(e)}")
        return JsonResponse({
            'draw': 1,
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
            'error': str(e)
        }, status=500)

# =============================================================================
# ✅ القسم 3: إدارة الخصائص التقنية
# =============================================================================
@login_required
def gestion_caracteristiques(request):
    """إدارة الخصائص التقنية مع شجرة هرمية"""
    query = request.GET.get('q', '')
    all_caracts = Caracteristique.objects.all().select_related('parent')
    
    if query:
        all_caracts = all_caracts.filter(nom__icontains=query)
    
    tree_map = {c.id: {'node': c, 'children': []} for c in all_caracts}
    roots = []
    for c in all_caracts:
        if c.parent and c.parent.id in tree_map:
            tree_map[c.parent.id]['children'].append(tree_map[c.id])
        elif not c.parent:
            roots.append(tree_map[c.id])
    
    form = None
    edit_id = request.GET.get('edit')
    
    if edit_id:
        instance = get_object_or_404(Caracteristique, id=edit_id)
        if request.method == 'POST':
            form = CaracteristiqueForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                messages.success(request, f"Caractéristique '{form.instance.nom}' mise à jour.")
                return redirect('articles:gestion_caracteristiques')
        else:
            form = CaracteristiqueForm(instance=instance)
    else:
        if request.method == 'POST':
            form = CaracteristiqueForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Caractéristique '{form.instance.nom}' ajoutée.")
                return redirect('articles:gestion_caracteristiques')
        else:
            form = CaracteristiqueForm()
    
    if request.method == 'POST' and 'delete_id' in request.POST:
        delete_id = request.POST.get('delete_id')
        carac = get_object_or_404(Caracteristique, id=delete_id)
        carac.delete()
        messages.success(request, f"Caractéristique '{carac.nom}' supprimée.")
        return redirect('articles:gestion_caracteristiques')
    
    return render(request, 'articles/caracteristiques.html', {
        'roots': roots, 'form': form, 'query': query,
    })

# =============================================================================
# ✅ القسم 4: إدارة عائلات الترميز
# =============================================================================
@login_required
def famille_codification_view(request):
    """إدارة عائلات الترميز مع شجرة هرمية"""
    query = request.GET.get('q', '')
    families = ArticleFamily.objects.select_related('parent').all()
    
    if query:
        families = families.filter(Q(name__icontains=query) | Q(full_code__icontains=query))
    
    tree = {}
    roots = []
    for family in families:
        tree[family.id] = {'family': family, 'children': []}
    
    for family in families:
        if family.parent and family.parent.id in tree:
            tree[family.parent.id]['children'].append(tree[family.id])
        elif not family.parent:
            roots.append(tree[family.id])
    
    form = None
    edit_id = request.GET.get('edit')
    
    if edit_id:
        family_obj = get_object_or_404(ArticleFamily, id=edit_id)
        if request.method == 'POST':
            form = ArticleFamilyForm(request.POST, instance=family_obj)
            if form.is_valid():
                form.save()
                messages.success(request, f"Famille '{form.instance.name}' mise à jour.")
                return redirect('articles:famille_codification')
        else:
            form = ArticleFamilyForm(instance=family_obj)
    else:
        if request.method == 'POST':
            form = ArticleFamilyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Famille '{form.instance.name}' ajoutée.")
                return redirect('articles:famille_codification')
        else:
            form = ArticleFamilyForm()
    
    if request.method == 'POST' and 'delete_id' in request.POST:
        delete_id = request.POST.get('delete_id')
        family = get_object_or_404(ArticleFamily, id=delete_id)
        family.delete()
        messages.success(request, f"Famille '{family.name}' supprimée.")
        return redirect('articles:famille_codification')
    
    return render(request, 'articles/famille_codification.html', {
        'families': families, 'roots': roots, 'form': form, 'query': query,
    })

# =============================================================================
# ✅ القسم 5: APIs البحث
# =============================================================================
@login_required
def api_articles(request):
    """API للبحث عن السلع"""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
    
    sql = "SELECT COD_ART, LIB_ART FROM ARTICLE WHERE COD_ART LIKE %s OR LIB_ART LIKE %s"
    try:
        with connections['sql_server'].cursor() as cursor:
            search = f'%{query}%'
            cursor.execute(sql, [search, search])
            data = [{'id': row[0], 'nom': row[1]} for row in cursor.fetchall()]
            return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Erreur dans api_articles: {e}")
        return JsonResponse([], safe=False)

@login_required
def api_caracteristiques(request):
    """API للخصائص التقنية"""
    query = request.GET.get('q', '').strip()
    qs = Caracteristique.objects.all()
    if query:
        qs = qs.filter(nom__icontains=query)
    data = [{'id': c.id, 'nom': c.nom, 'parent': c.parent.id if c.parent else None} for c in qs]
    return JsonResponse(data, safe=False)

@login_required
def api_article_families(request):
    """API لعائلات الترميز"""
    query = request.GET.get('q', '').strip()
    all_families = ArticleFamily.objects.select_related('parent').all()
    if query:
        all_families = all_families.filter(Q(name__icontains=query) | Q(full_code__icontains=query))
    data = []
    for family in all_families.order_by('full_code')[:200]:
        data.append({
            'id': family.id, 'name': family.name, 'code_segment': family.code_segment,
            'full_code': family.full_code,
            'parent': {'id': family.parent.id} if family.parent else None
        })
    return JsonResponse(data, safe=False)

# =============================================================================
# ✅ القسم 6: الإحصائيات والبحث بالخصائص
# =============================================================================
@login_required
def statistiques_view(request):
    """عرض الإحصائيات"""
    cod_art = request.GET.get('cod_art', '').strip()
    nat_stock = request.GET.get('nat_stock', '').strip()
    val_art = request.GET.get('val_art', '').strip()
    date_min = request.GET.get('date_min', '')
    date_max = request.GET.get('date_max', '')
    
    context = {
        'cod_art': cod_art, 'nat_stock': nat_stock, 'val_art': val_art,
        'date_min': date_min, 'date_max': date_max,
    }
    return render(request, 'articles/statistiques.html', context)

@login_required
def recherche_par_caracteristiques(request):
    """البحث عن السلع باستخدام الخصائص"""
    return render(request, 'articles/recherche.html')

# =============================================================================
# ✅ القسم 7: التحليل الإحصائي للمقالات المرتبطة
# =============================================================================
@login_required
def api_article_related_stats(request, cod_art):
    """
    API: تحليل المقالات المرتبطة باستخدام جدول ArticleCorrelation فقط
    """
    try:
        if not cod_art:
            return JsonResponse({'error': 'COD_ART requis'}, status=400)
            
        from django.utils import timezone
        from datetime import timedelta
        from core.models import ArticleCorrelation
        
        last_week = timezone.now().date() - timedelta(days=7)
        cached_correlations = ArticleCorrelation.objects.filter(
            cod_art_ref=cod_art,
            last_movement_date__gte=last_week,
            is_active=True
        ).order_by('-support_percent')[:20]
        
        if cached_correlations.exists():
            related_articles = []
            for corr in cached_correlations:
                lib_art = _get_article_lib(corr.cod_art_related)
                related_articles.append({
                    'cod_art': corr.cod_art_related,
                    'lib_art': lib_art,
                    'co_occurrence': corr.support_count,
                    'co_occurrence_rate': float(corr.support_percent) if corr.support_percent else 0.0,
                    'confidence_level': corr.confidence_level or 'low',
                    'avg_time_gap_hours': float(corr.avg_time_gap_hours) if corr.avg_time_gap_hours else 0.0,
                    'sequence_order': corr.sequence_order or 'mixed',
                    'last_updated': corr.last_updated.isoformat() if corr.last_updated else None,
                })
            
            return JsonResponse({
                'status': 'cached',
                'cod_art': cod_art,
                'total_movements': sum(c.support_count for c in cached_correlations),
                'analysis_window_days': 7,
                'related_articles': related_articles,
                'is_incremental': True,
                'source': 'article_correlation_table',
                'last_update': cached_correlations.first().last_updated.isoformat() if cached_correlations.first() and cached_correlations.first().last_updated else None
            })
        
        return JsonResponse({
            'status': 'no_data',
            'cod_art': cod_art,
            'message': 'Aucune corrélation trouvée. Les données seront disponibles après la prochaine mise à jour incrémentale.',
            'related_articles': [],
            'source': 'article_correlation_table'
        })
        
    except ImportError:
        logger.warning("Table ArticleCorrelation non disponible")
        return JsonResponse({
            'status': 'no_data', 'cod_art': cod_art,
            'message': 'Le système de corrélation est en cours de déploiement.', 'related_articles': []
        })
    except Exception as e:
        logger.error(f"Erreur dans api_article_related_stats: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e), 'status': 'error', 'cod_art': cod_art}, status=500)

def _get_article_lib(cod_art):
    """دالة مساعدة لجلب اسم المقال من SQL Server"""
    try:
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("SELECT LIB_ART FROM ARTICLE WHERE COD_ART = %s", [cod_art])
            row = cursor.fetchone()
            return row[0] if row else 'Inconnu'
    except Exception as e:
        logger.warning(f"Erreur _get_article_lib: {e}")
        return 'Inconnu'

@login_required
def api_analysis_progress(request, workflow_id):
    result = get_or_start_analysis(workflow_id)
    return JsonResponse(result)

@login_required
def api_cleanup_workflows(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    count = cleanup_expired_workflows()
    return JsonResponse({'status': 'ok', 'cleaned_count': count})    

# =============================================================================
# ✅ القسم 8: الذكاء الاصطناعي
# =============================================================================
@login_required
@csrf_exempt
def api_article_ai_advice(request, cod_art):
    """API: تحليل المقال بالذكاء الاصطناعي"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # جلب معلومات المقال
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("""
                SELECT COD_ART, LIB_ART, CLASS_COUT, EMPL, DESIGNAT 
                FROM ARTICLE 
                WHERE COD_ART = %s
            """, [cod_art])
            row = cursor.fetchone()
            
            if not row:
                return JsonResponse({'error': 'Article non trouvé555'}, status=404)
            
            article_data = {
                'cod_art': row[0],
                'lib_art': row[1] or '',
                'class_cout': row[2] or '',
                'empl': row[3] or '',
                'designat': row[4] or ''
            }
        
        # جلب الخصائص التقنية
        caracteristiques = []
        try:
            carac_qs = ArticleCaracteristique.objects.filter(cod_art=cod_art).select_related('caracteristique')
            for ac in carac_qs:
                caracteristiques.append({
                    'nom': ac.caracteristique.nom,
                    'valeur': ac.valeur,
                    'unite': ac.caracteristique.unite
                })
        except Exception as e:
            logger.warning(f"Erreur chargement caractéristiques: {e}")
        
        # جلب معلومات العائلة
        family_data = None
        try:
            family_code = cod_art[:3] if len(cod_art) >= 3 else ''
            if family_code:
                family = ArticleFamily.objects.get(full_code=family_code)
                family_data = {'name': family.name, 'full_code': family.full_code}
        except ArticleFamily.DoesNotExist:
            pass
        
        # ✅ توليد النصائح (بدون API خارجي - نصائح مدمجة)
        usage_tips_fr = []
        recommended_accessories = []
        safety_notes = []
        
        # نصائح الاستخدام
        if article_data['class_cout']:
            usage_tips_fr.append(f"Article de classe {article_data['class_cout']} - Manipuler avec précaution")
        if article_data['empl']:
            usage_tips_fr.append(f"Stocké en emplacement {article_data['empl']}")
        
        # ملاحظات السلامة
        safety_notes.append("Porter les EPI appropriés lors de la manipulation")
        safety_notes.append("Vérifier l'état de l'article avant utilisation")
        
        return JsonResponse({
            'usage_tips_fr': usage_tips_fr,
            'usage_tips_ar': [],
            'recommended_accessories': recommended_accessories,
            'safety_notes': safety_notes
        })
    
    except Exception as e:
        logger.error(f"Erreur critique AI Advice: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erreur interne lors de l\'analyse IA'}, status=500)

# =============================================================================
# ✅ القسم 9: APIs مساعدة
# =============================================================================
@login_required
def api_nature_stock(request):
    natures = NatureStock.objects.all().order_by('code_nature')
    data = [{'code_nature': n.code_nature, 'libelle_nature': n.libelle_nature} for n in natures]
    return JsonResponse(data, safe=False)

@login_required
def api_article_basic_info(request, cod_art):
    try:
        logger.info(f"Recherche article: {cod_art}")
        
        with connections['sql_server'].cursor() as cursor:
            # التحقق من وجود المادة
            cursor.execute("""
                SELECT COD_ART, LIB_ART, CLASS_COUT, EMPL, DESIGNAT 
                FROM ARTICLE 
                WHERE COD_ART = %s
            """, [cod_art])
            
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Article non trouvé: {cod_art}")
                return JsonResponse({
                    'error': 'Article non trouvé',
                    'cod_art_recherche': cod_art
                }, status=404)
            
            logger.info(f"Article trouvé: {row[0]} - {row[1]}")
            
            return JsonResponse({
                'cod_art': row[0], 
                'lib_art': row[1] or '', 
                'class_cout': row[2] or '', 
                'empl': row[3] or '', 
                'designat': row[4] or ''
            })
            
    except Exception as e:
        logger.error(f"Erreur dans api_article_basic_info: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

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
            node = {'id': fam.id, 'name': fam.name, 'code_segment': fam.code_segment, 'full_code': fam.full_code, 'children': []}
            for child in fam.children.all():
                node['children'].append(build_tree(child))
            return node
        tree = build_tree(family)
        return JsonResponse({'family': tree})
    except ArticleSQL.DoesNotExist:
        return JsonResponse({'family': None, 'error': 'Article non trouvé333'}, status=200)
    except ArticleFamily.DoesNotExist:
        return JsonResponse({'family': None, 'error': 'Famille non trouvée'}, status=200)
    except Exception as e:
        return JsonResponse({'family': None, 'error': 'Erreur interne', 'details': str(e)}, status=500)

@login_required
def article_caracteristiques_with_cod(request, cod_art=None):
    selected_cod_art = cod_art or request.GET.get('cod_art')
    libelle = ""
    if selected_cod_art:
        try:
            article = ArticleSQL.objects.using('sql_server').get(COD_ART=selected_cod_art)
            libelle = article.LIB_ART
        except ArticleSQL.DoesNotExist:
            pass
    all_caracts = Caracteristique.objects.all().select_related('parent')
    tree_map = {c.id: {'node': c, 'children': []} for c in all_caracts}
    roots = []
    for c in all_caracts:
        if c.parent and c.parent.id in tree_map:
            tree_map[c.parent.id]['children'].append(tree_map[c.id])
        elif not c.parent:
            roots.append(tree_map[c.id])
    def flatten_tree(nodes, level=0):
        items = []
        for node_data in nodes:
            items.append({'node': node_data['node'], 'level': level})
            if node_data['children']:
                items.extend(flatten_tree(node_data['children'], level + 1))
        return items
    tree_items = flatten_tree(roots)
    values = {}
    if selected_cod_art:
        values_qs = ArticleCaracteristique.objects.filter(cod_art=selected_cod_art).values('caracteristique_id', 'valeur')
        values = {str(v['caracteristique_id']): v['valeur'] for v in values_qs}
    images = ArticleImage.objects.filter(cod_art=selected_cod_art) if selected_cod_art else []
    return render(request, 'articles/article_caracteristiques.html', {
        'tree_items': tree_items, 'selected_cod_art': selected_cod_art,
        'libelle': libelle, 'assigned_values': values, 'images': images,
    })

@login_required
def article_suivi_serial(request, cod_art):
    return render(request, 'articles/article_suivi_serial.html', {'cod_art': cod_art, 'title': f'Suivi Série: {cod_art}'})

# =============================================================================
# ✅ APIs للخصائص التقنية والصور
# =============================================================================
@login_required
def api_caracteristiques(request):
    query = request.GET.get('q', '').strip()
    qs = Caracteristique.objects.all()
    if query: qs = qs.filter(nom__icontains=query)
    data = [{'id': c.id, 'nom': c.nom, 'unite': c.unite} for c in qs]
    return JsonResponse(data, safe=False)

@login_required
def api_article_caract_values(request, cod_art):
    values = ArticleCaracteristique.objects.filter(cod_art=cod_art).values('caracteristique_id', 'valeur')
    data = {str(v['caracteristique_id']): v['valeur'] for v in values}
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def api_add_article_caract(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        cod_art = data.get('cod_art')
        caract_id = data.get('caract_id')
        valeur = data.get('valeur', '')
        if not cod_art or not caract_id:
            return JsonResponse({'status': 'error', 'message': 'Champs requis manquants'}, status=400)
        obj, created = ArticleCaracteristique.objects.update_or_create(
            cod_art=cod_art, caracteristique_id=caract_id, defaults={'valeur': valeur}
        )
        return JsonResponse({'status': 'ok', 'created': created, 'cod_art': obj.cod_art, 'caract_id': obj.caracteristique_id, 'valeur': obj.valeur})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@login_required
def api_delete_article_caract(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    try:
        data = json.loads(request.body)
        cod_art = data['cod_art']
        caract_id = data['caract_id']
        ArticleCaracteristique.objects.filter(cod_art=cod_art, caracteristique_id=caract_id).delete()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@login_required
def api_upload_article_image(request, cod_art):
    if request.method != 'POST' or not request.FILES.get('image'):
        return JsonResponse({'status': 'error', 'message': 'Aucune image reçue'}, status=400)
    try:
        image = request.FILES['image']
        img = ArticleImage.objects.create(cod_art=cod_art, image=image)
        return JsonResponse({'status': 'ok', 'id': img.id, 'url': img.image.url, 'uploaded_at': img.uploaded_at.strftime('%Y-%m-%d %H:%M')})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@login_required
def api_delete_article_image(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)
    try:
        data = json.loads(request.body)
        image_id = data['image_id']
        img = ArticleImage.objects.get(id=image_id)
        if os.path.isfile(img.image.path):
            os.remove(img.image.path)
        img.delete()
        return JsonResponse({'status': 'ok'})
    except ArticleImage.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)    

# =============================================================================
# ✅ API: تصدير الإحصائيات إلى Excel
# =============================================================================
@login_required
def export_stats_excel(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        tab = data.get('tab')
        cod_art = data.get('cod_art', '').strip()
        date_min = data.get('date_min', '')
        date_max = data.get('date_max', '')
        nat_stock = data.get('nat_stock', '').strip()
        val_art = data.get('val_art', '').strip()
        if not cod_art:
            return JsonResponse({'error': 'COD_ART requis'}, status=400)
        
        wb = Workbook()
        ws = wb.active
        ws.title = f"Stats_{tab}"
        ws['A1'] = f"Statistiques - {tab.upper()} - {cod_art}"
        ws['A1'].font = Font(bold=True, size=14)
        headers = ['Type', 'Date', 'N° Bon', 'Libellé', 'Quantité', 'Valeur']
        for col, header in enumerate(headers, 1):
            ws.cell(row=2, column=col, value=header).font = Font(bold=True)
        ws.cell(row=3, column=1, value=tab)
        ws.cell(row=3, column=2, value=datetime.now().strftime('%Y-%m-%d'))
        ws.cell(row=3, column=3, value='EXEMPLE')
        ws.cell(row=3, column=4, value='Article Exemple')
        ws.cell(row=3, column=5, value=100)
        ws.cell(row=3, column=6, value=1000.00)
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Stats_{cod_art}_{tab}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        return response
    except Exception as e:
        logger.error(f"Erreur export_stats_excel: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# =============================================================================
# ✅ القسم: الإحصائيات والرسوم البيانية
# =============================================================================
def reconstituer_stock_evolution(cursor, cod_art, date_min, date_max, session_id=None):
    """
    إعادة بناء تطور المخزون
    ✅ نجلب جميع الحركات من بداية السجل
    ✅ نخزن النتائج في جدول workflow للاختبار
    ✅ stock_value = المخزون قبل تطبيق الحركة (للحركات العادية)
    ✅ stock_value = qte_mvt (للجرد)
    """
    from core.models import StockEvolutionWorkflow
    
    if not cod_art:
        return {'stock_evolution': {}, 'stock_actuel': 0.0}
    
    # ✅ مسح البيانات القديمة لنفس الـ session
    if session_id:
        StockEvolutionWorkflow.objects.filter(
            session_id=session_id,
            cod_art=cod_art
        ).delete()
    
    # 1. المخزون الحالي من STOCK (هذا هو نتيجة آخر حركة)
    stock_actuel = 0.0
    try:
        cursor.execute("""
            SELECT ISNULL(SUM(QTE_SURSTK), 0)
            FROM STOCK
            WHERE COD_ART = %s
        """, [cod_art])
        row = cursor.fetchone()
        stock_actuel = float(row[0]) if row and row[0] is not None else 0.0
    except Exception as e:
        logger.warning(f"Erreur lecture stock actuel: {e}")
    
    # 2. جلب قواعد sign من naturebon (MySQL)
    nature_rules = {}
    try:
        for nb in NatureBon.objects.all():
            nature_rules[nb.code_nature] = nb.sign if nb.sign is not None else 0
    except Exception as e:
        logger.warning(f"Erreur chargement naturebon: {e}")
    
    # 3. ✅ جلب جميع الحركات من بداية السجل (بدون فلتر تاريخ!)
    all_movements = []
    try:
        cursor.execute("""
            SELECT 
                f.date_b,
                f.qte_mvt,
                f.nature_bon,
                f.class_cout
            FROM fiche_ebc f
            WHERE f.cod_art = %s
              AND f.class_cout IS NOT NULL
              AND LTRIM(RTRIM(f.class_cout)) <> ''
            ORDER BY f.date_b DESC
        """, [cod_art])
        
        for row in cursor.fetchall():
            date_b, qte_mvt, nature_bon, class_cout = row
            all_movements.append({
                'date_b': date_b,
                'qte_mvt': float(qte_mvt or 0),
                'nature_bon': str(nature_bon or '').strip().upper(),
                'class_cout': str(class_cout or '').strip().upper()
            })
    except Exception as e:
        logger.error(f"Erreur chargement mouvements fiche_ebc: {e}")
    
    # 4. تطبيق الخوارزمية العكسية
    stock_evolution = {}
    stock = stock_actuel  # ✅ نبدأ من المخزون الحالي (15.0)
    
    # نقطة البداية (اليوم)
    today_str = date.today().isoformat()
    stock_evolution[today_str] = round(stock, 2)
    
    # ✅ تخزين السطر الأول (INITIAL)
    if session_id:
        try:
            StockEvolutionWorkflow.objects.create(
                session_id=session_id,
                cod_art=cod_art,
                date_b=date.today(),
                stock_value=stock,  # ✅ 15.0
                movement_type='INITIAL',
                movement_qty=0,
                nature_bon=None,
                class_cout=None
            )
        except Exception as e:
            logger.warning(f"Erreur stockage workflow initial: {e}")
    
    # ✅ المرور على الحركات من الأحدث للأقدم
    for mv in all_movements:
        date_b = mv['date_b']
        date_str = date_b.isoformat() if hasattr(date_b, 'isoformat') else str(date_b)
        
        is_inv = (mv['class_cout'] == 'INV' or mv['nature_bon'] == 'INV')
        
        # ✅ حساب stock_value_to_save BEFORE تطبيق الحركة
        if is_inv:
            # للجرد: stock_value = qte_mvt (القيمة الفعلية بعد الجرد)
            stock_value_to_save = mv['qte_mvt']
        else:
            # للحركات العادية: stock_value = stock الحالي (قبل عكس الحركة)
            stock_value_to_save = stock
        
        # ✅ تطبيق الحركة (عكسها للرجوع للخلف)
        if is_inv:
            stock = mv['qte_mvt']
            movement_type = 'INV'
        else:
            sign = nature_rules.get(mv['nature_bon'], 0)
            stock -= (mv['qte_mvt'] * sign)
            movement_type = mv['nature_bon']
        
        # حفظ في stock_evolution (للحسابات)
        stock_evolution[date_str] = round(stock_value_to_save, 2)
        
        # ✅ تخزين في workflow
        if session_id:
            try:
                StockEvolutionWorkflow.objects.create(
                    session_id=session_id,
                    cod_art=cod_art,
                    date_b=date_b if isinstance(date_b, date) else datetime.strptime(date_str, '%Y-%m-%d').date(),
                    stock_value=stock_value_to_save,  # ✅ القيمة الصحيحة (قبل الحركة)
                    movement_type=movement_type,
                    movement_qty=mv['qte_mvt'],
                    nature_bon=mv['nature_bon'],
                    class_cout=mv['class_cout']
                )
            except Exception as e:
                logger.warning(f"Erreur stockage workflow: {e}")
    
    return {
        'stock_evolution': stock_evolution,
        'stock_actuel': stock_actuel
    }


def get_stock_at_date(stock_evolution, target_date, default_stock=0.0):
    """
    الحصول على المخزون في تاريخ معين
    ✅ يبحث عن أقرب تاريخ <= target_date
    ✅ يعيد المخزون المحفوظ في stock_evolution (وهو المخزون بعد الحركة)
    """
    if not stock_evolution or not target_date:
        return default_stock
    
    target_str = target_date.isoformat() if hasattr(target_date, 'isoformat') else str(target_date)
    
    # بحث مباشر
    if target_str in stock_evolution:
        return stock_evolution[target_str]
    
    # بحث عن أقرب تاريخ <= target_date
    try:
        from datetime import datetime as dt_cls
        target_dt = dt_cls.strptime(target_str, '%Y-%m-%d').date() if isinstance(target_str, str) else target_date
    except:
        return default_stock
    
    closest_date = None
    closest_stock = default_stock
    
    for d_str, s_val in stock_evolution.items():
        try:
            dt = dt_cls.strptime(d_str, '%Y-%m-%d').date() if isinstance(d_str, str) else d_str
            if dt <= target_dt:
                if closest_date is None or dt > closest_date:
                    closest_date = dt
                    closest_stock = s_val
        except:
            continue
    
    return closest_stock


def get_stock_before_date(stock_evolution, target_date, default_stock=0.0):
    """
    الحصول على المخزون قبل تاريخ معين
    ✅ يبحث عن آخر حركة قبل target_date (صارم <)
    ✅ يعيد المخزون بعد آخر حركة قبل target_date (وهو المخزون قبل الحركة في target_date)
    """
    if not stock_evolution or not target_date:
        return default_stock
    
    target_str = target_date.isoformat() if hasattr(target_date, 'isoformat') else str(target_date)
    
    try:
        from datetime import datetime as dt_cls
        target_dt = dt_cls.strptime(target_str, '%Y-%m-%d').date() if isinstance(target_str, str) else target_date
    except:
        return default_stock
    
    closest_date = None
    closest_stock = default_stock
    
    # ابحث عن آخر تاريخ < target_date (أقل من، وليس أقل أو يساوي)
    for d_str, s_val in stock_evolution.items():
        try:
            dt = dt_cls.strptime(d_str, '%Y-%m-%d').date() if isinstance(d_str, str) else d_str
            if dt < target_dt:  # صارم: أقل من فقط
                if closest_date is None or dt > closest_date:
                    closest_date = dt
                    closest_stock = s_val
        except:
            continue
    
    return closest_stock


# ✅ حذف دالة get_stock_after_movement - لم نعد نحتاجها!


def get_stock_after_movement(stock_evolution, date_b, qte_mvt, sign, stock_actuel):
    """
    حساب المخزون بعد حركة معينة
    = المخزون قبل الحركة + (الكمية * sign)
    ✅ يستخدم get_stock_before_date للحصول على المخزون قبل الحركة
    """
    # احصل على المخزون قبل هذه الحركة
    stock_before = get_stock_before_date(stock_evolution, date_b, stock_actuel)
    
    # احسب المخزون بعد الحركة
    stock_after = stock_before + (float(qte_mvt or 0) * sign)
    
    return round(stock_after, 2)


@login_required
def api_stock_evolution_debug(request):
    """API لعرض نتائج stock_evolution من جدول workflow"""
    session_id = request.session.session_key
    cod_art = request.GET.get('cod_art', '').strip()
    
    if not session_id or not cod_art:
        return JsonResponse({'error': 'Session ID ou COD_ART manquant'}, status=400)
    
    try:
        from core.models import StockEvolutionWorkflow
        
        results = StockEvolutionWorkflow.objects.filter(
            session_id=session_id,
            cod_art=cod_art
        ).order_by('-date_b')
        
        data = []
        for r in results:
            data.append({
                'date_b': r.date_b.strftime('%Y-%m-%d'),
                'stock_value': float(r.stock_value),
                'movement_type': r.movement_type or '',
                'movement_qty': float(r.movement_qty),
                'nature_bon': r.nature_bon or '',
                'class_cout': r.class_cout or ''
            })
        
        return JsonResponse({
            'cod_art': cod_art,
            'session_id': session_id,
            'total_records': len(data),
            'data': data
        })
    
    except Exception as e:
        logger.error(f"Erreur api_stock_evolution_debug: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# =============================================================================
# ✅ دالة مشتركة: بناء بيانات تطور المخزون للرسم البياني
# =============================================================================
def build_stock_chart_data(stock_evolution, date_min, date_max, stock_actuel=0.0):
    """
    بناء بيانات الرسم البياني لتطور المخزون حسب الشهر
    ✅ يأخذ آخر قيمة في كل شهر
    ✅ يستخدم stock_actuel كقيمة ابتدائية
    """
    stock_months = []
    stock_quantities = []
    
    try:
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                       'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
        current = start_date.replace(day=1)
        
        # تحويل إلى قائمة مرتبة
        evolution_list = []
        for d_str, s_val in stock_evolution.items():
            try:
                dt = datetime.strptime(d_str, '%Y-%m-%d').date()
                evolution_list.append((dt, s_val))
            except:
                continue
        evolution_list.sort(key=lambda x: x[0])
        
        # تتبع آخر قيمة معروفة - نبدأ من stock_actuel
        last_known_stock = stock_actuel
        
        while current <= end_date:
            month_label = f"{month_names[current.month-1]} {str(current.year)[-2:]}"
            
            # آخر يوم في الشهر
            if current.month == 12:
                last_day = current.replace(year=current.year+1, month=1, day=1) - timedelta(days=1)
            else:
                last_day = current.replace(month=current.month+1, day=1) - timedelta(days=1)
            
            # البحث عن آخر قيمة <= last_day
            stock_val = last_known_stock
            for dt, s_val in evolution_list:
                if dt <= last_day:
                    stock_val = s_val
                    last_known_stock = s_val
                else:
                    break
            
            stock_months.append(month_label)
            stock_quantities.append(round(stock_val, 2))
            
            # الشهر التالي
            if current.month == 12:
                current = current.replace(year=current.year+1, month=1)
            else:
                current = current.replace(month=current.month+1)
    except Exception as e:
        logger.error(f"Erreur graphique stock evolution: {e}")
    
    return stock_months, stock_quantities


@login_required
def get_stock_info_view(request):
    """
    إرجاع معلومات المخزون لمادة معينة
    """
    cod_art = request.GET.get('cod_art', '').strip()
    if not cod_art:
        return JsonResponse({'error': 'Code article requis'}, status=400)
    
    try:
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("""
                SELECT LIB_ART, ISNULL(CLASS_COUT, ''), ISNULL(EMPL, '')
                FROM ARTICLE 
                WHERE COD_ART = %s
            """, [cod_art])
            art_row = cursor.fetchone()
            
            if not art_row:
                cursor.execute("""
                    SELECT TOP 1 'Article inconnu', ISNULL(CLASS_COUT, ''), ''
                    FROM STOCK 
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
            
            cursor.execute("""
                SELECT 
                    ISNULL(SUM(QTE_SURSTK), 0),
                    ISNULL(AVG(PUMP/1000.0), 0)
                FROM STOCK 
                WHERE COD_ART = %s
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
        logger.error(f"Erreur get_stock_info: {str(e)}")
        return JsonResponse({
            'error': 'Erreur serveur',
            'libelle_article': 'Erreur',
            'classe_cout': 'Erreur',
            'emplacement': 'Erreur',
            'qte_surstk': 0,
            'pump': 0.0
        }, status=500)
        
@login_required
def statistiques_ajax_view(request):
    """
    نقطة الدخول العامة للإحصائيات
    """
    try:
        tab_type = request.GET.get('tab_type', 'article')
        tab = request.GET.get('tab')
        date_min = request.GET.get('date_min', '')
        date_max = request.GET.get('date_max', '')
        nat_stock = request.GET.get('nat_stock', '').strip()
        val_art = request.GET.get('val_art', '').strip()
        
        centre_cout = request.GET.get('centre_cout', '').strip() if tab_type == 'general' else None
        classe_cout = request.GET.get('classe_cout', '').strip() if tab_type == 'general' else None
        cod_art = request.GET.get('cod_art', '').strip() if tab_type == 'article' else None
        
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 20))
        order_column_index = request.GET.get('order[0][column]')
        order_dir = request.GET.get('order[0][dir]', 'asc')
        search_value = request.GET.get('search[value]', '').strip()
        
         # ✅ الحصول على session_id
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        if not date_min:
            date_min = (date.today() - timedelta(days=365)).isoformat()
        if not date_max:
            date_max = date.today().isoformat()
        
        handler_map = {}
        if tab_type == 'article':
            handler_map = {
                'consommation': get_consommation_data,
                'achat': get_achat_data,
                'retours': get_retours_art_data,
                'prestations': get_prestations_art_data,
                'mouvements': get_mouvements_data,
            }
            handler_args = (cod_art, nat_stock, val_art, date_min, date_max)
        else:
            handler_map = {
                'entrees': get_entrees_generales_data,
                'sorties': get_sorties_generales_data,
                'retours': get_retours_generales_data,
                'prestations': get_prestations_generales_data,
            }
            handler_args = (nat_stock, val_art, date_min, date_max, centre_cout, classe_cout)
        
        handler = handler_map.get(tab)
        if not handler:
            return JsonResponse({'error': 'Onglet ou type invalide'}, status=400)
        
        with connections['sql_server'].cursor() as cursor:
            result = handler(
                cursor, *handler_args,
                search_value=search_value,
                order_column_index=order_column_index,
                order_dir=order_dir,
                session_id=session_id
            )
            
            data = result.get('data', [])
            total_records = result.get('total_records', len(data))
            filtered_records = result.get('filtered_records', total_records)
            paged_data = data[start:start + length]
            
            response_data = {
                'draw': draw, 
                'recordsTotal': total_records, 
                'recordsFiltered': filtered_records, 
                'data': paged_data,
            }
            if 'total_valeur' in result: 
                response_data['total_valeur'] = result['total_valeur']
            if 'total_valeur_sorties' in result: 
                response_data['total_valeur_sorties'] = result['total_valeur_sorties']
            if 'months' in result: 
                response_data['months'] = result['months']
            if 'quantities' in result: 
                response_data['quantities'] = result['quantities']
            if 'datasets' in result: 
                response_data['datasets'] = result['datasets']
            if 'stock_months' in result: 
                response_data['stock_months'] = result['stock_months']
            if 'stock_quantities' in result: 
                response_data['stock_quantities'] = result['stock_quantities']
            if 'stock_actuel' in result: 
                response_data['stock_actuel'] = result['stock_actuel']
            return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Erreur dans statistiques_ajax_view: {e}\n{traceback.format_exc()}")
        return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)

# =============================================================================
# ✅  (مقالات مفردة)
# =============================================================================
def get_consommation_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                          search_value=None, order_column_index=None, order_dir='asc',
                          session_id=None):
    from core.models import NatureStock
    
    # =========================================================================
    # ✅ 1. إعادة بناء المخزون
    # =========================================================================
    stock_info = reconstituer_stock_evolution(cursor, cod_art, date_min, date_max, session_id=session_id)
    stock_evolution = stock_info.get('stock_evolution', {})
    stock_actuel = stock_info.get('stock_actuel', 0.0)
    
    # =========================================================================
    # ✅ 2. الاستعلام الأصلي
    # =========================================================================
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
    
    search_clause = ""
    search_params = []
    if search_value:
        search_conditions = ["e2.numero_bon LIKE %s", "e2.lib_art LIKE %s"]
        search_params = [f"%{search_value}%"] * len(search_conditions)
        search_clause = " AND (" + " OR ".join(search_conditions) + ")"
    
    order_clause = "ORDER BY e2.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'e2.date_b', '2': 'e2.numero_bon', '3': 'e2.lib_art', '4': 'e2.qte_mvt', '5': 'extra', '6': 'cc.lib_cl_c', '7': 'ct.lib_centre'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            if col_name == 'extra':
                order_clause = f"ORDER BY CASE WHEN e2.val_art = 1 THEN 1 WHEN e2.val_art = 2 THEN 2 WHEN e2.val_art = 3 THEN 3 WHEN e2.val_art = 4 THEN 4 ELSE 5 END {'ASC' if order_dir == 'asc' else 'DESC'}"
            else:
                order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
                order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"""
            SELECT 'Consommation' AS type, e2.date_b, e2.numero_bon, e2.lib_art, e2.qte_mvt, e2.lib_um,
            CASE WHEN e2.val_art = 1 THEN '100%%' WHEN e2.val_art = 2 THEN '75%%' WHEN e2.val_art = 3 THEN '25%%' WHEN e2.val_art = 4 THEN '0%%' ELSE 'Inconnu' END AS extra,
            'Sortie' AS sens, e2.nat_stock, e2.class_cout, cc.lib_cl_c, e2.centr_cout, ct.lib_centre
            FROM Etat_b2 e2
            LEFT JOIN clascout cc ON e2.class_cout = cc.class_cout
            LEFT JOIN centre ct ON e2.centr_cout = ct.centr_cout
            WHERE {full_where} {order_clause};
        """, full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e:
                logger.warning(f"Erreur chargement nature_stock depuis MySQL: {e}")
        
        # ✅ إثراء البيانات + إضافة stock_reconstitue
        data = []
        for row in raw_data:
            enriched_row = row.copy()
            nat_code = row.get('nat_stock')
            enriched_row['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched_row['lib_cl_c'] = enriched_row.get('lib_cl_c') or '—'
            enriched_row['lib_centre'] = enriched_row.get('lib_centre') or '—'
            
            # ✅ حساب المخزون بعد الحركة (Consommation = sortie, sign = -1)
            date_b = row.get('date_b')
            qte_mvt = row.get('qte_mvt', 0)
            enriched_row['stock_reconstitue'] = get_stock_after_movement(
                stock_evolution, 
                date_b, 
                qte_mvt, 
                -1,  # Consommation = sortie
                stock_actuel
            )
            
            data.append(enriched_row)
    except Exception as e:
        logger.error(f"Erreur données consommation: {str(e)}")
        data = []
    
    # =========================================================================
    # ✅ 3. بيانات الرسم البياني للكميات
    # =========================================================================
    months_data, quantities_data = [], []
    if cod_art and date_min and date_max:
        try:
            cursor.execute(f"SELECT YEAR(e2.date_b) AS yr, MONTH(e2.date_b) AS mth, SUM(e2.qte_mvt) AS total FROM Etat_b2 e2 WHERE {where_sql} GROUP BY YEAR(e2.date_b), MONTH(e2.date_b) ORDER BY yr, mth;", params)
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e:
            logger.error(f"Erreur graphique consommation: {str(e)}")
            months_data, quantities_data = ['Erreur'], [0]
    
    # =========================================================================
    # ✅ 4. بيانات تطور المخزون للرسوم البيانية
    # =========================================================================
    stock_months, stock_quantities = build_stock_chart_data(
        stock_evolution, 
        date_min, 
        date_max,
        stock_actuel
    )
    
    # =========================================================================
    # ✅ 5. حساب عدد السجلات
    # =========================================================================
    try:
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b2 e2 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b2 e2 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except:
        total_records = filtered_records = len(data)
    
    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'stock_months': stock_months,
        'stock_quantities': stock_quantities,
        'stock_actuel': stock_actuel,
        'total_records': total_records,
        'filtered_records': filtered_records
    }


def get_achat_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                   search_value=None, order_column_index=None, order_dir='asc',
                   session_id=None):
    from core.models import NatureStock
    
    # =========================================================================
    # ✅ 1. إعادة بناء المخزون
    # =========================================================================
    stock_info = reconstituer_stock_evolution(cursor, cod_art, date_min, date_max, session_id=session_id)
    stock_evolution = stock_info.get('stock_evolution', {})
    stock_actuel = stock_info.get('stock_actuel', 0.0)
    
    # =========================================================================
    # ✅ 2. الاستعلام الأصلي
    # =========================================================================
    where_clauses = ["a.COD_ART = %s"]
    params = [cod_art]
    if nat_stock:
        where_clauses.append("e1.nat_stock = %s")
        params.append(nat_stock)
    where_clauses.extend(["e1.date_b >= %s", "e1.date_b <= %s"])
    params.extend([date_min, date_max])
    where_sql = " AND ".join(where_clauses)
    
    search_clause = ""
    search_params = []
    if search_value:
        conditions = ["e1.numero_bon LIKE %s", "a.LIB_ART LIKE %s", "e1.doc_ref LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    
    order_clause = "ORDER BY e1.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {
            '0': 'type', '1': 'e1.date_b', '2': 'e1.numero_bon',
            '3': 'e1.qte_mvt', '4': 'e1.lib_um', '5': 'e1.class_cout',
            '6': 'cc.lib_cl_c', '7': 'libelle_nature', '8': 'PU',
            '9': 'e1.doc_ref', '10': 'ct.lib_centre'
        }
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            if col_name == 'PU':
                order_clause = f"ORDER BY CASE WHEN e1.qte_mvt > 0 THEN CAST(e1.valeur_tot AS FLOAT) / e1.qte_mvt ELSE 0 END {'ASC' if order_dir == 'asc' else 'DESC'}"
            else:
                order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
                order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"""
            SELECT 'Achat' AS type, e1.date_b, e1.numero_bon, a.LIB_ART AS lib_art,
                   e1.qte_mvt, e1.lib_um, e1.class_cout,
                   cc.lib_cl_c,
                   CASE WHEN e1.qte_mvt > 0 THEN CAST(e1.valeur_tot AS FLOAT) / e1.qte_mvt ELSE 0 END AS PU,
                   e1.doc_ref, e1.date_ref, 'Entrée' AS sens, e1.nat_stock,
                   ct.centr_cout, ct.lib_centre
            FROM Etat_b1 e1
            INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART
            LEFT JOIN clascout cc ON e1.class_cout = cc.class_cout
            LEFT JOIN (SELECT num, MAX(centr_cout) as centr_cout FROM fiche_ebc GROUP BY num) fe
                   ON e1.numero_bon = fe.num
            LEFT JOIN centre ct ON fe.centr_cout = ct.centr_cout
            WHERE {full_where} {order_clause};
        """, full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e:
                logger.warning(f"Erreur chargement nature_stock depuis MySQL: {e}")
        
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = enriched.get('lib_cl_c') or '—'
            enriched['lib_centre'] = enriched.get('lib_centre') or '—'
            enriched['lib_art'] = enriched.get('lib_art') or '—'
            
            # ✅ حساب المخزون بعد الحركة (Achat = entrée, sign = +1)
            date_b = row.get('date_b')
            qte_mvt = row.get('qte_mvt', 0)
            enriched['stock_reconstitue'] = get_stock_after_movement(
                stock_evolution, 
                date_b, 
                qte_mvt, 
                1,  # Achat = entrée
                stock_actuel
            )
            
            data.append(enriched)
    except Exception as e:
        logger.error(f"Erreur données achat: {str(e)}")
        data = []
    
    # =========================================================================
    # ✅ 3. بيانات الرسم البياني للكميات
    # =========================================================================
    months_data, quantities_data = [], []
    if cod_art and date_min and date_max:
        try:
            cursor.execute(
                f"SELECT YEAR(e1.date_b) AS yr, MONTH(e1.date_b) AS mth, SUM(e1.qte_mvt) AS total "
                f"FROM Etat_b1 e1 INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART "
                f"WHERE e1.cod_art = %s AND e1.date_b >= %s AND e1.date_b <= %s "
                f"GROUP BY YEAR(e1.date_b), MONTH(e1.date_b) ORDER BY yr, mth;",
                [cod_art, date_min, date_max]
            )
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                           'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e:
            logger.error(f"Erreur graphique achat: {str(e)}")
            months_data, quantities_data = ['Erreur'], [0]
    
    # =========================================================================
    # ✅ 4. بيانات تطور المخزون للرسوم البيانية
    # =========================================================================
    stock_months, stock_quantities = build_stock_chart_data(
        stock_evolution, 
        date_min, 
        date_max,
        stock_actuel
    )
    
    # =========================================================================
    # ✅ 5. حساب عدد السجلات
    # =========================================================================
    try:
        cursor.execute(
            f"SELECT COUNT(*) FROM Etat_b1 e1 INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART WHERE {where_sql}",
            params
        )
        total_records = cursor.fetchone()[0]
        cursor.execute(
            f"SELECT COUNT(*) FROM Etat_b1 e1 INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART WHERE {full_where}",
            full_params
        )
        filtered_records = cursor.fetchone()[0]
    except:
        total_records = filtered_records = len(data)
    
    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'stock_months': stock_months,
        'stock_quantities': stock_quantities,
        'stock_actuel': stock_actuel,
        'total_records': total_records,
        'filtered_records': filtered_records
    }


def get_retours_art_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                         search_value=None, order_column_index=None, order_dir='asc',
                         session_id=None):
    from core.models import NatureStock
    
    # =========================================================================
    # ✅ 1. إعادة بناء المخزون
    # =========================================================================
    stock_info = reconstituer_stock_evolution(cursor, cod_art, date_min, date_max, session_id=session_id)
    stock_evolution = stock_info.get('stock_evolution', {})
    stock_actuel = stock_info.get('stock_actuel', 0.0)
    
    # =========================================================================
    # ✅ 2. الاستعلام الأصلي
    # =========================================================================
    where_clauses = ["e3.cod_art = %s", "e3.date_b >= %s", "e3.date_b <= %s"]
    params = [cod_art, date_min, date_max]
    if nat_stock:
        where_clauses.append("e3.nat_stock = %s")
        params.append(nat_stock)
    if val_art:
        where_clauses.append("e3.val_art = %s")
        params.append(val_art)
    where_sql = " AND ".join(where_clauses)
    
    search_clause, search_params = "", []
    if search_value:
        conditions = ["e3.numero_bon LIKE %s", "e3.lib_art LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    
    order_clause = "ORDER BY e3.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'e3.date_b', '2': 'e3.numero_bon', '3': 'e3.lib_art', '4': 'e3.qte_mvt', '5': 'e3.nat_stock'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"""
            SELECT 'Retour' AS type, e3.date_b, e3.numero_bon, e3.lib_art, e3.qte_mvt, e3.lib_um, e3.nat_stock, e3.class_cout, e3.centr_cout, 'Entrée' AS sens
            FROM Etat_b3 e3 WHERE {full_where} {order_clause};
        """, full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e:
                logger.warning(f"Erreur chargement nature_stock: {e}")
        
        # ✅ إثراء البيانات + إضافة stock_reconstitue
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = row.get('class_cout') or '—'
            enriched['lib_centre'] = row.get('centr_cout') or '—'
            
            # ✅ حساب المخزون بعد الحركة (Retour = entrée, sign = +1)
            date_b = row.get('date_b')
            qte_mvt = row.get('qte_mvt', 0)
            enriched['stock_reconstitue'] = get_stock_after_movement(
                stock_evolution, 
                date_b, 
                qte_mvt, 
                1,  # Retour = entrée
                stock_actuel
            )
            
            data.append(enriched)
    except Exception as e:
        logger.error(f"Erreur données retours_art: {str(e)}")
        data = []
    
    # =========================================================================
    # ✅ 3. بيانات الرسم البياني
    # =========================================================================
    months_data, quantities_data = [], []
    if cod_art and date_min and date_max:
        try:
            cursor.execute(f"SELECT YEAR(e3.date_b) AS yr, MONTH(e3.date_b) AS mth, SUM(e3.qte_mvt) AS total FROM Etat_b3 e3 WHERE e3.cod_art = %s AND e3.date_b >= %s AND e3.date_b <= %s GROUP BY YEAR(e3.date_b), MONTH(e3.date_b) ORDER BY yr, mth;", [cod_art, date_min, date_max])
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e:
            logger.error(f"Erreur graphique retours_art: {str(e)}")
            months_data, quantities_data = ['Erreur'], [0]
    
    # ✅ بيانات تطور المخزون
    stock_months, stock_quantities = build_stock_chart_data(
        stock_evolution, 
        date_min, 
        date_max,
        stock_actuel
    )
    
    # =========================================================================
    # ✅ 4. حساب عدد السجلات
    # =========================================================================
    try:
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b3 e3 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b3 e3 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except:
        total_records = filtered_records = len(data)
    
    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'stock_months': stock_months,
        'stock_quantities': stock_quantities,
        'stock_actuel': stock_actuel,
        'total_records': total_records,
        'filtered_records': filtered_records
    }


def get_prestations_art_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                             search_value=None, order_column_index=None, order_dir='asc',
                             session_id=None):
    from core.models import NatureStock
    
    # =========================================================================
    # ✅ 1. إعادة بناء المخزون
    # =========================================================================
    stock_info = reconstituer_stock_evolution(cursor, cod_art, date_min, date_max, session_id=session_id)
    stock_evolution = stock_info.get('stock_evolution', {})
    stock_actuel = stock_info.get('stock_actuel', 0.0)
    
    # =========================================================================
    # ✅ 2. الاستعلام الأصلي
    # =========================================================================
    where_clauses = ["e4.cod_art = %s", "e4.date_b >= %s", "e4.date_b <= %s"]
    params = [cod_art, date_min, date_max]
    if nat_stock:
        where_clauses.append("e4.nat_stock = %s")
        params.append(nat_stock)
    if val_art:
        where_clauses.append("e4.val_art = %s")
        params.append(val_art)
    where_sql = " AND ".join(where_clauses)
    
    search_clause, search_params = "", []
    if search_value:
        conditions = ["e4.numero_bon LIKE %s", "e4.lib_art LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    
    order_clause = "ORDER BY e4.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'e4.date_b', '2': 'e4.numero_bon', '3': 'e4.lib_art', '4': 'e4.qte_mvt', '5': 'e4.nat_stock'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"""
            SELECT 'Prestation' AS type, e4.date_b, e4.numero_bon, e4.lib_art, e4.qte_mvt, e4.lib_um, e4.nat_stock, e4.class_cout, e4.centr_cout, 'Sortie' AS sens
            FROM Etat_b4 e4 WHERE {full_where} {order_clause};
        """, full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e:
                logger.warning(f"Erreur chargement nature_stock: {e}")
        
        # ✅ إثراء البيانات + إضافة stock_reconstitue
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = row.get('class_cout') or '—'
            enriched['lib_centre'] = row.get('centr_cout') or '—'
            
            # ✅ حساب المخزون بعد الحركة (Prestation = sortie, sign = -1)
            date_b = row.get('date_b')
            qte_mvt = row.get('qte_mvt', 0)
            enriched['stock_reconstitue'] = get_stock_after_movement(
                stock_evolution, 
                date_b, 
                qte_mvt, 
                -1,  # Prestation = sortie
                stock_actuel
            )
            
            data.append(enriched)
    except Exception as e:
        logger.error(f"Erreur données prestations_art: {str(e)}")
        data = []
    
    # =========================================================================
    # ✅ 3. بيانات الرسم البياني
    # =========================================================================
    months_data, quantities_data = [], []
    if cod_art and date_min and date_max:
        try:
            cursor.execute(f"SELECT YEAR(e4.date_b) AS yr, MONTH(e4.date_b) AS mth, SUM(e4.qte_mvt) AS total FROM Etat_b4 e4 WHERE e4.cod_art = %s AND e4.date_b >= %s AND e4.date_b <= %s GROUP BY YEAR(e4.date_b), MONTH(e4.date_b) ORDER BY yr, mth;", [cod_art, date_min, date_max])
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e:
            logger.error(f"Erreur graphique prestations_art: {str(e)}")
            months_data, quantities_data = ['Erreur'], [0]
    
    # ✅ بيانات تطور المخزون
    stock_months, stock_quantities = build_stock_chart_data(
        stock_evolution, 
        date_min, 
        date_max,
        stock_actuel
    )
    
    # =========================================================================
    # ✅ 4. حساب عدد السجلات
    # =========================================================================
    try:
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b4 e4 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b4 e4 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except:
        total_records = filtered_records = len(data)
    
    return {
        'data': data,
        'months': months_data,
        'quantities': quantities_data,
        'stock_months': stock_months,
        'stock_quantities': stock_quantities,
        'stock_actuel': stock_actuel,
        'total_records': total_records,
        'filtered_records': filtered_records
    }


def get_mouvements_data(cursor, cod_art, nat_stock, val_art, date_min, date_max,
                        search_value=None, order_column_index=None, order_dir='asc',
                        session_id=None):
    from core.models import NatureStock
    
    # =========================================================================
    # ✅ 1. إعادة بناء المخزون
    # =========================================================================
    stock_info = reconstituer_stock_evolution(cursor, cod_art, date_min, date_max, session_id=session_id)
    stock_evolution = stock_info.get('stock_evolution', {})
    stock_actuel = stock_info.get('stock_actuel', 0.0)
    
    all_movements = []
    if not cod_art or not date_min or not date_max:
        return {'data': [], 'months': [], 'datasets': [], 
                'stock_months': [], 'stock_quantities': [], 'stock_actuel': 0.0,
                'total_records': 0, 'filtered_records': 0}
    
    try:
        start_date = datetime.strptime(date_min, '%Y-%m-%d').date().replace(day=1)
        end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
        month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        months_data = []
        current = start_date
        while current <= end_date:
            months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
            current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        
        achat_data = [0.0] * len(months_data)
        consommation_data = [0.0] * len(months_data)
        retours_data = [0.0] * len(months_data)
        prestations_data = [0.0] * len(months_data)
        
        def get_month_index(date_b):
            if isinstance(date_b, str):
                date_b = datetime.strptime(date_b, '%Y-%m-%d').date()
            idx = ((date_b.year - start_date.year) * 12 + date_b.month - start_date.month)
            return idx if 0 <= idx < len(months_data) else None
        
        def build_params_and_conditions(base_table_alias, has_val_art=False):
            conditions = [f"{base_table_alias}.date_b >= %s", f"{base_table_alias}.date_b <= %s", f"{base_table_alias}.cod_art = %s"]
            params = [date_min, date_max, cod_art]
            if nat_stock:
                conditions.append(f"{base_table_alias}.nat_stock = %s")
                params.append(nat_stock)
            if has_val_art and val_art:
                conditions.append(f"{base_table_alias}.val_art = %s")
                params.append(val_art)
            return " AND ".join(conditions), params
        
        # =========================================================================
        # ✅ 2. استعلامات الرسم البياني
        # =========================================================================
        queries = [
            ("SELECT e1.date_b, e1.qte_mvt FROM Etat_b1 e1 WHERE {}", build_params_and_conditions('e1', False), achat_data),
            ("SELECT e2.date_b, e2.qte_mvt FROM Etat_b2 e2 WHERE {}", build_params_and_conditions('e2', True), consommation_data),
            ("SELECT e3.date_b, e3.qte_mvt FROM Etat_b3 e3 WHERE {}", build_params_and_conditions('e3', True), retours_data),
            ("SELECT e4.date_b, e4.qte_mvt FROM Etat_b4 e4 WHERE {}", build_params_and_conditions('e4', True), prestations_data),
        ]
        for sql_template, (where_clause, params), target_list in queries:
            try:
                cursor.execute(sql_template.format(where_clause), params)
                for row in cursor.fetchall():
                    idx = get_month_index(row[0])
                    if idx is not None:
                        target_list[idx] += float(row[1]) if row[1] else 0.0
            except Exception as e:
                logger.error(f"Erreur requête mouvements (chart): {str(e)}")
        
        # =========================================================================
        # ✅ 3. استعلامات الجدول
        # =========================================================================
        columns_list = ['type', 'date_b', 'numero_bon', 'lib_art', 'qte_mvt', 'extra', 'sens', 'nat_stock', 'lib_um', 'class_cout', 'lib_cl_c', 'centr_cout', 'lib_centre', 'ref_doc']
        table_queries = [
            (f"SELECT 'Achat' AS type, e1.date_b, e1.numero_bon, a.LIB_ART AS lib_art, e1.qte_mvt, CASE WHEN e1.qte_mvt > 0 THEN CAST(e1.valeur_tot AS FLOAT) / e1.qte_mvt ELSE 0 END AS extra, 'Entrée' AS sens, e1.nat_stock, e1.lib_um, e1.class_cout, cc.lib_cl_c, fe.centr_cout, ct.lib_centre, e1.doc_ref AS ref_doc FROM Etat_b1 e1 INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART LEFT JOIN clascout cc ON e1.class_cout = cc.class_cout LEFT JOIN (SELECT num, MAX(centr_cout) as centr_cout FROM fiche_ebc GROUP BY num) fe ON e1.numero_bon = fe.num LEFT JOIN centre ct ON fe.centr_cout = ct.centr_cout WHERE {{}}", build_params_and_conditions('e1', False)),
            (f"SELECT 'Consommation' AS type, e2.date_b, e2.numero_bon, e2.lib_art, e2.qte_mvt, CASE WHEN e2.val_art = 1 THEN '100%%' WHEN e2.val_art = 2 THEN '75%%' WHEN e2.val_art = 3 THEN '25%%' WHEN e2.val_art = 4 THEN '0%%' ELSE 'Inconnu' END AS extra, 'Sortie' AS sens, e2.nat_stock, e2.lib_um, e2.class_cout, cc.lib_cl_c, e2.centr_cout, ct.lib_centre, NULL AS ref_doc FROM Etat_b2 e2 LEFT JOIN clascout cc ON e2.class_cout = cc.class_cout LEFT JOIN centre ct ON e2.centr_cout = ct.centr_cout WHERE {{}}", build_params_and_conditions('e2', True)),
            (f"SELECT 'Retour' AS type, e3.date_b, e3.numero_bon, e3.lib_art, e3.qte_mvt, NULL AS extra, 'Entrée' AS sens, e3.nat_stock, e3.lib_um, e3.class_cout, cc.lib_cl_c, e3.centr_cout, ct.lib_centre, NULL AS ref_doc FROM Etat_b3 e3 LEFT JOIN clascout cc ON e3.class_cout = cc.class_cout LEFT JOIN centre ct ON e3.centr_cout = ct.centr_cout WHERE {{}}", build_params_and_conditions('e3', True)),
            (f"SELECT 'Prestation' AS type, e4.date_b, e4.numero_bon, e4.lib_art, e4.qte_mvt, NULL AS extra, 'Sortie' AS sens, e4.nat_stock, e4.lib_um, e4.class_cout, cc.lib_cl_c, e4.centr_cout, ct.lib_centre, NULL AS ref_doc FROM Etat_b4 e4 LEFT JOIN clascout cc ON e4.class_cout = cc.class_cout LEFT JOIN centre ct ON e4.centr_cout = ct.centr_cout WHERE {{}}", build_params_and_conditions('e4', True)),
        ]
        
        # خريطة sign لكل نوع حركة
        sign_map = {
            'Achat': 1,
            'Consommation': -1,
            'Retour': 1,
            'Prestation': -1
        }
        
        for sql_template, (where_clause, params) in table_queries:
            try:
                cursor.execute(sql_template.format(where_clause), params)
                for row in cursor.fetchall():
                    d = dict(zip(columns_list, row))
                    date_b = d.get('date_b')
                    qte_mvt = d.get('qte_mvt', 0)
                    movement_type = d.get('type', '')
                    sign = sign_map.get(movement_type, 0)
                    d['stock_reconstitue'] = get_stock_after_movement(
                        stock_evolution, 
                        date_b, 
                        qte_mvt, 
                        sign, 
                        stock_actuel
                    )
                    all_movements.append(d)
            except Exception as e:
                logger.error(f"Erreur requête tabulaire mouvements: {str(e)}")
        
        # =========================================================================
        # ✅ 4. إثراء البيانات
        # =========================================================================
        nat_codes = list(set(row.get('nat_stock') for row in all_movements if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e:
                logger.warning(f"Erreur chargement nature_stock depuis MySQL: {e}")
        
        cleaned_movements = []
        for row in all_movements:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = enriched.get('lib_cl_c') or '—'
            enriched['lib_centre'] = enriched.get('lib_centre') or '—'
            enriched['lib_art'] = enriched.get('lib_art') or '—'
            enriched['ref_doc'] = (enriched.get('ref_doc') or '').strip()
            cleaned_movements.append(enriched)
        all_movements = cleaned_movements
        
        # =========================================================================
        # ✅ 5. الفلترة والترتيب
        # =========================================================================
        if search_value:
            search_val = search_value.lower()
            all_movements = [item for item in all_movements if search_val in str(item.get('numero_bon', '')).lower() or search_val in str(item.get('lib_art', '')).lower() or search_val in str(item.get('type', '')).lower() or search_val in str(item.get('ref_doc', '')).lower()]
        
        if order_column_index and order_column_index.isdigit():
            columns_map = {'0': 'type', '1': 'date_b', '2': 'numero_bon', '3': 'lib_art', '4': 'qte_mvt', '5': 'extra', '6': 'sens', '7': 'libelle_nature', '8': 'lib_cl_c', '9': 'lib_centre'}
            if order_column_index in columns_map:
                sort_key = columns_map[order_column_index]
                reverse_order = order_dir != 'asc'
                try:
                    all_movements.sort(key=lambda x: (x.get(sort_key) is None, x.get(sort_key)), reverse=reverse_order)
                except:
                    all_movements.sort(key=lambda x: x['date_b'], reverse=True)
        else:
            all_movements.sort(key=lambda x: x['date_b'], reverse=True)
        
        # =========================================================================
        # ✅ 6. Datasets للرسم البياني
        # =========================================================================
        datasets = [
            {'label': 'Achats', 'data': achat_data, 'borderColor': '#0d6efd', 'backgroundColor': 'rgba(13, 110, 253, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#0d6efd'},
            {'label': 'Consommation', 'data': consommation_data, 'borderColor': '#dc3545', 'backgroundColor': 'rgba(220, 53, 69, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#dc3545'},
            {'label': 'Retours', 'data': retours_data, 'borderColor': '#198754', 'backgroundColor': 'rgba(25, 135, 84, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#198754'},
            {'label': 'Prestations', 'data': prestations_data, 'borderColor': '#6f42c1', 'backgroundColor': 'rgba(111, 66, 193, 0.2)', 'tension': 0.3, 'pointBackgroundColor': '#6f42c1'}
        ]
        
        # =========================================================================
        # ✅ 7. بيانات تطور المخزون
        # =========================================================================
        stock_months, stock_quantities = build_stock_chart_data(
            stock_evolution, 
            date_min, 
            date_max,
            stock_actuel
        )
        
        return {
            'data': all_movements,
            'months': months_data,
            'datasets': datasets,
            'stock_months': stock_months,
            'stock_quantities': stock_quantities,
            'stock_actuel': stock_actuel,
            'total_records': len(all_movements),
            'filtered_records': len(all_movements)
        }

    except Exception as e:
        logger.error(f"Erreur critique get_mouvements_data: {str(e)}")
        return {
            'data': [], 'months': [], 'datasets': [],
            'stock_months': [], 'stock_quantities': [], 'stock_actuel': 0.0,
            'total_records': 0, 'filtered_records': 0
        }

# =============================================================================
# ✅ ملخص المقال مع Table Croisée ديناميكية
# =============================================================================
@login_required
def api_article_summary(request, cod_art):
    """
    ملخص المقال: جدول محوري (Table Croisée)
    ✅ فصل الحركات العادية عن حركات الجرد (class_cout = 'INV')
    ✅ حركات الجرد تظهر كصفوف مستقلة مع عمود INV ثابت
    ✅ توزيع المخزون يعرض جميع nat_stock بغض النظر عن الفلاتر
    ✅ حساب Écart d'inventaire (الفرق بين المخزون المحسوب والفعلي)
    """
    if not cod_art:
        return JsonResponse({'error': 'COD_ART requis'}, status=400)
    
    # 1. استخراج الفلاتر
    date_min = request.GET.get('date_min', '')
    date_max = request.GET.get('date_max', '')
    nat_stock_filter = request.GET.get('nat_stock', '').strip()
    val_art_filter = request.GET.get('val_art', '').strip()
    classe_cout_filter = request.GET.get('classe_cout', '').strip()
    centre_cout_filter = request.GET.get('centre_cout', '').strip()
    
    try:
        # 2. جلب معلومات المقال
        with connections['sql_server'].cursor() as cursor:
            cursor.execute("SELECT COD_ART, LIB_ART FROM ARTICLE WHERE COD_ART = %s", [cod_art])
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'error': 'Article non trouvé'}, status=404)
            cod_art_db, lib_art = row[0], row[1]

        # 3. جلب قواعد التوقيع من naturebon (MySQL)
        nature_rules = {n.code_nature: n.sign for n in NatureBon.objects.all()}

        # 4. ✅ جلب المخزون الفعلي من STOCK - بدون فلاتر (للعرض الشامل)
        stock_sql = """
            SELECT VAL_ART, NAT_STOCK, SUM(QTE_SURSTK) as total_stock
            FROM STOCK 
            WHERE COD_ART = %s
            GROUP BY VAL_ART, NAT_STOCK
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(stock_sql, [cod_art_db])
            stock_rows = cursor.fetchall()
        
        # بناء قاموس المخزون الفعلي: {(val_art, nat_stock): total_stock}
        actual_stock_by_nat = {}
        for val_art, nat_stock, total_stock in stock_rows:
            actual_stock_by_nat[(val_art, nat_stock)] = float(total_stock) if total_stock else 0.0
        
        # 5. ✅ جلب عدد الأسطر لكل (cod_art, val_art) لتحديد nat_stock في حالة الجرد
        count_sql = """
            SELECT VAL_ART, COUNT(*) as cnt
            FROM STOCK
            WHERE COD_ART = %s
            GROUP BY VAL_ART
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(count_sql, [cod_art_db])
            count_rows = cursor.fetchall()
            stock_count_by_val_art = {row[0]: row[1] for row in count_rows}
        
        # بناء قاموس nat_stock الافتراضي لكل val_art
        default_nat_stock_by_val_art = {}
        for val_art, count in stock_count_by_val_art.items():
            if count == 1:
                with connections['sql_server'].cursor() as cursor:
                    cursor.execute("""
                        SELECT NAT_STOCK FROM STOCK 
                        WHERE COD_ART = %s AND VAL_ART = %s
                    """, [cod_art_db, val_art])
                    row = cursor.fetchone()
                    if row:
                        default_nat_stock_by_val_art[val_art] = row[0]
            else:
                default_nat_stock_by_val_art[val_art] = '1'
        
        # حساب الإجمالي الكلي وتوزيعه حسب nat_stock
        total_actual_stock = sum(actual_stock_by_nat.values())
        stock_distribution = {}
        for (val_art, nat_stock), qty in actual_stock_by_nat.items():
            if nat_stock not in stock_distribution:
                stock_distribution[nat_stock] = 0.0
            stock_distribution[nat_stock] += qty

        # 6. ✅ بناء شروط WHERE المشتركة للحركات
        base_conditions = [
            "e.cod_art = %s",
            "e.class_cout IS NOT NULL",
            "LTRIM(RTRIM(e.class_cout)) <> ''"
        ]
        params = [cod_art_db]

        if date_min:
            base_conditions.append("e.date_b >= %s"); params.append(date_min)
        if date_max:
            base_conditions.append("e.date_b <= %s"); params.append(date_max)
        if nat_stock_filter:
            base_conditions.append("s.nat_stock = %s"); params.append(nat_stock_filter)
        if val_art_filter:
            base_conditions.append("s.val_art = %s"); params.append(val_art_filter)
        if classe_cout_filter:
            base_conditions.append("e.class_cout = %s"); params.append(classe_cout_filter)
        if centre_cout_filter:
            base_conditions.append("e.centr_cout = %s"); params.append(centre_cout_filter)

        where_clause = " AND ".join(base_conditions)

        # 7. ✅ الاستعلام الأول: الحركات العادية (class_cout <> 'INV')
        sql_regular = f"""
            SELECT 
                e.class_cout, e.centr_cout, e.val_art, e.nature_bon,
                SUM(e.qte_mvt) as total_qte,
                c.lib_cl_c, ct.lib_centre
            FROM fiche_ebc e
            INNER JOIN STOCK s ON e.cod_art = s.COD_ART AND e.val_art = s.VAL_ART
            LEFT JOIN clascout c ON e.class_cout = c.class_cout
            LEFT JOIN centre ct ON e.centr_cout = ct.centr_cout
            WHERE {where_clause}
              AND e.class_cout <> 'INV'
            GROUP BY e.class_cout, e.centr_cout, e.val_art, e.nature_bon, c.lib_cl_c, ct.lib_centre
            ORDER BY e.class_cout, e.val_art, e.nature_bon
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql_regular, params)
            regular_movements = cursor.fetchall()

        # 8. ✅ الاستعلام الثاني: حركات الجرد (class_cout = 'INV') - بدون GROUP BY
        sql_inv = f"""
            SELECT 
                e.class_cout, e.centr_cout, e.val_art, e.nature_bon,
                e.qte_mvt,
                CONVERT(VARCHAR(10), e.date_b, 103) as date_b_str,
                e.date_b as date_b_raw,
                c.lib_cl_c, ct.lib_centre
            FROM fiche_ebc e
            INNER JOIN STOCK s ON e.cod_art = s.COD_ART AND e.val_art = s.VAL_ART
            LEFT JOIN clascout c ON e.class_cout = c.class_cout
            LEFT JOIN centre ct ON e.centr_cout = ct.centr_cout
            WHERE {where_clause}
              AND e.class_cout = 'INV'
            ORDER BY e.date_b ASC
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql_inv, params)
            inv_movements = cursor.fetchall()

        # 9. ✅ الاستعلام الثالث: جلب كل الحركات (عادية + جرد) لحساب stock_evolution
        sql_all_movements = f"""
            SELECT
                e.nature_bon,
                e.qte_mvt,
                e.date_b,
                e.class_cout
            FROM fiche_ebc e
            INNER JOIN STOCK s ON e.cod_art = s.COD_ART AND e.val_art = s.VAL_ART
            WHERE e.cod_art = %s
              AND e.class_cout IS NOT NULL
              AND LTRIM(RTRIM(e.class_cout)) <> ''
            ORDER BY e.date_b ASC
        """
        
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql_all_movements, [cod_art_db])
            all_movements_for_stock = cursor.fetchall()

        # 10. ✅ بناء stock_evolution: قاموس {date_str: stock_value}
        stock_evolution = {}
        stock_calc = 0.0
        
        for nature_bon, qte_mvt, date_b, class_cout in all_movements_for_stock:
            nature_bon_str = str(nature_bon).strip() if nature_bon else ''
            qte_mvt_float = float(qte_mvt) if qte_mvt is not None else 0.0
            class_cout_str = str(class_cout).strip() if class_cout else ''
            
            # تحويل التاريخ إلى string
            if hasattr(date_b, 'isoformat'):
                date_str = date_b.isoformat()
            else:
                date_str = str(date_b)
            
            # حفظ المخزون قبل هذه الحركة
            if date_str not in stock_evolution:
                stock_evolution[date_str] = stock_calc
            
            # تطبيق الحركة
            if class_cout_str.upper() == 'INV' or nature_bon_str.upper() == 'INV':
                # جرد: إعادة ضبط المخزون
                stock_calc = qte_mvt_float
            else:
                # حركة عادية: تطبيق sign
                sign = nature_rules.get(nature_bon_str, 0)
                stock_calc += (qte_mvt_float * sign)
        
        # دالة مساعدة: الحصول على المخزون قبل تاريخ معين (صارم <)
        def get_stock_before_date(target_date_str):
            try:
                from datetime import datetime as dt_cls
                # محاولة تحويل من صيغة dd/mm/yyyy
                try:
                    target_dt = dt_cls.strptime(target_date_str, '%d/%m/%Y').date()
                except:
                    # محاولة من صيغة yyyy-mm-dd
                    try:
                        target_dt = dt_cls.strptime(target_date_str, '%Y-%m-%d').date()
                    except:
                        return 0.0
                
                closest_date = None
                closest_stock = 0.0
                
                for d_str, s_val in stock_evolution.items():  # ✅ تم التصحيح: stock_evolution بدلاً من stock_evolution_for_inv
                    try:
                        dt = dt_cls.strptime(d_str, '%Y-%m-%d').date()
                        # ✅ صارم قبل الجرد (نستخدم < وليس <=)
                        if dt < target_dt:
                            if closest_date is None or dt > closest_date:
                                closest_date = dt
                                closest_stock = s_val
                    except:
                        continue
                
                return closest_stock
            except Exception as e:
                logger.warning(f"Erreur get_stock_before_date: {e}")
                return 0.0

        # 11. بناء الهيكل المحوري في Python
        pivot_data = {}
        all_nature_bons = set()
        val_art_map = {'1': '100%', '2': '75%', '3': '25%', '4': '0%'}

        # أ) معالجة الحركات العادية
        for class_cout, centr_cout, val_art, nature_bon, total_qte, lib_cl_c, lib_centre in regular_movements:
            class_cout = str(class_cout).strip()
            nature_bon = str(nature_bon).strip() if nature_bon else 'N/A'
            val_art = str(val_art).strip() if val_art else '0'
            safe_qty = float(total_qte) if total_qte is not None else 0.0
            
            all_nature_bons.add(nature_bon)
            key = (class_cout, val_art)
            if key not in pivot_data:
                pivot_data[key] = {
                    'class_cout': class_cout, 'lib_cl_c': lib_cl_c or class_cout,
                    'centr_cout': centr_cout, 'lib_centre': lib_centre or centr_cout,
                    'val_art': val_art, 'lib_val_art': val_art_map.get(val_art, f'{val_art}%'),
                    'nature_bons': {}, 'total_entrees': 0.0, 'total_sorties': 0.0, 
                    'stock_net': 0.0
                }
            
            sign = nature_rules.get(nature_bon, 0)
            movement_value = safe_qty * sign
            pivot_data[key]['nature_bons'][nature_bon] = pivot_data[key]['nature_bons'].get(nature_bon, 0.0) + safe_qty
            
            if movement_value > 0:
                pivot_data[key]['total_entrees'] += movement_value
            elif movement_value < 0:
                pivot_data[key]['total_sorties'] += abs(movement_value)
            
            pivot_data[key]['stock_net'] += movement_value

        # 12. ✅ معالجة حركات الجرد كصفوف مستقلة + حساب Écart
        inv_rows = []
        for class_cout, centr_cout, val_art, nature_bon, qte_mvt, date_b_str, date_b_raw, lib_cl_c, lib_centre in inv_movements:
            class_cout = str(class_cout).strip()
            val_art = str(val_art).strip() if val_art else '0'
            safe_qty = float(qte_mvt) if qte_mvt is not None else 0.0
            
            # ✅ حساب المخزون قبل الجرد والفرق
            stock_avant = get_stock_before_date(date_b_str)
            ecart = safe_qty - stock_avant
            
            # تحديد نوع الفرق
            if ecart > 0:
                ecart_type = 'surplus'
            elif ecart < 0:
                ecart_type = 'manquant'
            else:
                ecart_type = 'exact'
            
            inv_rows.append({
                'class_cout': class_cout,
                'lib_cl_c': lib_cl_c or class_cout,
                'centr_cout': centr_cout,
                'lib_centre': lib_centre or centr_cout,
                'val_art': val_art,
                'lib_val_art': val_art_map.get(val_art, f'{val_art}%'),
                'inv_qty': safe_qty,
                'stock_avant_inv': round(stock_avant, 2),
                'ecart_inv': round(ecart, 2),
                'ecart_type': ecart_type,
                'date': date_b_str
            })

        # 13. ✅ تصحيح stock_net للسطور من جدول STOCK (القيمة الفعلية)
        for key in pivot_data.keys():
            val_art = key[1]
            actual_stock_for_val_art = sum(
                qty for (va, ns), qty in actual_stock_by_nat.items() if va == val_art
            )
            pivot_data[key]['stock_net'] = actual_stock_for_val_art

        # 14. تحويل البيانات إلى قائمة مرتبة
        final_data = []
        sorted_nature_bons = sorted(list(all_nature_bons))
        
        # إضافة الحركات العادية أولاً
        for key in sorted(pivot_data.keys()):
            row_data = pivot_data[key]
            row = {
                'class_cout': row_data['class_cout'], 'lib_cl_c': row_data['lib_cl_c'],
                'centr_cout': row_data['centr_cout'], 'lib_centre': row_data['lib_centre'],
                'val_art': row_data['val_art'], 'lib_val_art': row_data['lib_val_art'],
                'is_inv_row': False
            }
            for nature_bon in sorted_nature_bons:
                row[f'nature_{nature_bon}'] = round(row_data['nature_bons'].get(nature_bon, 0.0), 2)
            
            row['total_entrees'] = round(row_data['total_entrees'], 2)
            row['total_sorties'] = round(row_data['total_sorties'], 2)
            row['stock_net'] = round(row_data['stock_net'], 2)
            row['inv_qty'] = 0.0  # الحركات العادية لا تحتوي على INV
            row['stock_avant_inv'] = 0.0
            row['ecart_inv'] = 0.0
            row['ecart_type'] = ''
            row['date'] = ''
            final_data.append(row)
        
        # إضافة صفوف حركات الجرد في النهاية (مرتبة حسب التاريخ)
        inv_rows_sorted = sorted(inv_rows, key=lambda x: x['date'])
        for inv_row in inv_rows_sorted:
            row = {
                'class_cout': inv_row['class_cout'],
                'lib_cl_c': inv_row['lib_cl_c'],
                'centr_cout': inv_row['centr_cout'],
                'lib_centre': inv_row['lib_centre'],
                'val_art': inv_row['val_art'],
                'lib_val_art': inv_row['lib_val_art'],
                'is_inv_row': True,
                'inv_qty': round(inv_row['inv_qty'], 2),
                'stock_avant_inv': inv_row.get('stock_avant_inv', 0.0),
                'ecart_inv': inv_row.get('ecart_inv', 0.0),
                'ecart_type': inv_row.get('ecart_type', 'exact'),
                'date': inv_row['date']
            }
            # الأعمدة الديناميكية فارغة لحركات الجرد
            for nature_bon in sorted_nature_bons:
                row[f'nature_{nature_bon}'] = 0.0
            row['total_entrees'] = 0.0
            row['total_sorties'] = 0.0
            row['stock_net'] = round(inv_row['inv_qty'], 2)
            final_data.append(row)

        # 15. حساب الإجماليات العامة
        grand_total = {
            'total_entrees': round(sum(r['total_entrees'] for r in final_data if not r.get('is_inv_row')), 2),
            'total_sorties': round(sum(r['total_sorties'] for r in final_data if not r.get('is_inv_row')), 2),
            'stock_net': round(total_actual_stock, 2),
            'stock_distribution': {k: round(v, 2) for k, v in stock_distribution.items()},
            'nature_totals': {},
            'total_ecart_surplus': round(sum(r.get('ecart_inv', 0.0) for r in final_data if r.get('is_inv_row') and r.get('ecart_inv', 0.0) > 0), 2),
            'total_ecart_manquant': round(sum(abs(r.get('ecart_inv', 0.0)) for r in final_data if r.get('is_inv_row') and r.get('ecart_inv', 0.0) < 0), 2),
            'total_inv_count': sum(1 for r in final_data if r.get('is_inv_row'))
        }
        
        for nature_bon in sorted_nature_bons:
            grand_total['nature_totals'][f'nature_{nature_bon}'] = round(
                sum(r.get(f'nature_{nature_bon}', 0.0) for r in final_data if not r.get('is_inv_row')), 2
            )

        return JsonResponse({
            'cod_art': cod_art_db,
            'lib_art': lib_art,
            'columns': sorted_nature_bons,
            'data': final_data,
            'grand_total': grand_total,
            'actual_stock': round(total_actual_stock, 2)
        })

    except Exception as e:
        logger.error(f"Erreur dans api_article_summary: {e}", exc_info=True)
        return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)

# =============================================================================
# ✅ دوال جديدة: إحصائيات عامة (بدون فلتر cod_art)
# =============================================================================
@login_required
def get_entrees_generales_data(cursor, nat_stock, val_art, date_min, date_max,
                                centre_cout=None, classe_cout=None,
                                search_value=None, order_column_index=None, order_dir='asc'):
    from core.models import NatureStock
    where_clauses = ["e1.date_b >= %s", "e1.date_b <= %s"]
    params = [date_min, date_max]
    if nat_stock: where_clauses.append("e1.nat_stock = %s"); params.append(nat_stock)
    if val_art: where_clauses.append("e1.val_art = %s"); params.append(val_art)
    if centre_cout: where_clauses.append("e1.centr_cout = %s"); params.append(centre_cout)
    if classe_cout: where_clauses.append("e1.class_cout = %s"); params.append(classe_cout)
    where_sql = " AND ".join(where_clauses)
    search_clause, search_params = "", []
    if search_value:
        conditions = ["e1.numero_bon LIKE %s", "e1.lib_art LIKE %s", "e1.doc_ref LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    order_clause = "ORDER BY e1.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'e1.date_b', '2': 'e1.numero_bon', '3': 'e1.lib_art', '4': 'e1.qte_mvt', '5': 'e1.valeur_tot', '6': 'e1.doc_ref'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"SELECT 'Entrée' AS type, e1.date_b, e1.numero_bon, e1.lib_art, e1.qte_mvt, e1.lib_um, e1.nat_stock, e1.class_cout, e1.centr_cout, e1.valeur_tot, e1.doc_ref, 'Entrée' AS sens FROM Etat_b1 e1 WHERE {full_where} {order_clause};", full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e: logger.warning(f"Erreur chargement nature_stock: {e}")
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = row.get('class_cout') or '—'
            enriched['lib_centre'] = row.get('centr_cout') or '—'
            data.append(enriched)
    except Exception as e: logger.error(f"Erreur données entrees_generales: {str(e)}"); data = []
    months_data, quantities_data, total_valeur = [], [], 0.0
    if date_min and date_max:
        try:
            cursor.execute(f"SELECT COALESCE(SUM(e1.valeur_tot), 0) FROM Etat_b1 e1 WHERE {where_sql}", params)
            total_valeur = float(cursor.fetchone()[0] or 0)
            cursor.execute(f"SELECT YEAR(e1.date_b) AS yr, MONTH(e1.date_b) AS mth, SUM(e1.valeur_tot) AS total FROM Etat_b1 e1 WHERE {where_sql} GROUP BY YEAR(e1.date_b), MONTH(e1.date_b) ORDER BY yr, mth;", params)
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e: logger.error(f"Erreur graphique entrees_generales: {str(e)}"); months_data, quantities_data = ['Erreur'], [0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b1 e1 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b1 e1 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except: total_records = filtered_records = len(data)
    return {'data': data, 'months': months_data, 'quantities': quantities_data, 'total_valeur': total_valeur, 'total_records': total_records, 'filtered_records': filtered_records}

@login_required
def get_sorties_generales_data(cursor, nat_stock, val_art, date_min, date_max,
                                centre_cout=None, classe_cout=None,
                                search_value=None, order_column_index=None, order_dir='asc'):
    from core.models import NatureStock
    where_clauses = ["f.date_b >= %s", "f.date_b <= %s", "f.nature_bon LIKE 'b2'"]
    params = [date_min, date_max]
    if nat_stock: where_clauses.append("f.nat_stock = %s"); params.append(nat_stock)
    if val_art: where_clauses.append("f.val_art = %s"); params.append(val_art)
    if centre_cout: where_clauses.append("f.centr_cout = %s"); params.append(centre_cout)
    if classe_cout: where_clauses.append("f.class_cout = %s"); params.append(classe_cout)
    where_sql = " AND ".join(where_clauses)
    search_clause, search_params = "", []
    if search_value:
        conditions = ["f.num LIKE %s", "a.LIB_ART LIKE %s", "ct.lib_centre LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    order_clause = "ORDER BY f.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'f.date_b', '2': 'f.num', '3': 'a.LIB_ART', '4': 'f.qte_mvt', '5': 'u.LIB_UM', '6': 'cc.lib_cl_c', '7': 'ct.lib_centre', '8': 'PU', '9': 'extra'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            if col_name == 'PU': order_clause = f"ORDER BY (COALESCE(s.PUMP, 0) / 1000.0) {'ASC' if order_dir == 'asc' else 'DESC'}"
            elif col_name == 'extra': order_clause = f"ORDER BY ((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt) {'ASC' if order_dir == 'asc' else 'DESC'}"
            else:
                order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
                order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"""
            SELECT 'Sortie' AS type, f.date_b, f.num AS numero_bon, a.LIB_ART AS lib_art, f.qte_mvt, u.LIB_UM AS unite, f.nat_stock, f.class_cout, cc.lib_cl_c, f.centr_cout, ct.lib_centre, COALESCE(s.PUMP, 0) / 1000.0 AS PU, (COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt AS extra, 'Sortie' AS sens, b2.ref_doc AS ref_document
            FROM fiche_ebc f INNER JOIN ARTICLE a ON f.cod_art = a.COD_ART
            LEFT JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
            LEFT JOIN clascout cc ON f.class_cout = cc.class_cout
            LEFT JOIN centre ct ON f.centr_cout = ct.centr_cout
            LEFT JOIN STOCK s ON f.cod_art = s.COD_ART AND f.val_art = s.VAL_ART
            LEFT JOIN Bon_b2_ebc b2 ON f.cod_art = b2.cod_art AND f.num = b2.numero_bon AND f.date_b = b2.date_b
            WHERE {full_where} {order_clause};
        """, full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e: logger.warning(f"Erreur chargement nature_stock: {e}")
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = enriched.get('lib_cl_c') or '—'
            enriched['lib_centre'] = enriched.get('lib_centre') or '—'
            enriched['unite'] = enriched.get('unite') or '—'
            data.append(enriched)
    except Exception as e: logger.error(f"Erreur données sorties_generales: {str(e)}"); data = []
    months_data, quantities_data, total_valeur_sorties = [], [], 0.0
    if date_min and date_max:
        try:
            cursor.execute(f"SELECT COALESCE(SUM((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt), 0) FROM fiche_ebc f LEFT JOIN STOCK s ON f.cod_art = s.COD_ART AND f.val_art = s.VAL_ART WHERE {where_sql}", params)
            total_valeur_sorties = float(cursor.fetchone()[0] or 0)
            cursor.execute(f"SELECT YEAR(f.date_b) AS yr, MONTH(f.date_b) AS mth, SUM((COALESCE(s.PUMP, 0) / 1000.0) * f.qte_mvt) AS total FROM fiche_ebc f LEFT JOIN STOCK s ON f.cod_art = s.COD_ART AND f.val_art = s.VAL_ART WHERE {where_sql} GROUP BY YEAR(f.date_b), MONTH(f.date_b) ORDER BY yr, mth;", params)
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e: logger.error(f"Erreur graphique sorties_generales: {str(e)}"); months_data, quantities_data = ['Erreur'], [0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM fiche_ebc f INNER JOIN ARTICLE a ON f.cod_art = a.COD_ART WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM fiche_ebc f INNER JOIN ARTICLE a ON f.cod_art = a.COD_ART WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except: total_records = filtered_records = len(data)
    return {'data': data, 'months': months_data, 'quantities': quantities_data, 'total_valeur_sorties': total_valeur_sorties, 'total_records': total_records, 'filtered_records': filtered_records}

@login_required
def get_retours_generales_data(cursor, nat_stock, val_art, date_min, date_max,
                                centre_cout=None, classe_cout=None,
                                search_value=None, order_column_index=None, order_dir='asc'):
    from core.models import NatureStock
    where_clauses = ["e3.date_b >= %s", "e3.date_b <= %s"]
    params = [date_min, date_max]
    if nat_stock: where_clauses.append("e3.nat_stock = %s"); params.append(nat_stock)
    if val_art: where_clauses.append("e3.val_art = %s"); params.append(val_art)
    if centre_cout: where_clauses.append("e3.centr_cout = %s"); params.append(centre_cout)
    if classe_cout: where_clauses.append("e3.class_cout = %s"); params.append(classe_cout)
    where_sql = " AND ".join(where_clauses)
    search_clause, search_params = "", []
    if search_value:
        conditions = ["e3.numero_bon LIKE %s", "e3.lib_art LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    order_clause = "ORDER BY e3.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'e3.date_b', '2': 'e3.numero_bon', '3': 'e3.lib_art', '4': 'e3.qte_mvt', '5': 'e3.nat_stock'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"SELECT 'Retour' AS type, e3.date_b, e3.numero_bon, e3.lib_art, e3.qte_mvt, e3.lib_um, e3.nat_stock, e3.class_cout, e3.centr_cout, 'Entrée' AS sens FROM Etat_b3 e3 WHERE {full_where} {order_clause};", full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e: logger.warning(f"Erreur chargement nature_stock: {e}")
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = row.get('class_cout') or '—'
            enriched['lib_centre'] = row.get('centr_cout') or '—'
            data.append(enriched)
    except Exception as e: logger.error(f"Erreur données retours_generales: {str(e)}"); data = []
    months_data, quantities_data = [], []
    if date_min and date_max:
        try:
            cursor.execute(f"SELECT YEAR(e3.date_b) AS yr, MONTH(e3.date_b) AS mth, SUM(e3.qte_mvt) AS total FROM Etat_b3 e3 WHERE {where_sql} GROUP BY YEAR(e3.date_b), MONTH(e3.date_b) ORDER BY yr, mth;", params)
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e: logger.error(f"Erreur graphique retours_generales: {str(e)}"); months_data, quantities_data = ['Erreur'], [0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b3 e3 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b3 e3 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except: total_records = filtered_records = len(data)
    return {'data': data, 'months': months_data, 'quantities': quantities_data, 'total_records': total_records, 'filtered_records': filtered_records}

@login_required
def get_prestations_generales_data(cursor, nat_stock, val_art, date_min, date_max,
                                    centre_cout=None, classe_cout=None,
                                    search_value=None, order_column_index=None, order_dir='asc'):
    from core.models import NatureStock
    where_clauses = ["e4.date_b >= %s", "e4.date_b <= %s"]
    params = [date_min, date_max]
    if nat_stock: where_clauses.append("e4.nat_stock = %s"); params.append(nat_stock)
    if val_art: where_clauses.append("e4.val_art = %s"); params.append(val_art)
    if centre_cout: where_clauses.append("e4.centr_cout = %s"); params.append(centre_cout)
    if classe_cout: where_clauses.append("e4.class_cout = %s"); params.append(classe_cout)
    where_sql = " AND ".join(where_clauses)
    search_clause, search_params = "", []
    if search_value:
        conditions = ["e4.numero_bon LIKE %s", "e4.lib_art LIKE %s"]
        search_params = [f"%{search_value}%"] * len(conditions)
        search_clause = " AND (" + " OR ".join(conditions) + ")"
    order_clause = "ORDER BY e4.date_b DESC"
    if order_column_index and order_column_index.isdigit():
        columns_map = {'1': 'e4.date_b', '2': 'e4.numero_bon', '3': 'e4.lib_art', '4': 'e4.qte_mvt', '5': 'e4.nat_stock'}
        if order_column_index in columns_map:
            col_name = columns_map[order_column_index]
            order_dir_sql = 'ASC' if order_dir == 'asc' else 'DESC'
            order_clause = f"ORDER BY {col_name} {order_dir_sql}"
    try:
        full_where = where_sql + search_clause
        full_params = params + search_params
        cursor.execute(f"SELECT 'Prestation' AS type, e4.date_b, e4.numero_bon, e4.lib_art, e4.qte_mvt, e4.lib_um, e4.nat_stock, e4.class_cout, e4.centr_cout, 'Sortie' AS sens FROM Etat_b4 e4 WHERE {full_where} {order_clause};", full_params)
        columns = [col[0] for col in cursor.description]
        raw_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        nat_codes = list(set(row.get('nat_stock') for row in raw_data if row.get('nat_stock')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e: logger.warning(f"Erreur chargement nature_stock: {e}")
        data = []
        for row in raw_data:
            enriched = row.copy()
            nat_code = row.get('nat_stock')
            enriched['libelle_nature'] = nature_labels.get(nat_code, nat_code or '—')
            enriched['lib_cl_c'] = row.get('class_cout') or '—'
            enriched['lib_centre'] = row.get('centr_cout') or '—'
            data.append(enriched)
    except Exception as e: logger.error(f"Erreur données prestations_generales: {str(e)}"); data = []
    months_data, quantities_data = [], []
    if date_min and date_max:
        try:
            cursor.execute(f"SELECT YEAR(e4.date_b) AS yr, MONTH(e4.date_b) AS mth, SUM(e4.qte_mvt) AS total FROM Etat_b4 e4 WHERE {where_sql} GROUP BY YEAR(e4.date_b), MONTH(e4.date_b) ORDER BY yr, mth;", params)
            rows = cursor.fetchall()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            start_date = datetime.strptime(date_min, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_max, '%Y-%m-%d').date()
            current = start_date.replace(day=1)
            data_dict = {(row[0], row[1]): float(row[2]) for row in rows}
            while current <= end_date:
                key = (current.year, current.month)
                months_data.append(f"{month_names[current.month-1]} {str(current.year)[-2:]}")
                quantities_data.append(data_dict.get(key, 0.0))
                current = current.replace(month=current.month + 1) if current.month < 12 else current.replace(year=current.year+1, month=1)
        except Exception as e: logger.error(f"Erreur graphique prestations_generales: {str(e)}"); months_data, quantities_data = ['Erreur'], [0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b4 e4 WHERE {where_sql}", params)
        total_records = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM Etat_b4 e4 WHERE {full_where}", full_params)
        filtered_records = cursor.fetchone()[0]
    except: total_records = filtered_records = len(data)
    return {'data': data, 'months': months_data, 'quantities': quantities_data, 'total_records': total_records, 'filtered_records': filtered_records}


        
# =============================================================================
# ✅ تصدير إلى Excel
# =============================================================================
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
        table_data, columns, chart_data, chart_months, query_params, where_sql = [], [], [], [], [], ""
        with connections['sql_server'].cursor() as cursor:
            if tab == 'achat' and cod_art:
                query = """SELECT e1.doc_ref, e1.date_b, e1.numero_bon, a.LIB_ART, e1.qte_mvt, CASE WHEN e1.qte_mvt > 0 THEN CAST(e1.valeur_tot AS FLOAT) / e1.qte_mvt ELSE 0 END AS PU FROM Etat_b1 e1 INNER JOIN ARTICLE a ON e1.cod_art = a.COD_ART WHERE a.COD_ART = %s ORDER BY e1.date_b DESC"""
                cursor.execute(query, [cod_art])
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()
            elif tab == 'entrees':
                where_clauses = ["e1.date_b >= %s", "e1.date_b <= %s"]
                query_params = [date_min, date_max]
                where_sql = " AND ".join(where_clauses)
                query = f"SELECT e1.date_b, e1.numero_bon, e1.lib_art, e1.qte_mvt, e1.valeur_tot FROM Etat_b1 e1 WHERE {where_sql} ORDER BY e1.date_b DESC"
                cursor.execute(query, query_params)
                columns = [col[0] for col in cursor.description]
                table_data = cursor.fetchall()
        wb = Workbook()
        ws = wb.active
        ws.title = tab.capitalize() if tab else 'Statistiques'
        ws.merge_cells('A1:F1')
        ws['A1'] = f"Statistiques - {tab.capitalize() if tab else 'Export'} ({date_min} au {date_max})"
        ws['A1'].font = Font(size=16, bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
        if columns and table_data:
            column_mapping = {'date_b': 'Date', 'numero_bon': 'N° Bon', 'lib_art': 'Libellé', 'qte_mvt': 'Quantité', 'PU': 'Prix Unitaire (TND)', 'valeur_tot': 'Valeur Totale (TND)'}
            headers = [column_mapping.get(col, col) for col in columns]
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=3, column=col_num, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
                cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
            for row_num, row_data in enumerate(table_data, 4):
                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num, value=value)
                    cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
                    if columns[col_num-1] == 'date_b' and value: cell.number_format = 'dd/mm/yyyy'
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Statistiques_{tab or "export"}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        return response
    except Exception as e:
        logger.error(f"Erreur export Excel: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# =============================================================================
# ✅ تصدير نتائج البحث والفلترة إلى Excel
# =============================================================================
@login_required
def export_articles_excel(request):
    """
    تصدير نتائج البحث والفلترة من قائمة المقالات إلى ملف Excel.
    يستخدم نفس منطق الفلترة الموجود في api_articles_data.
    """
    try:
        # --- استخراج الفلاتر ---
        cod_art = request.GET.get('cod_art', '').strip()
        lib_art = request.GET.get('lib_art', '').strip()
        class_cout = request.GET.get('class_cout', '').strip()
        lib_um = request.GET.get('lib_um', '').strip()
        empl = request.GET.get('empl', '').strip()
        qte_min = request.GET.get('qte_min', '').strip()
        qte_max = request.GET.get('qte_max', '').strip()
        pu_min = request.GET.get('pu_min', '').strip()
        pu_max = request.GET.get('pu_max', '').strip()
        val_art = request.GET.get('val_art', '').strip()
        nat_stock = request.GET.get('nat_stock', '').strip()

        # --- بناء SQL ---
        sql = """
            SELECT
                a.COD_ART, a.LIB_ART, a.CLASS_COUT, a.DATE_CREAT, a.DERNIER_MV,
                a.EMPL, s.PUMP, u.LIB_UM, s.QTE_STOCK, s.QTE_SURSTK, s.VAL_ART,
                s.NAT_STOCK, s.QTE_SURSTK * s.PUMP / 1000 AS VALEUR, a.DESIGNAT
            FROM ARTICLE a
            INNER JOIN STOCK s ON a.COD_ART = s.COD_ART
            INNER JOIN T_UNITES u ON a.UNITE_MES = u.UNITE_MES
            WHERE 1 = 1
        """
        conditions = []
        values = []

        def clean_like(value):
            if not value:
                return None
            clean = value.replace('%', '').replace('_', '').replace('[', '').replace(']', '')
            return f'%{clean}%'

        if cod_art:
            for part in re.split(r'\s+', cod_art):
                if part:
                    conditions.append("a.COD_ART LIKE %s")
                    values.append(clean_like(part))

        if lib_art:
            for kw in re.split(r'\s+', lib_art.strip()):
                if kw:
                    conditions.append("a.LIB_ART LIKE %s")
                    values.append(clean_like(kw))

        if class_cout:
            conditions.append("a.CLASS_COUT = %s")
            values.append(class_cout)

        if lib_um:
            conditions.append("u.LIB_UM = %s")
            values.append(lib_um)

        if empl:
            conditions.append("a.EMPL LIKE %s")
            values.append(clean_like(empl))

        if qte_min and qte_min.replace('.', '', 1).isdigit():
            conditions.append("s.QTE_SURSTK >= %s")
            values.append(float(qte_min))

        if qte_max and qte_max.replace('.', '', 1).isdigit():
            conditions.append("s.QTE_SURSTK <= %s")
            values.append(float(qte_max))

        if pu_min and pu_min.replace('.', '', 1).isdigit():
            conditions.append("s.PUMP >= %s")
            values.append(str(float(pu_min) * 1000))

        if pu_max and pu_max.replace('.', '', 1).isdigit():
            conditions.append("s.PUMP <= %s")
            values.append(str(float(pu_max) * 1000))

        if val_art in ['1', '2', '3', '4']:
            conditions.append("s.VAL_ART = %s")
            values.append(val_art)

        if nat_stock:
            conditions.append("s.NAT_STOCK = %s")
            values.append(nat_stock)

        if conditions:
            sql += " AND " + " AND ".join(conditions)

        sql += " ORDER BY a.CLASS_COUT, a.COD_ART"

        # --- جلب البيانات ---
        rows = []
        with connections['sql_server'].cursor() as cursor:
            cursor.execute(sql, values)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                data['PU'] = round(data['PUMP'] / 1000, 3) if data['PUMP'] else 0
                rows.append(data)

        # --- إثراء بـ libelle_nature ---
        nat_codes = list(set(item.get('NAT_STOCK') for item in rows if item.get('NAT_STOCK')))
        nature_labels = {}
        if nat_codes:
            try:
                nature_qs = NatureStock.objects.filter(code_nature__in=nat_codes).only('code_nature', 'libelle_nature')
                nature_labels = {n.code_nature: n.libelle_nature for n in nature_qs}
            except Exception as e:
                logger.warning(f"Erreur chargement nature_stock: {e}")

        for item in rows:
            item['libelle_nature'] = nature_labels.get(item.get('NAT_STOCK'), item.get('NAT_STOCK') or '—')

        # ==========================================
        # ✅ إنشاء ملف Excel
        # ==========================================
        wb = Workbook()
        ws = wb.active
        ws.title = "Articles"

        # --- العنوان ---
        ws.merge_cells('A1:N1')
        ws['A1'] = "Liste des Articles - Pétro Dashboard"
        ws['A1'].font = Font(size=16, bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 30

        # --- معلومات الفلترة ---
        ws.merge_cells('A2:N2')
        filters_info = []
        if cod_art: filters_info.append(f"Code: {cod_art}")
        if lib_art: filters_info.append(f"Libellé: {lib_art}")
        if class_cout: filters_info.append(f"Classe: {class_cout}")
        if lib_um: filters_info.append(f"Unité: {lib_um}")
        if empl: filters_info.append(f"Emplacement: {empl}")
        if qte_min or qte_max: filters_info.append(f"Qté: {qte_min or '0'} → {qte_max or '∞'}")
        if pu_min or pu_max: filters_info.append(f"PU: {pu_min or '0'} → {pu_max or '∞'}")
        if val_art: filters_info.append(f"VAL_ART: {val_art}")
        if nat_stock: filters_info.append(f"Nature: {nat_stock}")
        filters_text = " | ".join(filters_info) if filters_info else "Aucun filtre appliqué"

        ws['A2'] = f"Filtres: {filters_text}"
        ws['A2'].font = Font(size=10, italic=True, color="34495E")

        ws.merge_cells('A3:N3')
        ws['A3'] = f"Date d'export: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Total: {len(rows)} article(s)"
        ws['A3'].font = Font(size=10, italic=True, color="34495E")

        # --- رؤوس الأعمدة ---
        headers = [
            ('Code Article', 15),
            ('Libellé', 35),
            ('Désignation', 40),
            ('Classe Coût', 12),
            ('Emplacement', 12),
            ('Unité', 10),
            ('PU (TND)', 12),
            ('Qté Stock', 12),
            ('Qté Surstock', 14),
            ('Valeur (TND)', 15),
            ('VAL_ART', 10),
            ('Nature Stock', 18),
            ('Date Création', 14),
            ('Dernier MV', 14),
        ]

        header_row = 5
        for col_num, (header, width) in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF", size=11)
            cell.fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin')
            )
            ws.column_dimensions[get_column_letter(col_num)].width = width
        ws.row_dimensions[header_row].height = 25

        # --- تعبئة البيانات ---
        val_art_map = {'1': '100%', '2': '75%', '3': '25%', '4': '0%'}

        for row_num, item in enumerate(rows, header_row + 1):
            row_data = [
                item.get('COD_ART', ''),
                item.get('LIB_ART', ''),
                item.get('DESIGNAT', ''),
                item.get('CLASS_COUT', ''),
                item.get('EMPL', ''),
                item.get('LIB_UM', ''),
                item.get('PU', 0),
                float(item.get('QTE_STOCK') or 0),
                float(item.get('QTE_SURSTK') or 0),
                float(item.get('VALEUR') or 0),
                val_art_map.get(str(item.get('VAL_ART', '')), str(item.get('VAL_ART', ''))),
                item.get('libelle_nature', '—'),
                item.get('DATE_CREAT'),
                item.get('DERNIER_MV'),
            ]

            for col_num, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                cell.border = Border(
                    left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin')
                )
                cell.alignment = Alignment(vertical="center")

                if col_num in [13, 14] and value:
                    if hasattr(value, 'strftime'):
                        cell.number_format = 'dd/mm/yyyy'
                    else:
                        cell.value = str(value)
                elif col_num in [7, 8, 9, 10]:
                    cell.number_format = '#,##0.000'
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                elif col_num == 11:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    if value == '100%':
                        cell.fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
                        cell.font = Font(bold=True, color="155724")
                    elif value == '75%':
                        cell.fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
                        cell.font = Font(bold=True, color="004085")
                    elif value == '25%':
                        cell.fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
                        cell.font = Font(bold=True, color="856404")
                    elif value == '0%':
                        cell.fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
                        cell.font = Font(bold=True, color="721C24")
                elif col_num in [1, 2, 3]:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            if row_num % 2 == 0:
                for col_num in range(1, len(headers) + 1):
                    if col_num != 11:
                        ws.cell(row=row_num, column=col_num).fill = PatternFill(
                            start_color="F8F9FA", end_color="F8F9FA", fill_type="solid"
                        )

        # --- صف الإجماليات ---
        if rows:
            total_row = header_row + len(rows) + 1
            ws.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True, size=11)

            total_qte_stock = sum(float(item.get('QTE_STOCK') or 0) for item in rows)
            total_qte_surstk = sum(float(item.get('QTE_SURSTK') or 0) for item in rows)
            total_valeur = sum(float(item.get('VALEUR') or 0) for item in rows)

            for col, val in [(8, total_qte_stock), (9, total_qte_surstk), (10, total_valeur)]:
                c = ws.cell(row=total_row, column=col, value=val)
                c.number_format = '#,##0.000'
                c.font = Font(bold=True, color="155724" if col == 10 else "000000")
                c.alignment = Alignment(horizontal="right")

            for col_num in range(1, len(headers) + 1):
                c = ws.cell(row=total_row, column=col_num)
                c.fill = PatternFill(start_color="D5DBDB", end_color="D5DBDB", fill_type="solid")
                c.border = Border(
                    left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='medium'), bottom=Side(style='medium')
                )

        # --- تجميد + فلتر ---
        ws.freeze_panes = 'A6'
        ws.auto_filter.ref = f"A{header_row}:N{header_row + len(rows)}"

        # --- إرجاع الملف ---
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        filename = f"Articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Erreur export_articles_excel: {str(e)}", exc_info=True)
        messages.error(request, f"Erreur lors de l'export: {str(e)}")
        return redirect('articles:list')