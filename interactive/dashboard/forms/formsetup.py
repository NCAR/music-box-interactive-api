import json


def formula_setup():
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        data = json.loads(f.read())

    formulas = data["formula"]
    print(formulas)
    return formulas


def value_setup():
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        data = json.loads(f.read())

    values = data["value"]
    return values


def unit_setup():
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        data = json.loads(f.read())

    units = data["unit"]
    return units


formula_setup()
value_setup()
unit_setup()
