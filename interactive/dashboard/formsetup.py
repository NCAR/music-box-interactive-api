import json


with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
    blankSpecies = json.loads(f.read())

formulas = blankSpecies["Formula"]
initialValues = blankSpecies["Initial Value"]
units = blankSpecies["Units"]

print(units)