from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth import authenticate, login
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.cryptography import RSA, CryptoFernet

from accounts.serializers import ProfileSerializer, UserRegisterSerializer

from .models import RSAKeys, Users
from .extraModules import crypOperation, getSHA256Hash, prepareKeys
# Create your views here.

class APILoginView(APIView):
    """
        API to login user
        Inputs: email, citizenship_no, password
        API Endpoint: api/accounts/login/
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        citizenship_no = data.get('citizenship_no')
        password = data.get('password')
    
        user = Users.objects.filter(email=email).first()
        if user:
            if user.is_active:
                # key = bytes(password, 'utf-8')
                key = getSHA256Hash(password)
                print(key)
                # key = b'NJoRb4atyUIeb+qCNn2CUMl2kgvl0MUROxheStO7tYg='
                fernet = CryptoFernet(key)
                # cipher = fernet.encrypt("My name is dipan")
                # print(cipher)
                # plain = fernet.decrypt(cipher)
                # print(plain)
                citizenship_no_decrypted = fernet.decrypt(user.citizenship_no )
                if citizenship_no == citizenship_no_decrypted:
                    user_obj = authenticate(self.request, email=email, password=password )
                    if user_obj != None:
                        refresh = RefreshToken.for_user(user)
                        token = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token)
                        }

                        self.payload['message'] = 'User logged in successfully'
                        self.payload['details']['token'] = token
                        return Response(self.payload, status=status.HTTP_200_OK)
                    else:
                        self.payload['message'] = "Incorrect password"
                else:
                    self.payload['message'] = "Incorrect citizenship number"
            else:
                self.payload['message'] = "Please verify your email to login."
        else:
            self.payload['message'] = 'Incorrect contact number'
        return Response(self.payload, status=status.HTTP_403_FORBIDDEN)
        # return  Response(self.payload, status=status.HTTP_400_BAD_REQUEST)


class APIRegisterView(APIView):
    """
        API to register user
        Inputs: first_name, last_name, email, citizenship_no, password, password2
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



class ProfileView(APIView):
    authentication_classes = (JWTAuthentication, )
    """
    API to View, Edit Profile  of user. 
    """
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)
    
    def post(self, *args, **kwargs):
        data = self.data
        serializer = ProfileSerializer(data=data)
        if serializer.valid():
            
            serializer.save()
            self.payload['message'] = 'Profile updated successfully'
            self.payload['message']['details'] = serializer.data
            return Response(self.payload, status=status.HTTP_200_OK)
        return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)


