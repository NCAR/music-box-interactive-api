import csv
from zipfile import ZipFile
from django.conf import settings
import os
from .save import load, save, export
import json
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





# converts uploaded csv input file to dictionary of values
def handle_uploaded_csv(f):
    content = f.read()
    new = str(content.decode('utf-8'))
    if ',' in new:
        listed = new.split(',')
    for i in listed:
        if '\r\n' in i:
            listed[listed.index(i)] = i.replace('\r\n', '')
    while '' in listed:
        listed.remove('')
    dictFromFile = {}
    fileitems = int(len(listed) / 2)
    for j in listed:
        dictFromFile.update({j: listed[listed.index(j) + fileitems]})
        if len(dictFromFile) == fileitems:
            break
    
    return(dictFromFile)
        
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


# loads uploaded zip configuration
def handle_uploaded_zip_config(f):
    content = f.read()
    file_name = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/zip_upload"), 'uploaded.zip')
    g = open(file_name, 'wb')
    g.write(content)
    g.close()

    with ZipFile(file_name, 'r') as zip:
        zip.printdir()
        zip.extractall()


def copyConfigFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()
      

#copy all files to the static/zip/config_copy directory to be zipped
def copy_files_for_zipping():
    destination_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/config_copy")
    camp_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/config_copy/camp_data")

    filelist = ['my_config.json', 'camp_data/config.json', 'camp_data/mechanism.json', 'camp_data/species.json', 'camp_data/tolerance.json']
    config = open_json('my_config.json')
    for key in config['evolving conditions']:
        if os.path.isfile(os.path.join(config_path, key)):
            filelist.append(key)
    
    for f in filelist:
        copyConfigFile(os.path.join(config_path, f), os.path.join(destination_path, f))
    
    return filelist

# create configuration zip
def create_config_zip():
    filelist = copy_files_for_zipping()
    folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/config_copy")

    zip_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/output/config.zip")
    from_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/config_copy")


    with ZipFile(zip_path, 'w') as zip:
        for i in filelist:
            zip.write(os.path.join(from_path,i), i)


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



