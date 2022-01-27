
from core.celery import app
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from .tokensOperations import account_activation_token



# @app.task
def send_verification(user_id,first_name, domain):
    """
    Sends verification email after user account
    is created successfully.
    """
    user_model = get_user_model()
    try:
        user = user_model.objects.get(id=user_id)
        protocol_used = 'http'
        ac_token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        email_subject = 'Verify your e-mail for BallotChain'
        message = f'Dear {first_name} \n' \
            f'Thank you for the registration. To use full features of BallotChain please verify your account by clicking the link below, \n' \
            f'{protocol_used}://{domain}/api/accounts/activate/{uid}/{ac_token}/'
        send_mail(
            email_subject,
            message,
            'admin@ballotchain.com.np',
            [user.email],
            fail_silently=False
        )
    except user_model.DoesNotExist:
        print("Error occured")
