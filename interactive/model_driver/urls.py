from django.urls import path
from . import views

urlpatterns = [
    path('run', views.run, name='run'),
    path('check', views.check),
    path('download', views.download, name="download"),
    path('check-load', views.check_load)
]
