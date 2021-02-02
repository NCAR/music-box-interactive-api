from django.urls import path, include

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('',          views.landing_page, name='default'),
    path('home',          views.landing_page, name='default'),
    path('getting_started', views.getting_started_page, name='getting started'),
    path('visualize', views.visualize, name='visualize'),
    path('conditions/options', views.options, name='options'),
    path('conditions/species', views.species, name='species'),
    path('conditions/initial', views.initial_conditions, name='inital conditions'),
    path('conditions/evolving', views.evolving_conditions, name='evolving conditions'),
    path('conditions/review', views.review, name='visualize'),
    path('conditions', views.options),
    path('conditions/new-species', views.new_species),
    path('conditions/save-formula', views.species),
    path('conditions/species-csv', views.csv),
    path('conditions/cond-csv', views.init_csv),
    path('conditions/evolving-file', views.evolv_file),
    path('conditions/evolv-lr-txt', views.evolv_lr),
    path('conditions/photo-ncf', views.photo_ncf),
    path('conditions/new-initial-reaction-rate', views.new_initial_reaction_rate),
    path('conditions/initial-reaction-rates', views.initial_reaction_rates),
    path('conditions/run', views.conditions),
    path('conditions/species/remove', views.remove),
    path('conditions/download_config', views.download_file),
    path('conditions/config_json', views.config_json),
    path('conditions/linear_combination_form', views.linear_combination_form),
    path('conditions/evolv-linear-combo', views.evolv_linear_combo),
    path('conditions/evolving-linear-combination', views.evolving_linear_combination),
    path('conditions/photo_datetime_form', views.photo_dt_form),
    path('conditions/photo_start_results', views.save_photo_dt),
    path('conditions/logging-toggle', views.toggle_logging),
    path('conditions/logging-toggle-check', views.toggle_logging_check),
    path('conditions/clear-evolv-files', views.clear_evolv_files),
    path('conditions/load-example', views.load_example),
    path('conditions/examplefile', views.example_file)
]
