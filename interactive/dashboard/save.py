import json
import os
import shutil
from distutils.dir_util import copy_tree
from django.conf import settings
import logging
from interactive.tools import *
from csv import reader
import random
from scipy.io import netcdf


config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")
initial_reaction_rates_file_path = os.path.join(config_path, 'initial_reaction_rates.csv')

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Put the data from post request into post.json

def load(dicti):
    dump_json('post.json', dicti)


# returns the initial species concentrations
def initial_species_concentrations():
    initial_values = {}
    species = open_json('species.json')
    for key in species["formula"]:
        formula = species["formula"][key]
        units = species["unit"][key]
        value = species["value"][key]
        initial_values[formula] = { "value": value, "units": units }
    return initial_values


# saves a set of initial species concentrations
def initial_species_concentrations_save(initial_values):
    formulas = {}
    units = {}
    values = {}
    i = 0
    for key, value in initial_values.items():
        name = "Species " + str(i)
        formulas[name] = key
        units[name] = value["units"]
        values[name] = value["value"]
        i += 1
    file_data = {}
    file_data["formula"] = formulas
    file_data["unit"] = units
    file_data["value"] = values
    dump_json('species.json', file_data)


# adds/updates entries in an initial conditions file
def add_to_initial_conditions_file(file_path, delimiter, dictionary):
    initial_conditions = {}
    if os.path.isfile(file_path):
        with open(file_path) as f:
            initial_conditions = initial_conditions_file_to_dictionary(f, delimiter)
            f.close()
    for key, value in dictionary.items():
        initial_conditions[key] = value
    with open(file_path, 'w') as f:
        dictionary_to_initial_conditions_file(initial_conditions, f, delimiter)
        f.close()


# converts initial conditions file to dictionary
def initial_conditions_file_to_dictionary(input_file, delimiter):
    content = input_file.read()
    lines = content.split('\n')
    keys = [lines[0]]
    values = [lines[1]]
    if delimiter in content:
        keys = lines[0].split(delimiter)
        values = lines[1].split(delimiter)
    dictionary = {}
    for key in keys:
         key_label = '' if key == '__blank__' else key
         dictionary[key_label] = values[keys.index(key)]
    return(dictionary)

# converts a dictionary to an initial conditions file
def dictionary_to_initial_conditions_file(dictionary, output_file, delimiter):
    column_names = ''
    column_values = ''
    for key, value in dictionary.items():
        key_label = '__blank__' if key == '' else key
        column_names += key_label + delimiter
        column_values += str(value) + delimiter
    output_file.write(column_names[:-1] + '\n' + column_values[:-1])


# save data from the initial reaction rates form
def save_initial_reaction_rates(form):
    initial_rate_data = {}
    current_MUSICA_name = ''
    for key in form:
        if key.split('.')[0] == 'reaction-MUSICA-name':
            current_MUSICA_name = form[key]
        if key.split('.')[0] == 'initial-value':
            initial_rate_data[current_MUSICA_name] = form[key]
    if initial_rate_data:
        with open(initial_reaction_rates_file_path, 'w') as f:
            dictionary_to_initial_conditions_file(initial_rate_data, f, ',')
    else:
        if os.path.exists(initial_reaction_rates_file_path):
            os.remove(initial_reaction_rates_file_path)
    export()


# Combines all individual configuration json files and writes to the config file readable by the mode
def export():
    species = open_json('species.json')
    options = open_json('options.json')
    initials = open_json('initials.json')

    #gets evolving conditions section if it exists
    oldConfig = open_json('my_config.json')
    if 'evolving conditions' in oldConfig:
        evolves = oldConfig['evolving conditions']
    else:
        evolves = {}

    config = {}

    # write model options section

    options_section = {}

    options_section.update({"grid": options["grid"]})
    options_section.update({"chemistry time step ["+ options["chem_step.units"] + "]": options["chemistry_time_step"]})
    options_section.update({"output time step ["+ options["output_step.units"] + "]": options["output_time_step"]})
    options_section.update({"simulation length ["+ options["simulation_length.units"] + "]": options["simulation_length"]})

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

    # write initial reaction rates section

    if os.path.isfile(initial_reaction_rates_file_path):
        config.update({ "initial conditions" : { "initial_reaction_rates.csv" : { } } })
    else:
        config.pop("initial conditions", None)

    config.update({
        "model components": [
        {
            "type": "CAMP",
            "configuration file" : "camp_data/config.json",
            "override species" : {
            "M" : { "mixing ratio mol mol-1" : 1.0 }
        },
            "suppress output" : {
            "M" : { }
        }
      }
    ]
    })

    # write dict as json
    dump_json('my_config.json', config)
    logging.info('my_config.json updated')


# Save the data from the post request to the relevant configuration json

