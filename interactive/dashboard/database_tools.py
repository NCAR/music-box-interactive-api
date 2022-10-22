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
import matplotlib
from plots import mpl_helper
import pandas as pd
from io import StringIO
from numpy import vectorize
from interactive.tools import *
import io
import matplotlib.pyplot as plt
from unicodedata import decimal
from urllib import request
import math
from bisect import bisect_left
import hashlib
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
    try:
        modekl = models.ModelRun.objects.get(uid=uid)
        return modekl
    except models.ModelRun.DoesNotExist:
        # if not, create new model run
        model_run = create_model_run(uid)
        return model_run


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
    reaction_data = user.config_files['/camp_data/reactions.json']["camp-data"]
    reaction_data[0]['reactions'] = [r for r in reaction_data[0]['reactions'] if not species_name in r['reactants'].keys() and not species_name in r['products'].keys()]
    for entry in reaction_data:
        if entry['type'] == "CHEM_REACTION":
            if species_name in entry['species']:
                reaction_data.remove(entry)
    user.config_files['/camp_data/reactions.json']["camp-data"] = reaction_data
    
    user.save()


    # now remove the species from my_config.json
    # check if my_config_path exists
    if not user.config_files['/my_config.json']:
        return
    chem_species = user.config_files['/my_config.json']
    if 'chemical species' in chem_species.keys():
        if species_name in chem_species['chemical species']:
            del chem_species['chemical species'][species_name]
    user.config_files['/my_config.json'] = chem_species
    
    
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


# is reactions valid
def is_reactions_valid(uid):
    reactions = get_reactions_info(uid)
    if len(reactions) > 0:
        return True
    return False
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
    # check if input_file exists
    if input_file not in user.config_files:
        return {}
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
    running = False
    try:
        model = models.ModelRun.objects.get(uid=uid)
        current_status = model.is_running
        if current_status is True:
            running = True
            status = 'running'
        else:
            status = 'not running'
            # fetch for errors + results
            if '/error.json' in model.results:
                if model.results['/error.json'] != {}:
                    status = 'error'
            if '/MODEL_RUN_COMPLETE' in model.results:
                status = 'done'
    except models.ModelRun.DoesNotExist:
        status = 'not_started'
    response_message.update({'status': status, 'session_id': uid, 'running': running})

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

def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '__' in reaction:
        reaction = reaction.replace('__', ' (')
        reaction = reaction+")"
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction
def tolerance(uid):
    # grab camp_data/species.json
    species_file = get_user(uid).config_files['/camp_data/species.json']
    default_tolerance = 1e-14
    species_list = species_file['camp-data']
    for spec in species_list:
        if 'absolute tolerance' not in spec:
            spec.update({'absolute tolerance': default_tolerance})

    species_dict = {j['name']:j['absolute tolerance'] for j in species_list}
    return species_dict

# get plot from model run
def get_plot(uid, prop, plot_units):
    # get output.csv from model run
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    matplotlib.use('agg')
        
    (figure, axes) = mpl_helper.make_fig(top_margin=0.6, right_margin=0.8)
    csv = pd.read_csv(output_csv, encoding='latin1')
    titles = csv.columns.tolist()
    csv.columns = csv.columns.str.strip()
    subset = csv[['time', str(prop.strip())]]
    model_output_units = 'mol/m-3'
    #make unit conversion if needed
    if plot_units:
        converter = vectorize(create_unit_converter(model_output_units, plot_units))
        if is_density_needed(model_output_units, plot_units):
            subset[str(prop.strip())] = converter(subset[str(prop.strip())], {'density': csv['ENV.number_density_air'].iloc[[-1]], 'density units':'mol/m-3 '})
        else:
            subset[str(prop.strip())] = converter(subset[str(prop.strip())])

    subset.plot(x="time", ax=axes)

    # set labels and title
    axes.set_xlabel(r"time / s")
    name = prop.split('.')[1]
    if prop.split('.')[0] == 'CONC':
        if 'myrate__' not in prop.split('.')[1]:
            axes.set_ylabel("("+plot_units+")")
            axes.set_title(beautifyReaction(name))
            #unit converter for tolerance      
            if plot_units:
                ppm_to_plot_units = create_unit_converter('ppm', plot_units)
            else:
                ppm_to_plot_units = create_unit_converter('ppm', model_output_units)

            if is_density_needed('ppm', plot_units):
                density = float(csv['ENV.number_density_air'].iloc[[-1]])
                pp = float(tolerance(uid)[name])
                du = 'density units'
                units = 'mol/m-3 '
                de = 'density'
                tolerance_tmp = ppm_to_plot_units(pp, {de: density, du: units})
            else:
                pp = float(tolerance(uid)[name])
                tolerance_tmp = ppm_to_plot_units(pp)

            #this determines the minimum value of the y axis range. minimum value of ymax = tolerance * tolerance_yrange_factor
            tolerance_yrange_factor = 5
            ymax_minimum = tolerance_yrange_factor * tolerance_tmp
            property_maximum = subset[str(prop.strip())].max()
            if ymax_minimum > property_maximum:
                axes.set_ylim(-0.05 * ymax_minimum, ymax_minimum)
        else:
            name = name.split('__')[1]
            axes.set_ylabel(r"(mol/m^3 s^-1)")
            axes.set_title(beautifyReaction(name))
    elif prop.split('.')[0] == 'ENV':
        axes.set_title(sub_props_names(name))
        if name == 'temperature':
            axes.set_ylabel(r"K")
        elif name == 'pressure':
            axes.set_ylabel(r"Pa")
        elif name == 'number_density_air':
            axes.set_ylabel(r"moles/m^3")

    # axes.legend()
    axes.grid(True)
    axes.get_legend().remove()
    # Store image in a string buffer
    buffer = io.BytesIO()
    figure.savefig(buffer, format='png')
    plt.close(figure)
    return buffer
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

