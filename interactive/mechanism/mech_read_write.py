import json
from django.conf import settings
import logging
import os
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def molecule_info():
    logging.info('getting molecule_info')
    mechanism = open_json('datamolec_info.json')['mechanism']
    return mechanism['species']


def molecule_list():
    mechanism = open_json('datamolec_info.json')['mechanism']
    molecules = mechanism['species']
    return list(molecules.keys())


def molecule_menu_names():
    m_list = molecule_list()
    newlist = []
    for name in m_list:
        if len(name) > 8:
            shortname = name[0:8] + '..'
            newlist.append(shortname)
        else:
            newlist.append(name)
    zipped = zip(m_list, newlist)
    return zipped


def henry_equations(value):
    equation1 = "\\" + "begin{equation} H_{e f f}=K_{H}\left(1+" + "\\" + "frac{K_{1}}{K_{2}}[H+]" + "\\" + "right) " + "\\" + "end{equation}"
    equation2 = "\\" + "begin{equation}H_{e f f}=K_{H}" + "\\" + "left(1+" + "\\" + "frac{K_{1}}{[H+]}" + "\\" + "left(1+" + "\\" + "frac{K_{2}}{[H+]}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    equation3 = "\\" + "begin{equation}K_{H}=\mathrm{kh}_{298} " + "\\" + "exp " + "\\" + "left(" + "\\" + "mathrm{dh}_{r}" + "\\" + "left(" + "\\" + "frac{1}{T}-" + "\\" + "frac{1}{298}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    equation4 = "\\" + "begin{equation}K_{1}=\mathrm{k} 1_{298} " + "\\" + "exp " + "\\" + "left(" + "\\" + "operatorname{dh} 1_{r}" + "\\" + "left(" + "\\" + "frac{1}{T}-" + "\\" + "frac{1}{298}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    equation5 = "\\" + "begin{equation}K_{2}=\mathrm{k} 2_{298} " + "\\" + "exp " + "\\" + "left(" + "\\" + "mathrm{dh} 2_{r}" + "\\" + "left(" + "\\" + "frac{1}{T}-" + "\\" + "frac{1}{298}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    if value == 0:
        return([equation1, equation3, equation4, equation5])
    if value == 1:
        return([equation2, equation3, equation4, equation5])


# loads molecule info into form stage json
def stage_form_info(item):
    initial = molecule_info()[item]
    dump_json('form_stage.json', initial)
    dump_json('mol_name.json', {'name': item})


# reads dict from form stage json
def initialize_form():
    info = open_json('form_stage.json')
    logging.info('filling molecule edit form')
    return info


# checks which molecule form was last initialized
def id_molecule():
    info = open_json('mol_name.json')
    return info['name']


# mathjax names and display names for form fields
def pretty_names():
    names = {
        "formula": "Formula:",
        'solve': "Solve Type:",
        'hl.henrys_law_type': "Henry's Law Type:",
        'hl.at 298K.value': "\\" + "begin{equation} \mathrm{kh}_{298}\end{equation}",
        'hl.exponential factor.value': "\\" + "begin{equation}\mathrm{dh}_{r}\end{equation}",
        'hl.k1_298': "\\" + "begin{equation}\mathrm{k1}_{298}\end{equation}",
        'hl.dh1_r': "\\" + "begin{equation}\mathrm{dh1}_{r}\end{equation}",
        'hl.k2_298': "\\" + "begin{equation}\mathrm{k2}_{298}\end{equation}",
        'hl.dh2_r': "\\" + "begin{equation}\mathrm{dh2}_{r}\end{equation}",
        'mw.value': "Molecular Weight:",
        'standard_name': "Standard Name:",
        'kh_298': "\\" + "begin{equation} \mathrm{kh}_{298}\end{equation}",
        'dh_r': "\\" + "begin{equation}\mathrm{dh}_{r}\end{equation}",
        'k1_298': "\\" + "begin{equation}\mathrm{k1}_{298}\end{equation}",
        'dh1_r': "\\" + "begin{equation}\mathrm{dh1}_{r}\end{equation}",
        'k2_298': "\\" + "begin{equation}\mathrm{k2}_{298}\end{equation}",
        'dh2_r': "\\" + "begin{equation}\mathrm{dh2}_{r}\end{equation}",
        'henrys_law_type': "Henry's Law Type:",
        'transport': "Transport:",
        'moleculename': "Molecule Name:"
    }
    return names



#saves updated molecule info from form into mechanism
def save_mol(name, myDict):
    logging.info('saving molecule...')    
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    molecules = mechanism['species']
    old = molecules[name]
    for key in myDict:
        if key.split('.')[0] == 'hl':
            old['henrys law constant'][key.split('.')[1]].update({key.split('.')[2]: myDict[key]})
        elif key.split('.')[0] == 'mw':
            old['molecular weight'].update({key.split('.')[1]: myDict[key]})
        else:
            old.update({key: myDict[key]})
    molecules.update({name: old})
    mechanism.update({'molecules':molecules})
    datafile.update({'mechanism': mechanism})
    dump_json('datamolec_info.json', datafile)
    logging.info('...saved')




# saves info from 'new molecule form' into mechanism
def new_m(myDict):
    logging.info('adding new molecule...')
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    molecules = mechanism['species']
    new = {
                "formula": myDict['formula'],
                "henrys law constant": {
                    "at 298K": {
                        "value": myDict['hl.at 298K.value'],
                        "units": "?"
                    },
                    "exponential factor": {
                        "value": myDict['hl.exponential factor.value'],
                        "units": "K"
                    }
                },
                "molecular weight": {
                    "value": myDict['mw.value'],
                    "units": "kg/mol"
                }
            }
    molecules.update({myDict['moleculename']: new})
    mechanism.update({'species': molecules})
    datafile.update({'mechanism': mechanism})
    dump_json('datamolec_info.json', datafile)
    logging.info('...added')



# returns a list of molecule names to search on
def search_list():
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    molecules = mechanism['molecules']
    name_list = []
    for i in molecules:
        name_list.append(i['moleculename'])
    return name_list
