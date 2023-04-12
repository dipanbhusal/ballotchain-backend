from django.urls import path 
from . import views

urlpatterns = [
    path('mine/', views.BlockMineView.as_view()),
    path('transactions/new/', views.CreateTransactionsView.as_view()),
    path('chain/', views.ListChainView.as_view()),
    path('nodes/register/', views.RegisterNodeView.as_view()),
    path('nodes/resolve/', views.NodesResolveView.as_view())
]