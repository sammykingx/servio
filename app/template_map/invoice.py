from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("invoice")

class Invoices:
    SUMMARY = _BASE_FOLDER.base_folder_files("invoice-overview.html")
    CREATE_INVOICE = _BASE_FOLDER.base_folder_files("create-invoice.html")