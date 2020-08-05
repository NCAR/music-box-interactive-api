from django.urls import path, include

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',          views.configure, name='default'),
    path('visualize', views.visualize, name='visualize'),
    path('configure/options', views.options, name='options'),
    path('configure/species', views.values, name='species'),
    path('configure/init-cond', views.init, name='inital conditions'),
    path('configure/evolv-cond', views.evolv, name='evolving'),
    path('configure/photolysis', views.photolysis, name='visualize'),
    path('configure/review', views.review, name='visualize'),
    path('configure', views.configure),
    path('configure/save-value', views.values),
    path('configure/save-formula', views.species),
    path('configure/save-unit', views.units),
    path('configure/new-species', views.new_species),
    path('configure/species-csv', views.csv),
    path('configure/cond-csv', views.init_csv),
    path('configure/cond-units', views.init_units),
    path('configure/run', views.configure),
    path('configure/model/run', include('model_driver.urls'))
]
