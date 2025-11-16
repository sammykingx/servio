from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import traceback


class EmailService:
    """
    A clean, reusable email helper that handles:
    - Loading template
    - Setting context
    - Rendering HTML
    - Sending email
    """

    def __init__(self, to_email: str):
        self.to_email = to_email
        self.subject = None
        self.template = None
        self.context = {}
        
    def _build_message(self):
        if not self.template:
            raise ValueError("Email template not set")
        return render_to_string(self.template, self.context)

    def _send(self, html_body: str):
        if not (self.subject and self.to_email):
            raise ValueError("Email subject or recipient not set")
        
        msg = EmailMultiAlternatives(
            subject=self.subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.to_email],
        )
        msg.attach_alternative(html_body, "text/html")
        try:
            msg.send()
            return True
        except Exception as e:
            # logger.error("Error sending email: %s", e)
            # logger.error(traceback.format_exc())
            print("ERROR SENDING MAIL: ", e)
            traceback.print_exc()
            return False

    def set_subject(self, subject: str):
        self.subject = subject
        return self

    def use_template(self, template_path: str):
        self.template = template_path
        return self

    def with_context(self, **kwargs):
        self.context.update(kwargs)
        return self

    def send(self):
        html = self._build_message()
        return self._send(html)
