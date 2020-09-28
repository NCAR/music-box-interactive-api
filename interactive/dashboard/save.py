import json
import os
from django.conf import settings
import logging
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Put the data from post request into post.json

def load(dict):
    with open(os.path.join(config_path, "post.json"), 'w') as outfile:
        json.dump(dict, outfile, indent=4)


# Combines all individual configuration json files and writes to the config file readable by the mode
def export():
    with open(os.path.join(config_path, "species.json")) as a:
        species = json.loads(a.read())

    with open(os.path.join(config_path, "options.json")) as b:
        options = json.loads(b.read())

    with open(os.path.join(config_path, "initials.json")) as c:
        initials = json.loads(c.read())

    with open(os.path.join(config_path, "photo.json")) as d:
        photo = json.loads(d.read())

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
    config.update({
        "chemistry": {
            "type": "MICM",
            "solver": {
                "type": "Rosenbrock",
                "absolute tolerance": 1.0e-12,
                "relative tolerance": 1.0e-4
            }
        }
    })

    # write dict as json

    with open(os.path.join(config_path, "my_config.json"), 'w') as f:
        json.dump(config, f, indent=4)
    
    logging.info('my_config.json updated')


# Save the data from the post request to the relevant configuration json

def save(type):
    with open(os.path.join(config_path, "post.json")) as g:
        dictionary = json.loads(g.read())

    with open(os.path.join(config_path, "species.json")) as f:
        species = json.loads(f.read())

    with open(os.path.join(config_path, "options.json")) as h:
        options = json.loads(h.read())

    with open(os.path.join(config_path, "initials.json")) as i:
        initials = json.loads(i.read())

    with open(os.path.join(config_path, "photo.json")) as j:
        photo = json.loads(j.read())

 # Saves the formulas for chemical species

    if type == 'formula':
        for key in dictionary:
            species["formula"].update({key: dictionary[key]})
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species, f, indent=4)
        logging.info('Species updated')

 # Saves initial concentration values for chemical species

    if type == 'value':
        for key in dictionary:
            species["value"].update({key: dictionary[key]})
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species, f, indent=4)
        logging.info('Species updated')

 # Saves units for species concentration

    if type == 'unit':
        for key in dictionary:
            species["unit"].update({key: dictionary[key]})
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species, f, indent=4)
        logging.info('Species updated')

 # Saves box model options

    if type == 'options':
        for key in dictionary:
            options.update({key: dictionary[key]})
        with open(os.path.join(config_path, "options.json"), 'w') as f:
            json.dump(options, f, indent=4)
        logging.info('box model options updated')

 # Saves initial condtions for the model

    if type == 'conditions':
        for key in dictionary:
            initials['values'].update({key: dictionary[key]})
        with open(os.path.join(config_path, "initials.json"), 'w') as f:
            json.dump(initials, f, indent=4)
        logging.info('initial conditions updated')

 # Saves units for the initial conditions

    if type == 'cond_units':
        for key in dictionary:
            initials['units'].update({key: dictionary[key]})
        with open(os.path.join(config_path, "initials.json"), 'w') as f:
            json.dump(initials, f, indent=4)
        logging.info('initial conditions updated')

 # Saves units for the initial conditions

    if type == 'photo-reactions':
        for key in dictionary:
            photo['reactions'].update({key: dictionary[key]})
        with open(os.path.join(config_path, "photo.json"), 'w') as f:
            json.dump(photo, f, indent=4)
        logging.info('photolysis updated')

 # Saves units for the initial conditions

    if type == 'photo-values':
        for key in dictionary:
            photo['initial value'].update({key: dictionary[key]})
        with open(os.path.join(config_path, "photo.json"), 'w') as f:
            json.dump(photo, f, indent=4)
        logging.info('photolysis updated')
    export()


# Adds a new blank species to the species configuration json

def new():
    with open(os.path.join(config_path, "species.json")) as f:
        config = json.loads(f.read())

    number = 1+ len(config['formula'])
    name = 'Species ' + str(number)

    config['formula'].update({name: "Enter Formula"})

    config['value'].update({name: 0})

    config['unit'].update({name: 'mol m-3'})

    with open(os.path.join(config_path, "species.json"), 'w') as f:
        json.dump(config, f, indent=4)
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
    removed = id.split('.')[0]
    with open(os.path.join(config_path, "species.json")) as f:
        specs = json.loads(f.read())

    specs["formula"].pop(removed)
    specs["value"].pop(removed)
    specs["unit"].pop(removed)

    with open(os.path.join(config_path, "species.json"), 'w') as f:
        json.dump(specs, f, indent=4)

    export()


# load config json for review

def review_json():
    with open(os.path.join(config_path, "my_config.json")) as f:
        config = json.loads(f.read())
    
    return config

# add new photolysis reaction:

def new_photolysis():
    with open(os.path.join(config_path, "photo.json")) as f:
        photo = json.loads(f.read())

    number = 1+ len(photo['reactions'])
    name = 'reaction ' + str(number)

    photo['reactions'].update({name: "Enter Reaction"})

    photo['initial value'].update({name: 0})

    with open(os.path.join(config_path, "photo.json"), 'w') as f:
        json.dump(photo, f, indent=4)

# fills form json files with info from config file
def reverse_export():
    with open(os.path.join(config_path, "my_config.json")) as f:
        config = json.loads(f.read())
    
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
    
    with open(os.path.join(config_path, "photo.json"), 'w') as f:
        json.dump(photo_dict, f, indent=4)
    
    with open(os.path.join(config_path, "initials.json"), 'w') as f:
        json.dump(initial_dict, f, indent=4)

    with open(os.path.join(config_path, "options.json"), 'w') as f:
        json.dump(option_dict, f, indent=4)

    with open(os.path.join(config_path, "species.json"), 'w') as f:
        json.dump(species_dict, f, indent=4)


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
        with open(os.path.join(config_path, "initials.json"), 'w') as f:
            json.dump(initial_dict, f, indent=4)

    if len(species_dict['formula']) > 0:
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species_dict, f, indent=4)

    export()