# returns species in csv
def get_species(uid):
    # read csv for uid
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    csv = pd.read_csv(output_csv, encoding='latin1')
    concs = [x for x in csv.columns if 'CONC' in x]
    clean_concs = [x.split('.')[1] for x in concs if 'myrate' not in x]
    return clean_concs


# returns length of csv
def get_simulation_length(uid):
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    csv = pd.read_csv(output_csv, encoding='latin1')
    return int(csv['time'].iloc[-1])


# get user inputted step length
def get_step_length(uid):
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    csv = pd.read_csv(output_csv, encoding='latin1')
    if csv.shape[0] - 1 > 2:
        return int(csv['time'].iloc[1])
    else:
        return 0


# get entire time column from results
def time_column_list(uid):
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    csv = pd.read_csv(output_csv, encoding='latin1')
    return csv['time'].tolist()


# make list of indexes of included reactions
def find_reactions(list_of_species, reactions_json):
    r_list = reactions_json['camp-data'][0]['reactions']
    included = {}
    for reaction in r_list:
        reactants = []
        products = []
        if 'reactants' in reaction:
            reactants = reaction['reactants']

        if 'products' in reaction:
            products = reaction['products']

        for species in list_of_species:
            if (species in products) or (species in reactants):
                included.update({r_list.index(reaction): {}})
    return list(included)


# make list of indexes into reaction names
def name_included_reactions(included_reactions, reactions_json):
    r_list = reactions_json['camp-data'][0]['reactions']
    names_dict = {}
    for reaction_index in included_reactions:
        reaction = r_list[reaction_index]
        if 'reactants' in reaction:
            reactants = reaction['reactants']
        else:
            reactants = ['null']
        if 'products' in reaction:
            products = reaction['products']
        else:
            products = ['null']
        name = '_'.join(reactants) + '->' + '_'.join(products)
        names_dict.update({reaction_index: name})
    return names_dict


# make reaction hot hot hot by adding some nicer arrows and cleaning it up
def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction


# undo beautifyReaction (usually used when indexing dictionaries)
def unbeautifyReaction(reaction):
    if '→' in reaction:
        reaction = reaction.replace(' → ', '->')
    if '+' in reaction:
        reaction = reaction.replace(' + ', '_')
    return reaction


# return list of species, reactions, species size and colors.
def findReactionsAndSpecies(list_of_species, reactions_data, blockedSpecies):
    contained_reactions = {}
    species_nodes = {}
    reactions_nodes = {}
    species_colors = {}
    species_sizes = {}
    for el in list_of_species:
        if el not in blockedSpecies:
            # create empty dict for each species
            species_nodes.update({el: {}})
    for r in reactions_data['camp-data'][0]['reactions']:
        for species in list_of_species:
            species_colors.update({species: "#6b6bdb"})
            species_sizes.update({species: 40})
            if 'reactants' in r:
                if species in r['reactants']:
                    tmp_val = reactions_data['camp-data'][0]['reactions']
                    contained_reactions.update(
                        {tmp_val.index(r): {}})
                    reaction_string = ""
                    for reactant in r['reactants']:
                        species_nodes.update({reactant: {}})
                        reaction_string = reaction_string + reactant + "_"
                    # remove last _ and replace with ->
                    reaction_string = reaction_string[:-1] + "->"
                    for product in r['products']:
                        species_nodes.update({product: {}})
                        reaction_string = reaction_string + product + "_"
                    if r['products'] != [] and len(r['products']) != 0:
                        reaction_string = reaction_string[:-1]
                    reactions_nodes.update({reaction_string: {}})
                if species in r['products']:
                    tmp_val = reactions_data['camp-data'][0]['reactions']
                    contained_reactions.update(
                        {tmp_val.index(r): {}})
                    reaction_string = ""
                    for reactant in r['reactants']:
                        species_nodes.update({reactant: {}})
                        reaction_string = reaction_string + reactant + "_"
                    # remove last + and replace with →
                    reaction_string = reaction_string[:-1] + "->"
                    for product in r['products']:
                        species_nodes.update({product: {}})
                        reaction_string = reaction_string + product + "_"
                    reaction_string = reaction_string[:-1]
                    reactions_nodes.update({reaction_string: {}})
    for speci in species_nodes:
        if speci not in list_of_species:
            species_colors.update({speci: "#94b8f8"})
            species_sizes.update({speci: 20})
    return (contained_reactions, species_nodes,
            reactions_nodes, species_colors, species_sizes)


