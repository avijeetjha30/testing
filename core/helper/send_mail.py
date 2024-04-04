from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template


class SendMail:

    def __init__(self):
        pass

    def send_mail(self, email, subject, message, email_template):
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [
            email,
        ]
        template = get_template(email_template).render({'link': message})
        send_mail(subject, message, email_from, recipient_list, fail_silently=False, html_message=template)
        return True
