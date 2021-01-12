import json
from django.conf import settings
import logging
import os
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

species_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")
reactions_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")

def species_info():
    logging.info('getting species_info')
    with open(species_path) as f:
        camp_data = json.loads(f.read())
    return camp_data['pmc-data']


def species_list():
    species_list = []
    for entry in species_info():
      if entry['type'] == "CHEM_SPEC":
          species_list.append(entry['name'])
    return species_list


def species_menu_names():
    m_list = species_list()
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


# loads chemical species info into form stage json
def stage_form_info(item):
    initial = species_info()[item]
    dump_json('form_stage.json', initial)
    dump_json('species_name.json', {'name': item})


# reads dict from form stage json
def initialize_form():
    info = open_json('form_stage.json')
    logging.info('filling species edit form')
    return info


# checks which chemical species form was last initialized
def id_species():
    info = open_json('species_name.json')
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
        'speciesname': "Species Name:"
    }
    return names



#saves updated chemical species info from form into mechanism
def save_species(name, myDict):
    logging.info('saving species...')
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    species = mechanism['species']
    old = species[name]
    for key in myDict:
        if key.split('.')[0] == 'hl':
            old['henrys law constant'][key.split('.')[1]].update({key.split('.')[2]: myDict[key]})
        elif key.split('.')[0] == 'mw':
            old['molecular weight'].update({key.split('.')[1]: myDict[key]})
        else:
            old.update({key: myDict[key]})
    species.update({name: old})
    mechanism.update({'species':species})
    datafile.update({'mechanism': mechanism})
    dump_json('datamolec_info.json', datafile)
    logging.info('...saved')




# saves info from 'new species form' into mechanism
def new_m(myDict):
    logging.info('adding new chemical species...')
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    species = mechanism['species']
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
    species.update({myDict['speciesname']: new})
    mechanism.update({'species': species})
    datafile.update({'mechanism': mechanism})
    dump_json('datamolec_info.json', datafile)
    logging.info('...added')



# returns a list of species names to search on
def search_list():
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    species = mechanism['species']
    name_list = species.keys()
    return name_list



#------------------------------

# REACTION FUNCTIONS:

# converts from "O__O3" format to  "O3 -> 3O" format
def convert_reaction_format(stringg):
    equalses = stringg.replace('__', ' -> ')
    plusses = equalses.replace('_',' + ')
    return plusses


# returns a list of reaction names, ex: "O3 -> 3O"
def reaction_name_list():
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    reactions = mechanism['processes']
    r_list = []
    for key in reactions:
        equalses = key.replace('__', ' -> ')
        plusses = equalses.replace('_',' + ')
        r_list.append(plusses)
    return r_list


# returns a dictionary of reactions
def reaction_dict():
    logging.info('getting reaction info..')
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    reactions = mechanism['processes']
    logging.info('..retrieved')
    return reactions
    

# returns zipped list of tuples with shortened names. [[long_name, short_name], [], ...]
def reaction_menu_names():
    r_list = reaction_name_list()
    newlist = []
    for name in r_list:
        if len(name) > 40:
            shortname = name[0:38] + '...'
            newlist.append(shortname)
        else:
            newlist.append(name)
    zipped = zip(reaction_dict().keys(), newlist)
    return zipped


# saves a reaction info to 'reaction_stage.json'
def stage_reaction_form(name):
    initial = reaction_dict()[name]
    dump_json('reaction_stage.json', initial)


# reads 'reaction_stage.json' to fill initial values for edit forms
def initialize_reactions():
    logging.info('filling form')
    info = open_json('reaction_stage.json')
    return info

