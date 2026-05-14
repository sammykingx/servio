from django.urls import include, path
from . import workspace
from . import marketplace

urlpatterns = [
    path("workspace/", include(workspace)),
    path("oppurtunities/", include(marketplace)),
]