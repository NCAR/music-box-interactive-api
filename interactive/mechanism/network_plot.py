from pyvis.network import Network
import os
import json
from django.conf import settings


def generate_network_plot(species, path_to_template=os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/plot.html"),  path_to_reactions=os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")):
    net = Network(directed=True)
    
    with open(path_to_reactions, 'r') as f:
        reactions_data = json.load(f)

    contained_reactions = {}

    for r in reactions_data['camp-data'][0]['reactions']:
        if 'reactants' in r:
            if species in r['reactants']:
                contained_reactions.update({reactions_data['camp-data'][0]['reactions'].index(r): {}})
            if species in r['products']:
                contained_reactions.update({reactions_data['camp-data'][0]['reactions'].index(r): {}})

    print(contained_reactions)
    nodes = {}
    edges = []

    if contained_reactions:
        for i in contained_reactions:
            reactants = [x for x in reactions_data['camp-data'][0]['reactions'][i]['reactants']]
            products = [x for x in reactions_data['camp-data'][0]['reactions'][i]['products']]
            first = '+'.join(reactants)
            second = '+'.join(products)
            name = first + '->' + second
            net.add_node(name, label=name,  color='green', borderWidthSelected=3)
            for j in reactants:
                nodes.update({j: {}})
                edges.append([j, name])
            for k in products:
                nodes.update({k: {}})
                edges.append([name, k])
    else:
        net.add_node(species, label=species, )
    if species in nodes:
        nodes.pop(species)
    net.add_node(species, label=species, color='blue', size=50)
    for n in nodes:
        net.add_node(n, label=n, borderWidthSelected=3, size=40)
    for e in edges:
        net.add_edge(e[0], e[1])

    net.force_atlas_2based(gravity=-100, overlap=1)
    net.show(str(path_to_template))

