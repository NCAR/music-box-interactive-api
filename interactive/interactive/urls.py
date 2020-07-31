
from django.urls import path, include

urlpatterns = [
    path('', include('dashboard.urls')),
    path('plots/', include('plots.urls')),
    path('configure/', include('dashboard.urls')),
    path('model/', include('model_driver.urls')),
    path('mechanism/', include('mechanism.urls'))
]
