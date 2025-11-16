from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        kwargs['timeout'] = 10  # timeout in seconds
        super().__init__(*args, **kwargs)

