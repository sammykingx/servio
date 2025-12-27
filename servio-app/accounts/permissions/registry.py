"""
Central permission registry.

Format:
GROUP_NAME: {
    "app_label": [permission_codenames]
}
"""

ROLE_PERMISSIONS = {
    "member": {
        "business_accounts": [
            "create_business_account",
        ],
    },

    "provider": {
        "business_accounts": [
            "view_busines_page",
        ],
    },

    "staff": {},

    "admin": {
        "*": ["*"],  # special handling
    },
}
