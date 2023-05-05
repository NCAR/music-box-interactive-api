from api import models
from api.response_models import RunStatus

import hashlib
import json
import logging

logger = logging.getLogger(__name__)

def user_exists(uid):
    try:
        models.SessionUser.objects.get(uid=uid)
    except models.SessionUser.DoesNotExist:
        return False
    return True

# get user based on uid
def get_user_or_start_session(uid):
    # check if user exists
    try:
        user = models.SessionUser.objects.get(uid=uid)
        return user
    except models.SessionUser.DoesNotExist:
        # if not, create new user
        user = create_user(uid)
        return user


# get model run based on uid
def get_model_run(uid):
    try:
        model = models.ModelRun.objects.get(uid=uid)
        return model
    except models.ModelRun.DoesNotExist:
        # if not, create new model run
        model_run = create_model_run(uid)
        return model_run


# get config files of user
def get_config_files(uid):
    return get_user_or_start_session(uid).config_files


# get csv files of user
def get_csv_files(uid):
    return get_user_or_start_session(uid).csv_files


# get results of model run
def get_results(uid):
    return get_model_run(uid).results


# get is running of model run
def get_is_running(uid):
    return get_model_run(uid).is_running


# set config files of user
def set_config_files(uid, config_files):
    user = get_user_or_start_session(uid)
    user.config_files = config_files
    user.save()


# set csv files of user
def set_csv_files(uid, csv_files):
    user = get_user_or_start_session(uid)
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
    logging.info("["+str(uid)+"] set running to: "+str(is_running))
    model_run.save()


# create new user
def create_user(uid):
    user = models.SessionUser(uid=uid)
    user.save()
    return user


# create new model run
def create_model_run(uid):
    model_run = models.ModelRun(uid=uid)
    model_run.save()
    return model_run


# delete user
def delete_user(uid):
    user = get_user_or_start_session(uid)
    user.delete()


# delete model run
def delete_model_run(uid):
    model_run = get_model_run(uid)
    model_run.delete()


# delete all users
def delete_all_users():
    models.SessionUser.objects.all().delete()


# delete all model runs
def delete_all_model_runs():
    models.ModelRun.objects.all().delete()


# delete all config files
def delete_all_config_files(uid):
    user = get_user_or_start_session(uid)
    user.config_files = {}
    user.save()


# delete all csv files
def delete_all_csv_files(uid):
    user = get_user_or_start_session(uid)
    user.csv_files = {}
    user.save()


# delete results
def delete_results(uid):
    model_run = get_model_run(uid)
    model_run.results = {}
    model_run.save()


# set specific config file of user
def set_config_file(uid, filename, config_file):
    user = get_user_or_start_session(uid)
    user.config_files[filename] = config_file
    user.save()


# set specific csv file of user
def set_csv_file(uid, filename, csv_file):
    user = get_user_or_start_session(uid)
    user.csv_files[filename] = csv_file
    user.save()


# delete specific config file of user
def delete_config_file(uid, filename):
    user = get_user_or_start_session(uid)
    del user.config_files[filename]
    user.save()


# delete specific csv file of user
def delete_csv_file(uid, filename):
    user = get_user_or_start_session(uid)
    del user.csv_files[filename]
    user.save()


# search all users for checksum of config files,
# and check if should_cache is true.
# [return] list of uids of users that
# have should_cache equal to true for their current model run.
def search_for_config_checksum(checksum):
    users = models.SessionUser.objects.all()
    uids = []
    for user in users:
        if user.config_checksum == checksum:
            if user.should_cache:
                uids.append(user.uid)
    return uids


# get species menu of user
def get_mechanism(uid):
    user = get_user_or_start_session(uid)
    # check if species.json exists
    species = []
    reactions = []
    if '/camp_data/species.json' in user.config_files:
        camp_data = user.config_files['/camp_data/species.json']["camp-data"]
        species = []
        for entry in camp_data:
            if entry['type'] == "CHEM_SPEC":
                species.append(entry['name'])
    if '/camp_data/reactions.json' in user.config_files:
        reactions = user.config_files['/camp_data/reactions.json']["camp-data"][0]['reactions']
    return {
        'species': sorted(species),
        'reactions': reactions
    }

# get species detail of user
def get_species_detail(uid, species_name):
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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


# get reactions details of user
def get_reactions_info(uid):
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
    camp_data = user.config_files['/camp_data/reactions.json']["camp-data"]
    camp_data[0]['reactions'].pop(index)
    user.config_files['/camp_data/reactions.json']["camp-data"] = camp_data
    user.save()


# save reaction for user
def save_reaction(uid, reaction_data):
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
    print("* returning model options: ", user.config_files['/options.json'])
    return user.config_files['/options.json']


