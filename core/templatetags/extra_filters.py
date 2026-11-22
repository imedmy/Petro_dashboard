# core/templatetags/extra_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    يسمح باسترجاع قيمة من قاموس باستخدام متغير.
    مثال: {{ my_dict|get_item:dynamic_key }}
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(str(key))
    return None

@register.filter
def get_range(value):
    """
    يحول رقمًا إلى نطاق (range) لاستخدامه في حلقة for.
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)