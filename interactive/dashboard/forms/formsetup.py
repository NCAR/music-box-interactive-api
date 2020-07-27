import json

def speciesSetup():
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        blankSpecies = json.loads(f.read())

    formulas = blankSpecies["default"]["Formula"]
    initialValues = blankSpecies["default"]["Initial Value"]
    units = blankSpecies["default"]["Units"]

    return [formulas, initialValues, units]


def loadconfig():
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        blankSpecies = json.loads(f.read())

    formulas = blankSpecies["new"]["Formula"]
    initialValues = blankSpecies["new"]["Initial Value"]
    units = blankSpecies["new"]["Units"]

    return [formulas, initialValues, units]