def save(type):
    dictionary = open_json('post.json')
    species = open_json('species.json')
    options = open_json('options.json')
    initials = open_json('initials.json')


 # Saves the formulas for chemical species

    if type == 'formula':
        for key in dictionary:
            species["formula"].update({key: dictionary[key]})
        dump_json('species.json', species)
        logging.info('Species updated')

 # Saves initial concentration values for chemical species

    if type == 'value':
        for key in dictionary:
            species["value"].update({key: dictionary[key]})
        dump_json('species.json', species)
        logging.info('Species updated')

 # Saves units for species concentration

    if type == 'unit':
        for key in dictionary:
            species["unit"].update({key: dictionary[key]})
        dump_json('species.json', species)
        logging.info('Species updated')

 # Saves box model options

    if type == 'options':
        for key in dictionary:
            options.update({key: dictionary[key]})
        dump_json('options.json', options)
        logging.info('box model options updated')

 # Saves initial condtions for the model

    if type == 'conditions':
        for key in dictionary:
            initials['values'].update({key: dictionary[key]})
        dump_json('initials.json', initials)
        logging.info('initial conditions updated')

 # Saves units for the initial conditions

    if type == 'cond_units':
        for key in dictionary:
            initials['units'].update({key: dictionary[key]})
        dump_json('initials.json', initials)
        logging.info('initial conditions updated')

    export()


# Adds a new blank species to the species configuration json

def new():
    config = open_json('species.json')

    number = 1+ len(config['formula'])
    name = 'Species ' + str(number)

    config['formula'].update({name: "Enter Formula"})

    config['value'].update({name: 0})

    config['unit'].update({name: 'mol m-3'})

    dump_json('species.json', config)
    logging.info('new species added')


def save_species(form):
    formulas = {}
    values = {}
    units = {}

    for key in form:
        section = key.split('.')[1]
        name = key.split('.')[0]
        if section == 'Formula':
            formulas.update({name: form[key]})
        if section == 'Initial Value':
            values.update({name: form[key]})
        if section == 'Units':
            units.update({name: form[key]})

    load(formulas)
    save('formula')

    load(values)
    save('value')

    load(units)
    save('unit')


def save_init(form):
    values = {}
    units = {}

    for key in form:
        section = key.split('.')[1]
        name = key.split('.')[0]
        if section == 'init':
            values.update({name: form[key]})
        if section == 'units':
            units.update({name: form[key]})

    load(values)
    save('conditions')

    load(units)
    save('cond_units')


# add an entry to the list of initial reaction rates/rate constants
def add_initial_reaction_rate():
    add_to_initial_conditions_file(initial_reaction_rates_file_path, ',', { "": 0.0 })
    export()


# remove an entry from the list of initial reaction rates/rate constants
def delete_initial_reaction_rate(reaction_name):
    if not os.path.exists(initial_reaction_rates_file_path): return
    with open(initial_reaction_rates_file_path) as f:
        initial_rates = initial_conditions_file_to_dictionary(f, ',')
        f.close()
    initial_rates.pop(reaction_name)
    if not initial_rates:
        if os.path.exists(initial_reaction_rates_file_path):
            os.remove(initial_reaction_rates_file_path)
    else:
        with open(initial_reaction_rates_file_path, 'w') as f:
            dictionary_to_initial_conditions_file(initial_rates, f, ',')
            f.close()
    export()


#remove a species from the species json

def remove_species(id):
    sp_file = open_json('species.json')

    di = {}
    for key in sp_file['formula']:
        subdi = {}
        subdi.update({'formula': sp_file['formula'][key]})
        subdi.update({'value': sp_file['value'][key]})
        subdi.update({'unit': sp_file['unit'][key]})
        di.update({key: subdi})

    di.pop(id)

    empty = {
        'formula': {},
        'value': {},
        'unit': {}
    }

    i = 1
    for key in di:
        name = 'Species ' + str(i)
        for item in di[key]:
            empty[item].update({name: di[key][item]})
        i = i + 1


    dump_json('species.json', empty)
    export()


# load config json for review

def review_json():
    config = open_json('my_config.json')
    return config

# add new photolysis reaction:

def new_photolysis():
    photo = open_json('photo.json')

    number = 1+ len(photo['reactions'])
    name = 'reaction ' + str(number)
    photo['reactions'].update({name: "Enter Reaction"})
    photo['initial value'].update({name: 0})

    dump_json('photo.json', photo)

# fills form json files with info from my_config file
def reverse_export():
    config = open_json('my_config.json')
    
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
            initial_dict['values'].update({condition: config['environmental conditions'][condition][entry]})
            unit = entry.split('[')[1]
            unit = unit.split(']')[0]
            initial_dict['units'].update({condition: unit})

    dump_json('initials.json', initial_dict)
    dump_json('options.json', option_dict)
    dump_json('species.json', species_dict)


