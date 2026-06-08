from django.urls import include, path
from . import workspace
from . import marketplace
from . import workroom


urlpatterns = [
    path("workspace/", include(workspace)),
    path("oppurtunities/", include(marketplace)),
    path("workroom/", include(workroom)),
]