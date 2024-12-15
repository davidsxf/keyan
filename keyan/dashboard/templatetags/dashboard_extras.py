from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """获取字典中的值"""
    if dictionary is None:
        return None
    return dictionary.get(str(key))

@register.filter(name='to_wan')
def to_wan(value):
    """将数值转换为万元"""
    if value is None:
        return '0'
    value = Decimal(str(value))
    return '{:,.2f}'.format(value / 10000)

@register.filter(name='div')
def div(value, arg):
    """除法运算"""
    try:
        if value is None or arg is None or arg == 0:
            return 0
        return Decimal(str(value)) / Decimal(str(arg))
    except:
        return 0

@register.filter(name='mul')
def mul(value, arg):
    """乘法运算"""
    try:
        if value is None or arg is None:
            return 0
        return Decimal(str(value)) * Decimal(str(arg))
    except:
        return 0

@register.filter(name='percentage')
def percentage(value, decimals=1):
    """将小数转换为百分比"""
    try:
        if value is None:
            return '0%'
        return f"{value * 100:.{decimals}f}%"
    except:
        return '0%'