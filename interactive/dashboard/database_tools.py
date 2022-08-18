# import django models
from django.db import models
# import models from interactive/dashboard
from dashboard import models
# from interactive.mechanism.species import species_list
import jsonfield
import os
import json
from pyvis.network import Network
import logging


# get user based on uid
def get_user(uid):
    # check if user exists
    try:
        user = models.User.objects.get(uid=uid)
        return user
    except models.User.DoesNotExist:
        # if not, create new user
        user = create_user(uid)
        return user


# get model run based on uid
def get_model_run(uid):
    return models.ModelRun.objects.get(uid=uid)


# get config files of user
def get_config_files(uid):
    return get_user(uid).config_files


# get csv files of user
def get_csv_files(uid):
    return get_user(uid).csv_files


# get results of model run
def get_results(uid):
    return get_model_run(uid).results


# get is running of model run
def get_is_running(uid):
    return get_model_run(uid).is_running


# set config files of user
def set_config_files(uid, config_files):
    user = get_user(uid)
    user.config_files = config_files
    user.save()


# set csv files of user
def set_csv_files(uid, csv_files):
    user = get_user(uid)
    user.csv_files = csv_files
    user.save()

# set results of model run
def set_results(uid, results):
    model_run = get_model_run(uid)
    model_run.results = results
    model_run.save()


# set is running of model run
def set_is_running(uid, is_running):
    model_run = get_model_run(uid)
    model_run.is_running = is_running
    model_run.save()


# create new user
def create_user(uid):
    user = models.User(uid=uid)
    user.save()
    return user


# create new model run
def create_model_run(uid):
    model_run = models.ModelRun(uid=uid)
    model_run.save()
    return model_run


# delete user
def delete_user(uid):
    user = get_user(uid)
    user.delete()


# delete model run
def delete_model_run(uid):
    model_run = get_model_run(uid)
    model_run.delete()


# delete all users
def delete_all_users():
    models.User.objects.all().delete()


# delete all model runs
def delete_all_model_runs():
    models.ModelRun.objects.all().delete()


# delete all config files
def delete_all_config_files(uid):
    user = get_user(uid)
    user.config_files = {}
    user.save()


# delete all csv files
def delete_all_csv_files(uid):
    user = get_user(uid)
    user.csv_files = {}
    user.save()


# delete results
def delete_results(uid):
    model_run = get_model_run(uid)
    model_run.results = {}
    model_run.save()


# set specific config file of user
def set_config_file(uid, filename, config_file):
    user = get_user(uid)
    user.config_files[filename] = config_file
    user.save()


# set specific csv file of user
def set_csv_file(uid, filename, csv_file):
    user = get_user(uid)
    user.csv_files[filename] = csv_file
    user.save()


# delete specific config file of user
def delete_config_file(uid, filename):
    user = get_user(uid)
    del user.config_files[filename]
    user.save()


# delete specific csv file of user
def delete_csv_file(uid, filename):
    user = get_user(uid)
    del user.csv_files[filename]
    user.save()


# search all users for checksum of config files,
# and check if should_cache is true.
# [return] list of uids of users that
# have should_cache equal to true for their current model run.
def search_for_config_checksum(checksum):
    users = models.User.objects.all()
    uids = []
    for user in users:
        if user.config_checksum == checksum:
            if user.should_cache:
                uids.append(user.uid)
    return uids


