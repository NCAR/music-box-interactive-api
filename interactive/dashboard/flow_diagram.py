from unicodedata import decimal
from pyvis.network import Network
import os
import json
from django.conf import settings
import pandas as pd
import math

# paths to mechansim files
path_to_reactions = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")
path_to_species = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")

# path to output html file
path_to_template = os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/flow_plot.html")


# returns species in csv
def get_species():
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    concs = [x for x in csv.columns if 'CONC' in x]
    clean_concs = [x.split('.')[1] for x in concs if 'myrate' not in x]
    return clean_concs


#returns length of csv
def get_simulation_length():
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    return csv.shape[0] -1


#scales values linearly- smallest becomses 1 and largest becomes maxwidth
def relative_linear_scaler(maxWidth, di):
    print(di)
    li = di.items()
    vals = [i[1] for i in li]
    min_val = abs(min(vals))
    range = max(vals) - min(vals)
    scaled = [(x[0], (((x[1] + min_val)/range)* int(maxWidth)) + 1) for x in li]
    return dict(scaled)


#scales values on log- smallest becomes 1 and largest becomes maxwidth
def relative_log_scaler(maxWidth, di):
    print(maxWidth)
    li = di.items()
    logged = []
    for i in li:
        # fail safe for null->null value and so we don't divide/log by 0
        if str(i[0]) != 'null->null' and float(0.0) != float(i[1]):
            # we cant take the log of a number less than 1/ FIGURE OUT WEIRD null->null error
            print("adding i: "+str(i))
            logged.append((i[0], math.log(i[1])))
            
    # logged = [(i[0], math.log(i[1])) for i in li]
    vals = [i[1] for i in logged]
    min_val = abs(min(vals))
    range = max(vals) - min(vals)
    if max(vals) == min(vals): #case where we only have one element selected
        range = 1
    scaled = [(x[0], (float(((x[1] + min_val)/range))* float(maxWidth)) + 1) for x in logged]
    return dict(scaled)


# returns raw widths from dataframe
def trim_dataframe(df, start, end):
    print('trim function', start, end)
    for col in df.columns:
        col.strip()

    rates_cols = [x for x in df.columns if 'myrate' in x]
    rates = df[rates_cols]
    first_and_last = rates.iloc[[start, end]]
    difference = first_and_last.diff()
    values = dict(difference.iloc[-1])
    widths = {}
    for key in values:
        widths.update({key.split('.')[1]: values[key]})
    widths = {key.split('__')[1]: widths[key] for key in widths}
    return widths


# make list of indexes of included reactions
def find_reactions(list_of_species, reactions_json):
    r_list = reactions_json['camp-data'][0]['reactions']
    included = {}
    for reaction in r_list:
        reactants = []
        products = []
        if 'reactants' in reaction:
            reactants = reaction['reactants']

        if 'products' in reaction:
            products = reaction['products']

        for species in list_of_species:
            if (species in products) or (species in reactants):
                included.update({r_list.index(reaction): {}})
                print('prod,react', products, reactants, species)
    # print('included', list(included))
    return list(included)


# make list of indexes into reaction names
def name_included_reactions(included_reactions, reactions_json):
    r_list = reactions_json['camp-data'][0]['reactions']
    names_dict = {}
    for reaction_index in included_reactions:
        reaction = r_list[reaction_index]
        if 'reactants' in reaction:
            reactants = reaction['reactants']
        else:
            reactants = ['null']
        if 'products' in reaction:
            products = reaction['products']
        else:
            products = ['null']
        name = '_'.join(reactants) + '->' + '_'.join(products)
        names_dict.update({reaction_index: name})
    return names_dict


# generates dict with list of edges and list of nodes: di = {'edges': [], 'species_nodes': [], r_nodes: []}
def find_edges_and_nodes(contained_reactions, reactions_names_dict, reactions_json, widths_dict):
    edges = {}
    s_nodes = {}
    r_nodes = []
    r_list = reactions_json['camp-data'][0]['reactions']
    for r_index in contained_reactions:
        reaction = r_list[r_index]
        reaction_name = reactions_names_dict[r_index]
        r_nodes.append(reaction_name)
        try:
            width = widths_dict[reaction_name]
            if 'reactants' in reaction:
                reactants = reaction['reactants']
                for r in reactants:
                    edge = (r, reaction_name, width)
                    edges.update({edge: {}})
                    s_nodes.update({r: {}})
            if 'products' in reaction:
                products = reaction['products']
                for p in products:
                    edge = (reaction_name, p, width)
                    edges.update({edge: {}})
                    s_nodes.update({p: {}})
        except KeyError as e:
            print("discovered key error, most likely the element's scaled width is 0")
    return {'edges': list(edges), 'species_nodes': list(s_nodes), 'reaction_nodes': r_nodes}


# parent function for generating flow diagram
def generate_flow_diagram(request_dict):

    if 'startStep' not in request_dict:
        request_dict.update({'startStep': 1})

    if 'maxArrowWidth' not in request_dict:
        request_dict.update({'maxArrowWidth': 10})

    # load csv file
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)

    start_step = int(request_dict['startStep'])
    end_step = int(request_dict['endStep'])

    # get irr change from dataframe
    trimmed = trim_dataframe(csv, start_step, end_step)

    # scale with correct scaling function
    scale_type = request_dict['arrowScalingType']
    max_width = request_dict['maxArrowWidth']

    if scale_type == 'log':
        scaled = relative_log_scaler(max_width, trimmed)
    else:
        scaled = relative_linear_scaler(max_width, trimmed)

    widths = scaled

    # load species json and reactions json

    with open(path_to_reactions, 'r') as f:
        reactions_data = json.load(f)

    with open(path_to_species, 'r') as f:
        species_data = json.load(f)

    # make list of contained reactions for included species
    selected_species = request_dict['includedSpecies'].split(',')
    contained_reactions = find_reactions(selected_species, reactions_data)
    contained_reaction_names = name_included_reactions(contained_reactions, reactions_data)
    # make lists of edges and nodes
    network_content = find_edges_and_nodes(contained_reactions, contained_reaction_names, reactions_data, widths)

    #add edges and nodes
    net = Network(height='100%', width='100%',directed=True) #force network to be 100% width and height before it's sent to page so we don't have cross-site scripting issues
    
    # net.add_nodes(network_content['species_nodes'], color=['blue' for x in range(len(network_content['species_nodes']))], size=['50' for x in range(len(network_content['species_nodes']))]) # add all nodes at once and fill color array with blue
    # net.add_nodes(network_content['reaction_nodes'], color=['green' for x in range(len(network_content['reaction_nodes']))]) # all nodes at once and fill color array with green
    # ********************* ^^^^ ABOVE CODE ADDS COLORS BUT ALSO CREATES VISUAL BUGS. FOR NOW JUST ADD NODES ^^^^ *********************

    net.add_nodes(network_content['species_nodes']) # add all nodes at once and fill color array with blue
    net.add_nodes(network_content['reaction_nodes'], color=['#FF7F7F' for x in range(len(network_content['reaction_nodes']))]) # all nodes at once and fill color array with green
    
    # net.add_edges(network_content['edges'], title = [x for x in widths]) # add all edges at once and fill title array with widths
    
    net.add_edges(network_content['edges'])
    print(network_content['edges'])
    # print("[DEBUG] Finished Adding nodes + edges:", net)
    print("[DEBUG] pushing new table to page")
    #save as html
    net.force_atlas_2based(gravity=-200, overlap=1)
    net.show(path_to_template)
