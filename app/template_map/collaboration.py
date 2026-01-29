from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("collaborations")

class Collabs:
    LIST_COLLABORATIONS = _BASE_FOLDER.base_folder_files("list.html")
    DETAILS = _BASE_FOLDER.base_folder_files("details.html")
    CREATE = _BASE_FOLDER.base_folder_files("create.html")
    EDIT =  _BASE_FOLDER.base_folder_files("edit.html")
    
    class Proposals:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("proposals")
        
        LIST = f"{__SUB_FOLDER}/list.html"
        DETAILS = f"{__SUB_FOLDER}/detail.html"
        
    class Oppurtunities:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("oppurtunities")
        
        LIST = f"{__SUB_FOLDER}/list.html"
        DETAIL = f"{__SUB_FOLDER}/detail.html"
        ACCEPT_OFFER = f"{__SUB_FOLDER}/accept-offer.html"
        