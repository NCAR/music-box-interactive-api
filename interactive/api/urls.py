from django.urls import path

import api.api as api

app_name = 'api'

urlpatterns = [
    path('api/load-example/', api.LoadExample.as_view(), name='set-example'),
    path('api/run', api.RunView.as_view(), name='run'),
    path('api/run-status', api.RunStatusView.as_view(), name='run_status'),
]
