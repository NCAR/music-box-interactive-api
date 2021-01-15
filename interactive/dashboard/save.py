import json
import os
from django.conf import settings
import logging
from interactive.tools import *
from csv import reader
import random

config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Put the data from post request into post.json

def load(dicti):
    dump_json('post.json', dicti)


# Combines all individual configuration json files and writes to the config file readable by the mode
def export():
    species = open_json('species.json')
    options = open_json('options.json')
    initials = open_json('initials.json')
    photo = open_json('photo.json')

    #gets evolving conditions section if it exists
    oldConfig = open_json('my_config.json')
    if 'evolving conditions' in oldConfig:
        evolves = oldConfig['evolving conditions']
    else:
        evolves = ''
    

    config = {}

    # write model options section

    options_section = {}

    options_section.update({"grid": options["grid"]})
    options_section.update({"chemistry time step [min]": options["chemistry_time_step"]})
    options_section.update({"output time step [hr]": options["output_time_step"]})
    options_section.update({"simulation length [hr]": options["simulation_length"]})

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

    # write photolysis section
    photo_section = {}

    for i in photo['reactions']:
        reaction = photo['reactions'][i]
        value = photo['initial value'][i]

        string = "initial value [s-1]"

        photo_section.update({reaction: {string: value}})


    # write sections to main dict

    config.update({"box model options": options_section})
    config.update({"chemical species": species_section})
    config.update({"environmental conditions": init_section})
    config.update({"photolysis": photo_section})

    if evolves:
        config.update({'evolving conditions': evolves})

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
    
    photo = open_json('photo.json')
   

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

 # Saves units for the initial conditions

    if type == 'photo-reactions':
        for key in dictionary:
            photo['reactions'].update({key: dictionary[key]})
        dump_json('photo.json', photo)
        logging.info('photolysis updated')

 # Saves units for the initial conditions

    if type == 'photo-values':
        for key in dictionary:
            photo['initial value'].update({key: dictionary[key]})
        dump_json('photo.json', photo)
        logging.info('photolysis updated')
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


def save_photo(form):
    reactions = {}
    values = {}

    for key in form:
        section = key.split('.')[1]
        name = key.split('.')[0]
        if section == 'r_form':
            reactions.update({name: form[key]})
        if section == 'init':
            values.update({name: form[key]})
    
    load(reactions)
    save('photo-reactions')

    load(values)
    save('photo-values')


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
    
    photo_dict = {
        "reactions": {},
        "initial value": {}
    }
    i = 1
    for reaction in config['photolysis']:
        name = "reaction " + str(i)
        photo_dict['reactions'].update({name: reaction})
        for entry in config['photolysis'][reaction]:
            photo_dict['initial value'].update({name: config['photolysis'][reaction][entry]})
        
        i = i+1
    
    dump_json('photo.json', photo_dict)
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
        elif 'ENV.' in key:
            env.update({key.replace('ENV.', ''): uploaded_dict[key]})

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
        
    export()


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
            file_header_dict.update({i:['NETCDF FILE']})
    return file_header_dict


def save_linear_combo(comboDict):
    name = 'combo' + str(random.randint(0, 9999))

    output_dict = {
        'properties': {},
        'scale factor': 1.0
    }
    if comboDict['Scale Factor'] == '':
        comboDict.pop('Scale Factor')
    for key in comboDict:
        if 'on' in comboDict[key]:
            output_dict['properties'].update({
                'CONC.' + key.split('.')[1]: {}
            })
        elif key == 'Scale Factor':
            output_dict.update({'scale factor': float(comboDict[key])})
            
    
    config = open_json('my_config.json')
    evolving_conditions = config['evolving conditions']
    lcs = config['evolving conditions']['evolving_conditions.csv']['linear combinations']
    
    lcs.update({name: output_dict})
    evolving_conditions.update({"evolving_conditions.csv":{'linear combinations': lcs}})
    config.update({'evolving conditions':evolving_conditions})
    dump_json('my_config.json', config)


def display_linear_combinations():
    config = open_json('my_config.json')
    if 'evolving conditions' not in config:
        return []
    elif 'evolving_conditions.csv' in config['evolving conditions']:
        lcs = config['evolving conditions']['evolving_conditions.csv']['linear combinations']
    else:
        return []
    
    lc_list = []

    for combo in lcs:
        props = []
        for key in lcs[combo]['properties']:
            props.append(key.split('.')[1])
        scale = lcs[combo]['scale factor']
        lc_list.append([props, scale])
    
    return lc_list


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