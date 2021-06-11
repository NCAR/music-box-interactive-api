import os
import time
import subprocess
from django.conf import settings
from interactive.tools import *
from mechanism.reactions import reactions_are_valid
from shutil import rmtree
import json

if "MUSIC_BOX_BUILD_DIR" in os.environ:
    mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    interface_solo = False
else:
    print(os.environ)
    mb_dir = ''
    interface_solo = True

out_path = os.path.join(mb_dir, 'output.csv')
error_path = os.path.join(mb_dir, 'error.json')
copy_path = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/past.csv')
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/my_config.json")
old_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/old_config.json")
complete_path = os.path.join(mb_dir, 'MODEL_RUN_COMPLETE')


config_dest = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/config.json')

config_folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")
camp_folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data")

def copyConfigFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()

reactions_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")
species_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")


def add_integrated_rates():
    with open(reactions_path) as f:
            r_data = json.loads(f.read())

    with open(species_path) as h:
            s_data = json.loads(h.read())

    names_list = []
    reactions = r_data['pmc-data'][0]['reactions']
    for r in reactions:
        reactants = [j for j in r['reactants']]
        products = [m for m in r['products']]
        name = "myrate__" + '_'.join(reactants) + "->" + '_'.join(products)
        r['products'].update({name: {}})
        names_list.append(name)
    
    for name in names_list:
        s_data['pmc-data'].append({"name": name, "type": "CHEM_SPEC"})

    r_data['pmc-data'][0].update({'reactions': reactions})
    with open(reactions_path, 'w') as g:
        json.dump(r_data, g)
    
    with open(species_path, 'w') as i:
        json.dump(s_data, i)


def create_file_list():
    config = open_json('my_config.json')
    filelist = []
    configFolderContents = os.listdir(config_folder_path)

    for configSection in config:
        section = config[configSection]
        for configItem in section:
            if '.' in configItem:
                filelist.append(configItem)
    
    for name in filelist:
        if name not in configFolderContents:
            filelist.remove(name)
    return filelist


def setup_run():
    if interface_solo:
        return {'model_running': False, 'error_message': 'Model not connected to interface.'}
    if not reactions_are_valid():
        return {'model_running': False, 'error_message': 'At least one reaction must be present for the model to run.'}

    if os.path.isfile(complete_path):
        os.remove(complete_path)
    if os.path.isfile(out_path):
        os.remove(out_path)
    if os.path.isfile(error_path):
        os.remove(error_path)

    with open(reactions_path) as h:
        reactions_data = json.load(h)

    with open(species_path) as j:
        species_data = json.load(j)

    add_integrated_rates()

    config = open_json('my_config.json')

    newpath = os.path.join(mb_dir, 'mb_configuration')
    if os.path.exists(newpath):
        rmtree(newpath)
        os.mkdir(newpath)
    else:
        os.mkdir(newpath)
    filelist = create_file_list()
    filelist.append('my_config.json')
    print(filelist)
    for f in filelist:
        copyConfigFile(os.path.join(config_folder_path, f), os.path.join(newpath, f))

    camp_path = os.path.join(mb_dir, 'camp_data')
    if os.path.exists(camp_path):
        rmtree(camp_path)
    os.mkdir(camp_path)
    for f in os.listdir(camp_folder_path):
        copyConfigFile(os.path.join(camp_folder_path, f), os.path.join(camp_path, f))

    time.sleep(0.1)

    filelist.remove('my_config.json')
    for f in filelist:
        copyConfigFile(os.path.join('/build/mb_configuration', f), os.path.join('/build', f))
    process = subprocess.Popen([r'./music_box', r'./mb_configuration/my_config.json'], cwd=mb_dir)

    with open(reactions_path, 'w') as k:
        json.dump(reactions_data, k)

    with open(species_path, 'w') as l:
        json.dump(species_data, l)

    return {'model_running': True}

# copy inital config file on first model run
def setup_config_check():
    copyConfigFile(config_path, old_path)


