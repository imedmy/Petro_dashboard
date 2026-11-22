# apps/dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from datetime import date
import sys
import traceback

from core.models import Page, PermissionMatrix, SuiviDossier


@login_required
def dashboard_view(request):
    """
    لوحة التحكم الرئيسية: تعرض الإحصائيات والدوسيهات المتأخرة
    """
    try:
        # === 1. تحميل قائمة القوائم الجانبية ===
        menu_items = []
        pages = Page.objects.filter(is_active=True).order_by('order')
        
        for page in pages:
            perm, created = PermissionMatrix.objects.get_or_create(
                user=request.user,
                page=page,
                defaults={
                    'can_consulte': False,
                    'can_insert': False,
                    'can_update': False,
                    'can_delete': False
                }
            )
            if perm.can_consulte:
                menu_items.append({
                    'page': page,
                    'perm': perm
                })
        
        # === 2. جلب الطلبات المتأخرة (Instance أو Litige) ===
        last_dates = (
            SuiviDossier.objects
            .filter(influence_sur_dossier__in=['instance', 'litige'])
            .values('numero_com')
            .annotate(last_date=Max('date_etape'))
        )
        
        commandes_en_retard = []
        
        for item in last_dates:
            suivi = SuiviDossier.objects.filter(
                numero_com=item['numero_com'],
                date_etape=item['last_date'],
                influence_sur_dossier__in=['instance', 'litige']
            ).first()
            
            if suivi:
                today = date.today()
                years = today.year - suivi.date_etape.year
                months = today.month - suivi.date_etape.month
                days = today.day - suivi.date_etape.day
                
                if days < 0:
                    months -= 1
                    if today.month == 1:
                        prev_month_days = (date(today.year - 1, 12, 1) - date(today.year - 1, 11, 1)).days
                    else:
                        prev_month_days = (date(today.year, today.month - 1, 1) - date(today.year, today.month - 2, 1)).days
                    days += prev_month_days
                
                if months < 0:
                    years -= 1
                    months += 12
                
                # تحديد لون الحالة
                if years > 0 or months >= 6:
                    color_class = 'table-danger'
                elif months >= 2:
                    color_class = 'table-warning'
                else:
                    color_class = 'table-info'
                
                commandes_en_retard.append({
                    'numero_com': suivi.numero_com,
                    'dat_com': suivi.dat_com,
                    'influence': suivi.get_influence_sur_dossier_display(),
                    'date_etape': suivi.date_etape,
                    'duree_texte': f"{years} ans, {months} mois, {days} jours" if years > 0 else f"{months} mois, {days} jours",
                    'color_class': color_class,
                })
        
        # === 3. إعادة التحويل مع جميع المتغيرات ===
        return render(request, 'dashboard/dashboard.html', {
            'menu_items': menu_items,
            'title': 'Tableau de bord',
            'commandes_en_retard': commandes_en_retard,
        })
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f"""
            <h1>Erreur Interne</h1>
            <p><strong>Type:</strong> {exc_type.__name__}</p>
            <p><strong>Message:</strong> {str(e)}</p>
            <pre>{trace}</pre>
        """)