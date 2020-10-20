from django.shortcuts import render, redirect
from .mech_read_write import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from .moleculeforms import *
from django.contrib import messages
from .reactionforms import *
from .build_response import *
from django.conf import settings
import mimetypes


def molecules(request):
    context = {
        'molecs': molecule_list(),
        'shortnames': molecule_menu_names(),
        'searchForm': MoleculeSearchForm
    }
    if 'name' in request.GET:
        messages.success(request, request.GET['name'])
    return render(request, 'mechanism/molecules.html', context)


def reactions(request):
    context = {
        'reacts': reaction_name_list(),
        'searchForm': ReactionSearchForm,
        'shortnames': reaction_menu_names()
    }
    return render(request, 'mechanism/reactions.html', context)


# populates molecule page with species info
def load(request):
    item = request.GET['name']
    response = populate_mol_info(item)
    return response


def edit(request):
    name = request.GET['name']
    stage_form_info(name)
    formresponse = build_mol_edit_form(name)
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
    item = id_molecule()
    data = request.GET
    myDict = data.dict()
    save_mol(item, myDict)
    messages.success(request, item)

    return HttpResponseRedirect('/mechanism/molecules')


def new_molec(request):
    return build_new_mol_form()


def new_molec_save(request):
    data = request.GET
    myDict = data.dict()
    newMoleculeName = myDict['moleculename']
    new_m(myDict)
    messages.success(request, newMoleculeName)

    return HttpResponseRedirect('/mechanism/molecules')


def molec_search(request):
    query = request.GET['query']
    mechlist = search_list()
    if query in mechlist:
        messages.success(request, query)
        return HttpResponseRedirect('/mechanism/molecules')
    else:
        messages.error(request, 'molecule not found')
        return HttpResponseRedirect('/mechanism/molecules')


def load_r(request):
    name = request.GET['name']
    
    return populate_react_info(name)


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
    name = request.GET['name']
    messages.success(request, name)
    return redirect('/mechanism/molecules')


def download_mechanism(request):
    fl_path = os.path.join(settings.BASE_DIR, 'dashboard/static/mechanism/datamolec_info.json')
    filename = 'datamolec_info.json'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


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
