from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("payments")

class Payments:
    SUMMARY = _BASE_FOLDER.base_folder_files("transactions.html")
