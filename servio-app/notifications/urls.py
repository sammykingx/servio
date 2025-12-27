from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from .views import toggle_notification_channel
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
        toggle_notification_channel,
        name=NotificationsURLNames.TOGGLE_NOTIFICATION_CHANNELS
    ),
]