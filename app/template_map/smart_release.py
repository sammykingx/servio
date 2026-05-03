from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("smart-release")

class SmartReleaseTemplates:
    OVERVIEW = _BASE_FOLDER.base_folder_files("overview.html")
    