# used to get closest value for time_column_list
def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before


# return list of raw widths for arrows. Also set new minAndMax
def findReactionRates(reactions_nodes, df, start, end,
                      uid):
    rates_cols = [x for x in df.columns if 'myrate' in x]
    reactionsToAdd = []
    for re in reactions_nodes:
        # convert index of reaction into actual reaction name
        reactionsToAdd.append(re)
    rates = df[rates_cols]
    first = 0
    last = len(time_column_list(uid))-1
    # find closest time value to start, NOT USED RN
    closest_val = take_closest(time_column_list(uid), start)
    print(" [DEBUG] closest_val: " + str(closest_val))
    if start != 1:
        # check if start is in time_column_list
        if start in time_column_list(uid):
            first = time_column_list(uid).index(start)
        else:
            first = time_column_list(uid).index(closest_val)

        # check if end is in time_column_list
        if end in time_column_list(uid):
            last = time_column_list(uid).index(end)
        else:
            last = time_column_list(uid).index(take_closest(time_column_list(uid), end))
    first_and_last = rates.iloc[[first, last]]
    difference = first_and_last.diff()
    values = dict(difference.iloc[-1])
    widths = {}
    for key in values:
        if key.split('.')[1].split("__")[1] in reactionsToAdd:
            widths.update({key.split('.')[1].split("__")[1]: float(
                str('{:0.3e}'.format(values[key])))})
    return widths


# get the actual min and max
def minAndmax(reaction_nodes, quantities, widths):
    min_val = 999999999999
    max_val = 0
    for reaction in reaction_nodes:
        products_data, reactants_data = getProductsAndReactionsFrom(reaction)
        for product in products_data:
            edge = reaction + "__TO__" + product
            try:
                val = quantities[edge]*widths[reaction]
                if val < min_val:
                    min_val = val
                if val > max_val:
                    max_val = val
            except KeyError:
                logging.info("reaction with no product")
        for reactant in reactants_data:
            edge = reactant + "__TO__" + reaction
            try:
                val = quantities[edge]*widths[reaction]
                if val < min_val:
                    min_val = val
                if val > max_val:
                    max_val = val
            except KeyError:
                logging.info("reaction with no reactant")
    return (min_val*0.999), (max_val*1.001)


# 1) calculate new widths for the arrows by multiplying quantity of species
# 2) calculate new min and max
# 3) set colors for arrows
def sortYieldsAndEdgeColors(reactions_nodes, reactions_data,
                            widths, blockedSpecies, list_of_species):
    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    global previous_vals
    raw_yields = {}
    edgeColors = {}
    quantities, total_quantites, reaction_names_on_hover = findQuantities(
        reactions_nodes, reactions_data)
    newmin, newmax = minAndmax(reactions_nodes, quantities, widths)
    minAndMaxOfSelectedTimeFrame = [newmin, newmax]
    newMin = str('{:0.3e}'.format(newmin))
    prev0 = str('{:0.3e}'.format(previous_vals[0]))
    newMax = str('{:0.3e}'.format(newmax))
    prev1 = str('{:0.3e}'.format(previous_vals[1]))
    if (newMin != prev0 or newMax != prev1):
        userSelectedMinMax = [newmin, newmax]
    userMM = userSelectedMinMax  # short version to clean up code
    for reaction in reactions_nodes:

        products_data, reactants_data = getProductsAndReactionsFrom(reaction)
        for product in products_data:
            if product != "NO_PRODUCTS":
                name = reaction+"__TO__"+product
                tmp = widths[reaction]*quantities[name]
                if (tmp <= userMM[1]
                        and tmp >= userMM[0]):
                    edgeColors.update({name: "#FF7F7F"})
                else:
                    # for grey lines, we wanna make their value the min/max
                    if tmp > userMM[1]:
                        tmp = userMM[1]
                    elif tmp < userMM[0]:
                        tmp = userMM[0]
                    edgeColors.update({name: "#e0e0e0"})
                if (reaction not in blockedSpecies
                        and product not in blockedSpecies):
                    raw_yields.update(
                        {name: tmp})
            else:
                print("|_ found no products for reaction:", reaction)
        for reactant in reactants_data:
            tmp_reaction = reaction
            name = reactant+"__TO__"+reaction
            if products_data == ['']:
                name = name.replace("->", "-")
                tmp_reaction = tmp_reaction.replace("->", "-")
            qt = quantities[reactant+"__TO__"+tmp_reaction]
            tmp = widths[reaction]*qt
            if (tmp <= userMM[1]
                    and tmp >= userMM[0]):
                if reactant in list_of_species:
                    edgeColors.update({name: "#6b6bdb"})
                else:
                    edgeColors.update({name: "#94b8f8"})
            else:
                if tmp > userMM[1]:
                    tmp = userMM[1]
                elif tmp < userMM[0]:
                    tmp = userMM[0]
                edgeColors.update({name: "#e0e0e0"})
            if (reactant not in blockedSpecies
                    and tmp_reaction not in blockedSpecies):
                raw_yields.update(
                    {reactant+"__TO__"+reaction: tmp})
    return (raw_yields, edgeColors, quantities,
            total_quantites, reaction_names_on_hover)


