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
    # main page rendering paths:
    path('',          views.landing_page),
    path('home',          views.landing_page),
    path('getting_started', views.getting_started_page),
    path('visualize', views.visualize),
    path('flow', views.flow),
    path('get_flow', views.get_flow),
    path('show_flow', views.render_flow),
    # -----------------------------------
    # conditions pages rendering paths:
    path('conditions', views.options),
    path('conditions/options', views.options),
    path('conditions/initial', views.initial_conditions),
    path('conditions/evolving', views.evolving_conditions),
    # -----------------------------------
    # conditions pages editing and ajax paths:
    # initial conditions paths
    path('conditions/initial-conditions-files',
         views.initial_conditions_files_handler),
    path('conditions/initial-conditions-file-remove',
         views.initial_conditions_file_remove_handler),
    path('conditions/initial-species-concentrations',
         views.initial_species_concentrations_handler),
    path('conditions/initial-species-concentrations-save',
         views.initial_species_concentrations_save_handler),
    path('conditions/initial-reaction-rates',
         views.initial_reaction_rates_handler),
    path('conditions/initial-reaction-rates-save',
         views.initial_reaction_rates_save_handler),
    path('conditions/cond-csv', views.init_csv),
    # evolving conditions paths
    path('conditions/evolving-file', views.evolv_file),
    path('conditions/download_config', views.download_file),
    path('conditions/config_json', views.config_json),
    path('conditions/linear_combination_form', views.linear_combination_form),
    path('conditions/evolv-linear-combo', views.evolv_linear_combo),
    path('conditions/evolving-linear-combination',
         views.evolving_linear_combination),
    path('conditions/logging-toggle', views.toggle_logging),
    path('conditions/logging-toggle-check', views.toggle_logging_check),
    path('conditions/clear-evolv-files', views.clear_evolv_files),
    path('conditions/load-example', views.load_example),
    path('conditions/examplefile', views.example_file),
    path('conditions/remove-linear-combination', views.remove_linear),
    path('conditions/report', views.report_bug),
    # unit conversion paths
    path('conditions/convert', views.convert_values),
    # returns unit options for unit type in unit conversion tool
    path('conditions/unit-options', views.unit_options),
    path('conditions/conversion-calculator', views.convert_calculator),
    path('conditions/unit-conversion-arguments',
         views.unit_conversion_arguments),
    # -----------------------------------
    # file download paths:
    path('download_config', views.download_file),
    path('download', views.download_handler),
    # -----------------------------------
    # api paths:
    path('api-docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('yaml/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),

    path('api/remove-species/', api.RemoveSpeciesView.as_view(),
         name='remove-species'),
    path('api/add-species/', api.AddSpeciesView.as_view(),
         name='add-species'),
    path('api/plot-species/', api.PlotSpeciesView.as_view(),
         name='plot-species'),

    path('api/remove-reaction/', api.RemoveReactionView.as_view(),
         name='remove-reaction'),
    path('api/save-reaction/', api.SaveReactionView.as_view(),
         name='save-reaction'),
    path('api/reaction-type-schema/',
         api.ReactionTypeSchemaView.as_view(), name='reaction-type-schema'),

    path('api/model-options/', api.ModelOptionsView.as_view(),
         name='model-options'),
    path('api/initial-conditions-files/',
         api.InitialConditionsFiles.as_view(),
         name='initial-conditions-files'),
    path('api/initial-species-concentrations/',
         api.InitialSpeciesConcentrations.as_view(),
         name='initial-species-concentrations'),
    path('api/initial-conditions-setup/',
         api.InitialConditionsSetup.as_view(),
         name='initial-conditions-setup'),

    path('api/initial-reaction-rates/', api.InitialReactionRates.as_view(),
         name='initial-initial-reaction-ratess'),
    path('api/conditions-species-list/',
         api.ConditionsSpeciesList.as_view(), name='conditions-species-list'),
    path('api/reaction-musica-names-list/',
         api.MusicaReactionsList.as_view(),
         name='reaction-musica-names-list'),

    path('api/convert-values/', api.ConvertValues.as_view(),
         name='convert-values'),
    path('api/unit-conversion-arguments/',
         api.UnitConversionArguments.as_view(),
         name='unit-conversion-arguments'),
    path('api/unit-options/', api.UnitOptions.as_view(), name='unit-options'),
    path('api/conversion-calculator/', api.ConversionCalculator.as_view(),
         name='conversion-calculator'),

    path('api/evolving-conditions/', api.EvolvingConditions.as_view(),
         name='evolving-conditions'),
    path('api/linear-combinations/', api.EvolvingConditions.as_view(),
         name='linear-combinations'),

    path('api/health/', api.HealthView.as_view(), name='health'),
    path('api/check-load/', api.CheckLoadView.as_view(), name='check-load'),
    path('api/check/', api.CheckView.as_view(), name='check'),
    path('api/run/', api.RunView.as_view(), name='run'),

    path('api/plots/get_basic_details/',
         api.GetBasicDetails.as_view(), name='get-visualize-details'),
    path('api/plots/get_contents/',
         api.GetPlotContents.as_view(), name='get_contents'),
    path('api/plots/get/', api.GetPlot.as_view(), name='get-plots'),
    path('api/plots/get_flow_details/', api.GetFlowDetails.as_view(),
         name='get-flow-diagram-details'),
    path('api/plots/get_flow/', api.GetFlow.as_view(),
         name='get-flow-diagram'),

    path('api/download_config/', api.DownloadConfig.as_view(),
         name='download_config'),
    path('api/download_results/', api.DownloadResults.as_view(),
         name='download_results'),

    path('api/config_json/', api.ConfigJsonUpload.as_view(),
         name='load-config-from-files'),
    path('api/remove_initial_conditions_file/',
         api.RemoveInitialConditionsFile.as_view(),
         name='remove_initial_conditions_file'),
    path('api/init_csv/', api.InitCSV.as_view(), name='init_csv'),
    path('api/clear_evolution_files/', api.ClearEvolutionFiles.as_view(),
         name='clear_evolution_files'),
    path('api/evolv_file/', api.EvolvFileUpload.as_view(),
         name='evolv_file_upload'),

    path('api/load-example/', api.ExampleView.as_view(), name='set-example'),
    path('api/run-model/', api.RunView.as_view(), name='run-model')
]
