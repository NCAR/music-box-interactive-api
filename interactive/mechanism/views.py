from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from .reactions import *
from .species import *
import mimetypes
from interactive.tools import *
from .network_plot import *

# returns a list of species whose concentrations can be specified
def conditions_species_list_handler(request):
    species_list = { "species" : conditions_species_list() }
    return JsonResponse(species_list)


# returns a json object for a chemical species from the mechanism
def species_detail_handler(request):
    if not 'name' in request.GET:
        return JsonResponse({"error":"missing species name"})
    for entry in species_info():
        if entry['type'] == 'CHEM_SPEC' and entry['name'] == request.GET['name']:
            species_convert_to_SI(entry)
            return JsonResponse(entry)
    return JsonResponse({})


# renders the chemical species page
def species_home_handler(request):
    context = {
        'species_menu_names': species_menu_names(),
    }
    return render(request, 'mechanism/species.html', context)


# removes a chemical species from the mechanism
def species_remove_handler(request):
    if not 'name' in request.GET:
        return HttpResponseBadRequest("missing species name")
    species_remove(request.GET['name'])
    return HttpResponse('')


# saves a chemical species to the mechanism
def species_save_handler(request):
    if request.method != 'POST':
        return JsonResponse({"error":"saving chemical species should be POST request"})
    species_data = json.loads(request.body)
    if not 'name' in species_data:
        return JsonResponse({"error":"missing species name"})
    species_data['type'] = "CHEM_SPEC"
    species_remove(species_data['name'])
    species_save(species_data)
    return JsonResponse({})


# renders the reactions page
def reactions_home_handler(request):
    context = {
        'reaction_menu_names': reaction_menu_names()
    }
    return render(request, 'mechanism/reactions.html', context)


# returns a json object for a reaction from the mechanism
def reaction_detail_handler(request):
    if not 'index' in request.GET:
        return JsonResponse({"error":"missing reaction index"})
    reaction_detail = reactions_info()[int(request.GET['index'])]
    reaction_detail['index'] = int(request.GET['index'])
    return JsonResponse(reaction_detail)


# returns the set of reactions with MUSICA names and units for setting rates/rate constants
def reaction_musica_names_list_handler(request):
    musica_names = reaction_musica_names()
    return JsonResponse({ 'reactions': musica_names })


# returns the schema for a particular reaction type
def reaction_type_schema_handler(request):
    if not 'type' in request.GET:
        return JsonResponse({"error":"missing reaction type"})
    schema = reaction_type_schema(request.GET['type'])
    return JsonResponse(schema)


# removes a reaction from the mechanism
def reaction_remove_handler(request):
    if not 'index' in request.GET:
        return HttpResponseBadRequest("missing reaction index")
    reaction_remove(int(request.GET['index']))
    return HttpResponse('')


# saves a reaction to the mechanism
def reaction_save_handler(request):
    if request.method != 'POST':
        return JsonResponse({"error":"saving a reaction should be a POST request"})
    reaction_data = json.loads(request.body)
    reaction_save(reaction_data)
    return JsonResponse({})


# creates network plot
def species_network_plotter(request):
    species = request.GET['name']
    generate_network_plot()
    return render(request, 'network_plot/plot.html')