import json


def formula_setup():
    with open('/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        data = json.loads(f.read())

    formulas = data["formula"]
    return formulas


def value_setup():
    with open('/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        data = json.loads(f.read())

    values = data["value"]
    return values


def unit_setup():
    with open('/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        data = json.loads(f.read())

    units = data["unit"]
    return units


def option_setup():
    with open('/music-box-interactive/interactive/dashboard/static/config/options.json') as f:
        data = json.loads(f.read())

    return data


def ini_cond_setup():
    with open('/music-box-interactive/interactive/dashboard/static/config/initials.json') as f:
        data = json.loads(f.read())

    return data
