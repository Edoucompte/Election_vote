from django.urls import path, include

from vote.views1.candidate import CandidateApprouveView, CandidateDetailView, CandidateView, CandidateListView
from vote.views1.election import ElectionDetailView, ElectionView
from vote.views1.user import CustomUserDetailView, CustomUserView, MassUserView
from vote.views1.vote import VoteDetailView, VoteView


#from vote.views1 import CustomUserDetailView, CustomUserView, ProfilElecteurDetailView, ProfilElecteurView
from . import views 

from rest_framework import routers

from vote.views import CandidatureModelViewSet, CustomUserModelViewSet, ElectionModelViewSet, VoteModelViewSet

router = routers.DefaultRouter()
router.register(r'users', CustomUserModelViewSet)
router.register(r'elections', ElectionModelViewSet)
router.register(r'votes', VoteModelViewSet)
router.register(r'candidatures', CandidatureModelViewSet)

urlpatterns = [
    #path('votes/', views.votes)
    #path('', include(router.urls)),

    path('users/', CustomUserView.as_view(), name='User view'),
    path('users/<int:pk>/', CustomUserDetailView.as_view(), name='User detail view'),
    path('users/mass/', MassUserView.as_view()),
    path('elections/', ElectionView.as_view()),
    path('elections/<int:pk>/', ElectionDetailView.as_view()),
    path('elections/<int:election_id>/candidates/', CandidateListView.as_view(), name='Approuved candidates list'),
    # path('elections/<int:election_id>/resultats/', CandidateListView.as_view(), name='Elections results'),
    path('candidatures/', CandidateView.as_view()),
    path('candidatures/<int:pk>/', CandidateDetailView.as_view()),
    path('candidatures/<int:pk>/approuve/', CandidateApprouveView.as_view()),
    path('votes/', VoteView.as_view()),
    #path('votes/<int:pk>/', VoteDetailView.as_view()),
]