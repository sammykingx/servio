from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("proposals")

class Proposals:
    RECEIVED_PROPOSALS = _BASE_FOLDER.base_folder_files("recieved-proposals.html")
    SENT_PROPOSALS = _BASE_FOLDER.base_folder_files("sent-proposals.html")
    PROPOSAL_LIST = _BASE_FOLDER.base_folder_files("proposal-list.html")
    DETAILS = _BASE_FOLDER.base_folder_files("detail.html")
    VIEW_DELIEVERABLES = _BASE_FOLDER.base_folder_files("view-delieverables.html")