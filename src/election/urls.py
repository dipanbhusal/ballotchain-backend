from django.urls import path
from . import views

urlpatterns = [
    path('candidate-list/', views.CandidatesListView.as_view() ),
    path('candidate-detail/', views.CandidateDetailView.as_view() ),

    path('party-list/', views.PartiesListView.as_view() ),
    path('party-detail/', views.PartyDetailView.as_view() ),

    path('cast-vote/', views.CastVoteView.as_view() ),

    path('election-result/', views.ElectionResultView.as_view())


]