class AuthURLNames:
    LOGIN = "account_login"
    LOGIN_ACCESS_CODE = "account_request_login_code"
    VERIFY_ACCESS_CODE = "account_confirm_login_code"
    LOGOUT = "account_logout"
    
    
    # REGISTRATION
    SIGNUP = "account_signup"
    EMAIL_VERIFICATION_SENT = "account_email_verification_sent"
    EMAIL_CONFIRMATION = "account_confirm_email" # for email confirmation
    # account_email: manages email addresses
    
    
    # PASSWORD RESET
    PASSWORD_RESET = "account_reset_password"
    PASSWORD_RESET_CHANGE = "account_change_password"
    # account_reset_password_done
    # account_reset_password_from_key
    # account_reset_password_from_key_done
    # account_set_password
    
    
    # SOCIAL ACCOUNTS
    # socialaccount_connections
    # socialaccount_signup
    # socialaccount_login_error
    # socialaccount_login_cancelled
    
    # OTHERS
    ACCOUNT_RECOVERY_OPTIONS = "account_recovery_options"
    ACCOUNT_DASHBOARD = ""
    # account_reauthenticate
    # account_inactive
