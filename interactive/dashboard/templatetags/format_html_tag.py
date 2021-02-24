from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def format_html_tag(value):
    return value.replace(" ","-")
