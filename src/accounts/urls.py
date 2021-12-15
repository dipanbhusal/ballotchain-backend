from django.urls import path

from .views import APILoginView, APIRegisterView

urlpatterns = [
    path('login/', APILoginView.as_view()),
    path('register/', APIRegisterView.as_view()),
]