# create line widths scaling based on user selected option
def calculateLineWeights(maxWidth, species_yields, scale_type):
    # use fluxes from map we setup, scale the values, add weights and whatnot
    maxVal = -1
    minVal = 99999999
    rawVal = {}
    numOfInvalids = 0
    if scale_type == 'log':
        if species_yields != {}:

            li = species_yields
            logged = []
            for i in li:
                # fail safe for null->null value
                if (str(i) != 'null->null'
                        and float(0.0) != float(species_yields[i])):
                    rawVal.update({i: species_yields[i]})
                    try:
                        logged.append((i, math.log(species_yields[i])))
                        if species_yields[i] < minVal:
                            minVal = species_yields[i]
                        if species_yields[i] > maxVal:
                            maxVal = species_yields[i]
                    except ValueError:
                        numOfInvalids = numOfInvalids+1
                        logged.append(
                            (i, abs(math.log(abs(species_yields[i])))))
                        if abs(species_yields[i]) < minVal:
                            minVal = abs(species_yields[i])
                        if abs(species_yields[i]) > maxVal:
                            maxVal = abs(species_yields[i])

            vals = [i[1] for i in logged]
            min_val = abs(min(vals, default="EMPTY"))
            range = max(vals) - min(vals, default="EMPTY")
            if max(vals) == min(vals, default="EMPTY"):
                range = 1
            scaled = [(x[0], (float(((x[1] + min_val)/range))
                       * float(maxWidth)) + 1) for x in logged]
            return list(scaled), minVal, maxVal, rawVal
        else:
            return list([]), -1, 999999999, {}
    else:
        li = species_yields
        vals = [species_yields[i] for i in li]
        min_val = abs(min(vals, default="EMPTY"))

        minVal = min_val
        maxVal = abs(max(vals, default="EMPTY"))

        range = max(vals) - min(vals, default="EMPTY")
        scaled = [(x, (((species_yields[x] + min_val)/range)
                   * int(maxWidth)) + 1) for x in li]
        return list(scaled), minVal, maxVal, {}


# 1) load reactions from output file, and create a list of reactions
# 2) load species and reaction rates
# 3) scale arrows and handle colors for arrows outside of range
# 4) create nodes and edges for graph
def new_find_reactions_and_species(list_of_species, reactions_data,
                                   blockedSpecies, df, start,
                                   end, max_width, scale_type,
                                   cs):

    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    global previous_vals
    logging.info(" ***************************************")
    logging.info("*= [1/6] FINDING REACTIONS AND SPECIES =*")
    logging.info(" ***************************************")

    (contained_reactions, species_nodes,
     reactions_nodes, species_colors,
     species_sizes) = findReactionsAndSpecies(
        list_of_species, reactions_data, blockedSpecies)

    logging.info("|_ got species nodes: " + str(species_nodes))
    logging.info("|_ got reactions nodes: " + str(reactions_nodes))
    logging.info(" *******************************************")
    logging.info("*= [2/6] FINDING INTEGRATED REACTION RATES =*")
    logging.info(" *******************************************")

    widths = findReactionRates(reactions_nodes, df, start, end, cs)

    logging.info(" *************************************")
    logging.info("*= [3/6] sorting yields from species =*")
    logging.info(" *************************************")

    (raw_yields, edgeColors, quantities,
     total_quantites, reaction_names_on_hover) = sortYieldsAndEdgeColors(
        reactions_nodes, reactions_data, widths,
        blockedSpecies, list_of_species)

    logging.info(" *********************************")
    logging.info("*= [4/6] calculating line widths =*")
    logging.info(" *********************************")
    (scaledLineWeights, minVal, maxVal,
     raw_yield_values) = calculateLineWeights(
        max_width, raw_yields, scale_type)
    # print("|_ got scaled line weights:", scaledLineWeights)
    logging.info("|_ got min and max: " + str(minVal) + " and " + str(maxVal))
    logging.info(" ********************************* ")
    logging.info("*= [6/6] calculating line colors =*")
    logging.info(" ********************************* ")
    re_no = reactions_nodes
    sp_no = species_nodes
    sp_no = scaledLineWeights
    b = blockedSpecies
    # quantities = [] #actually do this later
    return (CalculateEdgesAndNodes(re_no, sp_no, sp_no, b),
            raw_yields, edgeColors, quantities, minVal, maxVal,
            raw_yield_values, species_colors, species_sizes,
            total_quantites, reaction_names_on_hover)


