from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.species_home_handler),
    path('reactions', views.reactions_home_handler),
    path('reaction-detail', views.reaction_detail_handler),
    path('reaction-musica-names', views.reaction_musica_names_handler),
    path('reaction-type-schema', views.reaction_type_schema_handler),
    path('reaction-remove', views.reaction_remove_handler),
    path('reaction-save', views.reaction_save_handler),
    path('species', views.species_home_handler),
    path('species-detail', views.species_detail_handler),
    path('species-remove', views.species_remove_handler),
    path('species-save', views.species_save_handler),
    ]
