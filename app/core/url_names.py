class AuthURLNames:
    LOGIN = "account_login"
    LOGIN_LINK = "account_request_login_code"
    VERIFY_LOGIN_LINK = "account_confirm_login_code"
    LOGOUT = "account_logout"

    # REGISTRATION
    SIGNUP = "account_signup"
    EMAIL_VERIFICATION_SENT = "account_email_verification_sent"
    EMAIL_CONFIRMATION = "account_confirm_email"
    RESEND_VERIFICATION_EMAIL = "resend_verification_email"

    # PASSWORD RESET
    REQUEST_PASSWORD_RESET = (
        "account_reset_password"  # request password reset link
    )
    PASSWORD_RESET = "account_set_password"
    PASSWORD_RESET_DONE = "account_reset_password_done"
    PASSWORD_CHANGE = "account_change_password"  # actual password change
    PASSWORD_CHANGE_DONE = "account_change_password_done"
    # account_reset_password_from_key
    # account_reset_password_from_key_done

    # SOCIAL ACCOUNTS
    # socialaccount_connections
    # socialaccount_signup
    # socialaccount_login_error
    # socialaccount_login_cancelled

    # OTHERS
    ACCOUNT_RECOVERY_OPTIONS = "account_recovery_options"
    ACCOUNT_DASHBOARD = "dashboard"
    ACCOUNT_PROFILE = "account_profile"
    ACCOUNT_SETTINGS = "account_settings"
    SWITCH_TO_BUSINESS = "switch_to_business"
    # account_reauthenticate
    # account_inactive

    # ACCOUNT UPDATES
    UPDATE_SOCIAL_LINKS = "update_social_links"
    UPDATE_PERSONAL_INFO = "update_personal_info"
    UPDATE_PROFILE_INFO = "update_profile_info"
    UPDATE_ADDRESS_INFO = "update_address_info"
    UPLOAD_PROFILE_PICTURE = "upload_profile_picture"
    
class OnboardingURLS:
    class Users:
        APP_NAME = "onboarding_users"
        
        WELCOME = "start_onboarding"
        PROFILE_SETUP = "onborading_step_one"
        EXPERTISE_AND_NICHE = "onborading_step_two"
        OBJECTIVES = "onboarding_step_three"
        COMPLETE = "onboarding_complete"
        
    class Providers:
        APP_NAME = "onboarding_providers"
    
class NotificationsURLNames:
    TOGGLE_NOTIFICATION_CHANNELS = "toggle_notification_channels"
    
    
class BusinessURLS:
    VIEW_BUSINESS_PAGE = "view_business_page"
    REGISTER_BUSINESS = "register_business"
    BUSINESS_ONBOARDING = "business_onboarding"
    UPLOAD_BUSINESS_LOGO = "upload_business_logo"
    SERVICES = "business_services"
    SCHEDULE = "business_schedule"

    
class CollaborationURLS:
    LIST_COLLABORATIONS = "list_collaborations"
    SELECT_COLLABORATION_TYPE = "select_collaboration_type"
    CREATE_COLLABORATION = "create_collaboration"
    DETAIL_COLLABORATION = "view_collaboration"
    EDIT_COLLABORATION = "edit_collaboration"
    LIVE_COLLABORATION_EDIT = "live_edit_collaboration"
    COLLABORATION_PAYMENTS = "collaboration_payment"
    DELETE_COLLABORATION = "delete_collaboration"
    START_COLLABORATION = "start_collaboration"
    
    
class OppurtunitiesURLS:
    ALL = "all_oppurtunities"
    DETAIL = "oppurtunity_detail"
    ACCEPT_OFFER = "accept_oppurtunity_offer"
  
    
class ProposalURLS:
    SENT_PROPOSALS = "sent_proposals"
    RECEIVED_PROPOSALS = "gig_with_proposals_listings"
    PROPOSAL_LISTINGS = "proposal_listings"
    UPDATE_PROPOSAL_STATUS = "update_proposal_status"
    VIEW_DELIEVERABLES = "view_proposal_deliverables"
    
    # not used
    DETAILS = "negotiation_details"
    GIG_NEGOTIATIONS = "gig_negotiations"
    
    
class ContractURLS:
    PREVIEW_CONTRACT = "preview_contract"
    BUILD_CONTRACT = "build_contract"
    
    
class PaymentURLS:
    USER_PAYMENT_SUMMARY = "payment_summary"
    PAY_SUBSCRIPTION = "pay_subscriptions"
    SUBSCRIPTION_CHECKOUT_OPTION = "subscription_checkout_option"
    SUBSCRIPTION_CHECKOUT = "subscription_checkout"
    PAYMENT_VERIFICATION = "payment_verification"
    CANCELLED_PAYMENT_CHECKOUT = "cancelled_payment_checkout"
    CHECKOUT_COMPLETE = "checkout_complete"
    GIG_PAYMENT_SUMMARY = "gig_payment_summary"
    SELECT_GIG_PAYMENT_METHOD = "process_gig_payment"
    GIG_CARD_PAYMENT = "gig_card_payment"
    GIG_PAYMENT_RESPONSE = "gig_payment_response"
    GIG_PAYMENT_COMPLETE = "gig_payment_complete"
    
    # WEBHOOKS
    PAYSTACK_WEBHOOK = "paytack_webhook"
    STRIPE_WEBHOOK = "stripe_webhook"
    
    
class EscrowURLS:
    OVERVIEW = "escrow_overview"
    DETAILS = "escrow_details"
    
    
class ReviewURLS:
    OVERVIEW = "account_reviews"
