from django.urls import path, include

from vote.views1 import CustomUserDetailView, CustomUserView, ProfilElecteurDetailView, ProfilElecteurView
from . import views 

from rest_framework import routers

from vote.views import CandidatureModelViewSet, CustomUserModelViewSet, ElectionModelViewSet, ProfilElecteurModelViewSet, ProfilSuperviseurModelViewSet, VoteModelViewSet

router = routers.DefaultRouter()
#router.register(r'users', CustomUserModelViewSet)
router.register(r'electeurs', ProfilElecteurModelViewSet)
router.register(r'superiveurs', ProfilSuperviseurModelViewSet)
router.register(r'elections', ElectionModelViewSet)
router.register(r'votes', VoteModelViewSet)
router.register(r'candidatures', CandidatureModelViewSet)

urlpatterns = [
    #path('votes/', views.votes)
    path('', include(router.urls)),

    path('v2/users/', CustomUserView.as_view()),
    path('v2/users/<int:pk>/', CustomUserDetailView.as_view()),
    path('v2/electeurs/', ProfilElecteurView.as_view()),
    path('v2/electeurs/<int:pk>/', ProfilElecteurDetailView.as_view()),
    

]