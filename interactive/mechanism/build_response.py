from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from .mech_read_write import *
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from .moleculeforms import *
from django.contrib import messages
from .reactionforms import *
from .build_response import *
from django.conf import settings
import mimetypes


def populate_mol_info(item):

    molec_dict = molecule_info()
    info = molec_dict[item]
    response = HttpResponse()
    labels = pretty_names()
    response.write('<h2>' + item + '</h2>')
    response.write('<h3><a href="/mechanism/searchR?query=' + item + '">View reactions</a></h3>')
    response.write('<button id="mech_edit" h_type="" class="mech_edit" species="'+ item + '">Edit</button>')
    response.write('<h3><table>')
    response.write('<tr><td>Formula:<td><td>' + str(info['formula']) + '</td></tr>')
    response.write('<tr><td>Molecular Weight:<td><td>' + str(info['molecular weight']['value']) + '</td><td>' + info['molecular weight']['units'] + '</td></tr>')
    response.write('<tr><td>Henrys Law:</td>')
    response.write('<td><table><tr><td>At 298K:</td><td>' + str(info['henrys law constant']['at 298K']['value']) + '</td><td>' + info['henrys law constant']['at 298K']['units'] + '</td></tr>')
    response.write('<tr><td>Exponential Factor:</td><td>' + str(info['henrys law constant']['exponential factor']['value']) + '</td><td>' + info['henrys law constant']['exponential factor']['units'] + '</td></tr>')
    response.write('</table></td></tr>')

    return response



def build_mol_edit_form(name):
    labels = pretty_names()
    molec_dict = molecule_info()
    info = molec_dict[name]
    formresponse = HttpResponse()
    formresponse.write('<h2>' + name + '</h2>')
    formresponse.write('<form action="save" method="get" class="mechform" id="' + name + '">')
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


def build_new_mol_form():
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