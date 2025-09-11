from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView, 
#     TokenRefreshView,
# )

from vote.views1 import ConnexionView

schema_view = swagger_get_schema_view(
    openapi.Info(
        title='Api Vote election',
        default_version='v1.0.0',
        description='Cette Api permet de gerer les votes pour les elections',
        ),
        public=True
    )

router = DefaultRouter()
router.register('auth', ConnexionView, basename='Connexion')


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api-auth/', include('rest_framework.urls')),

    #web endpoints
    #path('vote/', include('vote.urls')),

    # API Endpoints
    path('api/v1/', 
        include([
            path('', include('vote.urls')),
            path('', include(router.urls))
        ]),
    ),
    path('swagger/schema', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),

    #auth routes
    #path('api/token/', ConnexionView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh/', refresh, name='token_refresh'),
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
