from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.species),
    path('species', views.species),
    path('reactions', views.reactions),
    path('load', views.load),
    path('equation', views.equation),
    path('save', views.save),
    path('newspecies', views.new_species),
    path('newM', views.new_species_save),
    path('searchM', views.species_search),
    path('load_reaction', views.load_r),
    path('save_r', views.save_r),
    path('r_to_m', views.r_to_m),
    path("load_reaction_equation", views.reaction_equations),
    path('searchR', views.search_reactions)
    ]
