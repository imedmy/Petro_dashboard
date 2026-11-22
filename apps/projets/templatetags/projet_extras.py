# apps/projets/templatetags/projet_extras.py
from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal, InvalidOperation

register = template.Library()


# ============================================================
# SECTION 1: FILTERS - BADGES & COLORS
# ============================================================

@register.filter(name='stat_badge')
def stat_badge(statut):
    """
    إرجاع لون Bootstrap badge حسب الحالة
    الاستخدام: {{ projet.statut|stat_badge }}
    """
    mapping = {
        # Statuts Projet
        'PLANIFIE': 'secondary',
        'EN_COURS': 'success',
        'SUSPENDU': 'warning',
        'ACHEVE': 'info',
        'RESILIE': 'danger',
        # Statuts Lot/Ouvrage
        'NON_COMMENCE': 'secondary',
        # Statuts Tâche
        'A_FAIRE': 'secondary',
        'EN_REVIEW': 'primary',
        'BLOQUEE': 'danger',
        'TERMINEE': 'success',
        'ANNULEE': 'dark',
        # Statuts Décompte
        'PREPARE': 'secondary',
        'SOUMIS': 'primary',
        'VALIDE': 'info',
        'PAYE': 'success',
        'REJETE': 'danger',
        # Statuts Avenant
        'EN_PREPARATION': 'secondary',
        'SIGNE': 'primary',
        'APPROUVE': 'success',
        # Statuts Facture Extra
        'BROUILLON': 'secondary',
        'SOUMISE': 'primary',
        'APPROUVEE': 'success',
        'PAYEE': 'info',
        # Statuts Garantie
        'ACTIVE': 'success',
        'MAINLEVEE': 'info',
        'UTILISEE': 'warning',
        'EXPIREE': 'dark',
        # Statuts GED
        'BROUILLON': 'warning',
        'VALIDE': 'success',
        'ARCHIVE': 'info',
        'OBSOLETE': 'secondary',
        # Statuts Livrable
        'LIVRE': 'success',
        'REFUSE': 'danger',
        # Statuts Workflow
        'TERMINE': 'success',
    }
    return mapping.get(statut, 'secondary')


@register.filter(name='stat_label')
def stat_label(statut):
    """
    إرجاع نص الحالة بالفرنسية
    الاستخدام: {{ projet.statut|stat_label }}
    """
    mapping = {
       'PLANIFIE': 'Planifié',
        'EN_COURS': 'En cours',
        'SUSPENDU': 'Suspendu',
        'ACHEVE': 'Achevé',
        'RESILIE': 'Résilié',
        'NON_COMMENCE': 'Non commencé',
        'A_FAIRE': 'À faire',
        'EN_REVIEW': 'En révision',
        'BLOQUEE': 'Bloquée',
        'TERMINEE': 'Terminée',
        'ANNULEE': 'Annulée',
        'PREPARE': 'Préparé',
        'SOUMIS': 'Soumis',
        'VALIDE': 'Validé',
        'PAYE': 'Payé',
        'REJETE': 'Rejeté',
        'EN_PREPARATION': 'En préparation',
        'SIGNE': 'Signé',
        'APPROUVE': 'Approuvé',
        'ACTIVE': 'Active',
        'MAINLEVEE': 'Mainlevée',
        'UTILISEE': 'Utilisée',
        'EXPIREE': 'Expirée',
    }
    return mapping.get(statut, statut)


@register.filter(name='priorite_badge')
def priorite_badge(priorite):
    """
    إرجاع لون Bootstrap badge حسب الأولوية
    الاستخدام: {{ projet.priorite|priorite_badge }}
    """
    mapping = {
        'BASSE': 'secondary',
        'MOYENNE': 'info',
        'HAUTE': 'warning',
        'CRITIQUE': 'danger',
        'URGENTE': 'danger',
    }
    return mapping.get(priorite, 'secondary')


@register.filter(name='priorite_icon')
def priorite_icon(priorite):
    """
    إرجاع أيقونة Bootstrap حسب الأولوية
    الاستخدام: {{ projet.priorite|priorite_icon }}
    """
    mapping = {
        'BASSE': 'bi-arrow-down-circle',
        'MOYENNE': 'bi-dash-circle',
        'HAUTE': 'bi-arrow-up-circle',
        'CRITIQUE': 'bi-exclamation-triangle-fill',
        'URGENTE': 'bi-exclamation-octagon-fill',
    }
    return mapping.get(priorite, 'bi-dash-circle')


# ============================================================
# SECTION 2: FILTERS - FORMATAGE DES MONTANTS
# ============================================================

