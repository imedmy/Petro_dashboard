# core/context_processors.py
from .models import Page, PermissionMatrix

def menu_items(request):
    """
    هذا الـ processor يُضيف menu_items تلقائيًا إلى كل قوالب
    شرط أن يكون المستخدم مسجل دخوله
    """
    if request.user.is_authenticated:
        try:
            pages = Page.objects.filter(is_active=True).order_by('order')
            items = []
            for page in pages:
                perm, created = PermissionMatrix.objects.get_or_create(
                    user=request.user,
                    page=page,
                    defaults={'can_consulte': False}
                )
                if perm.can_consulte:
                    items.append({'page': page, 'perm': perm})
            return {'menu_items': items}
        except:
            return {'menu_items': []}
    return {'menu_items': []}