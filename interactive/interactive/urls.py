from django.urls import path, include
# Root url tree
# Dashboard.urls contains landing and getting started pages + conditions editing pages

urlpatterns = [
    path('', include('dashboard.urls')),
    path('plots/', include('plots.urls')),
    path('model/', include('model_driver.urls')),
    path('mechanism/', include('mechanism.urls'))
]
