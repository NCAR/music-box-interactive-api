import csv
from django.conf import settings
import os
from .save import load, save, export
import json
from django.conf import settings
import logging
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")


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
        

def validate_config(testDict):
    with open(os.path.join(config_path, "my_config.json")) as f:
        config = json.loads(f.read())
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


def handle_uploaded_json(f):
    content = f.read()
    decoded = content.decode('utf-8')
    config = json.loads(decoded)
    validation = validate_config(config)
    print(validation)
    if validation['success']:
        with open(os.path.join(config_path, "my_config.json"), 'w') as outfile:
            json.dump(config, outfile, indent=4)
