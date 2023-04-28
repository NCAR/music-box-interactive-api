from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

import admin.api as api

app_name = 'admin'

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="MusicBox interactive API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include('api.urls')),
    path('', include('plots.urls')),
    path('admin/health', api.HealthView.as_view(), name='health'),
    path('admin/swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
