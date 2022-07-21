import os
import json
from django.conf import settings
from django.http import HttpResponse
from .unit_dict import *
from .conversion_dict import *
from .converter_class import Unit


# get path for filename
def file_path(filename):
    locations = {
        'initials.json': 'config',
        'my_config.json': 'config',
        'options.json': 'config',
        'photo.json': 'config',
        'post.json': 'config',
        'species.json': 'config',
        'chapman.json': 'mechanism',
        'datamolec_info.json': 'mechanism',
        'datamolec_info copy.json': 'mechanism',
        'form_stage.json': 'mechanism',
        'latex.json': 'mechanism',
        'reaction_stage.json': 'mechanism',
        'T1mozcart.json': 'mechanism',
        'mol_name.json': 'mechanism',
        'linear_combinations.json': 'config',
        'log_config.json': 'log',
        'old_config.json': 'config',
        'run_button.json': 'config',
        'plots_configuration.json': 'config'
    }
    file_loc = locations[filename]
    if file_loc == "config":
        return os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/config"), filename)
    elif file_loc == "mechanism":
        return os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/mechanism"), filename)
    elif file_loc == "log":
        return os.path.join(os.path.join(settings.BASE_DIR, "dashboard/static/log"), filename)



# open json file with filename
def open_json(filename):
    path = file_path(filename)
    with open(path) as f:
        dicti = json.loads(f.read())
    return dicti


def direct_open_json(filePath):
    with open(filePath) as f:
        dicti = json.loads(f.read())
    return dicti


def direct_dump_json(filePath, content):
    with open(filePath, 'w') as f:
        json.dump(content, f, indent=4)
        # json.dump(content, f)


# save dictionary as json to a file
def dump_json(filename, content):
    path = file_path(filename)
    with open(path, 'w') as f:
        json.dump(content, f, indent=4)


# turns 'E a' notation to "10^a" notations
def sci_note(dirty):
    if 'e' in dirty:
        a = dirty.split('e')
        b = a[0].strip('0')
        c = b.strip('.')
        scinote = c + '*10^{' + a[1] + '}'
    else: scinote = dirty
    return scinote

# same as sci_note() but with tags for mathjax rendering
def sci_note_jax(dirty):
    if 'e' in dirty:
        a = dirty.split('e')
        b = a[0].strip('0')
        c = b.strip('.')
        scinote = c + '*10^{' + a[1] + '}'
    else: scinote = dirty
    jax = "\\" + "begin{equation}" + scinote + "\\" + "end{equation}"
    return jax

# converts parameter labels to mathjax items
def param_jax(dirty):
    if "_" in dirty:
        a = dirty.split('_')
        b = "_{" + a[1] + "}"
        return "\\" + "begin{equation}" + a[0] + b + "=\\" + "end{equation}"
    else:
        return "\\" + "begin{equation}" + dirty + "=\\" + "end{equation}"


def copyAFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()


def create_unit_converter(initial_unit, final_unit):
    convertObject = Unit(conversionTree, unitDict)
    my_converter = convertObject.convert(initial_unit, final_unit)
    return my_converter


def is_density_needed(a, b):
    units = unitDict
    type_a = units[a]['subtype']
    type_b = units[b]['subtype']
    if type_a == type_b:
        return False
    else:
        return True


def getUnitTypes():
    return conversionTree.keys()


def get_required_arguments(initial_unit, final_unit):
    convertObject = Unit(conversionTree, unitDict)
    args = convertObject.get_arguments(initial_unit, final_unit)
    return args

