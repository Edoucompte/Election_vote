from django.urls import path, include

from vote.views1 import CandidateView, CandidateDetailView
from vote.views1.election import ElectionDetailView, ElectionView
from vote.views1.user import CustomUserDetailView, CustomUserView
from vote.views1.vote import VoteDetailView, VoteView


#from vote.views1 import CustomUserDetailView, CustomUserView, ProfilElecteurDetailView, ProfilElecteurView
#from . import views 

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

    path('v2/users/', CustomUserView.as_view()),
    path('v2/users/<int:pk>/', CustomUserDetailView.as_view()),
    path('v2/elections/', ElectionView.as_view()),
    path('v2/elections/<int:pk>/', ElectionDetailView.as_view()),
    path('v2/candidatures/', CandidateView.as_view()),
    path('v2/candidatures/<int:pk>/', CandidateDetailView.as_view()),
    path('v2/votes/', VoteView.as_view()),
    path('v2/votes/<int:pk>/', VoteDetailView.as_view()),
    

]