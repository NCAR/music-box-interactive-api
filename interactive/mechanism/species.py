import json
from django.conf import settings
import logging
import os
import time
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

species_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")

# returns the full set of json objects from the species file
def species_info():
    logging.info('getting chemical species data from file')
    with open(species_path) as f:
        camp_data = json.loads(f.read())
        f.close()
    return camp_data['pmc-data']


# returns the list of chemical species names from the species file
def species_list():
    species_list = []
    for entry in species_info():
      if entry['type'] == "CHEM_SPEC":
          species_list.append(entry['name'])
    return sorted(species_list)


# returns a list of chemical species names from the species file for use in a menu
def species_menu_names():
    logging.info('getting list of species names')
    m_list = species_list()
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
def species_remove(species_name):
    logging.info("removing species '" + species_name + "'")
    species = species_info()
    index = 0
    for entry in species:
        if entry['type'] == "CHEM_SPEC" and entry['name'] == species_name:
            species.pop(index)
            break
        index += 1
    json_data = {}
    json_data['pmc-data'] = species
    with open(species_path, 'w') as f:
        json.dump(json_data, f, indent=2)
        f.close()


# saves a chemical species to the mechanism
def species_save(species_data):
    logging.info("saving species '" + species_data['name'] + "'")
    json_data = {}
    species_convert_from_SI(species_data)
    json_data['pmc-data'] = species_info()
    json_data['pmc-data'].append(species_data)
    with open(species_path, 'w') as f:
        json.dump(json_data, f, indent=2)
        f.close()

# patch to allow interface to use SI units until CAMP is updated to use all SI units
def species_convert_from_SI(species_data):
    if 'absolute tolerance [mol mol-1]' in species_data:
        species_data['absolute tolerance'] = species_data['absolute tolerance [mol mol-1]'] * 1.0e6 # mol mol-1 -> ppm
        species_data.pop('absolute tolerance [mol mol-1]')

# patch to allow interface to use SI units until CAMP is updated to use all SI units
def species_convert_to_SI(species_data):
    if 'absolute tolerance' in species_data:
        species_data['absolute tolerance [mol mol-1]'] = species_data['absolute tolerance'] * 1.0e-6 # ppm -> mol mol-1
        species_data.pop('absolute tolerance')


#creates a dictionary of species tolerances for plot minimum scales
def tolerance_dictionary():
    species_file_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")
    with open(species_file_path) as f:
        species_file = json.loads(f.read())
    default_tolerance = 1e-14
    species_list = species_file['pmc-data']
    for spec in species_list:
        if 'absolute tolerance' not in spec:
            spec.update({'absolute tolerance': default_tolerance})

    species_dict = {j['name']:j['absolute tolerance'] for j in species_list}
    return species_dict