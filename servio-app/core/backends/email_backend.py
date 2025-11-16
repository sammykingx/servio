from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        print(f"EMAIL BACKEND KWARGS BEFORE: {kwargs}\n")
        kwargs['timeout'] = 10  # timeout in seconds
        print(f"EMAIL BACKEND KWARGS AFTER: {kwargs}\n")
        super().__init__(*args, **kwargs)

