import csv
from zipfile import ZipFile
from distutils.dir_util import copy_tree
from django.conf import settings
import os
from .save import load, save, export
import json
import glob
from django.conf import settings
from interactive.tools import *
import logging
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")


# handles all uploaded evolving conditions files
def manage_uploaded_evolving_conditions_files(f, filename):
    filetype = filename.split('.')[1]
    
    content = f.read()
    destination = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/config"), filename)
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    #writes config json pointing to csv file
    config = open_json('my_config.json')
    if 'evolving conditions' in config:
        evolvs = config['evolving conditions']
    else:
        evolvs = {}
    evolvs.update({filename: {
                'linear combinations': {}
            }
    })
    config.update({'evolving conditions': evolvs})
    dump_json('my_config.json', config)


#checks uploaded configuration against current config file
def validate_config(testDict):
    config = open_json('my_config.json')
    requirements = []
    for key in config:
        requirements.append(key)
    
    errors = []

    for item in requirements:
        if item not in testDict:
            errors.append(item)
    
    if len(errors) > 0:
        return {'success': False, 'errors': errors}
    elif len(errors) == 0:
        return {'success': True}

# loads uploaded json file into dictionary, validates, and saves to json file
def handle_uploaded_json(f):
    content = f.read()
    decoded = content.decode('utf-8')
    config = json.loads(decoded)
    validation = validate_config(config)
    print(validation)
    if validation['success']:
        dump_json('my_config.json', config)


def copyConfigFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()


# loads uploaded zip configuration
def handle_uploaded_zip_config(f):
    content = f.read()
    file_name = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/zip/uploaded"), 'uploaded.zip')
    g = open(file_name, 'wb')
    g.write(content)
    g.close()

    #unzipps into /static/zip/unzipped
    with ZipFile(file_name, 'r') as zip:
        zip.extractall(os.path.join(settings.BASE_DIR, "dashboard/static/zip/unzipped"))

    needed_files = ['my_config.json', 'camp_data/config.json', 'camp_data/reactions.json', 'camp_data/species.json', 'camp_data/tolerance.json']
    with open(os.path.join(settings.BASE_DIR, "dashboard/static/zip/unzipped/config/my_config.json")) as f:
        config = json.loads(f.read())

    #looks for evolving conditions files
    if 'evolving conditions' in config:
        for key in config['evolving conditions']:
            if '.' in key:
                needed_files.append(key)

    #checks that all neccesary files are in the zip
    for f in needed_files:
        if not os.path.isfile(os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/zip/unzipped/config"), f)):
            logging.info('missing needed file from upload: ' + f)
            return False

    #copy files into config folder
    config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")
    src_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/unzipped/config")
    copy_tree(src_path, config_path)

    return True


# create configuration zip
def create_config_zip():
    destination_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/config_copy")
    copy_tree(config_path, destination_path)
    zip_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/output/config.zip")
    with ZipFile(zip_path, 'w') as zip:
        for filepath in glob.iglob(destination_path + '/**', recursive=True):
            relative_path = os.path.relpath(filepath, destination_path)
            if str(relative_path) == 'my_config.json'\
                or str(relative_path) == 'initial_reaction_rates.csv'\
                or str(relative_path).startswith('camp_data'):
                zip.write(filepath, os.path.join('config/', os.path.relpath(filepath, destination_path)))


# saves uploaded loss rates file to config folder
def handle_uploaded_loss_rates(f):
    content = f.read()
    destination = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/config"), 'loss_rates.txt')
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    #writes config json pointing to text file
    config = open_json('my_config.json')
    if 'evolving conditions' in config:
        evolvs = config['evolving conditions']
    else:
        evolvs = {}
    evolvs.update({'loss_rates.txt': {}
    })
    config.update({'evolving conditions': evolvs})
    dump_json('my_config.json', config)


#check if loss rates have been uploaded
def check_loss_uploaded():
    if os.path.isfile(os.path.join(config_path, 'loss_rates.txt')):
        if os.path.getsize(os.path.join(config_path, 'loss_rates.txt')) > 0:
            return True
        else:
            return False
    else:
        return False



# saves uploaded photo rate file to config folder
def handle_uploaded_p_rates(f):
    content = f.read()
    destination = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/config"), 'photo_rates.nc')
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    #writes config json pointing to csv file
    config = open_json('my_config.json')
    if 'evolving conditions' in config:
        evolvs = config['evolving conditions']
    else:
        evolvs = {}
    evolvs.update({
        'photo_rates.nc': {}
    })
    config.update({'evolving conditions': evolvs})
    dump_json('my_config.json', config)


#check if photolysis rates have been uploaded
def check_photo_uploaded():
    if os.path.isfile(os.path.join(config_path, 'photo_rates.nc')):
        if os.path.getsize(os.path.join(config_path, 'photo_rates.nc')) > 0:
            return True
        else:
            return False
    else:
        return False


# create configuration zip
def create_report_zip(report_dict):
    config = open_json('my_config.json')
    config.update({'bug report': report_dict})
    dump_json('my_config.json', config)
    create_config_zip()