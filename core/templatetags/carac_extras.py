# core/templatetags/famille_extras.py
from django import template

register = template.Library()

@register.filter
def get_range(value):
    """
    إرجاع نطاق من 0 إلى value (مفيد للمسافات حسب المستوى)
    مثال: {% for i in 3|get_range %} → [0,1,2]
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)