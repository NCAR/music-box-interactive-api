from django.urls import path, include

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',          views.options, name='default'),
    path('visualize', views.visualize, name='visualize'),
    path('configure/options', views.options, name='options'),
    path('configure/species', views.species, name='species'),
    path('configure/init-cond', views.init, name='inital conditions'),
    path('configure/evolv-cond', views.evolv, name='evolving'),
    path('configure/photolysis', views.photolysis, name='visualize'),
    path('configure/review', views.review, name='visualize'),
    path('configure', views.options),
    path('configure/new-species', views.new_species),
    path('configure/save-formula', views.species),
    path('configure/species-csv', views.csv),
    path('configure/cond-csv', views.init_csv),
    path('configure/evolv-csv', views.evolv_csv),
    path('configure/photo-csv', views.photo_csv),
    path('configure/new-photo', views.new_photo),
    path('configure/run', views.configure),
    path('configure/species/remove', views.remove),
    path('configure/download_config', views.download_file),
    path('configure/config_json', views.config_json),
    path('configure/linear_combination_form', views.linear_combination_form),
    path('configure/evolv-linear-combo', views.evolv_linear_combo)
]