def post_model_options(uid, newOptions):
    user = get_user_or_start_session(uid)
    print("* setting model options: ", newOptions)
    user.config_files['/options.json']['camp-data'] = newOptions
    user.save()


# get initial conditions files of user
def get_initial_conditions_files(uid):
    user = get_user_or_start_session(uid)
    values = {}
    config = user.config_files['/my_config.json']
    if 'initial conditions' in config:
        values = config['initial conditions']
    return values


# get conditions species list
def get_condition_species(uid):
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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
    error = {}
    try:
        model = get_model_run(uid)
        logger.debug(f"model: {model}")
        logger.debug(f"model.status: {model.status}")
        logger.debug(f"model.results: {model.results}")
        status = RunStatus(model.status)
        if status == RunStatus.ERROR:
            error = model.results.error
    except models.ModelRun.DoesNotExist:
        status = RunStatus.NOT_FOUND
        logger.info(f"[{uid}] model run not found for user")
    return {'status': status, 'error': error}

# convert to/from model config format
def export_to_database_path(uid):
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
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
        arrhenius_schema = ('/music-box-interactive/interactive/mechanism/'
                            'arrhenius_schema.json')
        # arrhenius_schema = os.path.join(
        #     BASE_DIR, '/mechanism/arrhenius_schema.json')
        with open(arrhenius_schema) as file:
            json_file = json.load(file)
            schema = json_file["schema"]
            schema['reactants']['children']['key'] = species
            schema['products']['children']['key'] = species

    elif reaction_type == 'EMISSION':
        emission_schema = ('/music-box-interactive/interactive/mechanism/'
                           'emission_schema.json')
        # emission_schema_schema = os.path.join(
        #     BASE_DIR, '/mechanism/emission_schema.json')
        with open(emission_schema) as file:
            json_file = json.load(file)
            schema = json_file["schema"]
            schema['species']['values'] = species

    elif reaction_type == 'FIRST_ORDER_LOSS':
        first_order_loss_schema = ('/music-box-interactive/interactive/'
                                   'mechanism/first_order_loss_schema.json')
        # first_order_loss_schema = os.path.join(
        #     BASE_DIR, '/mechanism/first_order_loss_schema.json')
        with open(first_order_loss_schema) as file:
            json_file = json.load(file)
            schema = json_file["schema"]
            schema['species']['values'] = species

    elif reaction_type == 'PHOTOLYSIS':
        photolysis_schema = ('/music-box-interactive/interactive/mechanism/'
                             'photolysis_schema.json')
        # photolysis_schema.json = os.path.join(
        #     BASE_DIR, '/mechanism/photolysis_schema.json')
        with open(photolysis_schema) as file:
            json_file = json.load(file)
            schema = json_file["schema"]
            schema['reactants']['children']['key'] = species
            schema['products']['children']['key'] = species

    elif reaction_type == 'TERNARY_CHEMICAL_ACTIVATION':
        ternary_chemical_activation_schema = ('/music-box-interactive/'
                                              'interactive/mechanism/'
                                              'ternary_chemical_'
                                              'activation_schema.json')
        # ternary_chemical_activation_schema.json = os.path.join(
        #     BASE_DIR, '/mechanism/ternary_chemical_activation_schema.json')
        with open(ternary_chemical_activation_schema) as file:
            json_file = json.load(file)
            schema = json_file["schema"]
            schema['reactants']['children']['key'] = species
            schema['products']['children']['key'] = species

    elif reaction_type == 'TROE':
        troe_schema = ('/music-box-interactive/interactive/mechanism/'
                       'troe_schema.json')
        # troe_schema.json = os.path.join(
        #     BASE_DIR, '/mechanism/troe_schema_schema.json')
        with open(troe_schema) as file:
            json_file = json.load(file)
            schema = json_file["schema"]
            schema['reactants']['children']['key'] = species
            schema['products']['children']['key'] = species
    return schema

# function that returns checksum of config + binary files for a given uid
def calculate_checksum(uid):
    # get user
    user = get_user_or_start_session(uid)
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
    user = get_user_or_start_session(uid)
    # get current checksum
    current_checksum = user.config_checksum
    # return current checksum
    return current_checksum

# set current checksum for user
def set_current_checksum(uid, checksum):
    # get user
    user = get_user_or_start_session(uid)
    # set current checksum
    user.config_checksum = checksum
    # save user
    user.save()

# function to search for user given checksum
def get_user_by_checksum(checksum):
    # query for user with checksum and should_cache = True
    user = models.SessionUser.objects.filter(config_checksum=checksum, should_cache=True).first()
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
