from django.urls import path

from . import views

urlpatterns = [
    path('run', views.run, name='run'),
    path('check', views.check),
    path('configure/model/run', views.run),
    path('download', views.download, name="download"),
]
