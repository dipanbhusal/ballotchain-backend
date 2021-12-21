from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth import authenticate, login

from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from accounts.cryptography import RSA, CryptoFernet

from accounts.serializers import UserRegisterSerializer

from .models import RSAKeys, Users
from .extraModules import getSHA256Hash, prepareKeys
# Create your views here.

class APILoginView(APIView):
    """
        API to login user
        Inputs: contact_no, citizenship_no, password
        API Endpoint: api/accounts/login/
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        rsa = RSA()
        contact_no = data.get('contact_no')
        citizenship_no = data.get('citizenship_no')
        password = data.get('password')
        first_name = data.get('first_name')
        fernet_key = getSHA256Hash(password)
        fernet = CryptoFernet(fernet_key)
        user = Users.objects.filter(contact_no=contact_no)
        if user:
            rsa_object = RSAKeys.objects.filter(user=user.first()).first()
            if rsa_object:
                n_e_d = fernet.decrypt(rsa_object.num_exp_d) # returns 'n-e-d' 

                prepared_public_key, prepared_private_key = prepareKeys(n_e_d)
                citizenship_no_encrypted = rsa.encrypt(citizenship_no, prepared_public_key)
                if user.first().citizenship_no == citizenship_no_encrypted:
                    user_obj = authenticate(self.request, contact_no=contact_no, password=password )
                    if user_obj != None:
                        refresh = RefreshToken.for_user(user.first())
                        token = {
                            'access': str(refresh),
                            'refresh': str(refresh.access_token)
                        }

                        login(self.request,user_obj)
                        self.payload['message'] = 'User logged in successfully'
                        self.payload['details']['token'] = token
                        return Response(self.payload, status=status.HTTP_200_OK)
                    else:
                        self.payload['message'] = "Incorrect password"
                else:
                    self.payload['message'] = "Incorrect citizenship number"
        else:
            self.payload['message'] = 'Incorrect contact number'
        return Response(self.payload, status=status.HTTP_403_FORBIDDEN)
        # return  Response(self.payload, status=status.HTTP_400_BAD_REQUEST)


class APIRegisterView(APIView):
    """
        API to register user
        Inputs: first_name, last_name, contact_no, citizenship_no, password, password2
        API Endpoint: api/accounts/register/
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self,request,  *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            serializer.save()
            self.payload['message'] = "User Created Successfully"
            return Response(self.payload, status=status.HTTP_200_OK, )
        self.payload['message'] = serializer.errors
        return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)



def test(request):
    
    return HttpResponse("test")