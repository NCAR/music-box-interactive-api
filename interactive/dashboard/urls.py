from django.urls import path, include

from . import views 
from . import api
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
# Root url tree
# Dashboard.urls contains landing and getting started pages
schema_view = get_schema_view(
   openapi.Info(
      title="MusicBox interactive API",
      default_version='v1',
      description="All API calls used in the MusicBox interactive",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)
app_name = 'dashboard'

urlpatterns = [
    #main page rendering paths:
    path('',          views.landing_page),
    path('home',          views.landing_page),
    path('getting_started', views.getting_started_page),
    path('visualize', views.visualize),
    path('flow', views.flow),
    path('get_flow', views.get_flow),
    path('show_flow', views.render_flow),
    # -----------------------------------
    #conditions pages rendering paths:
    path('conditions', views.options),
    path('conditions/options', views.options),
    path('conditions/initial', views.initial_conditions),
    path('conditions/evolving', views.evolving_conditions),
    # -----------------------------------
    #conditions pages editing and ajax paths:
        #initial conditions paths
    path('conditions/initial-conditions-files', views.initial_conditions_files_handler),
    path('conditions/initial-conditions-file-remove', views.initial_conditions_file_remove_handler),
    path('conditions/initial-species-concentrations', views.initial_species_concentrations_handler),
    path('conditions/initial-species-concentrations-save', views.initial_species_concentrations_save_handler),
    path('conditions/initial-reaction-rates', views.initial_reaction_rates_handler),
    path('conditions/initial-reaction-rates-save', views.initial_reaction_rates_save_handler),
    path('conditions/cond-csv', views.init_csv),
        #evolving conditions paths
    path('conditions/evolving-file', views.evolv_file),
    path('conditions/download_config', views.download_file),
    path('conditions/config_json', views.config_json),
    path('conditions/linear_combination_form', views.linear_combination_form),
    path('conditions/evolv-linear-combo', views.evolv_linear_combo),
    path('conditions/evolving-linear-combination', views.evolving_linear_combination),
    path('conditions/logging-toggle', views.toggle_logging),
    path('conditions/logging-toggle-check', views.toggle_logging_check),
    path('conditions/clear-evolv-files', views.clear_evolv_files),
    path('conditions/load-example', views.load_example),
    path('conditions/examplefile', views.example_file),
    path('conditions/remove-linear-combination', views.remove_linear),
    path('conditions/report', views.report_bug),
        #unit conversion paths
    path('conditions/convert', views.convert_values),
    path('conditions/unit-options', views.unit_options), # returns unit options for unit type in unit conversion tool
    path('conditions/conversion-calculator', views.convert_calculator),
    path('conditions/unit-conversion-arguments', views.unit_conversion_arguments),
    # -----------------------------------
    #file download paths:
    path('download_config', views.download_file),
    path('download', views.download_handler),
   
]
