from django.urls import path

from .views import APILoginView, APIRegisterView, test

urlpatterns = [
    path('test', test, name='test'),
    path('login/', APILoginView.as_view()),
    path('register/', APIRegisterView.as_view()),
]