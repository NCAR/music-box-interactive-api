from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.mechanism),
    path('molecules', views.molecules),
    path('reactions', views.reactions)
    ]