def get_files(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_files(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


# get species menu of user
def get_species_menu_list(uid):
    user = get_user(uid)
    # check if species.json exists
    if '/camp_data/species.json' not in user.config_files:
        return {'species_list_0': [], 'species_list_1': []}
    camp_data = user.config_files['/camp_data/species.json']["camp-data"]
    species_list = []
    for entry in camp_data:
        if entry['type'] == "CHEM_SPEC":
            species_list.append(entry['name'])
    m_list = sorted(species_list)
    newlist = []
    for name in m_list:
        if len(name) > 25:
            shortname = name[0:25] + '..'
            newlist.append(shortname)
        else:
            newlist.append(name)
    return {'species_list_0': m_list, 'species_list_1': newlist}


# get species detail of user
def get_species_detail(uid, species_name):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/species.json']["camp-data"]
    for entry in camp_data:
        if entry['type'] == "CHEM_SPEC":
            if entry['name'] == species_name:
                if 'absolute tolerance' in entry:
                    mol = entry['absolute tolerance']
                    name = 'absolute convergence tolerance [mol mol-1]'
                    # ppm -> mol mol-1
                    entry[name] = mol * 1.0e-6
                    entry.pop('absolute tolerance')

                return entry
    return None


# remove species for user
def remove_species(uid, species_name):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/species.json']["camp-data"]
    for entry in camp_data:
        if entry['type'] == "CHEM_SPEC":
            if entry['name'] == species_name:
                camp_data.remove(entry)
                break
    user.config_files['/camp_data/species.json']["camp-data"] = camp_data
    # find any reactions that use this species and remove them
    camp_data = user.config_files['/camp_data/reactions.json']["camp-data"]
    for entry in camp_data:
        if entry['type'] == "CHEM_REACTION":
            if species_name in entry['species']:
                camp_data.remove(entry)
    user.save()


# add species for user
def add_species(uid, species_data):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/species.json']["camp-data"]
    for entry in camp_data:
        if entry['type'] == "CHEM_SPEC":
            if entry['name'] == species_data['name']:
                camp_data.remove(entry)
                break
    entry = {'type': species_data['type'], 'name': species_data['name']}
    entry.update(species_data)
    camp_data.append(entry)
    user.config_files['/camp_data/species.json']["camp-data"] = camp_data
    user.save()


# generate network plot for user
def generate_database_network_plot(uid, species, path_to_template):
    user = get_user(uid)
    reactions_data = user.config_files['/camp_data/reactions.json']
    net = Network(directed=True)
    contained_reactions = {}

    for r in reactions_data['camp-data'][0]['reactions']:
        if 'reactants' in r:
            tmp = reactions_data['camp-data'][0]['reactions']
            if species in r['reactants']:
                contained_reactions.update({tmp.index(r): {}})
            if species in r['products']:
                contained_reactions.update({tmp.index(r): {}})

    logging.debug(contained_reactions)
    nodes = {}
    edges = []

    if contained_reactions:
        for i in contained_reactions:
            tmp = reactions_data['camp-data'][0]['reactions']
            reac_data = tmp[i]['reactants']
            prod_data = tmp[i]['products']
            reactants = [x for x in reac_data]
            products = [x for x in prod_data]
            first = '+'.join(reactants)
            second = '+'.join(products)
            name = first + '->' + second
            net.add_node(name, label=name,  color='green',
                         borderWidthSelected=3)
            for j in reactants:
                nodes.update({j: {}})
                edges.append([j, name])
            for k in products:
                nodes.update({k: {}})
                edges.append([name, k])
    else:
        net.add_node(species, label=species, )
    if species in nodes:
        nodes.pop(species)
    net.add_node(species, label=species, color='blue', size=50)
    for n in nodes:
        net.add_node(n, label=n, borderWidthSelected=3, size=40)
    for e in edges:
        net.add_edge(e[0], e[1])
    net.force_atlas_2based(gravity=-100, overlap=1)
    net.show(str(path_to_template))

# get reactions menu of user
def get_reactions_menu_list(uid):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/reactions.json']["camp-data"][0]['reactions']
    names = []

    for reaction in camp_data:
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


# get reactions details of user
def get_reactions_info(uid):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/reactions.json']["camp-data"][0]['reactions']
    return camp_data


# remove reaction for user
def remove_reaction(uid, index):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/reactions.json']["camp-data"]
    camp_data[0]['reactions'].pop(index)
    user.config_files['/camp_data/reactions.json']["camp-data"] = camp_data
    user.save()


# save reaction for user
def save_reaction(uid, reaction_data):
    user = get_user(uid)
    camp_data = user.config_files['/camp_data/reactions.json']
    if 'index' in reaction_data:
        index = reaction_data['index']
        reaction_data.pop('index')
        camp_data['camp-data'][0]['reactions'][index] = reaction_data
    else:
        camp_data['camp-data'][0]['reactions'].append(reaction_data)
    user.config_files['/camp_data/reactions.json'] = camp_data


# get model options of user
def get_model_options(uid):
    user = get_user(uid)
    print("* returning model options: ", user.config_files['/options.json'])
    return user.config_files['/options.json']


def post_model_options(uid, newOptions):
    user = get_user(uid)
    print("* setting model options: ", newOptions)
    user.config_files['/options.json']['camp-data'] = newOptions
    user.save()


# get initial conditions files of user
def get_initial_conditions_files(uid):
    user = get_user(uid)
    values = {}
    config = user.config_files['/my_config.json']
    if 'initial conditions' in config:
        values = config['initial conditions']
    return values


# get conditions species list
def get_condition_species(uid):
    user = get_user(uid)
    # species
    if '/camp_data/species.json' not in user.config_files:
        return {'species_list_0': [], 'species_list_1': []}
    camp_data = user.config_files['/camp_data/species.json']["camp-data"]
    species = []
    for entry in camp_data:
        if entry['type'] == "CHEM_SPEC":
            species.append(entry['name'])
    species = sorted(species)
    if 'M' in species:
        species.remove('M')
    return species


# get initial species concentrations
def get_initial_species_concentrations(uid):
    user = get_user(uid)
    initial_values = {}
    species = user.config_files['/species.json']
    if "formula" in species:
        for key in species["formula"]:
            formula = species["formula"][key]
            units = species["unit"][key]
            value = species["value"][key]
            initial_values[formula] = {"value": value, "units": units}
    return initial_values


# get the default units for a given variable
def default_units(prefix, name):
    if prefix == "EMIS":
        return "mol m-3 s-1"
    elif prefix == "LOSS":
        return "s-1"
    elif prefix == "PHOT":
        return "s-1"
    elif prefix == "ENV" and name == "temperature":
        return "K"
    elif prefix == "ENV" and name == "pressure":
        return "Pa"
    return ""


# converts initial conditions file to dictionary
def convert_initial_conditions_file(uid, delimiter):
    user = get_user(uid)
    input_file = '/initial_reaction_rates.csv'
    content = user.config_files[input_file]
    lines = content.split('\n')
    keys = [lines[0]]
    values = [lines[1]]
    if delimiter in content:
        keys = lines[0].split(delimiter)
        values = lines[1].split(delimiter)
    rates = {}
    for key in keys:
        key_parts = key.split('.')
        if len(key_parts) == 2:
            name = key_parts[0] + '.' + key_parts[1]
            units = default_units(key_parts[0], key_parts[1])
            rates[name] = {"value": values[keys.index(key)], "units": units}
        elif len(key_parts) == 3:
            name = key_parts[0] + '.' + key_parts[1]
            units = key_parts[2]
            rates[name] = {"value": values[keys.index(key)], "units": units}
    return rates


# converts dictionary to initial conditions file
def convert_initial_conditions_dict(uid, dictionary, output_file, delimiter):
    column_names = ''
    column_values = ''
    for key, value in dictionary.items():
        key_label = '' if key == '__blank__' else key
        if is_musica_reaction(uid, key_label):
            column_names += key_label + '.' + value["units"] + delimiter
            column_values += str(value["value"]) + delimiter
    user = get_user(uid)
    user.config_files[output_file] = column_names[:-1] + '\n' + column_values[:-1]
    user.save()


# check if it's a musica named reaction
def is_musica_reaction(uid, name):
    reactions = get_reactions_info(uid)
    name_parts = name.split('.')
    if len(name_parts) != 2:
        return False
    prefix = name_parts[0]
    MUSICA_name = name_parts[1]
    if not MUSICA_name:
        return False
    for reaction in reactions:
        if not "MUSICA name" in reaction:
            continue
        if MUSICA_name == reaction["MUSICA name"]:
            if prefix == "EMIS" and reaction["type"] == "EMISSION":
                return True
            if prefix == "LOSS" and reaction["type"] == "FIRST_ORDER_LOSS":
                return True
            if prefix == "PHOT" and reaction["type"] == "PHOTOLYSIS":
                return True
    return False


# returns the set of reactions with MUSICA names including the
# units for their rates or rate constants
def get_reaction_musica_names(uid):
    reactions = {}
    for reaction in get_reactions_info(uid):
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


# get status of a run
def get_run_status(uid):
    response_message = {}
    status = 'checking'
    try:
        model = models.ModelRun.objects.get(uid=uid)
        current_status = model.is_running
        if current_status is True:
            status = 'running'
        else:
            status = 'not running'
            # fetch for errors + results
            if '/error.json' in model.results:
                status = 'error'
            elif '/MODEL_RUN_COMPLETE' in model.results:
                status = 'done'
    except models.ModelRun.DoesNotExist:
        status = 'not_started'
    response_message.update({'status': status, 'session_id': uid})

    if status == 'error':
        errorfile = models.ModelRun.objects.get(uid=uid).results['/error.json']
        # search for the species which returned the error
        if "Property 'chemical_species%" in errorfile['message']:
            part = errorfile['message'].split('%')[1]
            specie = part.split("'")[0]
            spec_json = get_user(uid).config_files['/species.json']
            for key in spec_json['formula']:
                if spec_json['formula'][key] == specie:
                    response_message.update({'e_type': 'species'})
                    response_message.update({'spec_ID': key + '.Formula'})
        response_message.update({'e_code': errorfile['code']})
        response_message.update({'e_message': errorfile['message']})
    return response_message


# convert to/from model config format
def export_to_database_path(uid):
    user = get_user(uid)
    species = user.config_files['/species.json']
    options = user.config_files['/options.json']
    initials = user.config_files['/initials.json']

    oldConfig = user.config_files['/my_config.json']
    if 'evolving conditions' in oldConfig:
        evolves = oldConfig['evolving conditions']
    else:
        evolves = {}

    # gets initial conditions section if it exists
    if 'initial conditions' in oldConfig:
        initial_files = oldConfig['initial conditions']
    else:
        initial_files = {}

    config = {}

    # write model options section

    options_section = {}

    options_section.update({"grid": options["grid"]})
    time_step = "chemistry time step [" + options["chem_step.units"] + "]"
    options_section.update({time_step: options["chemistry_time_step"]})
    out_time = "output time step [" + options["output_step.units"] + "]"
    options_section.update({out_time: options["output_time_step"]})
    sim = "simulation length [" + options["simulation_length.units"] + "]"
    options_section.update({sim: options["simulation_length"]})

    # write chemical species section

    species_section = {}

    for i in species["formula"]:

        formula = species["formula"][i]
        units = species["unit"][i]
        value = species["value"][i]

        string = "initial value " + "[" + units + "]"

        species_section.update({formula: {string: value}})

    # write initial conditions section

    init_section = {}

    for i in initials["values"]:
        name = i
        units = initials["units"][i]
        value = initials["values"][i]

        string = "initial value " + "[" + units + "]"

        init_section.update({name: {string: value}})

    # write sections to main dict

    config.update({"box model options": options_section})
    config.update({"chemical species": species_section})
    config.update({"environmental conditions": init_section})
    config.update({'evolving conditions': evolves})
    config.update({'initial conditions': initial_files})

    config.update({
        "model components": [
            {
                "type": "CAMP",
                "configuration file": "camp_data/config.json",
                "override species": {
                    "M": {"mixing ratio mol mol-1": 1.0}
                },
                "suppress output": {
                    "M": {}
                }
            }
        ]
    })

    # dump config into my_config.json
    user.config_files['/my_config.json'] = config
    user.save()
    logging.info('Exported model config to my_config.json')


# export to database (used for conditions pages)
def export_to_database(uid):
    user = get_user(uid)
    config = user.config_files['/my_config.json']
    species_dict = {
        'formula': {},
        'value': {},
        'unit': {}
    }
    i = 1
    for key in config['chemical species']:
        name = 'Species ' + str(i)
        species_dict['formula'].update({name: key})
        unit = ""
        iv = 0
        for j in config['chemical species'][key]:
            unit = j.split('[')[1]
            unit = unit.split(']')[0]
            iv = config['chemical species'][key][j]
            species_dict['unit'].update({name: unit})
            species_dict['value'].update({name: iv})
        i = i+1

    option_dict = {}
    for key in config['box model options']:
        if '[' in key:
            fixedname = key.split(' [')[0]
            fixedname = fixedname.replace(' ', "_")
            option_dict.update({fixedname: config['box model options'][key]})
            unit = key.split(' [')[1]
            unit = unit.replace(']', "")
            if 'chemistry' in key:
                option_dict.update({"chem_step.units": unit})
            if 'output' in key:
                option_dict.update({"output_step.units": unit})
            if 'simulation' in key:
                option_dict.update({"simulation_length.units": unit})
        else:
            fixedname = key.replace(' ', "_")
            option_dict.update({fixedname: config['box model options'][key]})

    initial_dict = {
        'values': {},
        'units': {}
    }
    for condition in config['environmental conditions']:
        unit = ''
        for entry in config['environmental conditions'][condition]:
            tmp = config['environmental conditions'][condition][entry]
            initial_dict['values'].update({condition: tmp})
            unit = entry.split('[')[1]
            unit = unit.split(']')[0]
            initial_dict['units'].update({condition: unit})
    # dump initial_dict into initials.json
    user.config_files['/initials.json'] = initial_dict
    # dump option_dict into options.json
    user.config_files['/options.json'] = option_dict
    # dump species_dict into species.json
    user.config_files['/species.json'] = species_dict
    user.save()


# get reaction type schema for user
def get_reaction_type_schema(uid, reaction_type):
    user = get_user(uid)
    species = ""
    camp_data = user.config_files['/camp_data/species.json']["camp-data"]
    species_list = []
    for entry in camp_data:
        if entry['type'] == "CHEM_SPEC":
            species_list.append(entry['name'])
    species_list = sorted(species_list)
    for idx, entry in enumerate(species_list):
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