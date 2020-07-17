from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',          views.run_model, name='run_model'),
    path('run_model', views.run_model, name='run_model'),
    path('species',   views.species,   name='species'),
    path('reactions', views.reactions, name='reactions'),
    path('visualize', views.visualize, name='visualize'),
]
