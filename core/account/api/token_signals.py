# accounts/signals.py

from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user':
            reset_password_token.user,
        'username':
            reset_password_token.user.username,
        'email':
            reset_password_token.user.email,
        'reset_password_url':
            '{}?token={}'.format(
                instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
                reset_password_token.key
            )
    }

    print('reset_password_url', context['reset_password_url'])

    # render email text
    email_html_message = render_to_string(
        'email/user_reset_password.html', {'reset_password_url': context['reset_password_url']}
    )
    email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        'Password Reset for {title}'.format(title='Your Website Title'),
        # message:
        email_plaintext_message,
        # from:
        'noreply@yourdomain.com',
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, 'text/html')
    msg.send()


@receiver(reset_password_token_created)
def post_password_reset(sender, instance, reset_password_token, *args, **kwargs):
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'user_id': reset_password_token.user.id,
    }

    # user_ = OutstandingToken.objects.all().order_by('-id').first()
    user_ = OutstandingToken.objects.filter(
        user=context['user_id']
    ).exclude(id__in=BlacklistedToken.objects.values_list('token_id', flat=True),)
    for user in user_:
        try:
            blkl_user = RefreshToken(user.token)
            blkl_user.blacklist()
        except Exception as e:
            print(str(e))
