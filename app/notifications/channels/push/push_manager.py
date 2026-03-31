from notifications.domain.schemas import DeviceMeta, NotificationChannels, NotificationPayload
from registry_utils import get_registered_model


class PushManager:
    def __init__(self, user):
        self.user = user
        self.model = get_registered_model("notifications", "WebPushDeviceToken")
        
    def create_object(self, data:NotificationPayload):
        if data.channel != NotificationChannels.WEB_PUSH:
            raise ValueError("Invalid channel for PushManager")
        
        self.model.objects.update_or_create(
            token=data.token,
            defaults={
                "user": self.user,
                "is_active": data.state,
                "user_agent": data.deviceMeta.userAgent,
                "platform": data.deviceMeta.platform,
                "browser": data.deviceMeta.browser,
                "device": data.deviceMeta.device
            }
        )
        
    def deactivate_token(self, fcm_token):
        try:
            token_obj = self.model.objects.get(token=fcm_token, user=self.user)
            token_obj.deactivate()
        except self.model.DoesNotExist:
            pass  # Token not found, nothing to deactivate
        