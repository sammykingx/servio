from . import TemplateRegistryBase

_BASE_FOLDER = TemplateRegistryBase("reviews")

class Reviews:
    BUSINESS_REVIEWS = _BASE_FOLDER.base_folder_files("business-reviews.html")