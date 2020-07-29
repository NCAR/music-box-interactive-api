import json


def save(type):
    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/post.json') as g:
        dictionary = json.loads(g.read())

    print(dictionary)

    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json') as f:
        config = json.loads(f.read())

    if type == 'formula':
        for key in dictionary:
            config["formula"].update({key: dictionary[key]})

    if type == 'value':
        for key in dictionary:
            config["value"].update({key: dictionary[key]})

    if type == 'unit':
        for key in dictionary:
            config["unit"].update({key: dictionary[key]})

    with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/species.json', 'w') as f:
        json.dump(config, f, indent=4)



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



