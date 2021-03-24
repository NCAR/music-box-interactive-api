from django.urls import path, include
from . import views

urlpatterns = [
    # page rendering paths:
    path('', views.species_home_handler),                                         # renders the chemical species page
    path('reactions', views.reactions_home_handler),                              # renders the reactions page
    path('species', views.species_home_handler),                                  # renders the chemical species page
    # -----------------------------------
    # data returning paths:
    path('conditions-species-list', views.conditions_species_list_handler),       # returns a list of species
    path('reaction-detail', views.reaction_detail_handler),                       # returns a json object for a reaction from the mechanism
    path('reaction-musica-names-list', views.reaction_musica_names_list_handler), # returns the set of reactions with MUSICA names
    path('reaction-type-schema', views.reaction_type_schema_handler),             # returns the schema for a reaction type
    path('species-detail', views.species_detail_handler),                         # returns a json object for a chemical species
    # -----------------------------------
    #editing paths:
    path('reaction-remove', views.reaction_remove_handler),                       # removes a reaction
    path('reaction-save', views.reaction_save_handler),                           # saves a reaction
    path('species-remove', views.species_remove_handler),                         # removes a chemical species
    path('species-save', views.species_save_handler)                              # saves a chemical species
    ]
