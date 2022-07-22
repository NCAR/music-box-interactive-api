import json
from django.conf import settings
import logging
import os
import time
from .species import species_list
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

react = "dashboard/static/config/camp_data/reactions.json"
reactions_default = os.path.join(settings.BASE_DIR, react)


# returns the full set of reaction json objects from the reactions file
def reactions_info(reactions_path=reactions_default):
    logging.info('getting reaction data from file')
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
        f.close()
    return camp_data['camp-data'][0]['reactions']


# checks if the set of reactions is valid (ie if there is at least one reaction)
def reactions_are_valid(reactions_path=reactions_default):
    if len(reactions_info(reactions_path)) > 0:
        return True
    return False


# returns whether a reaction with the specified MUSICA name exists
def is_musica_named_reaction(name, reactions_path=reactions_default):
    reactions = reactions_info(reactions_path)
    name_parts = name.split('.')
    if len(name_parts) != 2: return False
    prefix = name_parts[0]
    MUSICA_name = name_parts[1]
    if not MUSICA_name: return False
    for reaction in reactions:
        if not "MUSICA name" in reaction: continue
        if MUSICA_name == reaction["MUSICA name"]:
            if prefix == "EMIS" and reaction["type"] == "EMISSION": return True
            if prefix == "LOSS" and reaction["type"] == "FIRST_ORDER_LOSS": return True
            if prefix == "PHOT" and reaction["type"] == "PHOTOLYSIS": return True
    return False


# creates a list of reaction names based on data from the reactions file for use in a menu
def reaction_menu_names(reactions_path=reactions_default):
    logging.info('getting list of reaction names')
    names = []

    for reaction in reactions_info(reactions_path):
        name = ''
        if 'reactants' in reaction.keys() and 'products' in reaction.keys():
            first_item_printed = False
            for reactant,count_dict in reaction['reactants'].items():
                if count_dict and count_dict['qty'] != 1:
                    name += (' + ' if first_item_printed else '') + str(count_dict['qty']) + ' ' + reactant
                    first_item_printed = True
                else:
                    name += (' + ' if first_item_printed else '') + reactant
                    first_item_printed = True
            name += '->'
            first_item_printed = False
            for product, yield_dict in reaction['products'].items():
                if yield_dict and yield_dict['yield'] != 1.0:
                    name += (' + ' if first_item_printed else ' ') + str(yield_dict['yield']) + ' ' + product
                    first_item_printed = True
                else:
                    name += (' + ' if first_item_printed else ' ') + product
                    first_item_printed = True
        else:
            name += reaction['type']
            if 'species' in reaction.keys():
                name += ': ' + reaction['species']
        if len(name) > 40:
            shortname = name[0:40] + '...'
            names.append(shortname)
        else:
            names.append(name)
    return names


# removes a reaction from the mechanism
def reaction_remove(reaction_index, reactions_path=reactions_default):
    logging.info('removing reaction ' + str(reaction_index))
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
        f.close()
    camp_data['camp-data'][0]['reactions'].pop(reaction_index)
    with open(reactions_path, 'w') as f:
        json.dump(camp_data, f, indent=4)
        f.close()


def remove_reactions_with_species(species, reactions_path=reactions_default,
                                  my_config_path=""):
    logging.info('removing reactions with species ' + species)
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
        f.close()
    camp_data['camp-data'][0]['reactions'] = [r for r in camp_data['camp-data'][0]['reactions'] if not species in r['reactants'].keys() and not species in r['products'].keys()]
    with open(reactions_path, 'w') as f:
        json.dump(camp_data, f, indent=4)
        f.close()
    
    # now remove the species from my_config.json
    # check if my_config_path exists
    if not os.path.exists(my_config_path):
        return
    with open(my_config_path) as f:
        chem_species = json.loads(f.read())
        f.close()
    print("chem_species: ", chem_species.keys())
    if 'chemical species' in chem_species.keys():
        if species in chem_species['chemical species']:
            print("* found species in chemical species")
            del chem_species['chemical species'][species]
    print("* returning chem_species: ", chem_species)
    with open(my_config_path, 'w') as f:
        json.dump(chem_species, f, indent=4)
        f.close()


# saves a reaction to the mechanism
def reaction_save(reaction_data, reactions_path=reactions_default):
    logging.info('adding reaction: ', reaction_data)
    with open(reactions_path) as f:
        camp_data = json.loads(f.read())
        f.close()
    if 'index' in reaction_data:
        index = reaction_data['index']
        reaction_data.pop('index')
        camp_data['camp-data'][0]['reactions'][index] = reaction_data
    else:
        camp_data['camp-data'][0]['reactions'].append(reaction_data)
    with open(reactions_path, 'w') as f:
        json.dump(camp_data, f, indent=4)
        f.close()


