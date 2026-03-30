from pydantic import BaseModel, model_validator
from enum import Enum


class NotificationChannels(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEB_PUSH = "web_push"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationPayload(BaseModel):
    channel: NotificationChannels
    state: bool
    token: str | None = None

    @model_validator(mode="after")
    def ensure_token(self):
        if self.channel == NotificationChannels.WEB_PUSH and not self.token:
            raise ValueError("Token is required for web push notifications")
        return self