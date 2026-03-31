from pydantic import BaseModel, model_validator, Field
from enum import Enum


class NotificationChannels(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEB_PUSH = "web_push"
    SMS = "sms"
    WHATSAPP = "whatsapp"

class DeviceMeta(BaseModel):
    userAgent: str
    platform: str
    browser: str
    device: str
    
    
class NotificationPayload(BaseModel):
    channel: NotificationChannels
    state: bool
    token: str | None = None
    deviceMeta: DeviceMeta = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_web_push_requirements(self):
        if self.channel == NotificationChannels.WEB_PUSH:
            if not self.token or not self.deviceMeta:
                raise ValueError(
                    "Both 'token' and 'deviceMeta' are required for web push notifications"
                )
        return self