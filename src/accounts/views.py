from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import authenticate, login

from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from accounts.serializers import UserRegisterSerializer

from .models import Users

# Create your views here.

# class LoginView(View):
#     form_class = UserLoginForm

#     def get(self, *args, **kwargs):
#         return render(self.request , 'accounts/login.html', {'form': self.form_class})

#     def post(self, *args, **kwargs):
#         form = self.form_class(self.request.POST)
#         if form.is_valid():
#             contact_no = form.cleaned_data.get('contact_no')
#             # citizenship_no = form.cleaned_data.get('citizenship_no')
#             password = form.cleaned_data.get('password')
#             user = Users.objects.filter(contact_no=contact_no).first()
#             if user:
#                 user_obj = authenticate(self.request, contact_no=contact_no, password=password )
#                 print('hhhh1', user_obj)
#                 if user_obj != None:
#                     refresh = RefreshToken.for_user(user)
#                     token = {
#                         'access': str(refresh),
#                         'refresh': str(refresh.access_token)
#                     }

#                     login(self.request,user_obj)
#                     print(token)
#                     return Response(token, status=status.HTTP_200_OK)
#             else:
#                 print('here 2')
#                 return render(self.request , 'accounts/login.html', {'form': self.form_class})
#         print('Nooo', form.errors)
#         return render(self.request , 'accounts/login.html', {'form': self.form_class})



class APILoginView(APIView):
    def dispatch(self, *args, **kwargs):
        self.payload = {
            'message':{}, 'details': {}
        }
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        contact_no = data.get('contact_no')
        # citizenship_no = data.get('citizenship_no')
        password = data.get('password')
        user = Users.objects.filter(contact_no=contact_no).first()
        if user:
            user_obj = authenticate(self.request, contact_no=contact_no, password=password )
            if user_obj != None:
                refresh = RefreshToken.for_user(user)
                token = {
                    'access': str(refresh),
                    'refresh': str(refresh.access_token)
                }

                login(self.request,user_obj)
                self.payload['message'] = 'User logged in successfully'
                self.payload['details']['token'] = token
                return Response(self.payload, status=status.HTTP_200_OK)
        else:
            self.payload['message'] = 'Invalid credentials'
            return Response(self.payload, status=status.HTTP_403_FORBIDDEN)
        return  Response(self.payload, status=status.HTTP_400_BAD_REQUEST)


class APIRegisterView(APIView):

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

