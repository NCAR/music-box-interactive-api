import json
from django.conf import settings
import os
from csv import reader



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
