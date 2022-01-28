import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    """
    Returns a token as hash value of given inputs
    """
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.is_active)
        )

account_activation_token = TokenGenerator()