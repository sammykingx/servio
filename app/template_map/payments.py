from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("payments")

class Payments:
    SUMMARY = _BASE_FOLDER.base_folder_files("transactions.html")
    SUBSCRIPTION = _BASE_FOLDER.base_folder_files("subcriptions.html")
    
    
    class GigPayments:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("gig-payment-flows")
        
        GIG_OVERVIEW = f"{__SUB_FOLDER}/overview.html"
        SELECT_PAYMENT_METHOD = f"{__SUB_FOLDER}/select-payment-method.html"
        CARD_DETAILS = f"{__SUB_FOLDER}/card-details.html"
        GIG_CHECKOUT_RESPONSE = f"{__SUB_FOLDER}/gig-checkout-response.html"
        GIG_PAYMENT_COMPLETE = F"{__SUB_FOLDER}/gig-payment-successfull.html"
        
    class Escrow:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("escrow")
        
        OVERVIEW = f"{__SUB_FOLDER}/overview.html"
        DETAILS = f"{__SUB_FOLDER}/details.html"
        
    class Checkouts:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("checkouts")
        
        SUBSCRIPTION_CHECKOUT_CURRENCY = f"{__SUB_FOLDER}/subcription-checkout-currency.html"
        SUBSCRIPTION_CHECKOUT = f"{__SUB_FOLDER}/subscription-checkout.html"
        SUBSCRIPTION_CHECKOUT_CANCELLED = f"{__SUB_FOLDER}/cancelled-subscription-checkout.html"
        
