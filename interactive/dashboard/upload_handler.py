import csv
from django.conf import settings
import os
from .save import load, save, export
import json
from django.conf import settings
from interactive.tools import *
import logging
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")


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


# saves uploaded evolving_conditions file to config folder
def handle_uploaded_evolve(f):
    content = f.read()
    destination = os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/config"), 'evolving_conditions.csv')
    g = open(destination, 'wb')
    g.write(content)
    g.close()

    #writes config json pointing to csv file
    config = open_json('my_config.json')
    if 'evolving conditions' in config:
        evolvs = config['evolving conditions']
    else:
        evolvs = {}
    evolvs.update({'evolving_conditions.csv': {
                'linear combinations': {}
            }
    })
    config.update({'evolving conditions': evolvs})
    dump_json('my_config.json', config)


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



