from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render, HttpResponse
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.accountOperations import add_to_chain

from accounts.cryptography import CryptoFernet
from accounts.middleware import get_user

from accounts.serializers import ProfileAllSerializer, ProfileSerializer, UserRegisterSerializer
from election.models import Election

from .models import Profile, Users
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
                key = getSHA256Hash(password)
                fernet = CryptoFernet(key)

                citizenship_no_decrypted = fernet.decrypt(user.citizenship_no )
                if citizenship_no == citizenship_no_decrypted:
                    user_obj = authenticate(self.request, email=email, password=password )
                    if user_obj != None:
                        refresh = RefreshToken.for_user(user)
                        token = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token)
                        }
                        user_data = {
                            'id': user.id
                        }
                        self.payload['message'] = 'User logged in successfully'
                        self.payload['details']['token'] = token

                        profile = Profile.objects.get(user=user)
                        cache.set(f"{user.id}_user", password)
                        self.payload['details']['user'] =  ProfileSerializer(profile).data
                        election = None
                        if profile.enrolled_election:
                            election = profile.enrolled_election.public_key
                        
                        self.payload['details']['enrolled_election'] = election
                        # self.payload['details']['userData'] =
                        return Response(self.payload, status=status.HTTP_200_OK)
                    else:
                        self.payload['message'] = "Incorrect password"
                else:
                    self.payload['message'] = "Incorrect citizenship number"
            else:
                self.payload['message'] = "Please verify your email to login."
        else:
            self.payload['message'] = 'Incorrect email'
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
        data = request.data
        data._mutable = True
        print(data)
        if data.get('enrolled_election') != "":
            data['enrolled_election'] = Election.objects.get(id=data['enrolled_election']).id
        serializer = UserRegisterSerializer(data=data)
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
    
    def get(self, *args, **kwargs):
        profile = Profile.objects.get(user=self.request.user)
        serializer = ProfileAllSerializer(profile)
        self.payload['message'] = 'Profile fetched successfully'
        self.payload['details']['profile'] = serializer.data
        return Response(self.payload, status=status.HTTP_200_OK)


class ProfileUpdateView(generics.UpdateAPIView):
    authentication_classes = (JWTAuthentication, )

    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        data = self.request.POST
        data._mutable = True
        profile = Profile.objects.get(user=self.request.user)
        if (not profile.citizenship_image_front and  self.request.FILES.get('citizenship_image_front', None) is not None) or (profile.citizenship_image_front and self.request.FILES.get('citizenship_image_front', None) is not None) :
            data['citizenship_image_front'] = self.request.FILES.get('citizenship_image_front')
        elif profile.citizenship_image_front and  self.request.FILES.get('citizenship_image_front', None) is None:
            data['citizenship_image_front'] = profile.citizenship_image_front
        if (not profile.citizenship_image_back and  self.request.FILES.get('citizenship_image_back', None) is not None) or (profile.citizenship_image_back and self.request.FILES.get('citizenship_image_back', None) is not None) :
            data['citizenship_image_back'] = self.request.FILES.get('citizenship_image_back')
        elif profile.citizenship_image_back and  self.request.FILES.get('citizenship_image_back', None) is None:
            data['citizenship_image_back'] = profile.citizenship_image_back
        data._mutable = False
        profile = Profile.objects.get(user=self.request.user)
        serializer = ProfileAllSerializer(Profile.objects.get(user=self.request.user), data=data)
        if serializer.is_valid():
            self.perform_update(serializer)
            if profile.enrolled_election:
                add_to_chain(profile)
            self.payload['message'] = 'Profile updated successfully'
            self.payload['details'] = serializer.data
            return Response(self.payload, status=status.HTTP_200_OK)

        return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)


