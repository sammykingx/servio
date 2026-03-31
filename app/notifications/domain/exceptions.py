class NotificationChannelError(Exception):
    """Base exception for notification channel errors."""
    def __int__(self, message="An error occurred with the notification channel."):
        self.message = message
        super().__init__(self.message)