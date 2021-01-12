from django.shortcuts import render, redirect
from .mech_read_write import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from .speciesforms import *
from django.contrib import messages
from .reactionforms import *
from .build_response import *
from django.conf import settings
import mimetypes


def species(request):
    context = {
        'species': species_list(),
        'shortnames': species_menu_names(),
        'searchForm': SpeciesSearchForm
    }
    if 'name' in request.GET:
        messages.success(request, request.GET['name'])
    return render(request, 'mechanism/species.html', context)


def reactions(request):
    context = {
        'reacts': reaction_name_list(),
        'searchForm': ReactionSearchForm,
        'shortnames': reaction_menu_names()
    }
    return render(request, 'mechanism/reactions.html', context)


# populates species page with species info
def load(request):
    name = request.GET['name']
    stage_form_info(name)
    formresponse = build_species_form(name)
    return formresponse


def equation(request):
    # name = request.GET['name']
    # molec_dict = molecule_info()
    # hType = int(molec_dict[name]['henrys_law']['henrys_law_type'])
    
    # equations = henry_equations(hType)
    # response = HttpResponse()
    # response.write("<lh><h3>Henry's Law Coefficient:</h3><lh>")
    # for i in equations:
    #     response.write('<li><h3>' + i + '</h3></li>')
    return HttpResponse()


def save(request):
    item = id_species()
    save_species(item, request.GET.data.dict())
    messages.success(request, item)
    return HttpResponseRedirect('/mechanism/species')


def new_species(request):
    return build_new_species_form()


def new_species_save(request):
    myDict = request.GET.dict()
    new_m(myDict)
    messages.success(request, myDict['speciesname'])
    return HttpResponseRedirect('/mechanism/species')


def species_search(request):
    query = request.GET['query']
    if query in search_list():
        messages.success(request, query)
        return HttpResponseRedirect('/mechanism/species')
    else:
        messages.error(request, 'chemical species not found')
        return HttpResponseRedirect('/mechanism/species')


def load_r(request):
    return populate_react_info(request.GET['name'])


def edit_r(request):
    name = request.GET['name']
    stage_reaction_form(name)
    labels = pretty_reaction_names()
    formresponse = HttpResponse()
    r_equation = unfilled_r_equations(reaction_dict()[name]['rate_constant'])
    formresponse.write('<h2>' + name + '</h2>')
    formresponse.write('<form action="save_r" method="get" class="mechform" id="' + name + '">')
    formresponse.write('<table><h3>')
    form = ReactionForm()
    for field in form:
        formresponse.write('<tr>')
        formresponse.write('<td><h3>' + labels[str(field.name)] + '</h3></td><td>')
        formresponse.write(field)
        formresponse.write('</td></tr>')
        if labels[str(field.name)] == 'Rate Call:':
            formresponse.write('<tr><td><h3>Rate Equation:<h3></td>')
            formresponse.write('<td>' + r_equation + '</td></tr>')
    formresponse.write('</table></h3>')
    formresponse.write('<button type="submit">Save</button></form>')


    return formresponse


def save_r(request):
    data = request.GET
    myDict = data.dict()
    item = id_reaction()
    newName = save_reacts(item, myDict)
    messages.success(request, newName)
    return HttpResponseRedirect('/mechanism/reactions')


def r_to_m(request):
    messages.success(request, request.GET['name'])
    return redirect('/mechanism/species')


def reaction_equations(request):
    r_name = request.GET['name']
    rc_info = reaction_dict()[r_name]['rate_constant']
    rate_equation = reaction_rate_equations(rc_info)
    response = HttpResponse("<td><h3>" + rate_equation + "</h3></td>")
    return response


def search_reactions(request):
    query = request.GET['query']
    resultlist = reaction_search(query)
    short_result_names = []
    shortnames = reaction_menu_names()
    for name in shortnames:
        if name[0] in resultlist:
            short_result_names.append(name)

    if len(resultlist) == 0:
        messages.error(request, 'No results found')
        return HttpResponseRedirect('/mechanism/reactions')

    context = {
        'reacts': reaction_name_list(),
        'searchForm': ReactionSearchForm,
        'shortnames': short_result_names
    }
    return render(request, 'mechanism/reactions.html', context)
