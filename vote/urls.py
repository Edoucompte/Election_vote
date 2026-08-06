from django.urls import path, include

from vote.views1.candidate import CandidateApprouveView, CandidateDetailView, CandidateView, CandidateListView
from vote.views1.election import ElectionDetailView, ElectionView

from vote.views1.user import CustomUserDetailView, CustomUserView, MassUserView, ResetUserPasswordView, \
    ConnectedUserView
from vote.views1.vote import VoteDetailView, VoteView
from vote.views1.stats import ElectionResultsView, ElectionStatsView, OrganisationStatsView, ElectorStatsView, \
    SendElectionResultsView


#from vote.views1 import CustomUserDetailView, CustomUserView, ProfilElecteurDetailView, ProfilElecteurView
from . import views 

from rest_framework import routers

from vote.views import CandidatureModelViewSet, CustomUserModelViewSet, ElectionModelViewSet, VoteModelViewSet

router = routers.DefaultRouter()
router.register(r'users/reset_password', ResetUserPasswordView, basename='user' )
# router.register(r'users', CustomUserModelViewSet)
# router.register(r'elections', ElectionModelViewSet)
# router.register(r'votes', VoteModelViewSet)
# router.register(r'candidatures', CandidatureModelViewSet)

urlpatterns = [
    #path('votes/', views.votes)
    path('', include(router.urls)),

    path('users/', CustomUserView.as_view(), name='User view'),
    path('users/<int:pk>/', CustomUserDetailView.as_view(), name='User detail view'),
    path('users/mass/', MassUserView.as_view()),
    path('users/candidatures/', ConnectedUserView.as_view({
        'get': 'get_connected_user_candidatures',
        'post': 'create_connected_user_candidature'
    }), name='Connected user view'),
    path('elections/', ElectionView.as_view()),
    path('elections/<int:pk>/', ElectionDetailView.as_view()),
    path('elections/<int:election_id>/candidates/', CandidateListView.as_view(), name='Approuved candidates list'),
    path('elections/<int:pk>/results/', ElectionResultsView.as_view(), name='Election results'),
    path('elections/<int:pk>/stats/', ElectionStatsView.as_view(), name='Election stats'),
    path('elections/<int:pk>/send-results/', SendElectionResultsView.as_view(), name='Send election results'),
    path('organisations/me/stats/', OrganisationStatsView.as_view(), name='Organisation stats'),
    path('electeur/stats/', ElectorStatsView.as_view(), name='Elector stats'),
    path('candidatures/', CandidateView.as_view()),
    path('candidatures/<int:pk>/', CandidateDetailView.as_view()),
    path('candidatures/<int:pk>/approuve/', CandidateApprouveView.as_view()),
    path('votes/', VoteView.as_view()),
    #path('votes/<int:pk>/', VoteDetailView.as_view()),
]