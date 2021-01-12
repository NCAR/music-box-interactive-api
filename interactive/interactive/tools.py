import os
import json
from django.conf import settings

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
        'old_config.json': 'config'
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

