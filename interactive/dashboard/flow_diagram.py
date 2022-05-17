from unicodedata import decimal
from urllib import request
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

raw_mol_rates = {}
maxMol = -1
minMol = 999999999999

filteredMaxMol = -1
filteredMinMol = 999999999999
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
    # print(di)
    li = di.items()
    vals = [i[1] for i in li]
    min_val = abs(min(vals))
    range = max(vals) - min(vals)
    scaled = [(x[0], (((x[1] + min_val)/range)* int(maxWidth)) + 1) for x in li]
    return dict(scaled)


#scales values on log- smallest becomes 1 and largest becomes maxwidth
def relative_log_scaler(maxWidth, di):
    # print(maxWidth)
    li = di.items()
    logged = []
    for i in li:
        print("got item", i)
        # fail safe for null->null value and so we don't divide/log by 0
        if str(i[0]) != 'null->null' and float(0.0) != float(i[1]):
            # we cant take the log of a number less than 1/ FIGURE OUT WEIRD null->null error
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
    global maxMol
    global minMol
    global filteredMaxMol
    global filteredMinMol
    global raw_mol_rates
    print('trim function', start, end)

    # reset min and max mol
    maxMol = -1
    minMol = 999999999999


    raw_mol_rates = {}
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
        raw_mol_rates.update({key.split('.')[1]: values[key]})
        # print("checking for max:", key, values[key], "max:", maxMol, " ====>",float(values[key]) > float(maxMol) or maxMol == -1)
        # print("checking for min:", key, values[key], "min:", minMol, " ====>",float(values[key]) < float(minMol) or minMol == 999999999999)
        if float(values[key]) > float(maxMol) or maxMol == -1:
            #new max
            maxMol = float(values[key])
        if float(values[key]) < float(minMol) or minMol == 999999999999:
            #new min
            minMol = float(values[key])
    widths = {key.split('__')[1]: widths[key] for key in widths}
    raw_mol_rates = {key.split('__')[1]: raw_mol_rates[key] for key in raw_mol_rates}
    if filteredMaxMol == -1:
        filteredMaxMol = maxMol
    if filteredMinMol == 999999999999:
        filteredMinMol = minMol
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
                # print('prod,react', products, reactants, species)
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

def isBlocked(blocked, element_or_reaction):
    for bl in blocked:
        if bl == element_or_reaction and len(blocked) != 0:
            return True
    return False
def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction
# generates dict with list of edges and list of nodes: di = {'edges': [], 'species_nodes': [], r_nodes: []}
def find_edges_and_nodes(contained_reactions, reactions_names_dict, reactions_json, widths_dict, blocked):
    global maxMol
    global minMol
    global raw_mol_rates
    edges = {}
    s_nodes = {}
    r_nodes = []

    edge_colors = []
    species_colors = {}
    reactions_colors = []
    r_list = reactions_json['camp-data'][0]['reactions']
    print("blocked list:", blocked)
    print("contained reactions count:", len(contained_reactions))
    for r_index in contained_reactions:
        reaction = r_list[r_index]
        reaction_name = reactions_names_dict[r_index]
        isInRange = (float(raw_mol_rates[reaction_name]) <= float(filteredMaxMol)) and (float(raw_mol_rates[reaction_name]) >= float(filteredMinMol))
        if isInRange:
            reactions_colors.append("#FF7F7F")
        else:
            print("out of range:", raw_mol_rates[reaction_name], " ===>", filteredMaxMol, filteredMinMol)
            reactions_colors.append("#ededed")

        r_nodes.append(beautifyReaction(reaction_name))
        try:
            width = widths_dict[reaction_name]
            if 'reactants' in reaction:
                reactants = reaction['reactants']
                for r in reactants:
                    edge = (r, beautifyReaction(reaction_name), width)
                    # check if in blocked list
                    if (isBlocked(blocked, r) == False or len(blocked) == 0 or blocked == ['']) and isInRange == True:
                        #if not blocked, dont add species node or edge
                        edges.update({edge: {}})
                        s_nodes.update({r: {}})
                        edge_colors.append("#94b8f8")
                        species_colors[r] = "#94b8f8"
                    elif (isBlocked(blocked, r) == False or len(blocked) == 0 or blocked == ['']) and isInRange == False:
                        #not in range, make grey
                        
                        edges.update({edge: {}})
                        s_nodes.update({r: {}})
                        edge_colors.append("#ededed")
                        species_colors[r] = "#ededed"

            if 'products' in reaction:
                products = reaction['products']
                for p in products:
                    edge = (beautifyReaction(reaction_name), p, width)
                    # check if in blocked list
                    if (isBlocked(blocked, p) == False or len(blocked) == 0 or blocked == ['']) and isInRange == True:
                        #if not blocked, dont add species node or edge
                        
                        edges.update({edge: {}})
                        s_nodes.update({p: {}})
                        edge_colors.append("#94b8f8")
                        species_colors[r] = "#94b8f8"
                    elif (isBlocked(blocked, p) == False or len(blocked) == 0 or blocked == ['']) and isInRange == False:
                        #not in range, make grey
                        edges.update({edge: {}})
                        s_nodes.update({p: {}})
                        edge_colors.append("#ededed")
                        species_colors[p] = "#ededed"

        except Exception as e:
            print("discovered key error, most likely the element's scaled width is 0")
            print("error e:", e)
    return {'edges': list(edges), 'species_nodes': list(s_nodes), 'reaction_nodes': r_nodes, 'edge_colors': edge_colors, 'species_colors': species_colors, 'reactions_colors': reactions_colors}

