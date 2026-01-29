from django import template
import re

register = template.Library()

@register.filter
def format_mobile_number(value):
    if not value:
        return "N/A"

    # Keep digits only, keep leading "+" if present
    cleaned = re.sub(r"[^\d+]", "", value)

    # Remove "+" for processing
    digits = cleaned.lstrip("+")

    # US / Canada (10 digits local)
    if len(digits) == 10 and digits[0] != "7" and digits[:3] != "234":
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    # US / Canada with country code +1
    if len(digits) == 11 and digits.startswith("1"):
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

    # Nigeria local 11 digits (starting with 0)
    if len(digits) == 11 and digits.startswith("0"):
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"

    # Nigeria international +234
    if digits.startswith("234") and len(digits) >= 13:
        return f"+234 ({digits[3:6]}) {digits[6:9]}-{digits[9:]}"

    # Russia +7
    if digits.startswith("7") and len(digits) == 11:
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:]}"

    # UK +44
    if digits.startswith("44") and len(digits) == 12:
        return f"+44 {digits[2:5]} {digits[5:8]} {digits[8:]}"

    # General Europe fallback (starts with 3 and >=11 digits)
    if digits.startswith("3") and len(digits) >= 11:
        return f"+{digits[:len(digits)-9]} {digits[-9:-6]} {digits[-6:-3]} {digits[-3:]}"

    # fallback
    return cleaned

