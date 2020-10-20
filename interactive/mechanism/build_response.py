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


def populate_react_info(name):
    info = reaction_dict()[name]
    response = HttpResponse()
    shortname = convert_reaction_format(name)
    if len(name) > 40:
        shortname = name[0:38] + '...'
    response.write('<h2>' + shortname + '</h2><h3>')
    response.write('<button id="mech_edit" r_type="' + info['rate constant']["type"] + '"class="mech_edit_R" reaction="'+ name + '">Edit</button>')
    response.write('<li>Reaction Type: ' + info['type'] + '</li>')

    response.write('<li><table><tr><td>Reactants:</td><td>')
    for reactant in info['reactants']:
        response.write('<li><a href="/mechanism/searchM?query=' + reactant + '">' + reactant + '</a></li>')
    response.write('</td></tr></table></li>')

    response.write('<li><table><tr><td>Products:</td><td>')
    for prod in info['products']:
        response.write('<li><a href="/mechanism/searchM?query=' + prod + '">' + info['products'][prod]['yield'] + ' ' + prod + '</a></li>')
    response.write('</td></tr></table></li>')

    response.write('<table><tr><td>Rate Constant Type:</td><td>' + info['rate constant']['type'] + '</td></tr>')
    for param in info['rate constant']['parameters']:
        response.write('<tr><td>' + param + ':</td><td>' + str(info['rate constant']['parameters'][param]['value']) + ' ' + info['rate constant']['parameters'][param]['unit'] + '</td></tr>')


    
        
        # response.write('<table><tr><td><h3>Rate:</h3></td><td><h3>' + str(info['rate']) + '</h3></td></tr>')
        # response.write('<tr><td><h3>Photolysis:</h3></td><td><h3>False</h3></td></tr>')
        # response.write('<tr><td><h3>Reactants:</h3></td><td><h3>')
        # for reactant in info['reactants']:
        #     response.write('<li><a href="molecules?name=' + reactant + '" id="' + reactant + '">' + reactant + '<a></li>') 
        # response.write('</h3></td></tr>')
        # response.write('<tr  id="rc_row" ><td><h3>Reaction Class:</h3></td><td><h3>' + info['rate_constant']['reaction_class'] + '</h3></td></tr>')
        # response.write('<tr><td><h3>Rate Constant Parameters:</h3></td><td><h3><table>')
        # for param in info['rate_constant']['parameters']:
        #     response.write('<tr><td>' + param_jax(param) + '</td><td>' + sci_note_jax(str(info['rate_constant']['parameters'][param])) + '</td></tr>')
        # response.write('</table></h3></td></tr>')
        # response.write('<tr><td><h3>Troe:</h3></td><td><h3>' + str(info['troe']) + '</h3></td></tr>')
        # response.write('<tr><td><h3>Products:</h3></td><td><h3>')
        # for product in info['products']:
        #     if product['coefficient'] == 1:
        #         product['coefficient'] = ''
        #     response.write('<li>' + str(product['coefficient']) + ' ' + '<a href="molecules?name=' + product['molecule'] + '" id="' + product['molecule'] + '">' + product['molecule'] + '</a></li>') 
        # response.write('</h3></td></tr></table>')
    response.write('</h3>')
    return response
    
    