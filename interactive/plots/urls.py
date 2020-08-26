from django.urls import path
from . import views

urlpatterns = [
    path('', views.get, name='get'),
    path('get_contents', views.get_contents),
    path('get', views.get, name='get'),
]