# load data from csv upload handler into config files
def uploaded_to_config(uploaded_dict):
    conc = {}
    env = {}

    for key in uploaded_dict:
        if 'CONC.' in key:
            conc.update({key.replace('CONC.', ''): uploaded_dict[key]})
            uploaded_dict.pop(key)
        elif 'ENV.' in key:
            env.update({key.replace('ENV.', ''): uploaded_dict[key]})
            uploaded_dict.pop(key)

    species_dict = {
        'formula': {},
        'value': {},
        'unit': {}
    }
    initial_dict = {
        'values': {},
        'units': {
        "temperature": "K",
        "pressure": "atm"
    }
    }
    

    i = 1
    for species in conc:
        name = 'Species ' + str(i)
        species_dict['formula'].update({name: species})
        species_dict['value'].update({name: conc[species]})
        species_dict['unit'].update({name: 'mol m-3'})
        i = i+1
    
    for condition in env:
        initial_dict['values'].update({condition: env['condition']})
    
    if len(initial_dict['values']) > 0:
        dump_json('initials.json', initial_dict)

    if len(species_dict['formula']) > 0:
        dump_json('species.json', species_dict)

    add_to_initial_conditions_file(os.path.join(config_path, 'initial_reaction_rates.csv'), ',', uploaded_dict)

    export()


# reads variables from netcdf file
def netcdf_header(filename):
    filepath = os.path.join(config_path, filename)
    ncf = netcdf.netcdf_file(filepath, 'r')
    return list(dict(ncf.variables).keys())


# load evolving_conditions data into an array

def display_evolves():
    with open(os.path.join(config_path, 'my_config.json')) as f:
        config = json.loads(f.read())

    e = config['evolving conditions']
    evolving_conditions_list = e.keys()

    file_header_dict = {} #contains a dictionary w/ key as filename and value as header of file
    for i in evolving_conditions_list:
        if '.csv' in i or '.txt' in i:
            path = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/config"), i)
            with open(path, 'r') as read_obj:
                csv_reader = reader(read_obj)
                list_of_rows = list(csv_reader)

            try:
                file_header_dict.update({i:list_of_rows[0]})
            except IndexError:
                file_header_dict.update({i:['EMPTY FILE']})
        elif '.nc' in i:
            netcdf_dims = netcdf_header(i)
            file_header_dict.update({i: netcdf_dims})
        new = {}
        for key in file_header_dict:
            val = file_header_dict[key]
            newval = [x.replace('.', "-") for x in val]
            new.update({key.replace('.', '-'): newval})  
        file_header_dict = new          
    return file_header_dict


def save_linear_combo(filename, combo, scale_factor):
    combo = [x.replace('CONC-', 'CONC.') for x in combo]
    combodict = {'properties': {}, 'scale factor': scale_factor}
    for i in combo:
        combodict['properties'].update({i:{}})
    config = open_json('my_config.json')
    evolving = config['evolving conditions']
    f = evolving[filename]
    lc = f['linear combinations']
    name = str(len(lc) + 1) + 'combination'
    lc.update({name: combodict})
    f.update({'linear combinations': lc})
    evolving.update({filename: f})
    config.update({'evolving conditions': evolving})
    dump_json('my_config.json', config)




def display_linear_combinations():
    config = open_json('my_config.json')
    if 'evolving conditions' not in config:
        return []
    else:
        filelist = config['evolving conditions'].keys()

    linear_combo_dict = {}

    for f in filelist:
        if config['evolving conditions'][f]['linear combinations']:
            for key in config['evolving conditions'][f]['linear combinations']:
                combo = config['evolving conditions'][f]['linear combinations'][key]['properties']
                c = [key for key in combo]
                linear_combo_dict.update({f.replace('.','-'): c})
    
    return linear_combo_dict


def save_photo_start_time(mydict):
    config = open_json('my_config.json')
    options = config['box model options']
    options.update({'simulation start': mydict})
    config.update({'box model options': options})
    dump_json('my_config.json', config)


def display_photo_start_time():
    config = open_json('my_config.json')
    if 'simulation start' in config['box model options']:
        return config['box model options']['simulation start']
    else:
        return {}
    

def clear_e_files():
    config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")
    with open(os.path.join(config_path, 'my_config.json')) as f:
        config = json.loads(f.read())

    e = config['evolving conditions']
    evolving_conditions_list = e.keys()    

    for i in evolving_conditions_list:
        file_path = os.path.join(config_path, i)
        try:
            os.remove(file_path)
        except:
            print('file not found')
    config.update({'evolving conditions': {}})
    dump_json('my_config.json', config)

    print('ev_conditions files cleared')
    return


def copyConfigFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()


# empty the contents of a directory
def empty_folder(path_to_folder):
    for filename in os.listdir(path_to_folder):
        file_path = os.path.join(path_to_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Error deleting %s: %s" % (file_path, e))


def load_example_configuration(name):
    examples_path = os.path.join(settings.BASE_DIR, 'dashboard/static/examples')
    example_folder_path = os.path.join(examples_path, name)
    config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")
    empty_folder(config_path)
    copy_tree(example_folder_path, config_path)
    reverse_export()
