from django import template

register = template.Library()

@register.filter
def prettify_status(value):
    """Convert underscores to spaces and title-case the string."""
    if not value:
        return ""
    return value.replace("_", " ").title()