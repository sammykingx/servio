from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("marketing")

class Marketing:
    SUMMARY = _BASE_FOLDER.base_folder_files("marketing-overview.html")
    CREATE_COUPONS = _BASE_FOLDER.base_folder_files("create-coupons.html")