def createLegend():
    x = -300
    y = -250
    legend_nodes = [
       'Element', 'Reaction'
    ]
    return legend_nodes
# parent function for generating flow diagram
def generate_flow_diagram(request_dict):
    global filteredMaxMol
    global filteredMinMol
    if ('maxMolval' in request_dict and 'minMolval' in request_dict) and (request_dict['maxMolval'] != '' and request_dict['minMolval'] != ''):
        filteredMaxMol = float(request_dict["maxMolval"])
        filteredMinMol = float(request_dict["minMolval"])
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
    network_content = find_edges_and_nodes(contained_reactions, contained_reaction_names, reactions_data, widths, request_dict['blockedSpecies'].split(','))

    #add edges and nodes
    net = Network(height='100%', width='100%',directed=True) #force network to be 100% width and height before it's sent to page so we don't have cross-site scripting issues


    print("species nodes:", network_content['species_nodes'], "color nodes:", network_content['species_colors'])
    print("reaction nodes:", network_content['reaction_nodes'], "edges:", network_content['edges'])
    net.add_nodes(network_content['reaction_nodes'], color=[x for x in network_content['reactions_colors']])
    for spec in network_content["species_nodes"]:
        network_content['species_colors'].setdefault(spec, "#94b8f8")
    net.add_nodes(network_content['species_nodes'], color=[network_content['species_colors'][x] for x in network_content['species_nodes']])
    
    
    net.add_edges(network_content['edges']) # add all edges
    
    print("[DEBUG] pushing new table to page using url:",path_to_template)
    #save as html
    net.force_atlas_2based(gravity=-200, overlap=1)
    net.show(path_to_template)

    with open(path_to_template, 'r+') as f:
        ###################################################################################################################
        # here we are going to replace the contents of the file with new html to avoid problems with cross-site scripting #
        ###################################################################################################################
        a = ''
        if minMol == 999999999999 or maxMol == -1:
            a = '<script>parent.document.getElementById("flow-start-range2").value = "NULL"; parent.document.getElementById("flow-end-range2").value = "NULL"; console.log("inputting NULL");'
        
        else:
            a = '<script>parent.document.getElementById("flow-start-range2").value = "'+str('{:0.3e}'.format(minMol))+'"; parent.document.getElementById("flow-end-range2").value = "'+str('{:0.3e}'.format(maxMol))+'"; console.log("Overrided element values via cross scripting?");'
        a = a + 'parent.document.getElementById("filterRange").value = parent.document.getElementById("flow-start-range2").value + " to " + parent.document.getElementById("flow-end-range2").value;' #update our filter range with new values
        a = a + 'parent.reloadSlider("'+str(filteredMinMol)+'", "'+str(filteredMaxMol)+'");</script>' #destroy slider and update slider entirely
        
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('</script>'):   # find a pattern so that we can add next to that line
                lines[i] = lines[i]+a
        f.truncate()
        f.seek(0)  # rewrite into the file
        for line in lines:
            f.write(line)
    