def getProductsAndReactionsFrom(reaction):
    reactants = []
    products = []
    no_products = []
    for reactant in reaction.split('->')[0].split('_'):
        reactants.append(reactant)
    if len(reaction.split('->')) > 1:
        # check for products
        for product in reaction.split('->')[1].split('_'):
            products.append(product)
    else:
        # if no products, set to NO_PRODUCTS
        products.append('NO_PRODUCTS')
        logging.info("|_ no products found for reaction:" + reaction)
        no_products.append(reaction)
    return products, reactants


def isSpeciesInReaction(reaction, species):
    for re in reaction:
        if species == re:
            return True
    return False


def reactionNameFromDictionary(r):
    reaction_string = ""
    for reactant in r['reactants']:
        reaction_string = reaction_string + reactant + "_"
    reaction_string = reaction_string[:-1] + \
        "->"  # remove last _ and replace with ->
    for product in r['products']:
        reaction_string = reaction_string + product + "_"
    reaction_string = reaction_string[:-1]

    return reaction_string


# return quantities of species in reactions
def findQuantities(reactions_nodes, reactions_json):
    global userSelectedMinMax
    global previous_vals
    global minAndMaxOfSelectedTimeFrame

    # save quantities for use in arrows
    quantities = {}

    # add quantities of every reaction selected for species
    total_quantites = {}

    reaction_names_on_hover = {}  # these names will be shown on hover

    r_list = reactions_json['camp-data'][0]['reactions']
    i = 0
    for reaction in r_list:
        if "products" in r_list[i]:
            # get products data at index reaction
            reaction_data = r_list[i]['products']
            # get reactants data at index reaction
            reactant_data = r_list[i]['reactants']

            reactants_string = ""
            products_string = ""

            speciesFromReaction = reactionNameFromDictionary(r_list[i])

            for reactant in reactant_data:
                reactant_name = reactant
                reactant_yield = reactant_data[reactant_name]
                inReac = isSpeciesInReaction(reactant_data, reactant_name)
                name = str(reactant_name)+"__TO__"+str(speciesFromReaction)
                if (reactant_yield == {}
                    and (isSpeciesInReaction(reaction_data, reactant_name)
                         or inReac)):
                    nme = str(reactant_name)+"__TO__"+str(speciesFromReaction)
                    quantities.update({nme: 1})
                    if str(speciesFromReaction) in reactions_nodes:
                        new_val = total_quantites.get(reactant_name, 0) + 1
                        total_quantites.update(
                            {str(reactant_name): new_val})
                        reactants_string += str(reactant_name)+"_"
                elif (isSpeciesInReaction(reaction_data, reactant_name)
                      or isSpeciesInReaction(reactant_data, reactant_name)):
                    reactant_yield = reactant_yield['qty']
                    quantities.update(
                        {name: reactant_yield})
                    if str(speciesFromReaction) in reactions_nodes:
                        new_val = total_quantites.get(reactant_name, 0)
                        total_quantites.update(
                            {str(reactant_name): new_val + reactant_yield})
                        reactants_string += (str(reactant_yield))
                        reactants_string += str(reactant_name)+"_"
                        rep = ".0"+str(product_name)
                        rep1 = str(product_name)
                        reactants_string = reactants_string.replace(rep, rep1)
            reactants_string = reactants_string[:-1]
            if len(reaction_data) == 0:
                products_string = "NO_PRODUCTS-"
            for product in reaction_data:
                product_name = product
                product_yield = reaction_data[product_name]

                # reaction_names_on_hover
                if (product_yield == {}
                    and (isSpeciesInReaction(reaction_data, product_name)
                         or isSpeciesInReaction(reactant_data, product_name))):
                    nme = str(speciesFromReaction)+"__TO__"+str(product_name)
                    quantities.update({nme: 1})
                    # check if reaction is included in user selected species
                    if str(speciesFromReaction) in reactions_nodes:
                        quan = total_quantites.get(product_name, 0)
                        new_val = quan + 1
                        total_quantites.update(
                            {str(product_name): new_val})
                        products_string += str(product_name)+"_"
                elif (isSpeciesInReaction(reaction_data, product_name)
                      or isSpeciesInReaction(reactant_data, product_name)):
                    product_yield = product_yield['yield']
                    name = str(speciesFromReaction)+"__TO__"+str(product_name)
                    quantities.update(
                        {name: product_yield})
                    if str(speciesFromReaction) in reactions_nodes:
                        quan = total_quantites.get(product_name, 0)
                        new_val = quan + product_yield
                        total_quantites.update(
                            {str(product_name): new_val})
                        tmp = str(product_yield) + str(product_name)+"_"
                        products_string += tmp
                        products_string = products_string.replace(".0"+str(
                            product_name), str(product_name))
            products_string = products_string[:-1]
            reaction_names_on_hover.update(
                {speciesFromReaction: reactants_string+"->"+products_string})
        i += 1
    return quantities, total_quantites, reaction_names_on_hover


