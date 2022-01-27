from django.http import JsonResponse
from django.core.cache import cache
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from .tasks import send_verification
from .cryptography import RSA, CryptoFernet
from .extraModules import getSHA256Hash, prepareKeys
from .models import Profile, Users, citizenship_image
from .tokensOperations import account_activation_token


def _createUser(validated_data):
    citizenship_no_cipher = getSHA256Hash(validated_data['citizenship_no'])
    if not Users.objects.filter(citizenship_hash=citizenship_no_cipher).exists():
        
        user = Users(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                citizenship_no=validated_data['citizenship_no'],
                citizenship_hash=getSHA256Hash(validated_data['citizenship_no'])
            )
        user.set_password(validated_data['password'])
        user.save()
        key = getSHA256Hash(validated_data['password'])
        fernet = CryptoFernet(key)
        user.citizenship_no = fernet.encrypt(validated_data['citizenship_no'])
        user.first_name = fernet.encrypt(validated_data['first_name'])
        user.last_name = fernet.encrypt(validated_data['last_name'])
        user.save()
        Profile.objects.create(user=user, is_voter=True)
        first_name=validated_data['first_name']
        send_verification(user.id,first_name, domain='127.0.0.1:8000')
        cache.set(f"{user.id}_user", key)
        data = {
            'message': 'Successfully created user',
            'status': 200,
            'user': user,
        }
        return data
    else:
        data = {
            'message': 'User with citizenship already exists',
            'status': 400
        }
        return data


def activate_account(request, uidb64, token):
    """
    Activates the user when user clicks the link.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Users.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        response = JsonResponse(
            {'verified': True,
            },
            status=status.HTTP_200_OK)
        return response
    else:
        return JsonResponse(
            {'error': _('Not valid link!')},
            status=status.HTTP_400_BAD_REQUEST
        )