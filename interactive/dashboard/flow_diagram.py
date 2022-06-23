from re import I, L
from statistics import quantiles
from unicodedata import decimal
from urllib import request
from pyvis.network import Network
import os
import json
from django.conf import settings
import pandas as pd
import math
# paths to mechansim files
path_to_reactions = os.path.join(
    settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")
path_to_species = os.path.join(
    settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")

# path to output html file
path_to_template = os.path.join(
    settings.BASE_DIR, "dashboard/templates/network_plot/flow_plot.html")

minAndMaxOfSelectedTimeFrame = [999999999999, -1]
userSelectedMinMax = [999999999999, -1]

previous_vals = [0, 1]


# returns species in csv
def get_species():
    csv_results_path = os.path.join(
        os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    concs = [x for x in csv.columns if 'CONC' in x]
    clean_concs = [x.split('.')[1] for x in concs if 'myrate' not in x]
    return clean_concs


# returns length of csv
def get_simulation_length():
    csv_results_path = os.path.join(
        os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    print("* got simulation length: ", (csv.shape[0] - 1))
    print("* got final time:", csv['time'].iloc[-1])
    return int(csv['time'].iloc[-1])


# get user inputted step length
def get_step_length():
    csv_results_path = os.path.join(
        os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    if csv.shape[0] - 1 > 2:
        return int(csv['time'].iloc[1])
    else:
        return 0


# get entire time column from results
def time_column_list():
    csv_results_path = os.path.join(
        os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    return csv['time'].tolist()


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


# check if element is in 'blocked' elements list
def isBlocked(blocked, element_or_reaction):
    for bl in blocked:
        if bl == element_or_reaction and len(blocked) != 0:
            return True
    return False


# make reaction hot hot hot by adding some nicer arrows and cleaning it up
def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
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


# return list of species, reactions, species size and colors.
def findReactionsAndSpecies(list_of_species, reactions_data, blockedSpecies):
    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    global previous_vals
    contained_reactions = {}
    species_nodes = {}
    reactions_nodes = {}
    species_colors = {}
    species_sizes = {}
    for el in list_of_species:
        if el not in blockedSpecies:
            # create empty dict for each species
            species_nodes.update({el: {}})
    for r in reactions_data['camp-data'][0]['reactions']:
        for species in list_of_species:
            species_colors.update({species: "#6b6bdb"})
            species_sizes.update({species: 40})
            if 'reactants' in r:
                if species in r['reactants']:
                    tmp_val = reactions_data['camp-data'][0]['reactions']
                    contained_reactions.update(
                        {tmp_val.index(r): {}})
                    reaction_string = ""
                    for reactant in r['reactants']:
                        species_nodes.update({reactant: {}})
                        reaction_string = reaction_string + reactant + "_"
                    # remove last _ and replace with ->
                    reaction_string = reaction_string[:-1] + "->"
                    for product in r['products']:
                        species_nodes.update({product: {}})
                        reaction_string = reaction_string + product + "_"
                    reaction_string = reaction_string[:-1]
                    reactions_nodes.update({reaction_string: {}})
                if species in r['products']:
                    tmp_val = reactions_data['camp-data'][0]['reactions']
                    contained_reactions.update(
                        {tmp_val.index(r): {}})
                    reaction_string = ""
                    for reactant in r['reactants']:
                        species_nodes.update({reactant: {}})
                        reaction_string = reaction_string + reactant + "_"
                    # remove last + and replace with →
                    reaction_string = reaction_string[:-1] + "->"
                    for product in r['products']:
                        species_nodes.update({product: {}})
                        reaction_string = reaction_string + product + "_"
                    reaction_string = reaction_string[:-1]
                    reactions_nodes.update({reaction_string: {}})
    for speci in species_nodes:
        if speci not in list_of_species:
            species_colors.update({speci: "#94b8f8"})
            species_sizes.update({speci: 20})
    return (contained_reactions, species_nodes,
            reactions_nodes, species_colors, species_sizes)


# return list of raw widths for arrows. Also set new minAndMax
def findReactionRates(reactions_nodes, df, start, end):
    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    global previous_vals
    rates_cols = [x for x in df.columns if 'myrate' in x]
    reactionsToAdd = []
    for re in reactions_nodes:
        # convert index of reaction into actual reaction name
        reactionsToAdd.append(re)
    rates = df[rates_cols]
    first = time_column_list().index(start)
    last = time_column_list().index(end)
    first_and_last = rates.iloc[[first, last]]
    difference = first_and_last.diff()
    values = dict(difference.iloc[-1])
    widths = {}
    for key in values:
        if key.split('.')[1].split("__")[1] in reactionsToAdd:
            widths.update({key.split('.')[1].split("__")[1]: float(
                str('{:0.3e}'.format(values[key])))})
            if values[key] < minAndMaxOfSelectedTimeFrame[0]:
                minAndMaxOfSelectedTimeFrame[0] = values[key]
            if values[key] > minAndMaxOfSelectedTimeFrame[1]:
                minAndMaxOfSelectedTimeFrame[1] = values[key]
    if (minAndMaxOfSelectedTimeFrame[0] == minAndMaxOfSelectedTimeFrame[1]
            and minAndMaxOfSelectedTimeFrame[1] > 0):

        minAndMaxOfSelectedTimeFrame[0] = 0
    mam = minAndMaxOfSelectedTimeFrame
    if (str(previous_vals[0]) != str(float(str('{:0.3e}'.format(mam[0]))))
        or str(previous_vals[1]) != str(float(str('{:0.3e}'.format(mam[1]))))
            or previous_vals[1] == 1):

        userSelectedMinMax = [float(str('{:0.3e}'.format(mam[0]))), float(
            str('{:0.3e}'.format(mam[1])))]
    return widths


# calculate new widths for the arrows by multiplying quantity of species
def sortYieldsAndEdgeColors(reactions_nodes, reactions_data,
                            widths, blockedSpecies, list_of_species):
    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    global previous_vals
    raw_yields = {}
    edgeColors = {}
    quantities, total_quantites, reaction_names_on_hover = findQuantities(
        reactions_nodes, reactions_data)
    userMM = userSelectedMinMax  # short version to clean up code
    print("|_ finished getting quantities:", quantities)
    for reaction in reactions_nodes:

        products_data, reactants_data = getProductsAndReactionsFrom(reaction)
        for product in products_data:
            print("|_ added interaction:", beautifyReaction(
                reaction), " ==> ", product)
            name = reaction+"__TO__"+product
            if (widths[reaction] <= userMM[1]
                    and widths[reaction] >= userMM[0]):
                edgeColors.update({name: "#FF7F7F"})
            else:
                edgeColors.update({name: "#e0e0e0"})
            if (reaction not in blockedSpecies
                    and product not in blockedSpecies):
                tmp = widths[reaction]*quantities[name]
                raw_yields.update(
                    {name: tmp})
        for reactant in reactants_data:
            print("|_ added interaction:", reactant,
                  " ==> ", beautifyReaction(reaction))
            name = reactant+"__TO__"+reaction
            if (reactant not in blockedSpecies
                    and reaction not in blockedSpecies):
                qt = quantities[reactant+"__TO__"+reaction]
                tmp = widths[reaction]*qt
                raw_yields.update(
                    {reactant+"__TO__"+reaction: tmp})
            if (widths[reaction] <= userMM[1]
                    and widths[reaction] >= userMM[0]):
                
                if reactant in list_of_species:
                    edgeColors.update({name: "#6b6bdb"})
                else:
                    edgeColors.update({name: "#94b8f8"})
            else:
                edgeColors.update({name: "#e0e0e0"})
    return (raw_yields, edgeColors, quantities,
            total_quantites, reaction_names_on_hover)


# create line widths scaling based on user selected option
def calculateLineWeights(maxWidth, species_yields, scale_type):
    # use fluxes from map we setup, scale the values, add weights and whatnot
    maxVal = -1
    minVal = 99999999
    rawVal = {}
    numOfInvalids = 0
    if scale_type == 'log':
        print("[5/7] logarithmically scaling weights...")
        if species_yields != {}:

            li = species_yields
            logged = []
            for i in li:
                # fail safe for null->null value
                if (str(i) != 'null->null'
                        and float(0.0) != float(species_yields[i])):
                    rawVal.update({i: species_yields[i]})
                    try:
                        logged.append((i, math.log(species_yields[i])))
                        if species_yields[i] < minVal:
                            minVal = species_yields[i]
                        if species_yields[i] > maxVal:
                            maxVal = species_yields[i]
                    except ValueError:
                        numOfInvalids = numOfInvalids+1
                        logged.append(
                            (i, abs(math.log(abs(species_yields[i])))))
                        if abs(species_yields[i]) < minVal:
                            minVal = abs(species_yields[i])
                        if abs(species_yields[i]) > maxVal:
                            maxVal = abs(species_yields[i])

            vals = [i[1] for i in logged]
            min_val = abs(min(vals))
            range = max(vals) - min(vals)
            if max(vals) == min(vals):
                range = 1
            scaled = [(x[0], (float(((x[1] + min_val)/range))
                       * float(maxWidth)) + 1) for x in logged]
            print("|_ found", numOfInvalids,
                  "invalid values, reversed the lines for them")
            print("[6/7] got logarithmically scaled weights")
            return list(scaled), minVal, maxVal, rawVal
        else:
            print("[7/7] no species selected, returning empty list")
            return list([]), -1, 999999999, {}
    else:
        print("[5/7] linearly scaling weights...")
        li = species_yields
        vals = [species_yields[i] for i in li]
        min_val = abs(min(vals))

        minVal = min_val
        maxVal = abs(max(vals))

        range = max(vals) - min(vals)
        scaled = [(x, (((species_yields[x] + min_val)/range)
                   * int(maxWidth)) + 1) for x in li]
        print("[6/7] got linearly scaled weights")
        return list(scaled), minVal, maxVal, {}


# bring everything together, call functions and debug
def new_find_reactions_and_species(list_of_species, reactions_data,
                                   blockedSpecies, df, start,
                                   end, max_width, scale_type):

    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    global previous_vals
    print(" ***************************************")
    print("*= [1/6] FINDING REACTIONS AND SPECIES =*")
    print(" ***************************************")

    (contained_reactions, species_nodes,
     reactions_nodes, species_colors,
     species_sizes) = findReactionsAndSpecies(
        list_of_species, reactions_data, blockedSpecies)

    print("|_ got species nodes: ", species_nodes)
    print("|_ got reactions nodes: ", reactions_nodes)
    print(" *******************************************")
    print("*= [2/6] FINDING INTEGRATED REACTION RATES =*")
    print(" *******************************************")

    widths = findReactionRates(reactions_nodes, df, start, end)

    print("|_ got raw widths:", widths)
    print(" *************************************")
    print("*= [3/6] sorting yields from species =*")
    print(" *************************************")

    (raw_yields, edgeColors, quantities,
     total_quantites, reaction_names_on_hover) = sortYieldsAndEdgeColors(
        reactions_nodes, reactions_data, widths,
        blockedSpecies, list_of_species)

    print("|_ got calculated yields:", raw_yields)
    print(" *********************************")
    print("*= [4/6] calculating line widths =*")
    print(" *********************************")
    (scaledLineWeights, minVal, maxVal,
     raw_yield_values) = calculateLineWeights(
        max_width, raw_yields, scale_type)
    print("|_ got scaled line weights:", scaledLineWeights)
    print("|_ got min and max:", minVal, "and", maxVal)
    print(" ********************************* ")
    print("*= [6/6] calculating line colors =*")
    print(" ********************************* ")
    re_no = reactions_nodes
    sp_no = species_nodes
    sp_no = scaledLineWeights
    b = blockedSpecies
    # quantities = [] #actually do this later
    return (CalculateEdgesAndNodes(re_no, sp_no, sp_no, b),
            raw_yields, edgeColors, quantities, minVal, maxVal,
            raw_yield_values, species_colors, species_sizes,
            total_quantites, reaction_names_on_hover)


def getProductsAndReactionsFrom(reaction):
    reactants = []
    products = []
    for reactant in reaction.split('->')[0].split('_'):
        reactants.append(reactant)
    for product in reaction.split('->')[1].split('_'):
        products.append(product)
    return products, reactants


def isSpeciesInReaction(reaction, species):
    for re in reaction:
        if species == re:
            return True
    return False


def reactionNameFromDictionary(r):
    reaction_string = ""
    for reactant in r['reactants']:
        reaction_string = reaction_string + reactant + "_"
    reaction_string = reaction_string[:-1] + \
        "->"  # remove last _ and replace with ->
    for product in r['products']:
        reaction_string = reaction_string + product + "_"
    reaction_string = reaction_string[:-1]

    return reaction_string


# return quantities of species in reactions
def findQuantities(reactions_nodes, reactions_json):
    global userSelectedMinMax
    global previous_vals
    global minAndMaxOfSelectedTimeFrame

    # save quantities for use in arrows
    quantities = {}

    # add quantities of every reaction selected for species
    total_quantites = {}

    reaction_names_on_hover = {}  # these names will be shown on hover

    r_list = reactions_json['camp-data'][0]['reactions']
    i = 0
    for reaction in r_list:
        if "products" in r_list[i]:
            # get products data at index reaction
            reaction_data = r_list[i]['products']
            # get reactants data at index reaction
            reactant_data = r_list[i]['reactants']

            reactants_string = ""
            products_string = ""

            speciesFromReaction = reactionNameFromDictionary(r_list[i])

            for reactant in reactant_data:
                reactant_name = reactant
                reactant_yield = reactant_data[reactant_name]
                inReac = isSpeciesInReaction(reactant_data, reactant_name)
                name = str(reactant_name)+"__TO__"+str(speciesFromReaction)
                if (reactant_yield == {}
                    and (isSpeciesInReaction(reaction_data, reactant_name)
                         or inReac)):
                    nme = str(reactant_name)+"__TO__"+str(speciesFromReaction)
                    quantities.update({nme: 1})
                    if str(speciesFromReaction) in reactions_nodes:
                        new_val = total_quantites.get(reactant_name, 0) + 1
                        total_quantites.update(
                            {str(reactant_name): new_val})
                        reactants_string += str(reactant_name)+"_"
                elif (isSpeciesInReaction(reaction_data, reactant_name)
                      or isSpeciesInReaction(reactant_data, reactant_name)):
                    reactant_yield = reactant_yield['qty']
                    
                    quantities.update(
                        {name: reactant_yield})
                    if str(speciesFromReaction) in reactions_nodes:
                        new_val = total_quantites.get(reactant_name, 0)
                        total_quantites.update(
                            {str(reactant_name): new_val + reactant_yield})
                        reactants_string += (str(reactant_yield))
                        reactants_string += str(reactant_name)+"_"
                        rep = ".0"+str(product_name)
                        rep1 = str(product_name)
                        reactants_string = reactants_string.replace(rep, rep1)
            reactants_string = reactants_string[:-1]
            for product in reaction_data:
                product_name = product
                product_yield = reaction_data[product_name]

                # reaction_names_on_hover
                if (product_yield == {}
                    and (isSpeciesInReaction(reaction_data, product_name)
                         or isSpeciesInReaction(reactant_data, product_name))):
                    nme = str(speciesFromReaction)+"__TO__"+str(product_name)
                    quantities.update({nme: 1})

                    # check if reaction is included in user selected species
                    if str(speciesFromReaction) in reactions_nodes:
                        quan = total_quantites.get(product_name, 0)
                        new_val = quan + 1
                        total_quantites.update(
                            {str(product_name): new_val})
                        products_string += str(product_name)+"_"
                elif (isSpeciesInReaction(reaction_data, product_name)
                      or isSpeciesInReaction(reactant_data, product_name)):
                    product_yield = product_yield['yield']
                    name = str(speciesFromReaction)+"__TO__"+str(product_name)
                    quantities.update(
                        {name: product_yield})
                    if str(speciesFromReaction) in reactions_nodes:
                        quan = total_quantites.get(product_name, 0)
                        new_val = quan + product_yield
                        total_quantites.update(
                            {str(product_name): new_val})
                        tmp = str(product_yield) + str(product_name)+"_"
                        products_string += tmp
                        products_string = products_string.replace(".0"+str(
                            product_name), str(product_name))
            products_string = products_string[:-1]
            reaction_names_on_hover.update(
                {speciesFromReaction: reactants_string+"->"+products_string})
        i += 1
    return quantities, total_quantites, reaction_names_on_hover


def CalculateEdgesAndNodes(reactions, species, scaledLineWeights,
                           blockedSpecies):
    print("[7/7] Creating edges and nodes...")
    species = {}
    edges = {}
    reactions = {}

    for weight in scaledLineWeights:

        fromElement = weight[0].split('__TO__')[0].replace("__TO__", "")
        ToElement = weight[0].split('__TO__')[1].replace("__TO__", "")
        lineWidth = float(weight[1])

        if "->" in fromElement:
            # reaction -> product
            edge = (beautifyReaction(fromElement), ToElement, lineWidth)
            edges.update({edge: {}})
            if species not in blockedSpecies:
                species.update({ToElement: {}})
            reactions.update({beautifyReaction(fromElement): {}})
        else:
            # reactant -> reaction
            edge = (fromElement, beautifyReaction(ToElement), lineWidth)
            edges.update({edge: {}})
            if species not in blockedSpecies:
                species.update({fromElement: {}})
            reactions.update({beautifyReaction(ToElement): {}})
    return {'edges': list(edges), 'species_nodes': list(species),
            'reaction_nodes': list(reactions)}


def createLegend():
    x = -300
    y = -250
    legend_nodes = [
        'Element', 'Reaction'
    ]
    return legend_nodes


# parent function for generating flow diagram
def getReactName(reaction_names_on_hover, x):
    return beautifyReaction(reaction_names_on_hover[unbeautifyReaction(x)])
def generate_flow_diagram(request_dict):
    global userSelectedMinMax
    global minAndMaxOfSelectedTimeFrame
    global previous_vals

    if (('maxMolval' in request_dict and 'minMolval' in request_dict)
        and (request_dict['maxMolval'] != ''
        and request_dict['minMolval'] != '')
        and (request_dict['maxMolval'] != 'NULL'
             and request_dict['minMolval'] != 'NULL')):
        userSelectedMinMax = [
            float(request_dict["minMolval"]),
            float(request_dict["maxMolval"])]
        print("new user selected min and max: ", userSelectedMinMax)
    if 'startStep' not in request_dict:
        request_dict.update({'startStep': 1})

    if 'maxArrowWidth' not in request_dict:
        request_dict.update({'maxArrowWidth': 10})
    minAndMaxOfSelectedTimeFrame = [999999999999, -1]
    # load csv file
    csv_results_path = os.path.join(
        os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)

    start_step = int(request_dict['startStep'])
    end_step = int(request_dict['endStep'])

    # scale with correct scaling function
    scale_type = request_dict['arrowScalingType']
    max_width = request_dict['maxArrowWidth']

    previousMin = float(request_dict["currentMinValOfGraph"])
    print("* previous min:",request_dict["currentMinValOfGraph"],"saved as",previousMin)
    previousMax = float(request_dict["currentMaxValOfGraph"])
    print("* previous max:",request_dict["currentMaxValOfGraph"],"saved as",previousMax)
    previous_vals = [previousMin, previousMax]

    isPhysicsEnabled = request_dict['isPhysicsEnabled']
    if isPhysicsEnabled == 'true':
        max_width = 2  # change for max width with optimized performance

    # load species json and reactions json

    with open(path_to_reactions, 'r') as f:
        reactions_data = json.load(f)

    # completely new method of creating nodes and filtering elements
    selected_species = request_dict['includedSpecies'].split(',')
    blockedSpecies = request_dict['blockedSpecies'].split(',')

    (network_content, raw_yields, edgeColors, quantities, minVal, maxVal,
     raw_yield_values, species_colors, species_sizes,
     total_quantites,
     reaction_names_on_hover) = new_find_reactions_and_species(
        selected_species, reactions_data, blockedSpecies,
        csv, start_step, end_step, max_width, scale_type)

    # add edges and nodes
    # force network to be 100% width and height before it's sent to page
    net = Network(height='100%', width='100%', directed=True)
    # make it so we can manually change arrow colors
    net.inherit_edge_colors(False)
    shouldMakeSmallNode = False
    if isPhysicsEnabled == "true":
        net.toggle_physics(False)
        # shouldMakeSmallNode = True
        # net.barnes_hut()
        net.force_atlas_2based()
    else:
        net.force_atlas_2based(gravity=-200, overlap=1)
    
    reac_nodes = network_content['reaction_nodes']
    hover_names = reaction_names_on_hover
    names = [getReactName(hover_names, x) for x in reac_nodes]
    colors = [species_colors[x] for x in network_content['species_nodes']]
    if shouldMakeSmallNode:
        net.add_nodes(names, color=["#FF7F7F" for x in reac_nodes], size=[
                      10 for x in list(reac_nodes)], title=names)
        net.add_nodes(network_content['species_nodes'], color=colors,
                      size=[
                        10 for x in list(network_content['species_nodes'])])
    else:
        net.add_nodes(names, color=[
                      "#FF7F7F" for x in reac_nodes], title=names)
        net.add_nodes(network_content['species_nodes'], color=colors,
                      size=[species_sizes[x] for x in list(
                        network_content['species_nodes'])])
    net.set_edge_smooth('dynamic')
    # add edges individually so we can modify contents
    i = 0
    values = edgeColors
    print("color values:", values)
    for edge in network_content['edges']:
        unbeu1 = unbeautifyReaction(edge[0])
        unbeu2 = unbeautifyReaction(edge[1])
        val = unbeu1+"__TO__"+unbeu2
        print("* loaded edge: ", edge)

        flux = str(raw_yields[unbeu1+"__TO__"+unbeu2])
        if values[val] == "#e0e0e0":
            # don't allow blocked edge to show value on hover
            if "→" in edge[0]:
                be1 = beautifyReaction(reaction_names_on_hover[unbeu1])
                net.add_edge(be1, edge[1], color=values[val], width=edge[2])
            elif "→" in edge[1]:
                be2 = beautifyReaction(reaction_names_on_hover[unbeu2])
                net.add_edge(edge[0], be2, color=values[val], width=edge[2])
            else:
                net.add_edge(edge[0], edge[1],
                             color=values[val], width=edge[2])
        else:
            # hover over arrow to show value for arrows within range

            # check if value is reaction by looking for arrow
            if "→" in edge[0]:
                be1 = beautifyReaction(reaction_names_on_hover[unbeu1])
                net.add_edge(be1, edge[1], color=values[val], width=float(
                             edge[2]), title="flux: "+flux)
            elif "→" in edge[1]:
                be2 = beautifyReaction(reaction_names_on_hover[unbeu2])
                net.add_edge(edge[0], be2, color=values[val], width=float(
                    edge[2]), title="flux: "+flux)
            else:
                net.add_edge(edge[0], edge[1], color=values[val],
                             width=float(edge[2]), title="flux: "+flux)
        i = i+1

    print("* is physics enabled: ", isPhysicsEnabled)

    net.show(path_to_template)
    if minAndMaxOfSelectedTimeFrame[0] == minAndMaxOfSelectedTimeFrame[1]:
        minAndMaxOfSelectedTimeFrame = [0, maxVal]
    with open(path_to_template, 'r+') as f:
        #############################################
        # here we are going to replace the contents #
        #############################################
        a = """<script>
        network.on("stabilizationIterationsDone", function () {
            network.setOptions( { physics: false } );
        });
        </script>"""
        print("((DEBUG)) [min,max] of selected time frame:",
              minAndMaxOfSelectedTimeFrame)
        print("((DEBUG)) [min,max] given by user:", userSelectedMinMax)
        formattedPrevMin = str('{:0.3e}'.format(previousMin))
        formattedPrevMax = str('{:0.3e}'.format(previousMax))
        formattedMinOfSelected = str(
            '{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))
        formattedMaxOfSelected = str(
            '{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))
        formattedUserMin = str('{:0.3e}'.format(userSelectedMinMax[0]))
        formattedUserMax = str('{:0.3e}'.format(userSelectedMinMax[1]))
        if (int(minAndMaxOfSelectedTimeFrame[1]) == -1
                or int(minAndMaxOfSelectedTimeFrame[0]) == 999999999999):
            a = """<script>
        parent.document.getElementById("flow-start-range2").value = "NULL";
        parent.document.getElementById("flow-end-range2").value = "NULL";
        console.log("inputting NULL");"""

        else:
            a = '<script>\
            parent.document.getElementById("flow-start-range2").value = \
            "'+formattedMinOfSelected+'";'
            a += 'parent.document.getElementById("flow-end-range2").value = \
                "'+str(
                formattedMaxOfSelected)+'";'
        a += """
            console.log("ALRIGHTY WE're SETTING NEW CURRENT MIN AND MAX");
        currentMinValOfGraph = """+formattedPrevMin+""";
        currentMaxValOfGraph = """+formattedPrevMax+""";
        console.log("here's what we got:", currentMinValOfGraph, currentMaxValOfGraph);
        """
        if (str(formattedPrevMin) != str(formattedMinOfSelected)
            or str(formattedPrevMax) != str(formattedMaxOfSelected)
                or previousMax == 1):
            print("previousMin:", formattedPrevMin,
                  "does not equal", formattedMinOfSelected)
            print("previousMax:", formattedPrevMax,
                  "does not equal", formattedMaxOfSelected)
            print("previousMin:", previousMin, "equals", 0)
            print("previousMax:", previousMax, "equals", 1)
            a += 'parent.document.getElementById("flow-start-range2").value =\
                "'+str(formattedMinOfSelected)+'";\
                    parent.document.getElementById("flow-end-range2").value =\
                "'+str(formattedMaxOfSelected)+'";'
            a += 'parent.reloadSlider("'+str(formattedMinOfSelected)+'", "'+str(formattedMaxOfSelected)+'", "'+str(
                formattedMinOfSelected)+'", "'+str(formattedMaxOfSelected)+'");</script>'
        else:
            print("looks like min and max are the same")
            if int(userSelectedMinMax[1]) != -1 or int(userSelectedMinMax[0]) != 999999999999:
                a += 'parent.document.getElementById("flow-start-range2").value = "'+str(
                    formattedUserMin)+'"; \
                        parent.document.getElementById("flow-end-range2").value = "'+formattedUserMax+'";'
                a += 'parent.reloadSlider("'+formattedUserMin+'", "'+formattedUserMax+'", "'+str(
                    formattedMinOfSelected)+'", "'+formattedMaxOfSelected+'");</script>'
            else:
                a += 'parent.reloadSlider("'+formattedMinOfSelected+'", "'+formattedMaxOfSelected+'", "'+str(
                    formattedMinOfSelected)+'", "'+formattedMaxOfSelected+'");</script>'
        if isPhysicsEnabled == 'true':
            # add options to reduce text size
            a += \
                """<script>
                var container = document.getElementById("mynetwork");
                var options = {physics: false,
                                nodes: {
                                    shape: "dot",
                                    size: 10,
                                    font: {size: 5}
                                    }
                                };
                var network = new vis.Network(container, data, options);
                </script>"""

        lines = f.readlines()
        for i, line in enumerate(lines):
            # find a pattern so that we can add next to that line
            if line.startswith('</script>'):
                lines[i] = lines[i]+a
        f.truncate()
        f.seek(0)  # rewrite into the file
        for line in lines:
            f.write(line)
