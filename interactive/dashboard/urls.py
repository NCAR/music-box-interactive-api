from django.urls import path, include

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',          views.landing_page, name='default'),
    path('intro',     views.landing_page, name='intro'),
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
    path('configure/evolv-lr-txt', views.evolv_lr),
    path('configure/photo-ncf', views.photo_ncf),
    path('configure/new-photo', views.new_photo),
    path('configure/run', views.configure),
    path('configure/species/remove', views.remove),
    path('configure/download_config', views.download_file),
    path('configure/config_json', views.config_json),
    path('configure/linear_combination_form', views.linear_combination_form),
    path('configure/evolv-linear-combo', views.evolv_linear_combo),
    path('configure/photo_datetime_form', views.photo_dt_form),
    path('configure/photo_start_results', views.save_photo_dt),
    path('configure/logging-toggle', views.toggle_logging),
    path('configure/logging-toggle-check', views.toggle_logging_check),
    path('configure/clear-evolv-files', views.clear_evolv_files)
]
