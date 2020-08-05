import json
import os
from django.conf import settings

config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")


def load(dict):
    with open(os.path.join(config_path, "post.json"), 'w') as outfile:
        json.dump(dict, outfile, indent=4)


def export():
    with open(os.path.join(config_path, "species.json")) as a:
        species = json.loads(a.read())

    with open(os.path.join(config_path, "options.json")) as b:
        options = json.loads(b.read())

    with open(os.path.join(config_path, "initials.json")) as c:
        initials = json.loads(c.read())

    config = {}

    # write model options section

    options_section = {}

    options_section.update({"grid": options["grid"]})
    options_section.update({"chemistry time step [min]": options["chemistry_time_step"]})
    options_section.update({"output time step [hr]": options["output_time_step"]})
    options_section.update({"simulation length [hr]": options["simulation_length"]})

    # write chemical species section

    species_section = {}

    for i in species["formula"]:

        formula = species["formula"][i]
        units = species["unit"][i]
        value = species["value"][i]

        string = "initial value " + "[" + units + "]"

        species_section.update({formula: {string: value}})

    # write initial conditions section

    init_section = {}

    for i in initials["values"]:
        name = i
        units = initials["units"][i]
        value = initials["values"][i]

        string = "initial value " + "[" + units + "]"

        init_section.update({name: {string: value}})

    # write sections to main dict

    config.update({"box model options": options_section})
    config.update({"chemical species": species_section})
    config.update({"environmental conditions": init_section})
    config.update({
        "chemistry": {
            "type": "MICM",
            "solver": {
                "type": "Rosenbrock",
                "absolute tolerance": 1.0e-12,
                "relative tolerance": 1.0e-4
            }
        }
    })

    # write dict as json

    with open(os.path.join(config_path, "my_config.json"), 'w') as f:
        json.dump(config, f, indent=4)



def save(type):
    with open(os.path.join(config_path, "post.json")) as g:
        dictionary = json.loads(g.read())

    with open(os.path.join(config_path, "species.json")) as f:
        species = json.loads(f.read())

    with open(os.path.join(config_path, "options.json")) as h:
        options = json.loads(h.read())

    with open(os.path.join(config_path, "initials.json")) as i:
        initials = json.loads(i.read())

    if type == 'formula':
        for key in dictionary:
            species["formula"].update({key: dictionary[key]})
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species, f, indent=4)

    if type == 'value':
        for key in dictionary:
            species["value"].update({key: dictionary[key]})
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species, f, indent=4)

    if type == 'unit':
        for key in dictionary:
            species["unit"].update({key: dictionary[key]})
        with open(os.path.join(config_path, "species.json"), 'w') as f:
            json.dump(species, f, indent=4)

    if type == 'options':
        for key in dictionary:
            options.update({key: dictionary[key]})
        with open(os.path.join(config_path, "options.json"), 'w') as f:
            json.dump(options, f, indent=4)

    if type == 'conditions':
        for key in dictionary:
            initials['values'].update({key: dictionary[key]})
        with open(os.path.join(config_path, "initials.json"), 'w') as f:
            json.dump(initials, f, indent=4)

    if type == 'cond_units':
        for key in dictionary:
            initials['units'].update({key: dictionary[key]})
        with open(os.path.join(config_path, "initials.json"), 'w') as f:
            json.dump(initials, f, indent=4)

    export()


def new():
    with open(os.path.join(config_path, "species.json")) as f:
        config = json.loads(f.read())

    number = 1+ len(config['formula'])
    name = 'Species ' + str(number)

    config['formula'].update({name: "Enter Formula"})

    config['value'].update({name: 0})

    config['unit'].update({name: 'mol m-3'})

    with open(os.path.join(config_path, "species.json"), 'w') as f:
        json.dump(config, f, indent=4)


