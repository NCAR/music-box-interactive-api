import json


def load(dict):
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/post.json',
              'w') as outfile:
        json.dump(dict, outfile, indent=4)


def save(type):
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/post.json') as g:
        dictionary = json.loads(g.read())

    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        species = json.loads(f.read())

    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/options.json') as h:
        options = json.loads(h.read())

    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/initials.json') as i:
        initials = json.loads(i.read())

    if type == 'formula':
        for key in dictionary:
            species["formula"].update({key: dictionary[key]})
        with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json',
                  'w') as f:
            json.dump(species, f, indent=4)

    if type == 'value':
        for key in dictionary:
            species["value"].update({key: dictionary[key]})
        with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json',
                  'w') as f:
            json.dump(species, f, indent=4)

    if type == 'unit':
        for key in dictionary:
            species["unit"].update({key: dictionary[key]})
        with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json',
                  'w') as f:
            json.dump(species, f, indent=4)

    if type == 'options':
        for key in dictionary:
            options.update({key: dictionary[key]})
        with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/options.json',
                      'w') as f:
            json.dump(options, f, indent=4)

    if type == 'conditions':
        for key in dictionary:
            initials['values'].update({key: dictionary[key]})
        with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/initials.json',
                      'w') as f:
            json.dump(initials, f, indent=4)

    if type == 'cond_units':
        for key in dictionary:
            initials['units'].update({key: dictionary[key]})
        with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/initials.json',
                      'w') as f:
            json.dump(initials, f, indent=4)


def new():
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        config = json.loads(f.read())

    number = 1+ len(config['formula'])
    name = 'Species ' + str(number)

    config['formula'].update({name: "Enter Formula"})

    config['value'].update({name: 0})

    config['unit'].update({name: 'mol m-3'})

    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json', 'w') as f:
        json.dump(config, f, indent=4)



