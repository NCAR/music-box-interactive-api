from django.urls import path
from . import api

urlpatterns = [
    path('api/plots/get_basic_details/',
         api.GetBasicDetails.as_view(), name='get-visualize-details'),
    path('api/plots/get_contents/',
         api.GetPlotContents.as_view(), name='get_contents'),
    path('api/plots/get/', api.GetPlot.as_view(), name='get-plots'),
    path('api/plots/get_flow_details/', api.GetFlowDetails.as_view(),
         name='get-flow-diagram-details'),
    path('api/plots/get_flow/', api.GetFlow.as_view(),
         name='get-flow-diagram'),
    path('api/plot-species/', api.PlotSpeciesView.as_view(),
         name='plot-species'),
]
