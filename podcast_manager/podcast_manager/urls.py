"""
URL configuration for podcast_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view as get_yasg_view
from drf_yasg import openapi
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# drf-yasg Swagger schema
yasg_schema_view = get_yasg_view(
    openapi.Info(
        title="Podcast Episode Manager API",
        default_version='v1',
        description="Swagger API documentation (drf-yasg)",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    
     # drf-yasg (Swagger)
    re_path(r'^swagger/$', yasg_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', yasg_schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # drf-spectacular
    path('spectacular/schema/', SpectacularAPIView.as_view(), name='schema'),  # Schema JSON
    path('spectacular/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('spectacular/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)