from django.urls import path

from . import api
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
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
    path('api/check-load/', api.CheckLoadView.as_view(), name='check-load'),
    path('api/check/', api.CheckView.as_view(), name='check'),
    path('api/clear_evolution_files/', api.ClearEvolutionFiles.as_view(), name='clear_evolution_files'),
    path('api/conditions-species-list/', api.ConditionsSpeciesList.as_view(), name='conditions-species-list'),
    path('api/config_json/', api.ConfigJsonUpload.as_view(), name='load-config-from-files'),
    path('api/conversion-calculator/', api.ConversionCalculator.as_view(), name='conversion-calculator'),
    path('api/convert-values/', api.ConvertValues.as_view(), name='convert-values'),

    path('api/download_config/', api.DownloadConfig.as_view(), name='download_config'),
    path('api/download_results/', api.DownloadResults.as_view(), name='download_results'),

    path('api/evolv_file/', api.EvolvFileUpload.as_view(), name='evolv_file_upload'),
    path('api/evolving-conditions/', api.EvolvingConditions.as_view(), name='evolving-conditions'),

    path('api/health/', api.HealthView.as_view(), name='health'),

    path('api/init_csv/', api.InitCSV.as_view(), name='init_csv'),
    path('api/initial-conditions-files/', api.InitialConditionsFiles.as_view(), name='initial-conditions-files'),
    path('api/initial-conditions-setup/', api.InitialConditionsSetup.as_view(), name='initial-conditions-setup'),
    path('api/initial-reaction-rates/', api.InitialReactionRates.as_view(), name='initial-initial-reaction-ratess'),
    path('api/initial-species-concentrations/', api.InitialSpeciesConcentrations.as_view(), name='initial-species-concentrations'),

    path('api/linear-combinations/', api.EvolvingConditions.as_view(), name='linear-combinations'),
    path('api/load-example/', api.ExampleView.as_view(), name='set-example'),

    path('api/model-options/', api.ModelOptionsView.as_view(), name='model-options'),

    path('api/reaction-musica-names-list/', api.MusicaReactionsList.as_view(), name='reaction-musica-names-list'),
    path('api/reaction-type-schema/', api.ReactionTypeSchemaView.as_view(), name='reaction-type-schema'),
    path('api/remove_initial_conditions_file/', api.RemoveInitialConditionsFile.as_view(), name='remove_initial_conditions_file'),
    path('api/run', api.RunView.as_view(), name='run'),

    path('api/save-reaction/', api.SaveReactionView.as_view(), name='save-reaction'),
    path('api/swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/unit-conversion-arguments/', api.UnitConversionArguments.as_view(), name='unit-conversion-arguments'),
    path('api/unit-options/', api.UnitOptions.as_view(), name='unit-options'),

    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('yaml/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