# returns the set of reactions with MUSICA names including the
# units for their rates or rate constants
def reaction_musica_names(reactions_path=reactions_default):
    logging.info('getting reactions with MUSICA names')
    reactions = {}
    for reaction in reactions_info(reactions_path):
        if 'MUSICA name' in reaction:
            if reaction['MUSICA name'] == '':
                continue
            if reaction['type'] == "EMISSION":
                reactions['EMIS.' + reaction['MUSICA name']] = \
                    { 'units': 'ppm s-1' }
            elif reaction['type'] == "FIRST_ORDER_LOSS":
                reactions['LOSS.' + reaction['MUSICA name']] = \
                    { 'units': 's-1' }
            elif reaction['type'] == "PHOTOLYSIS":
                reactions['PHOT.' + reaction['MUSICA name']] = \
                    { 'units' : 's-1' }
    return reactions


# returns the json schema for a particular reaction type
def reaction_type_schema(reaction_type, reactions_path=reactions_default):
    logging.info('getting schema for ' + reaction_type)
    species = ""
    rea = reactions_path.replace('reactions.json', 'species.json')
    for idx, entry in enumerate(species_list(rea)):
        if idx > 0:
            species += ";"
        species += entry
    schema = {}
    if reaction_type == "ARRHENIUS":
        schema = {
            'reactants' : {
                'type' : 'array',
                'as-object' : True,
                'description' : "Use the 'qty' property when a species appears more than once as a reactant.",
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'qty' : {
                            'type' : 'integer',
                            'default' : 1
                        }
                    }
                }
            },
            'products' : {
                'type' : 'array',
                'as-object' : True,
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'yield' : {
                            'type' : 'real',
                            'default' : 1.0,
                            'units' : 'unitless'
                        }
                    }
                }
            },
            'equation' : {
                'type' : 'math',
                'value' : 'k = Ae^{(\\frac{-E_a}{k_bT})}(\\frac{T}{D})^B(1.0+E*P)',
                'description' : 'k<sub>B</sub>: Boltzmann constant (J K<sup>-1</sup>); T: temperature (K); P: pressure (Pa)'
            },
            'A' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : '(# cm<sup>-3</sup>)<sup>-(n-1)</sup> s<sup>-1</sup>'
            },
            'Ea' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'J'
            },
            'B' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'unitless'
            },
            'D' : {
                'type' : 'real',
                'default' : 300.0,
                'units' : 'K'
            },
            'E' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'Pa<sup>-1</sup>'
            }
        }
    elif reaction_type == 'EMISSION':
        schema = {
            'species' : {
                'type' : 'string-list',
                'values' : species
            },
            'scaling factor' : {
                'type' : 'real',
                'default' : 1.0,
                'description' : 'Use the scaling factor to adjust emission rates from input data. A scaling factor of 1.0 results in no adjustment.',
                'units' : 'unitless'
            },
            'MUSICA name' : {
                'type' : 'string',
                'description' : 'Set a MUSICA name for this reaction to identify it in other parts of the model (e.g., input conditions). You may choose any name you like.'
            }
        }
    elif reaction_type == 'FIRST_ORDER_LOSS':
        schema = {
            'species' : {
                'type' : 'string-list',
                'values' : species
            },
            'scaling factor' : {
                'type' : 'real',
                'default' : 1.0,
                'description' : 'Use the scaling factor to adjust first order loss rate constants from input data. A scaling factor of 1.0 results in no adjustment.',
                'units' : 'unitless'
            },
            'MUSICA name' : {
                'type' : 'string',
                'description' : 'Set a MUSICA name for this reaction to identify it in other parts of the model (e.g., input conditions). You may choose any name you like.'
            }
        }
    elif reaction_type == 'PHOTOLYSIS':
        schema = {
            'reactants' : {
                'type' : 'array',
                'as-object' : True,
                'description' : "Use the 'qty' property when a species appears more than once as a reactant.",
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'qty' : {
                            'type' : 'integer',
                            'default' : 1
                        }
                    }
                }
            },
            'products' : {
                'type' : 'array',
                'as-object' : True,
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'yield' : {
                            'type' : 'real',
                            'default' : 1.0,
                            'units' : 'unitless'
                        }
                    }
                }
            },
            'scaling factor' : {
                'type' : 'real',
                'default' : 1.0,
                'description' : 'Use the scaling factor to adjust photolysis rate constants from input data. A scaling factor of 1.0 results in no adjustment.',
                'units' : 'unitless'
            },
            'MUSICA name' : {
                'type' : 'string',
                'description' : 'Set a MUSICA name for this reaction to identify it in other parts of the model (e.g., input conditions). You may choose any name you like.'
            }
        }
    elif reaction_type == 'TERNARY_CHEMICAL_ACTIVATION':
        schema = {
            'reactants' : {
                'type' : 'array',
                'as-object' : True,
                'description' : "Use the 'qty' property when a species appears more than once as a reactant.",
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'qty' : {
                            'type' : 'integer',
                            'default' : 1
                        }
                    }
                }
            },
            'products' : {
                'type' : 'array',
                'as-object' : True,
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'yield' : {
                            'type' : 'real',
                            'default' : 1.0,
                            'units' : 'unitless'
                        }
                    }
                }
            },
            'equation k_0' : {
                'type' : 'math',
                'value' : 'k_0 = k_{0A}e^{(\\frac{k_{0C}}{T})}(\\frac{T}{300.0})^{k_{0B}}'
            },
            'equation k_inf' : {
                'type' : 'math',
                'value' : 'k_{inf} = k_{infA}e^{(\\frac{k_{infC}}{T})}(\\frac{T}{300.0})^{k_{infB}}'
            },
            'equation k' : {
                'type' : 'math',
                'value' : 'k = \\frac{k_0}{1+k_0[\\mbox{M}]/k_{\\inf}}F_C^{(1+1/N[log_{10}(k_0[\\mbox{M}]/k_{\\inf})]^2)^{-1}}',
                'description' : 'T: temperature (K); M: number density of air (# cm<sup>-3</sup>)'
            },
            'k0_A' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : '(# cm<sup>-3</sup>)<sup>-(n-1)</sup> s<sup>-1</sup>'
            },
            'k0_B' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'unitless'
            },
            'k0_C' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'K<sup>-1</sup>'
            },
            'kinf_A' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : '(# cm<sup>-3</sup>)<sup>-(n-1)</sup> s<sup>-1</sup>'
            },
            'kinf_B' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'unitless'
            },
            'kinf_C' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'K<sup>-1</sup>'
            },
            "Fc" : {
                'type' : 'real',
                'default' : 0.6,
                'units' : 'unitless'
            },
            'N' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : 'unitless'
            }
        }
    elif reaction_type == 'TROE':
        schema = {
            'reactants' : {
                'type' : 'array',
                'as-object' : True,
                'description' : "Use the 'qty' property when a species appears more than once as a reactant.",
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'qty' : {
                            'type' : 'integer',
                            'default' : 1
                        }
                    }
                }
            },
            'products' : {
                'type' : 'array',
                'as-object' : True,
                'children' : {
                    'type' : 'object',
                    'key' : species,
                    'children' : {
                        'yield' : {
                            'type' : 'real',
                            'default' : 1.0,
                            'units' : 'unitless'
                        }
                    }
                }
            },
            'equation k_0' : {
                'type' : 'math',
                'value' : 'k_0 = k_{0A}e^{(\\frac{k_{0C}}{T})}(\\frac{T}{300.0})^{k_{0B}}'
            },
            'equation k_inf' : {
                'type' : 'math',
                'value' : 'k_{inf} = k_{infA}e^{(\\frac{k_{infC}}{T})}(\\frac{T}{300.0})^{k_{infB}}'
            },
            'equation k' : {
                'type' : 'math',
                'value' : 'k = \\frac{k_0[\\mbox{M}]}{1+k_0[\\mbox{M}]/k_{\\inf}}F_C^{(1+1/N[log_{10}(k_0[\\mbox{M}]/k_{\\inf})]^2)^{-1}}',
                'description' : 'T: temperature (K); M: number density of air (# cm<sup>-3</sup>)'
            },
            'k0_A' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : '(# cm<sup>-3</sup>)<sup>-(n-1)</sup> s<sup>-1</sup>'
            },
            'k0_B' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'unitless'
            },
            'k0_C' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'K<sup>-1</sup>'
            },
            'kinf_A' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : '(# cm<sup>-3</sup>)<sup>-(n-1)</sup> s<sup>-1</sup>'
            },
            'kinf_B' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'unitless'
            },
            'kinf_C' : {
                'type' : 'real',
                'default' : 0.0,
                'units' : 'K<sup>-1</sup>'
            },
            "Fc" : {
                'type' : 'real',
                'default' : 0.6,
                'units' : 'unitless'
            },
            'N' : {
                'type' : 'real',
                'default' : 1.0,
                'units' : 'unitless'
            }
        }
    return schema
