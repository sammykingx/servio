class AuthURLNames:
    LOGIN = "account_login"
    LOGIN_ACCESS_CODE = "account_request_login_code"
    VERIFY_ACCESS_CODE = "account_confirm_login_code"
    LOGOUT = "account_logout"
    
    
    # REGISTRATION
    SIGNUP = "account_signup"
    EMAIL_VERIFICATION_SENT = "account_email_verification_sent"
    EMAIL_CONFIRMATION = "account_confirm_email"
    # EMAIL_VERIFIED = "account_email_verified"
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

# email heading = Please Confirm Your Email Address
# http://localhost:8000/accounts/email/verify/NQ:1vEljJ:m-_uJP8n_Shgzhtpin39SF0Fs1CCbJEGAr0bDE8bmr0

# --------------------------------------
# account already exist template
# Content-Transfer-Encoding: 7bit
# Subject: Servio - Account Already Exists
# From: no-reply@servio.divgm.com
# To: user2@example.com
# Date: Sun, 02 Nov 2025 15:45:18 -0000
# Message-ID: <176209831890.7046.5940175979619397062@sammykingx.localdomain>

# Hello from localhost:8000!

# You are receiving this email because you or someone else tried to signup for an
# account using email address:

# user2@example.com

# However, an account using that email address already exists.  In case you have
# forgotten about this, please use the password forgotten procedure to recover
# your account:

# http://localhost:8000/accounts/recover-account/

# Thank you for using localhost:8000!
# localhost:8000

# --------------------------------------
# to: user2@example.com
# message: Hello from localhost:8000!

# You are receiving this email because you or someone else tried to signup for an
# account using email address:

# user2@example.com

# However, an account using that email address already exists.  In case you have
# forgotten about this, please use the password forgotten procedure to recover
# your account:

# http://localhost:8000/accounts/recover-account/

# Thank you for using localhost:8000!
# localhost:8000