@register.filter(name='format_montant')
def format_montant(value):
    """
    تنسيق المبلغ بفواصل الآلاف و 3 أرقام عشرية
    الاستخدام: {{ projet.montant_final|format_montant }}
    الناتج: 1 234 567,890
    """
    try:
        if value is None:
            return '0,000'
        value = Decimal(str(value))
        # تنسيق بالفرنسية (فاصلة بدلاً من نقطة)
        formatted = f"{value:,.3f}".replace(',', ' ').replace('.', ',')
        # استبدال الفاصلة العشرية
        parts = formatted.split(' ')
        if len(parts) > 1:
            last = parts[-1]
            if ',' in last:
                parts[-1] = last.replace(',', '.')
                return ' '.join(parts[:-1]) + ',' + parts[-1].split('.')[-1]
        return f"{value:,.3f}".replace(',', 'X').replace('.', ',').replace('X', ' ')
    except (InvalidOperation, ValueError, TypeError):
        return value


@register.filter(name='format_montant_simple')
def format_montant_simple(value):
    """
    تنسيق مبسط للمبلغ (بدون آلاف)
    الاستخدام: {{ montant|format_montant_simple }}
    الناتج: 1234,567
    """
    try:
        if value is None:
            return '0,000'
        value = Decimal(str(value))
        return f"{value:.3f}".replace('.', ',')
    except (InvalidOperation, ValueError, TypeError):
        return value


@register.filter(name='format_devise')
def format_devise(value, devise='TND'):
    """
    تنسيق المبلغ مع العملة
    الاستخدام: {{ montant|format_devise:"TND" }}
    الناتج: 1 234,567 TND
    """
    try:
        if value is None:
            return f"0,000 {devise}"
        formatted = format_montant(value)
        return f"{formatted} {devise}"
    except Exception:
        return f"{value} {devise}"


# ============================================================
# SECTION 3: FILTERS - PROGRESS & AVANCEMENT
# ============================================================

@register.filter(name='progress_color')
def progress_color(pourcentage):
    """
    إرجاع لون progress bar حسب النسبة
    الاستخدام: {{ projet.pourcentage_avancement|progress_color }}
    """
    try:
        value = float(pourcentage)
        if value >= 100:
            return 'success'
        elif value >= 75:
            return 'primary'
        elif value >= 50:
            return 'info'
        elif value >= 25:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary'


@register.filter(name='progress_width')
def progress_width(pourcentage):
    """
    ضمان أن النسبة بين 0 و 100
    الاستخدام: style="width: {{ pourcentage|progress_width }}%"
    """
    try:
        value = float(pourcentage)
        return max(0, min(100, value))
    except (ValueError, TypeError):
        return 0


@register.filter(name='is_retarde')
def is_retarde(date_fin_prevue):
    """
    التحقق من أن التاريخ متأخر
    الاستخدام: {% if projet.date_fin_prevue|is_retarde %}...{% endif %}
    """
    from django.utils import timezone
    if not date_fin_prevue:
        return False
    return date_fin_prevue < timezone.now().date()


@register.filter(name='jours_restants')
def jours_restants(date_fin):
    """
    حساب الأيام المتبقية حتى تاريخ معين
    الاستخدام: {{ projet.date_fin_prevue|jours_restants }}
    """
    from django.utils import timezone
    if not date_fin:
        return None
    try:
        delta = date_fin - timezone.now().date()
        return delta.days
    except Exception:
        return None


# ============================================================
# SECTION 4: FILTERS - FILE SIZE & TYPE
# ============================================================

@register.filter(name='file_size')
def file_size(size_bytes):
    """
    تنسيق حجم الملف
    الاستخدام: {{ doc.taille|file_size }}
    الناتج: 2.5 MB
    """
    try:
        size = float(size_bytes)
        if size < 1024:
            return f"{size:.0f} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"
    except (ValueError, TypeError):
        return size_bytes


@register.filter(name='file_icon')
def file_icon(filename):
    """
    إرجاع أيقونة Bootstrap حسب نوع الملف
    الاستخدام: <i class="bi {{ filename|file_icon }}"></i>
    """
    if not filename:
        return 'bi-file-earmark'

    filename_lower = str(filename).lower()

    if filename_lower.endswith('.pdf'):
        return 'bi-file-earmark-pdf'
    elif filename_lower.endswith(('.doc', '.docx')):
        return 'bi-file-earmark-word'
    elif filename_lower.endswith(('.xls', '.xlsx')):
        return 'bi-file-earmark-excel'
    elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        return 'bi-file-earmark-image'
    elif filename_lower.endswith(('.zip', '.rar', '.7z')):
        return 'bi-file-earmark-zip'
    elif filename_lower.endswith(('.txt', '.log')):
        return 'bi-file-earmark-text'
    elif filename_lower.endswith(('.mp4', '.avi', '.mov')):
        return 'bi-file-earmark-play'
    else:
        return 'bi-file-earmark'


