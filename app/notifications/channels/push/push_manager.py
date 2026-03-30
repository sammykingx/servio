from registry_utils import get_registered_model


class PushManager:
    def __init__(self, user):
        self.user = user
        self.model = get_registered_model("notifications", "WebPushDeviceToken")
        
    def create_object(self, channel_name, fcm_token, state=True):
        if channel_name != "web_push":
            raise ValueError("Invalid channel for PushManager")
        
        self.model.objects.update_or_create(
            token=fcm_token,
            defaults={
                "user": self.user,
                "is_active": state
            }
        )
        
    def deactivate_token(self, fcm_token):
        try:
            token_obj = self.model.objects.get(token=fcm_token, user=self.user)
            token_obj.deactivate()
        except self.model.DoesNotExist:
            pass  # Token not found, nothing to deactivate
        