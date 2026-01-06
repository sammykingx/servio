from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("payments")

class Payments:
    SUMMARY = _BASE_FOLDER.base_folder_files("transactions.html")
    
    class GigPayments:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("gig-payment-flows")
        
        GIG_OVERVIEW = f"{__SUB_FOLDER}/overview.html"
        GIG_PAYMENT_METHOD = f"{__SUB_FOLDER}/select-payment-method.html"
        CARD_PAYMENTS = f"{__SUB_FOLDER}/pay-with-card.html"
