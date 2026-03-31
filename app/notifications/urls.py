from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from .views import ToggleNotifications
from core.url_names import AuthURLNames
from core.url_names import NotificationsURLNames


urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=reverse_lazy(AuthURLNames.LOGIN), permanent=False
        ),
    ),
    path(
        "toggle/",
        ToggleNotifications.as_view(),
        name=NotificationsURLNames.TOGGLE_NOTIFICATION_CHANNELS
    ),
]