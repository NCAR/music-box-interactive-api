from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',          views.configure, name='default'),
    path('visualize', views.visualize, name='visualize'),
    path('configure/options', views.options, name='options'),
    path('configure/species', views.species, name='species'),
    path('configure/init-cond', views.init, name='inital conditions'),
    path('configure/evolv-cond', views.evolv, name='evolving'),
    path('configure/photolysis', views.photolysis, name='visualize'),
    path('configure/review', views.review, name='visualize'),
]
