# formatter for pyandantc errors
from pydantic import ValidationError

def format_pydantic_errors(err: ValidationError):
    formatted = []

    for err in err.errors():
        formatted.append({
            "field": ".".join(map(str, err["loc"])),
            "message": err["msg"],
            "type": err["type"],
        })

    return formatted