# ============================================================
# SECTION 5: SIMPLE TAGS - CALCULS
# ============================================================

@register.simple_tag
def calculer_pourcentage(part, total):
    """
    حساب النسبة المئوية
    الاستخدام: {% calculer_pourcentage 50 200 as pct %}{{ pct }}%
    الناتج: 25.0%
    """
    try:
        part = Decimal(str(part))
        total = Decimal(str(total))
        if total > 0:
            result = (part / total) * 100
            return round(float(result), 2)
        return 0
    except (InvalidOperation, ValueError, TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def calculer_ecart(prevu, reel):
    """
    حساب الفرق بين المتوقع والفعلي
    الاستخدام: {% calculer_ecart 100 120 as ecart %}
    الناتج: 20 (موجب = تأخير)
    """
    try:
        prevu = Decimal(str(prevu))
        reel = Decimal(str(reel))
        return float(reel - prevu)
    except (InvalidOperation, ValueError, TypeError):
        return 0


@register.simple_tag
def calculer_montant_net(montant_brut, retenue, penalites, tva_taux):
    """
    حساب المبلغ الصافي
    الاستخدام: {% calculer_montant_net 10000 500 100 19 as net %}
    """
    try:
        brut = Decimal(str(montant_brut))
        ret = Decimal(str(retenue))
        pen = Decimal(str(penalites))
        taux = Decimal(str(tva_taux))

        base_ht = brut - ret - pen
        tva = base_ht * (taux / 100)
        net = base_ht + tva

        return float(net)
    except (InvalidOperation, ValueError, TypeError):
        return 0


@register.simple_tag
def somme_liste(queryset, field_name):
    """
    حساب مجموع حقل معين في queryset
    الاستخدام: {% somme_liste lots 'montant' as total %}
    """
    try:
        total = sum(
            getattr(obj, field_name, 0) or 0
            for obj in queryset
        )
        return float(total)
    except Exception:
        return 0


# ============================================================
# SECTION 6: INCLUSION TAGS - COMPOSANTS RÉUTILISABLES
# ============================================================

@register.inclusion_tag('projets/partials/_progress_bar.html')
def progress_bar(pourcentage, show_label=True, size='md'):
    """
    عرض progress bar قابل لإعادة الاستخدام
    الاستخدام: {% progress_bar projet.pourcentage_avancement %}
    """
    return {
        'pourcentage': float(pourcentage or 0),
        'show_label': show_label,
        'size': size,
        'color': progress_color(pourcentage),
    }


@register.inclusion_tag('projets/partials/_stat_badge.html')
def render_stat_badge(statut):
    """
    عرض badge الحالة
    الاستخدام: {% render_stat_badge projet.statut %}
    """
    return {
        'statut': statut,
        'color': stat_badge(statut),
        'label': stat_label(statut),
    }


# ============================================================
# SECTION 7: FILTERS - DIVERS
# ============================================================

@register.filter(name='truncate_chars')
def truncate_chars(value, max_length=50):
    """
    اقتطاع النص مع إضافة ...
    الاستخدام: {{ description|truncate_chars:100 }}
    """
    if not value:
        return ''
    value = str(value)
    if len(value) <= max_length:
        return value
    return value[:max_length].rsplit(' ', 1)[0] + '...'


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    الحصولعلى قيمة من dict في القوالب
    الاستخدام: {{ my_dict|get_item:"key" }}
    """
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)


@register.filter(name='multiply')
def multiply(value, arg):
    """
    ضرب قيمتين
    الاستخدام: {{ quantite|multiply:prix_unitaire }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='divide')
def divide(value, arg):
    """
    قسمة قيمتين
    الاستخدام: {{ montant|divide:100 }}
    """
    try:
        arg = float(arg)
        if arg == 0:
            return 0
        return float(value) / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name='add_days')
def add_days(date, days):
    """
    إضافة أيام إلى تاريخ
    الاستخدام: {{ date_debut|add_days:30 }}
    """
    from datetime import timedelta
    try:
        if not date:
            return None
        return date + timedelta(days=int(days))
    except (ValueError, TypeError):
        return date


@register.filter(name='yes_no')
def yes_no(value):
    """
    تحويل Boolean إلى Oui/Non
    الاستخدام: {{ actif|yes_no }}
    """
    return 'Oui' if value else 'Non'


@register.filter(name='bool_icon')
def bool_icon(value):
    """
    تحويل Boolean إلى أيقونة
    الاستخدام: {{ actif|bool_icon }}
    """
    if value:
        return mark_safe('<i class="bi bi-check-circle-fill text-success"></i>')
    else:
        return mark_safe('<i class="bi bi-x-circle-fill text-danger"></i>')    