def CalculateEdgesAndNodes(reactions, species, scaledLineWeights,
                           blockedSpecies):
    logging.info("[7/7] Creating edges and nodes...")
    species = {}
    edges = {}
    reactions = {}

    for weight in scaledLineWeights:

        fromElement = weight[0].split('__TO__')[0].replace("__TO__", "")
        ToElement = weight[0].split('__TO__')[1].replace("__TO__", "")
        lineWidth = float(weight[1])

        if "->" in fromElement:
            # reaction -> product
            edge = (beautifyReaction(fromElement), ToElement, lineWidth)
            edges.update({edge: {}})
            if species not in blockedSpecies:
                species.update({ToElement: {}})
            reactions.update({beautifyReaction(fromElement): {}})
        else:
            # reactant -> reaction
            edge = (fromElement, beautifyReaction(ToElement), lineWidth)
            edges.update({edge: {}})
            if species not in blockedSpecies:
                species.update({fromElement: {}})
            reactions.update({beautifyReaction(ToElement): {}})
    return {'edges': list(edges), 'species_nodes': list(species),
            'reaction_nodes': list(reactions)}


def createLegend():
    x = -300
    y = -250
    legend_nodes = [
        'Element', 'Reaction'
    ]
    return legend_nodes


# get reaction name (when hovering on node) and beautify it
def getReactName(reaction_names_on_hover, x):
    name = ""
    try:
        name = beautifyReaction(reaction_names_on_hover[unbeautifyReaction(x)])
    except KeyError:
        name = x
    return name

