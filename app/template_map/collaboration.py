from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("collaborations")

class Collabs:
    LIST_COLLABORATIONS = _BASE_FOLDER.base_folder_files("list.html")
    DETAILS = _BASE_FOLDER.base_folder_files("details.html")
    CREATE = _BASE_FOLDER.base_folder_files("create.html")
    EDIT =  _BASE_FOLDER.base_folder_files("new-edit.html")
    LIVE_EDIT = _BASE_FOLDER.base_folder_files("live-edit.html")
    START_COLLABORATION = _BASE_FOLDER.base_folder_files("start-collaboration.html")
    
    class Proposals:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("proposals")
        
        RECEIVED_PROPOSALS = f"{__SUB_FOLDER}/recieved-proposals.html"
        SENT_PROPOSALS = f"{__SUB_FOLDER}/sent-proposals.html"
        PROPOSAL_LIST = f"{__SUB_FOLDER}/proposal-list.html"
        DETAILS = f"{__SUB_FOLDER}/detail.html"
        VIEW_DELIEVERABLES = f"{__SUB_FOLDER}/view-delieverables.html"
        
    class Oppurtunities:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("oppurtunities")
        
        LIST = f"{__SUB_FOLDER}/list.html"
        DETAIL = f"{__SUB_FOLDER}/detail.html"
        ACCEPT_OFFER = f"{__SUB_FOLDER}/accept-offer.html"
        
    class Contracts:
        __SUB_FOLDER = _BASE_FOLDER.subfolder("contracts")
        
        BUILD_CONTRACT = f"{__SUB_FOLDER}/contract-builder.html"
        VIEW_CONTRACT = f"{__SUB_FOLDER}/view-contract.html"
        