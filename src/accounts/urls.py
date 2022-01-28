from django.urls import path

from . import views, accountOperations

urlpatterns = [
    path('activate/<uidb64>/<token>/', accountOperations.activate_account, name='activate'),
    path('login/', views.APILoginView.as_view()),
    path('register/', views.APIRegisterView.as_view()),
]