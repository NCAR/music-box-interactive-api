from django.urls import path
from . import api

app_name = "plots"

urlpatterns = [
    path(
        "plots/get_basic_details/",
        api.GetBasicDetails.as_view(),
        name="get-visualize-details",
    ),
    path(
        "plots/get_contents/",
        api.GetPlotContents.as_view(),
        name="get_contents",
    ),
    path(
        "plots/get/",
        api.GetPlot.as_view(),
        name="get-plots"),
    path(
        "plots/get_flow_details/",
        api.GetFlowDetails.as_view(),
        name="get-flow-diagram-details",
    ),
    path(
        "plots/get_flow/",
        api.GetFlow.as_view(),
        name="get-flow-diagram"),
    path(
        "plots/get_D3_flow/",
        api.GetD3Flow.as_view(),
        name="get-D3-flow-diagram"),
    path(
        "plots/plot-species/",
        api.PlotSpeciesView.as_view(),
        name="plot-species",
    ),
]
