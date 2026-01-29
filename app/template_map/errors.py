from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("errors")

class Errors:
    ERROR_404 = _BASE_FOLDER.base_folder_files("404.html")
    ERROR_500 = _BASE_FOLDER.base_folder_files("500.html")