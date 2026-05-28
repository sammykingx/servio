from . import TemplateRegistryBase


_BASE_FOLDER = TemplateRegistryBase("contracts")

class Contract:
    ACCEPT_CONTRACT_TERMS = _BASE_FOLDER.base_folder_files("accept-contract-terms.html")
    LIST_CONTRACTS = _BASE_FOLDER.base_folder_files("list-contracts.html")
    CONTRACT_TIMELINE = _BASE_FOLDER.base_folder_files("contract-timeline.html")
    CONTRACT_BUILDER = _BASE_FOLDER.base_folder_files("contract-builder.html") # note used yet