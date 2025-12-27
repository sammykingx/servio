# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        print(
            ">>> SENDING MAIL USING TEMPLATE PREFIX:",
            template_prefix,
        )
        msg = super().send_mail(template_prefix, email, context)
        print(">>> MAIL SENT:", msg)
        return msg
