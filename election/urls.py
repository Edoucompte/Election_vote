from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

schema_view = swagger_get_schema_view(
    openapi.Info(
        title='Api Vote election',
        default_version='v1.0.0',
        description='Cette Api permet de gerer les votes pour les elections',
        ),
        public=True
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api-auth/', include('rest_framework.urls')),

    #web endpoints
    #path('vote/', include('vote.urls')),

    # API Endpoints
    path('api/v1/', include([
        path('', include('vote.urls')),
        path('swagger/schema', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema')
        ])
    ),
]
