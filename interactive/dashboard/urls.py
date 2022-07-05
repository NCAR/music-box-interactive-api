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
    # -----------------------------------
    #api paths:
    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('yaml/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('test-view/', api.TestAPIView.as_view(), name='test-view'),


    path('api/conditions/', api.ConditionsView.as_view(), name='current-conditions'),
    # path('api/mechanisms/', api.MechanismView.as_view(), name='current-mechanisms'),

    path('api/species/', api.SpeciesView.as_view(), name='current-species'),
    path('api/species-detail/', api.SpeciesDetailView.as_view(), name='species-detail'),
    path('api/remove-species/', api.RemoveSpeciesView.as_view(), name='remove-species'),
    path('api/add-species/', api.AddSpeciesView.as_view(), name='add-species'),
    path('api/plot-species/', api.PlotSpeciesView.as_view(), name='plot-species'),

    path('api/reactions/', api.ReactionsView.as_view(), name='current-reactions'),
    path('api/reactions-detail/', api.ReactionsDetailView.as_view(), name='reactions-detail'),
    path('api/remove-reaction/', api.RemoveReactionView.as_view(), name='remove-reaction'),
    path('api/save-reaction/', api.SaveReactionView.as_view(), name='save-reaction'),
    path('api/reaction-type-schema/', api.ReactionTypeSchemaView.as_view(), name='reaction-type-schema'),

    path('api/get-model-options/', api.GetModelOptionsView.as_view(), name='get-model-options'),

    # path('api/mechanisms/add/', api.AddMechanismView.as_view(), name='add-mechanisms'),
    path('api/load-example/', api.ExampleView.as_view(), name='set-example'),
    path('api/run-model/', api.RunView.as_view(), name='run-model'),
    path('api/session-id/', api.SessionView.as_view(), name='session-id')
]
