
from django.urls import path, include

urlpatterns = [
    path('', include('dashboard.urls')),
    path('model_driver/', include('model_driver.urls')),
    path('plots/', include('plots.urls')),
    path('configure/', include('configure.urls')),
    path('mechanism', include('mechanism.urls')),
]
