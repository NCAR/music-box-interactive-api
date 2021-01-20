import json
from django.conf import settings
import logging
import os
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

reactions_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")

# returns the full set of reaction json objects from the reactions file
def reactions_info():
    logging.info('getting reaction data from file')
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
    return camp_data['pmc-data'][0]['reactions']


# creates a list of reaction names based on data from the reactions file for use in a menu
def reaction_menu_names():
    logging.info('getting list of reaction names')
    names = []
    for reaction in reactions_info():
        name = ''
        for idx, reactant in enumerate(reaction['reactants']):
            if idx > 0:
                name += '+ '
            name += str(reactant) + ' '
        name += '->'
        for idx, product in enumerate(reaction['products']):
            if idx > 0:
                name += ' +'
            name += ' ' + str(product)
        if len(name) > 20:
            shortname = name[0:20] + '...'
            names.append(shortname)
        else:
            names.append(name)
    return names


# removes a reaction from the mechanism
def reaction_remove(reaction_index):
    logging.info('removing reaction ' + str(reaction_index))
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
    camp_data['pmc-data'][0]['reactions'].pop(index)
    with open(reactions_path, 'w') as f:
        json.dump(camp_data, f, indent=2)


# saves a chemical species to the mechanism
def reaction_save(reaction_data):
    logging.info('adding reaction')
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
    camp_data['pmc-data'][0]['reactions'].append(reaction_data)
    with open(reactions_path, 'w') as f:
        json.dump(camp_data, f, indent=2)
