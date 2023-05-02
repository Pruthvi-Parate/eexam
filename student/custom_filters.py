from django import template

register = template.Library()

@register.filter(name='floatdiv')
def floatdiv(value, arg):
    try:
        return float(value) / float(arg)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    
@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    return value * arg