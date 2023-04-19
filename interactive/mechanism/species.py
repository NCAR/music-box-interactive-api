import json
BASE_DIR = '/music-box-interactive/interactive'
try:
    from django.conf import settings
    BASE_DIR = settings.BASE_DIR
except:
    # Error handling
    pass
import logging
import os
import time
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
species = "dashboard/static/config/camp_data/species.json"
# species_default = os.path.join(BASE_DIR, species)
species_default = os.path.join(BASE_DIR, species)


# returns the full set of json objects from the species file
def species_info(species_path=species_default):
    with open(species_path) as f:
        camp_data = json.loads(f.read())
        f.close()
    return camp_data['camp-data']


# returns the list of chemical species names from the species file
def species_list(species_path=species_default):
    species_list = []
    for entry in species_info(species_path):
      if entry['type'] == "CHEM_SPEC":
          species_list.append(entry['name'])
    return sorted(species_list)


# returns the list of chemical species whose concentrations can be specified
def conditions_species_list(species_path=species_default):
    species = species_list(species_path)
    if 'M' in species: species.remove('M')
    return species


# returns a modified list
def api_species_menu_names(species_path=species_default):
    # logging.info('getting list of species names')
    m_list = species_list(species_path)
    newlist = []
    for name in m_list:
        if len(name) > 25:
            shortname = name[0:25] + '..'
            newlist.append(shortname)
        else:
            newlist.append(name)
    return {'species_list_0': m_list, 'species_list_1': newlist}


# returns a list of chemical species names from the species file for use
def species_menu_names(species_path=species_default):
    m_list = species_list(species_path)
    newlist = []
    for name in m_list:
        if len(name) > 25:
            shortname = name[0:25] + '..'
            newlist.append(shortname)
        else:
            newlist.append(name)
    zipped = zip(m_list, newlist)
    return zipped


# removes a chemical species from the mechanism
def species_remove(species_name, species_path=species_default):
    species = species_info(species_path)
    index = 0
    for entry in species:
        if entry['type'] == "CHEM_SPEC" and entry['name'] == species_name:
            species.pop(index)
            break
        index += 1
    json_data = {}
    json_data['camp-data'] = species
    with open(species_path, 'w') as f:
        json.dump(json_data, f, indent=2)
        f.close()


# saves a chemical species to the mechanism
def species_save(species_data, species_path=species_default):
    json_data = {}
    species_convert_from_SI(species_data)
    json_data['camp-data'] = species_info(species_path)
    json_data['camp-data'].append(species_data)
    with open(species_path, 'w') as f:
        json.dump(json_data, f, indent=2)
        f.close()


# patch to allow interface to use SI units until CAMP is
# updated to use all SI units
def species_convert_from_SI(species_data):
    if 'absolute convergence tolerance [mol mol-1]' in species_data:
        mol = species_data['absolute convergence tolerance [mol mol-1]']
        # mol mol-1 -> ppm
        species_data['absolute tolerance'] = mol * 1.0e6
        species_data.pop('absolute convergence tolerance [mol mol-1]')


# patch to allow interface to use SI units until CAMP is
# updated to use all SI units
def species_convert_to_SI(species_data):
    if 'absolute tolerance' in species_data:
        mol = species_data['absolute tolerance']
        name = 'absolute convergence tolerance [mol mol-1]'
        # ppm -> mol mol-1
        species_data[name] = mol * 1.0e-6
        species_data.pop('absolute tolerance')


#creates a dictionary of species tolerances for plot minimum scales
def tolerance_dictionary(species_file_path=species_default):
    with open(species_file_path) as f:
        species_file = json.loads(f.read())
    default_tolerance = 1e-14
    species_list = species_file['camp-data']
    for spec in species_list:
        if 'absolute tolerance' not in spec:
            spec.update({'absolute tolerance': default_tolerance})

    species_dict = {j['name']:j['absolute tolerance'] for j in species_list}
    return species_dict
