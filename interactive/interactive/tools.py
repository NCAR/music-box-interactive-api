import os
import json
from django.conf import settings
from django.http import HttpResponse

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


# creates a unit contersion function which converts from initial_unit to final_unit
# if units used are both mixing ratios or number densities:
# converter = create_unit_converter(initial_unit, final_unit)
# final = converter(initial)

# if units used are not both mixing ratios or number densities:
# converter = create_unit_converter(initial_unit, final_unit)
# final = converter(initial=i, density=density)

#factor is relative to the 'base unit' for each unit type (mol/mol and mol/m-3)
def get_units():
    unitDict = {
        'ppm':{
            'type': 'mixing ratio',
            'factor': 1e6
        },
        'ppb':{
            'type': 'mixing ratio',
            'factor': 1e9
        },
        'mol/mol':{
            'type': 'mixing ratio',
            'factor': 1
        },
        'mol/m-3':{
            'type': 'number density',
            'factor': 1
        },
        'molecule/m-3':{
            'type': 'number density',
            'factor': 6.0221415e23
        },
        'mol/cm-3':{
            'type': 'number density',
            'factor': 1e6
        },
        'molecule/cm-3':{
            'type': 'number density',
            'factor': 6.0221415e29
        },
        'K':{
            'type': 'temperature',
            'factor': 1,
            'offset': 273.15
        },
        'C':{
            'type': 'temperature',
            'factor': 1,
            'offset': 0
        },
        'F':{
            'type': 'temperature',
            'factor': 1.8,
            'offset': 32
        },
        'Pa':{
            'type': 'pressure',
            'factor': 1,
        },
        'atm':{
            'type': 'pressure',
            'factor': 9.86923e-6,
        },
        'bar':{
            'type': 'pressure',
            'factor': 1e-5,
        },
        'kPa':{
            'type': 'pressure',
            'factor': 0.001,
        },
        'hPa':{
            'type': 'pressure',
            'factor': 0.01,
        },
        'mbar':{
            'type': 'pressure',
            'factor': 0.01,
        }
    }
    return unitDict


def create_unit_converter(initial_unit, final_unit):
    units = get_units()

    if initial_unit not in units:
        print('initial not in unit contverter')
        return False
    if final_unit not in units:
        print('final not in unit contverter')
        return False
    unit_types = (units[initial_unit]['type'], units[final_unit]['type'])
    if unit_types[0] == unit_types[1]:
        if 'offset' not in units[initial_unit]:
            def converter(initial_value):
                new = (initial_value / units[initial_unit]['factor']) * units[final_unit]['factor']
                return new  
            return converter 
        else:
            def converter(initial_value):
                new = (((initial_value - units[initial_unit]['offset']) / units[initial_unit]['factor']) * units[final_unit]['factor']) + units[final_unit]['offset']
                return new  
            return converter
    else:
        def converter(initial_value, number_density, nd_units):
            base = initial_value / units[initial_unit]['factor']
            adjusted_density = number_density / units[nd_units]['factor']
            if unit_types[0] == 'number density':
                new = (base / adjusted_density) * units[final_unit]['factor']
            else:
                new = (base * adjusted_density) * units[final_unit]['factor']
            return new
        return converter


def is_density_needed(a, b):
    units = get_units()
    type_a = units[a]['type']
    type_b = units[b]['type']
    if type_a == type_b:
        return False
    else:
        return True


def make_unit_convert_form(unit_type):
    response = HttpResponse()
    units = get_units()
    if unit_type == "concentration":
        unit_options = [key for key in units if units[key]['type'] in ('number density', 'mixing ratio')]
        response.write('<div class="input-group mb-3"><select class="btn btn-primary dropdown-toggle concentration-select" id="initialValueUnit">')
        for unit in unit_options:
            response.write('<option value="')
            response.write(unit)
            response.write('">')
            response.write(unit)
            response.write('</option>')
        response.write('<input type="text" id="initialValue" class="form-control" placeholder="Enter value"></div>')
        response.write('<div id="densityFormHolder" class="input-group mb-3 d-none"><select class="btn btn-primary dropdown-toggle" id="densityUnit"><option value="mol/m-3">mol/m-3</option><option value="mol/cm-3">mol/cm-3</option><option value="molecule/m-3">molecule/m-3</option><option value="molecule/cm-3">molecule/cm-3</option></select><input type="text" id="densityValue" class="form-control" placeholder="Enter density"></div>')
        response.write('<div class="input-group mb-3"><span class="input-group-text">Convert to:</span><select class="btn btn-primary dropdown-toggle concentration-select" id="finalValueUnit">')
        for unit in unit_options:
            response.write('<option value="')
            response.write(unit)
            response.write('">')
            response.write(unit)
            response.write('</option>')
        response.write('</select></div>')
    else:
        unit_options = [key for key in units if units[key]['type'] == unit_type]
        response.write('<div class="input-group mb-3"><select class="btn btn-primary dropdown-toggle" id="initialValueUnit">')
        for unit in unit_options:
            response.write('<option value="')
            response.write(unit)
            response.write('">')
            response.write(unit)
            response.write('</option>')
        response.write('<input type="text" id="initialValue" class="form-control" placeholder="Enter value"></div>')
        response.write('<div class="input-group mb-3"><span class="input-group-text">Convert to:</span><select class="btn btn-primary dropdown-toggle" id="finalValueUnit">')
        for unit in unit_options:
            response.write('<option value="')
            response.write(unit)
            response.write('">')
            response.write(unit)
            response.write('</option>')
        response.write('</select></div>')
    response.write('<button id="convertSubmit" class="btn btn-primary">Convert</button>')
    return response

