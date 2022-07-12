from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
# Root url tree
# Dashboard.urls contains landing and getting started pages + conditions
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
schema = schema_view.with_ui('swagger', cache_timeout=0)
redoc = schema_view.with_ui('redoc', cache_timeout=0)
urlpatterns = [
    path('', include('dashboard.urls')),
    path('plots/', include('plots.urls')),
    path('model/', include('model_driver.urls')),
    path('mechanism/', include('mechanism.urls')),
    path('api-docs/', schema, name='schema-swagger-ui'),
    path('redoc/', redoc, name='schema-redoc')
]
