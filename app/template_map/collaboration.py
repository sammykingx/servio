from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("collaborations")

class Collabs:
    
    START_COLLABORATION = _BASE_FOLDER.base_folder_files("start-collaboration.html")
    
    class Workspace:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("projects")
        
        ALL_PROJECTS = f"{__SUB_FOLDER}/list.html"
        PROJECT_TYPE = f"{__SUB_FOLDER}/project-type.html"
        DETAILS = f"{__SUB_FOLDER}/details.html"
        CREATE_PROJECT = f"{__SUB_FOLDER}/create.html"
        EDIT_PROJECT =  f"{__SUB_FOLDER}/edit.html"
        LIVE_PROJECT_EDIT = f"{__SUB_FOLDER}/live-edit.html"
        
    class Marketplace:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("marketplace")
        
        LIST = f"{__SUB_FOLDER}/list.html"
        DETAIL = f"{__SUB_FOLDER}/detail.html"
        ENGAGEMENT_SUBMISSION = f"{__SUB_FOLDER}/engagement-submission.html"
        
    class Workforce:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("workroom")
        
        OVERVIEW = f"{__SUB_FOLDER}/overview.html"
        DEMO = f"{__SUB_FOLDER}/demo.html"
        
        