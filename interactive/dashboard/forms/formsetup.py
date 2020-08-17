import json
from django.conf import settings
import os

config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")

def formula_setup():
    with open(os.path.join(config_path, 'species.json')) as f:
        data = json.loads(f.read())

    formulas = data["formula"]
    return formulas


def value_setup():
    with open(os.path.join(config_path, 'species.json')) as f:
        data = json.loads(f.read())

    values = data["value"]
    return values


def unit_setup():
    with open(os.path.join(config_path, 'species.json')) as f:
        data = json.loads(f.read())

    units = data["unit"]
    return units


def option_setup():
    with open(os.path.join(config_path, 'options.json')) as f:
        data = json.loads(f.read())

    return data


def ini_cond_setup():
    with open(os.path.join(config_path, 'initials.json')) as f:
        data = json.loads(f.read())

    return data


def photo_setup():
    with open(os.path.join(config_path, 'photo.json')) as f:
        data = json.loads(f.read())

    return data


def ini_cond_units():
    with open(os.path.join(config_path, 'initials.json')) as f:
        data = json.loads(f.read())
        choices = {}
        temp = data['units']['temperature']
        if temp == 'K':
            templist = [('K', 'K'), ('C', 'C')]
        if temp == 'C':
            templist = [('C', 'C'), ('K', 'K')]
        else:
            templist = [('K', 'K'), ('C', 'C')]
        choices.update({'temperature': templist})

        press = data['units']['pressure']
        if press == 'atm':
            preslist = [[('atm', 'atm'), ('kPa', 'kPa'), ('bar', 'bar')]
        if press == 'kPa':
             preslist = [[('kPa', 'kPa'), ('atm', 'atm'), ('bar', 'bar')]
        if press == 'bar':
            preslist = [[('bar', 'bar'), ('atm', 'atm'), ('kPa', 'kPa')]
        else:
            preslist = [[('atm', 'atm'), ('kPa', 'kPa'), ('bar', 'bar')]

        choices.update({'pressure': preslist})

        return choices
