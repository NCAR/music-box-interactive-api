import pika
import os

import json
base_dir = '/music-box-interactive/interactive'
try:
    from django.conf import settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
    base_dir = settings.BASE_DIR
except:
    pass

from conversion_dict import conversionTree
from converter_class import Unit
from unit_dict import unitDict

def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '__' in reaction:
        reaction = reaction.replace('__', ' (')
        reaction = reaction+")"
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction

# undo beautifyReaction (usually used when indexing dictionaries)
def unbeautifyReaction(reaction):
    if '→' in reaction:
        reaction = reaction.replace(' → ', '->')
    if '+' in reaction:
        reaction = reaction.replace(' + ', '_')
    return reaction

# checks server by trying to connect
def check_for_rabbit_mq():
    """
    Checks if RabbitMQ server is running.
    """
    try:
        RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
        RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
        RABBIT_USER = os.environ["RABBIT_MQ_USER"]
        RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
        connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
        connection = pika.BlockingConnection(connParam)
        if connection.is_open:
            connection.close()
            return True
        else:
            connection.close()
            return False
    except pika.exceptions.AMQPConnectionError:
        return False

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
        cfg = os.path.join(base_dir, "dashboard/static/config")
        return os.path.join(cfg, filename)
    elif file_loc == "mechanism":
        cfg = os.path.join(base_dir, "dashboard/static/mechanism")
        return os.path.join(cfg, filename)
    elif file_loc == "log":
        cfg = os.path.join(base_dir, "dashboard/static/log")
        return os.path.join(cfg, filename)



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
