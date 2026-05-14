from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("contracts")

class Contract:
    VIEW_CONTRACT = _BASE_FOLDER.base_folder_files("view-contract.html")
    CONTRACT_BUILDER = _BASE_FOLDER.base_folder_files("contract-builder.html") # note used yet