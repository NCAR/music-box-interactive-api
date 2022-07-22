import csv
from unittest import case
from zipfile import ZipFile
from distutils.dir_util import copy_tree
from django.conf import settings
import os
from .save import load, save, export
import json
import glob
from django.conf import settings
from interactive.tools import *
from pathlib import Path
import logging
import shutil
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")

config_files_to_ignore = [
    'initials.json',
    'linear_combinations.json',
    'old_config.json',
    'options.json',
    'photo.json',
    'post.json',
    'reactions.json',
    'species.json',
    'README'
]
config_default = os.path.join(settings.BASE_DIR, "dashboard/static/config")
logging.basicConfig(filename='logs.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s', level=logging.DEBUG)
logging.basicConfig(filename='errors.log', filemode='w', format='%(asctime)s - [ERROR!!] %(message)s', level=logging.ERROR)


# reads csv file into dictionary
def manage_initial_conditions_files(f, filename, pathz=config_default):
    content = f.read()
    destination = os.path.join(pathz, filename)
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    # writes config json pointing to csv file
    config = direct_open_json(pathz+'/my_config.json')
    if 'initial conditions' in config:
        initials = config['initial conditions']
    else:
        initials = {}
    initials.update({filename: {}})
    config.update({'initial conditions': initials})
    direct_dump_json(pathz+'/my_config.json', config)


# removes an initial conditions file
def initial_conditions_file_remove(remove_request, path=config_default):
    # remove file
    filepath = os.path.join(path, remove_request['file name'])
    os.remove(filepath)

    # update config json
    config = direct_open_json(path+'/my_config.json')
    del config['initial conditions'][remove_request['file name']]
    direct_dump_json(path+'/my_config.json', config)


# handles all uploaded evolving conditions files
def manage_uploaded_evolving_conditions_files(f, filename,
                                              pathz=config_default):
    content = f.read()
    destination = os.path.join(pathz, filename)
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    # writes config json pointing to csv file
    config = direct_open_json(pathz+'/my_config.json')
    if 'evolving conditions' in config:
        evolvs = config['evolving conditions']
    else:
        evolvs = {}
    evolvs.update({filename: {
        'linear combinations': {}
    }
    })
    config.update({'evolving conditions': evolvs})
    direct_dump_json(pathz+'/my_config.json', config)


# checks uploaded configuration against current config file
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
def handle_uploaded_zip_config(f, uploaded_path="dashboard/static/zip",
                               config_path=config_default):
    content = f.read()
    file_name = os.path.join(os.path.join(
        settings.BASE_DIR, uploaded_path+"/uploaded"), 'uploaded.zip')
    logging.info("taking zip from " + file_name)
    if not os.path.isdir(file_name.replace('uploaded.zip', '')):
        # make dirs just in case
        os.makedirs(file_name.replace('uploaded.zip', ''))
    if not os.path.isfile(file_name):
        g = open(file_name, 'x')
    g = open(file_name, 'wb')
    logging.info("writing zip to " + file_name)
    g.write(content)
    g.close()

    # unzipps into /static/zip/unzipped
    with ZipFile(file_name, 'r') as zip:
        zip.extractall(os.path.join(
            settings.BASE_DIR, uploaded_path+"/unzipped"))
    logging.info("extracted zip into " +os.path.join(
            settings.BASE_DIR, uploaded_path+"/unzipped"))
    camp_files = ['camp_data/config.json', 'camp_data/reactions.json',
                  'camp_data/species.json', 'camp_data/tolerance.json']
    needed_files = ['my_config.json']
    needed_files.extend(camp_files)
    confg_sjon = "/unzipped/config_copy/my_config.json"
    print("* all files in unzipped dir: ", os.listdir(os.path.join(settings.BASE_DIR, uploaded_path+"/unzipped")))
    with open(os.path.join(settings.BASE_DIR, uploaded_path+confg_sjon)) as f:
        config = json.loads(f.read())

    # looks for evolving conditions files
    if 'evolving conditions' in config:
        for key in config['evolving conditions']:
            if '.' in key:
                needed_files.append(key)
    unzip = os.path.join(settings.BASE_DIR, uploaded_path+"/unzipped/config_copy")
    # checks that all neccesary files are in the zip
    for f in needed_files:
        if not os.path.isfile(os.path.join(unzip, f)):
            logging.info('missing needed file from upload: ' + f)
            return False

    # updates CAMP file format if necessary
    for file_name in camp_files:
        path = os.path.join(os.path.join(settings.BASE_DIR,
                            uploaded_path+"/unzipped/config_copy"), file_name)
        with open(path) as config_file:
            file_data = json.loads(config_file.read())
            config_file.close()
        if 'pmc-files' in file_data.keys():
            file_data['camp-files'] = file_data['pmc-files']
            del file_data['pmc-files']
        if 'pmc-data' in file_data.keys():
            file_data['camp-data'] = file_data['pmc-data']
            del file_data['pmc-data']
        with open(path, 'w') as config_file:
            json.dump(file_data, config_file, indent=2)
            config_file.close()

    # copy files into config folder
    src_path = os.path.join(
        settings.BASE_DIR, uploaded_path+"/unzipped/config_copy")
    copy_tree(src_path, config_path)

    return True


confg_def = os.path.join(settings.BASE_DIR,
                         "dashboard/static/zip/config_copy")
zip_pathj = "dashboard/static/zip/output/config.zip"


# create configuration zip
def create_config_zip(destination_path=confg_def,
                      zip_path=os.path.join(
                          settings.BASE_DIR, zip_pathj),
                      conf_path=config_path):
    copy_tree(conf_path, destination_path)
    if not os.path.isdir(zip_path.replace('config.zip', '')):
        # make dirs just in case
        os.makedirs(zip_path.replace('config.zip', ''))
    logging.info("* making zip @ " + zip_path)
    # create zip via shutil
    make_archive(destination_path, zip_path)

def make_archive(source, destination, format='zip'):
    base, name = os.path.split(destination)
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    print(f'Source: {source}\nDestination: {destination}\nArchive From: {archive_from}\nArchive To: {archive_to}\n')
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)
# saves uploaded loss rates file to config folder
def handle_uploaded_loss_rates(f):
    content = f.read()
    destination = os.path.join(os.path.join(
        settings.BASE_DIR, "dashboard/static/config"), 'loss_rates.txt')
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    # writes config json pointing to text file
    config = open_json('my_config.json')
    if 'evolving conditions' in config:
        evolvs = config['evolving conditions']
    else:
        evolvs = {}
    evolvs.update({'loss_rates.txt': {}
                   })
    config.update({'evolving conditions': evolvs})
    dump_json('my_config.json', config)


# check if loss rates have been uploaded
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
    destination = os.path.join(os.path.join(
        settings.BASE_DIR, "dashboard/static/config"), 'photo_rates.nc')
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    # writes config json pointing to csv file
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


# check if photolysis rates have been uploaded
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
