from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("collaborations")

class Collabs:
    LIST_COLLABORATIONS = _BASE_FOLDER.base_folder_files("list.html")
    DETAILS = _BASE_FOLDER.base_folder_files("details.html")
    CREATE = _BASE_FOLDER.base_folder_files("create.html")