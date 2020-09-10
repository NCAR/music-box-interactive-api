from django.shortcuts import render
from .mech_load import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .moleculeforms import *
from django.contrib import messages
from .reactionforms import *

def molecules(request):
    context = {
        'molecs': molecule_list(),
        'searchForm': MoleculeSearchForm
    }
    return render(request, 'mechanism/molecules.html', context)


def reactions(request):
    context = {
        'reacts': reaction_name_list(),
        'searchForm': ReactionSearchForm
    }
    return render(request, 'mechanism/reactions.html', context)


def load(request):
    molec_dict = molecule_info()
    item = request.GET['name']
    info = molec_dict[item]
    response = HttpResponse()
    labels = pretty_names()
    response.write('<h2>' + info['moleculename'] + '</h2>')
    response.write('<button id="mech_edit" h_type="' + info['henrys_law']["henrys_law_type"] + '"class="mech_edit" species="'+ info['moleculename'] + '">Edit</button>')
    response.write('<table><tr><td><h3>Solve Type:</h3></td><td><h3>' + info['solve'] + '</h3></td></tr>')
    if info['formula'] is not None:
        response.write('<tr><td><h3>Formula:</h3></td><td><h3>' + info['formula'] + '</h3></td></tr>')
    response.write('<tr><td><h3>Transport:</h3></td><td><h3>' + info['transport'] + '</h3></td></tr>')
    response.write('<tr><td><h3>Molecular Weight:</h3></td><td><h3>' + info['molecular_weight'] + '</h3></td></tr>')
    response.write('<tr><td><h3>Standard Name:</h3></td><td><h3>' + info['standard_name'] + '</h3></td></tr></table>')
    response.write('<table>')
    for key in info['henrys_law']:
        response.write('<tr><td><h3>' + labels[key] + '</h3></td><td><h3>' + info['henrys_law'][key] + '</h3></td></tr>')
    response.write('</table><button id="mech_edit" h_type="' + info['henrys_law']["henrys_law_type"] + '"class="mech_edit" species="'+ info['moleculename'] + '">Edit</button>')
    return response


def edit(request):
    name = request.GET['name']
    stage_form_info(name)
    labels = pretty_names()
    molec_dict = molecule_info()
    info = molec_dict[name]
    formresponse = HttpResponse()
    formresponse.write('<h2>' + info['moleculename'] + '</h2>')
    formresponse.write('<form action="save" method="get" class="mechform" id="' + name + '">')
    # formresponse.write('{% csrf_token %}')
    form = MoleculeForm()
    formresponse.write('<table>')
    for field in form:
        formresponse.write('<tr>')
        formresponse.write('<td><h3>' + labels[str(field.name)] + '</h3></td><td>')
        formresponse.write(field)
        formresponse.write('</td></tr>')
    formresponse.write('</table>')
    formresponse.write('<button type="submit">Save</button>')
    formresponse.write('</form>')

    return formresponse


def equation(request):
    name = request.GET['name']
    molec_dict = molecule_info()
    hType = int(molec_dict[name]['henrys_law']['henrys_law_type'])
    
    equations = henry_equations(hType)
    response = HttpResponse()
    response.write("<lh><h3>Henry's Law Coefficient:</h3><lh>")
    for i in equations:
        response.write('<li><h3>' + i + '</h3></li>')
    return response


def save(request):
    item = id_molecule()
    data = request.GET
    myDict = data.dict()
    save_mol(item, myDict)
    messages.success(request, item)

    return HttpResponseRedirect('/mechanism/molecules')


def new_molec(request):
    labels = pretty_names()
    formresponse = HttpResponse()
    formresponse.write('<h2>Add new molecule</h2>')
    formresponse.write('<form action="newM" method="get" class="mechform" id="newmolecform">')
    form = NewMoleculeForm()
    formresponse.write('<table>')
    for field in form:
        formresponse.write('<tr>')
        formresponse.write('<td><h3>' + labels[str(field.name)] + '</h3></td><td>')
        formresponse.write(field)
        formresponse.write('</td></tr>')
    formresponse.write('</table>')
    formresponse.write('<button type="submit">Save to mechanism</button>')
    formresponse.write('</form>')

    return formresponse


def new_molec_save(request):
    data = request.GET
    myDict = data.dict()
    newMoleculeName = data['moleculename']
    new_m(myDict)
    messages.success(request, newMoleculeName)

    return HttpResponseRedirect('/mechanism/molecules')


def molec_search(request):
    query = request.GET['query']
    mechlist = search_list()
    if (query in mechlist):
        messages.success(request, query)
        return HttpResponseRedirect('/mechanism/molecules')
    else:
        messages.error(request, 'molecule not found')
        return HttpResponseRedirect('/mechanism/molecules')


def load_r(request):
    name = request.GET['name']
    info = reaction_dict()[name]
    response = HttpResponse()
    response.write('<h2>' + name + '</h2>')
    response.write('<button id="mech_edit" r_type="' + info['rate_constant']["reaction_class"] + '"class="mech_edit_R" reaction="'+ name + '">Edit</button>')
    response.write('<table><tr><td><h3>Rate:</h3></td><td><h3>' + str(info['rate']) + '</h3></td></tr>')
    response.write('<tr><td><h3>Reactants:</h3></td><td><h3>')
    for reactant in info['reactants']:
        response.write('<li>' + reactant + '</li>') 
    response.write('</h3></td></tr>')
    response.write('<tr><td><h3>Rate Call:</h3></td><td><h3>' + info['rate_call'] + '</h3></td></tr>')
    response.write('<tr><td><h3>Rate Constant Parameters:</h3></td><td><h3><table>')
    for param in info['rate_constant']['parameters']:
        response.write('<tr><td>' + param + '</td><td>' + str(info['rate_constant']['parameters'][param]) + '</td></tr>')
    response.write('</table></h3></td></tr>')
    response.write('<tr><td><h3>Reaction Class:</h3></td><td><h3>' + info['rate_constant']['reaction_class'] + '</h3></td></tr>')
    response.write('<tr><td><h3>Troe:</h3></td><td><h3>' + str(info['troe']) + '</h3></td></tr>')
    response.write('<tr><td><h3>Products:</h3></td><td><h3>')
    for product in info['products']:
        if product['coefficient'] == 1:
             product['coefficient'] = ''
        response.write('<li>' + str(product['coefficient']) + ' ' + product['molecule'] + '</li>') 
    response.write('</h3></td></tr></table>')
    
    return response


def edit_r(request):
    name = request.GET['name']
    stage_reaction_form(name)
    labels = pretty_reaction_names()
    formresponse = HttpResponse()
    formresponse.write('<h2>' + name + '</h2>')
    formresponse.write('<form action="save_r" method="get" class="mechform" id="' + name + '">')
    formresponse.write('<table><h3>')
    form = ReactionForm()
    for field in form:
        formresponse.write('<tr>')
        formresponse.write('<td><h3>' + labels[str(field.name)] + '</h3></td><td>')
        formresponse.write(field)
        formresponse.write('</td></tr>')
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
