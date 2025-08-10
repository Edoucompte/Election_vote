from django.urls import path, include
from . import views 

from rest_framework import routers

from vote.views import CandidatureModelViewSet, CustomUserModelViewSet, ElectionModelViewSet, ProfilElecteurModelViewSet, ProfilSuperviseurModelViewSet, VoteModelViewSet

router = routers.DefaultRouter()
router.register(r'users', CustomUserModelViewSet)
router.register(r'electeurs', ProfilElecteurModelViewSet)
router.register(r'superiveurs', ProfilSuperviseurModelViewSet)
router.register(r'elections', ElectionModelViewSet)
router.register(r'votes', VoteModelViewSet)
router.register(r'candidatures', CandidatureModelViewSet)

urlpatterns = [
    #path('votes/', views.votes)
    path('', include(router.urls))
]