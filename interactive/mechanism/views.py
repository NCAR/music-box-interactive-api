from django.shortcuts import render
from .mech_load import *
from django.http import HttpResponse, HttpRequest


def molecules(request):
    context = {
        'molecs': molecule_list()
    }
    return render(request, 'mechanism/molecules.html', context)


def reactions(request):
    context = {}
    return render(request, 'mechanism/reactions.html', context)


def load(request):
    molec_dict = molecule_info()
    item = request.GET['name']
    info = molec_dict[item]
    response = HttpResponse()
    response.write('<h2>' + info['moleculename'] + '</h2>')
    
    return response