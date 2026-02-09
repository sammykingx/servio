from django import template

register = template.Library()

# not used
@register.filter
def get_item(dictionary:dict, key):
    return dictionary.get(key)
