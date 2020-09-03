from django.shortcuts import render
from .mech_load import *
from django.http import HttpResponse, HttpRequest
from .moleculeforms import *

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
    labels = pretty_names()
    response.write('<h2>' + info['moleculename'] + '</h2>')
    response.write('<table><tr><td><h3>Solve Type:</h3></td><td><h3>' + info['solve'] + '</h3></td></tr>')
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
    formresponse.write('<form method="post" class="mechform" id="' + name + '">')
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