# function called from API to get data for graph (AKA the main function)
def generate_flow_diagram(request_dict, uid, path_to_template):
    global userSelectedMinMax
    global minAndMaxOfSelectedTimeFrame
    global previous_vals

    if (('maxMolval' in request_dict and 'minMolval' in request_dict)
        and (request_dict['maxMolval'] != ''
        and request_dict['minMolval'] != '')
        and (request_dict['maxMolval'] != 'NULL'
             and request_dict['minMolval'] != 'NULL')):
        userSelectedMinMax = [
            float(request_dict["minMolval"]),
            float(request_dict["maxMolval"])]
        logging.info("new user selected min and max: " + str(userSelectedMinMax))
    if 'startStep' not in request_dict:
        request_dict.update({'startStep': 1})

    if 'maxArrowWidth' not in request_dict:
        request_dict.update({'maxArrowWidth': 10})
    minAndMaxOfSelectedTimeFrame = [999999999999, -1]
    # load csv file
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    csv = pd.read_csv(output_csv, encoding='latin1')

    start_step = int(request_dict['startStep'])
    end_step = int(request_dict['endStep'])

    # scale with correct scaling function
    scale_type = request_dict['arrowScalingType']
    max_width = request_dict['maxArrowWidth']

    previousMin = float(request_dict["currentMinValOfGraph"])
    previousMax = float(request_dict["currentMaxValOfGraph"])
    previous_vals = [previousMin, previousMax]

    isPhysicsEnabled = request_dict['isPhysicsEnabled']
    if isPhysicsEnabled == 'true':
        max_width = 2  # change for max width with optimized performance

    # load species json and reactions json
    user = get_user(uid)
    reactions_data = user.config_files['/camp_data/reactions.json']

    # completely new method of creating nodes and filtering elements
    selected_species = request_dict['includedSpecies'].split(',')
    blockedSpecies = request_dict['blockedSpecies'].split(',')

    (network_content, raw_yields, edgeColors, quantities, minVal, maxVal,
     raw_yield_values, species_colors, species_sizes,
     total_quantites,
     reaction_names_on_hover) = new_find_reactions_and_species(
        selected_species, reactions_data, blockedSpecies,
        csv, start_step, end_step, max_width, scale_type, uid)

    # add edges and nodes
    # force network to be 100% width and height before it's sent to page
    net = Network(height='100%', width='100%', directed=True)
    # make it so we can manually change arrow colors
    net.inherit_edge_colors(False)
    shouldMakeSmallNode = False
    if isPhysicsEnabled == "true":
        net.toggle_physics(False)
        net.force_atlas_2based()
    else:
        net.force_atlas_2based(gravity=-200, overlap=1)
    reac_nodes = network_content['reaction_nodes']
    hover_names = reaction_names_on_hover
    names = [getReactName(hover_names, x) for x in reac_nodes]
    colors = [species_colors[x] for x in network_content['species_nodes']]
    if shouldMakeSmallNode:
        net.add_nodes(names, color=["#FF7F7F" for x in reac_nodes], size=[
                      10 for x in list(reac_nodes)], title=names)
        net.add_nodes(network_content['species_nodes'], color=colors,
                      size=[
                        10 for x in list(network_content['species_nodes'])])
    else:
        net.add_nodes(names, color=[
                      "#FF7F7F" for x in reac_nodes], title=names)
        net.add_nodes(network_content['species_nodes'], color=colors,
                      size=[species_sizes[x] for x in list(
                        network_content['species_nodes'])])
    net.set_edge_smooth('dynamic')
    # add edges individually so we can modify contents
    i = 0
    values = edgeColors
    for edge in network_content['edges']:
        unbeu1 = unbeautifyReaction(edge[0])
        unbeu2 = unbeautifyReaction(edge[1])
        val = unbeu1+"__TO__"+unbeu2

        flux = str(raw_yields[unbeu1+"__TO__"+unbeu2])
        colorVal = ""
        try:
            colorVal = values[val]
        except KeyError:
            colorVal = values[val.replace('->', '-')]
        if colorVal == "#e0e0e0":
            # don't allow blocked edge to show value on hover
            if "→" in edge[0]:
                be1 = beautifyReaction(reaction_names_on_hover[unbeu1])
                net.add_edge(be1, edge[1], color=colorVal, width=edge[2])
            elif "→" in edge[1]:
                try:
                    be2 = beautifyReaction(reaction_names_on_hover[unbeu2])
                    net.add_edge(edge[0], be2, color=colorVal, width=edge[2])
                except KeyError:
                    be2 = beautifyReaction(unbeu2)
                    net.add_edge(edge[0], be2, color=colorVal, width=edge[2])
            else:
                net.add_edge(edge[0], edge[1],
                             color=colorVal, width=edge[2])
        else:
            # hover over arrow to show value for arrows within range

            # check if value is reaction by looking for arrow
            if "→" in edge[0]:
                be1 = beautifyReaction(reaction_names_on_hover[unbeu1])
                net.add_edge(be1, edge[1], color=colorVal, width=float(
                             edge[2]), title="flux: "+flux)
            elif "→" in edge[1]:
                try:
                    be2 = beautifyReaction(reaction_names_on_hover[unbeu2])
                    net.add_edge(edge[0], be2, color=colorVal, width=float(
                        edge[2]), title="flux: "+flux)
                except KeyError:
                    be2 = beautifyReaction(unbeu2)
                    net.add_edge(edge[0], be2, color=colorVal, width=float(
                        edge[2]), title="flux: "+flux)
            else:
                net.add_edge(edge[0], edge[1], color=colorVal,
                             width=float(edge[2]), title="flux: "+flux)
        i = i+1

    net.show(path_to_template)
    if minAndMaxOfSelectedTimeFrame[0] == minAndMaxOfSelectedTimeFrame[1]:
        minAndMaxOfSelectedTimeFrame = [0, maxVal]
    with open(path_to_template, 'r+') as f:
        #############################################
        # here we are going to replace the contents #
        #############################################
        a = """<script>
        network.on("stabilizationIterationsDone", function () {
            network.setOptions( { physics: false } );
        });
        </script>"""
        logging.debug("((DEBUG)) [min,max] of selected time frame: " +
            str(minAndMaxOfSelectedTimeFrame))
        logging.debug("((DEBUG)) [min,max] given by user: " + str(userSelectedMinMax))
        formattedPrevMin = str('{:0.3e}'.format(previousMin))
        formattedPrevMax = str('{:0.3e}'.format(previousMax))
        formattedMinOfSelected = str(
            '{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))
        formattedMaxOfSelected = str(
            '{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))
        formattedUserMin = str('{:0.3e}'.format(userSelectedMinMax[0]))
        formattedUserMax = str('{:0.3e}'.format(userSelectedMinMax[1]))
        if (int(minAndMaxOfSelectedTimeFrame[1]) == -1
                or int(minAndMaxOfSelectedTimeFrame[0]) == 999999999999):
            a = """<script>
        parent.document.getElementById("flow-start-range2").value = "NULL";
        parent.document.getElementById("flow-end-range2").value = "NULL";
        console.log("inputting NULL");"""

        else:
            a = '<script>\
            parent.document.getElementById("flow-start-range2").value = \
            "'+formattedMinOfSelected+'";'
            a += 'parent.document.getElementById("flow-end-range2").value = \
                "'+str(
                formattedMaxOfSelected)+'";'
        a += """
        currentMinValOfGraph = """+formattedPrevMin+""";
        currentMaxValOfGraph = """+formattedPrevMax+""";
        """
        if (str(formattedPrevMin) != str(formattedMinOfSelected)
            or str(formattedPrevMax) != str(formattedMaxOfSelected)
                or previousMax == 1):
            logging.debug("previousMin:" + str(formattedPrevMin) + 
                "does not equal " + str(formattedMinOfSelected))
            logging.debug("previousMax: " + str(formattedPrevMax) +
                " does not equal " + str(formattedMaxOfSelected))
            logging.debug("previousMin: " + str(previousMin) + " equals 0")
            logging.debug("previousMax: " + str(previousMax) + " equals 1")
            a += 'parent.document.getElementById("flow-start-range2").value =\
                "'+str(formattedMinOfSelected)+'";\
                    parent.document.getElementById("flow-end-range2").value =\
                "'+str(formattedMaxOfSelected)+'";'
            a += ('parent.reloadSlider("'+str(formattedMinOfSelected)+'","'
                + str(formattedMaxOfSelected)+'", "'+str(
                formattedMinOfSelected)+'", "'
                + str(formattedMaxOfSelected)+'", '+str(get_step_length(uid))+');</script>')
        else:
            logging.debug("looks like min and max are the same")
            isNotDefaultMin = int(userSelectedMinMax[0]) != 999999999999
            isNotDefaultmax = int(userSelectedMinMax[1]) != -1
            block1 = 'parent.document.getElementById("flow-start-range2")'
            rangeId = block1+'.value = '
            if isNotDefaultmax or isNotDefaultMin:
                a += (rangeId+str(
                    formattedUserMin)+'"; \
                        '+rangeId+'"'+formattedUserMax+'";')
                block1 = 'parent.reloadSlider("' + formattedUserMin + '", "'
                fmos = str(formattedMinOfSelected)
                block2 = formattedUserMax + '", "' + fmos
                block3 = '", "' + formattedMaxOfSelected + '", '+str(get_step_length(uid))+');\
                        </script>'
                a += block1 + block2 + block3
            else:
                fmos = formattedMinOfSelected
                block1 = 'parent.reloadSlider("' + fmos + '", "'
                block2 = formattedMaxOfSelected + '", "' + str(fmos)
                a += block1 + '", "' + formattedMaxOfSelected + '", '+str(get_step_length(uid))+');</script>'
        if isPhysicsEnabled == 'true':
            # add options to reduce text size
            a += \
                """<script>
                var container = document.getElementById("mynetwork");
                var options = {physics: false,
                                nodes: {
                                    shape: "dot",
                                    size: 10,
                                    font: {size: 5}
                                    }
                                };
                var network = new vis.Network(container, data, options);
                </script>"""

        lines = f.readlines()
        for i, line in enumerate(lines):
            # find a pattern so that we can add next to that line
            if line.startswith('</script>'):
                lines[i] = lines[i]+a
        f.truncate()
        f.seek(0)  # rewrite into the file
        for line in lines:
            f.write(line)
        f.close()
    # read from file and return the contents
    with open(path_to_template, 'r') as f:
        return f.read()

# function that returns checksum of config + binary files for a given uid
def calculate_checksum(uid):
    # get user
    user = get_user(uid)
    # get all config files and their checksums
    config_files = get_config_files(user)
    # binary files
    binary_files = user.binary_files
    # get checksums
    checksums = []
    for config_file in config_files:
        # encoded string
        encoded_string = json.dumps(config_files[config_file]).encode('utf-8')
        # create checksum of config file contents
        checksum = hashlib.md5(encoded_string).hexdigest()
        checksums.append(checksum.strip())
    
    # checksum of binary files
    for binary_file in binary_files:
        # encoded string from binary file
        encoded_string = binary_files[binary_file].encode('utf-8')
        # create checksum of config file contents
        checksum = hashlib.md5(encoded_string).hexdigest()
        checksums.append(checksum.strip())

    # create one checksum of all checksums
    checksum = hashlib.md5(''.join(checksums).encode('utf-8')).hexdigest()
    # return checksums
    return checksum

# function to return current checksum for user
def get_current_checksum(uid):
    # get user
    user = get_user(uid)
    # get current checksum
    current_checksum = user.config_checksum
    # return current checksum
    return current_checksum

# set current checksum for user
def set_current_checksum(uid, checksum):
    # get user
    user = get_user(uid)
    # set current checksum
    user.config_checksum = checksum
    # save user
    user.save()

# function to search for user given checksum
def get_user_by_checksum(checksum):
    # query for user with checksum and should_cache = True
    user = models.User.objects.filter(config_checksum=checksum, should_cache=True).first()
    # return user
    return user

# function to copy results from one user to another
def copy_results(from_uid, to_uid):
    logging.info("copying results from " + str(from_uid) + " to " + str(to_uid))
    # get ModelRun object from from_uid
    model_run = get_model_run(from_uid)
    # check if running = False, results aren't empty, and we aren't copying to the same user
    if model_run.is_running == False and model_run.results != {} and from_uid != to_uid:
        # get ModelRun object from to_uid
        model_run_to = get_model_run(to_uid)
        # copy results from from_uid to to_uid
        model_run_to.results = model_run.results
        # save model run
        model_run_to.save()
