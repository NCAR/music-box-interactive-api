from re import I, L
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

minAndMaxOfSelectedTimeFrame = [999999999999, -1]
userSelectedMinMax = [999999999999, -1]

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
# make list of indexes of included reactions, and names of all species that participate in them
def find_reactions_and_species(list_of_species, reactions_json):
    print("[2/7] finding reactions and species")
    r_list = reactions_json['camp-data'][0]['reactions']
    included_reactions = {}
    included_species = {}
    for species in list_of_species: # catches species that don't participate in any reactions
        included_species.update({species: {}})
    for reaction in r_list:
        reactants = []
        products = []
        if 'reactants' in reaction:
            reactants = reaction['reactants']

        if 'products' in reaction:
            products = reaction['products']

        for species in list_of_species:
            if (species in products) or (species in reactants):
                included_reactions.update({r_list.index(reaction): {}})
                if 'reactants' in reaction:
                    for reactant in reaction['reactants']:
                        included_species.update({reactant: {}})
                if 'products' in reaction:
                    for product in reaction['products']:
                        included_species.update({product: {}})

    return list(included_reactions), list(included_species)
# return two lists, one is all the species, the other is all the reaction nodes
# (using integrated reaction rates JUST for set of reaction we get)
def getAllNodes(request_dict, reactions_data):
    print("[1/7] Finding nodes via species and reactions")
    # 1) get selected species and get list of reactions from those
    # 2) use reactions to get list of species
    # 3) remove blocked species from list of species
    # 4) return lists
    selected_species = request_dict['includedSpecies'].split(',')
    blockedSpecies = request_dict['blockedSpecies'].split(',')

    reactions, species = find_reactions_and_species(selected_species, reactions_data)

    for spec in species:
        if spec in blockedSpecies:
            species.remove(spec)
    return reactions, species

    
# 1) pass csv file
# 2) start time, end time
# 3) list of reactions
def getIntegratedReactionRates(df, start, end, reactions):
    # return list of integrated reaction rates (the diffrence between start and end time) ONLY for selected/non-blocked reactions
    print("[3/7] getting integrated reaction rates")
    rates_cols = [x for x in df.columns if 'myrate' in x]

    reactionsToAdd = []
    for re in reactions:
        reactionsToAdd.append(rates_cols[re].replace(' CONC.', '')) #convert index of reaction into actual reaction name
    rates = df[rates_cols]
    first_and_last = rates.iloc[[start, end]]
    difference = first_and_last.diff()
    values = dict(difference.iloc[-1])
    widths = {}
    for key in values:
        if key.split('.')[1] in reactionsToAdd:
            widths.update({key.split('.')[1]: float(str('{:0.3e}'.format(values[key])))})
    
    widths = {key.split('__')[1]: widths[key] for key in widths}
    print("final widths:", widths)
    return widths
def updateMinOrMaxInTimeFrame(newvalue):
    #check if newvalue is greater than or less than the min and max of our dataframe
    global minAndMaxOfSelectedTimeFrame
    global userSelectedMinMax
    # print("comparing current minMax:",minAndMaxOfSelectedTimeFrame,"with new value:",newvalue)
    if newvalue < minAndMaxOfSelectedTimeFrame[0]:
        minAndMaxOfSelectedTimeFrame[0] = newvalue
        # if userSelectedMinMax[0] < minAndMaxOfSelectedTimeFrame[0] or userSelectedMinMax[0] == 999999999999:
        #     userSelectedMinMax[0] = minAndMaxOfSelectedTimeFrame[0]
        
    if newvalue > minAndMaxOfSelectedTimeFrame[1]:
        minAndMaxOfSelectedTimeFrame[1] = newvalue
        # if userSelectedMinMax[1] > minAndMaxOfSelectedTimeFrame[1] or userSelectedMinMax[1] == -1:
        #     userSelectedMinMax[1] = minAndMaxOfSelectedTimeFrame[1]
def CalculateRawYields(df, reactions_json, reactions, widths, blockedSpecies): #pass dataframe and reactions widths
    global userSelectedMinMax
    global minAndMaxOfSelectedTimeFrame
    # return a map where the key the species name and value is integrated reaction rate from previous function mulitplied by quantity/yield for this species
    # FORMAT FOR RETURN ARRAY: [{'N2__TO__O1D_N2->O_N2' : yield}, {'[FROM]__TO__[TO]': (reaction_rate * yield)}, ...]
    print("[4/7] sorting yields from species")
    calculatedYields = {}

    edgeColors = {}
    rates_cols = [x for x in df.columns if 'myrate' in x]

    reationsNamesList = []
    for re in reactions:
        reationsNamesList.append(rates_cols[re].replace(' CONC.', '').split('__')[1]) #convert index of reaction into actual reaction name


    r_list = reactions_json['camp-data'][0]['reactions']
    i=0
    for reaction in reactions:
        
        ######################################################
        # LOOK AT PRODUCTS AND GET FLUX FROM YIELD AND WIDTH #
        ######################################################
        reaction_data = r_list[reaction]['products'] #get products data at index reaction
        for product in reaction_data:
            product_name = product
            product_yield = reaction_data[product_name]
            if product_yield == {}:
                # no product yield, defaulting to reaction rate
                # print("(no product yield) ==> "+str(reationsNamesList[i])+"__TO__"+str(product_name)+" = "+str(widths[str(reationsNamesList[i])]))
                if float(widths[str(reationsNamesList[i])]) != float(0.0) and product_name not in blockedSpecies:
                    updateMinOrMaxInTimeFrame(float(widths[str(reationsNamesList[i])]))
                    
                    calculatedYields.update({str(reationsNamesList[i])+"__TO__"+str(product_name): widths[str(reationsNamesList[i])]})
                    # this value falls within the user selected min and max
                    if widths[str(reationsNamesList[i])] >= userSelectedMinMax[0] and widths[str(reationsNamesList[i])] <= userSelectedMinMax[1]:
                        edgeColors.update({str(reationsNamesList[i])+"__TO__"+str(product_name): '#FF7F7F'})
                    else:
                        edgeColors.update({str(reationsNamesList[i])+"__TO__"+str(product_name): '#e0e0e0'})
            else:
                # element has yield, multiply by reaction rate
                product_yield = product_yield['yield']
                new_yield = widths[str(reationsNamesList[i])]*product_yield
                if float(new_yield) != float(0.0) and product_name not in blockedSpecies:
                    updateMinOrMaxInTimeFrame(float(new_yield))
                    calculatedYields.update({str(reationsNamesList[i])+"__TO__"+str(product_name): float(new_yield)})
                    # this value falls within the user selected min and max
                    if float(new_yield) >= userSelectedMinMax[0] and float(new_yield) <= userSelectedMinMax[1]:
                        edgeColors.update({str(reationsNamesList[i])+"__TO__"+str(product_name): '#FF7F7F'})
                    else:
                        edgeColors.update({str(reationsNamesList[i])+"__TO__"+str(product_name): '#e0e0e0'})




        ######################################################
        # LOOK AT REACTANTS AND GET FLUX FROM YIELD AND WIDTH #
        ######################################################
        reaction_data = r_list[i]['reactants'] #get products data at index reaction
        for reactant in reaction_data:
            reactant_name = reactant
            reactant_yield = reaction_data[reactant_name]
            if reactant_yield == {}:
                # no product yield, defaulting to reaction rate
                if float(widths[str(reationsNamesList[i])]) != float(0.0) and str(reactant_name) not in blockedSpecies:
                    updateMinOrMaxInTimeFrame(float(widths[str(reationsNamesList[i])]))
                    calculatedYields.update({str(reactant_name)+"__TO__"+str(reationsNamesList[i]): widths[str(reationsNamesList[i])]})
                    # this value falls within the user selected min and max
                    if widths[str(reationsNamesList[i])] >= userSelectedMinMax[0] and widths[str(reationsNamesList[i])] <= userSelectedMinMax[1]:
                        edgeColors.update({str(reactant_name)+"__TO__"+str(reationsNamesList[i]): "#94b8f8"})
                    else:
                        edgeColors.update({str(reactant_name)+"__TO__"+str(reationsNamesList[i]): "#e0e0e0"})
            else:
                # element has yield, multiply by reaction rate
                reactant_yield = reactant_yield['qty']
                new_yield = widths[str(reationsNamesList[i])]*reactant_yield
                # print("(found reactant yield) ==> "+str(reactant_name)+"__TO__"+str(reationsNamesList[i])+" = "+str(new_yield))
                if float(new_yield) != float(0.0) and str(reactant_name) not in blockedSpecies:
                    updateMinOrMaxInTimeFrame(float(new_yield))

                    # this value falls within the user selected min and max
                    if float(new_yield) >= userSelectedMinMax[0] and float(new_yield) <= userSelectedMinMax[1]:
                        edgeColors.update({str(reactant_name)+"__TO__"+str(reationsNamesList[i]):  "#94b8f8"})
                    else:
                        edgeColors.update({str(reactant_name)+"__TO__"+str(reationsNamesList[i]): "#e0e0e0"})
        i=i+1
    if userSelectedMinMax[0] == 999999999999:
        userSelectedMinMax[0] = minAndMaxOfSelectedTimeFrame[0]
    if userSelectedMinMax[1] == -1:
        userSelectedMinMax[1] = minAndMaxOfSelectedTimeFrame[1]

    if userSelectedMinMax[0] < minAndMaxOfSelectedTimeFrame[0]:
        userSelectedMinMax[0] = minAndMaxOfSelectedTimeFrame[0]
    if userSelectedMinMax[1] > minAndMaxOfSelectedTimeFrame[1]:
        userSelectedMinMax[1] = minAndMaxOfSelectedTimeFrame[1]
    # print("min and max of selected time frame: ",minAndMaxOfSelectedTimeFrame,"user selected min and max: ",userSelectedMinMax)
    return calculatedYields, edgeColors
def calculateLineWeights(maxWidth, species_yields, scale_type):
    #use fluxes from map we setup, scale the values, add weights and whatnot (maybe say what color we want arrow to be)
    maxVal = -1
    minVal = 99999999
    if scale_type == 'log':
        print("[5/7] logarithmically scaling weights...")
        if species_yields != {}:

            li = species_yields
            logged = []
            for i in li:
                # fail safe for null->null value and so we don't divide/log by 0
                if str(i) != 'null->null' and float(0.0) != float(species_yields[i]):
                    # we cant take the log of a number less than 1/ FIGURE OUT WEIRD null->null error
                    try:
                        logged.append((i, math.log(species_yields[i])))
                        if species_yields[i] < minVal:
                            minVal = species_yields[i]
                        if species_yields[i] > maxVal:
                            maxVal = species_yields[i]
                    except:
                        print("|_ Detected log error, getting abs value: "+str(abs(math.log(abs(species_yields[i])))))
                        new_edge_equation = str(i.split("__TO__")[1])+"__TO__"+str(i.split("__TO__")[0])
                        print("     |_ Creating reversal line for: "+str(i))
                        print("           |_ ",new_edge_equation)
                        logged.append((i, abs(math.log(abs(species_yields[i])))))
            
            vals = [i[1] for i in logged]
            min_val = abs(min(vals))
            range = max(vals) - min(vals)
            if max(vals) == min(vals): #case where we only have one element selected
                range = 1
            scaled = [(x[0], (float(((x[1] + min_val)/range))* float(maxWidth)) + 1) for x in logged]
            print("[6/7] got logarithmically scaled weights")
            return list(scaled), minVal, maxVal
        else:
            print("[7/7] no species selected, returning empty list")
            return list([]), -1, 999999999
    else:
        print("[5/7] linearly scaling weights...")
        li = species_yields
        vals = [species_yields[i] for i in li]
        min_val = abs(min(vals))

        minVal = min_val
        maxVal = abs(max(vals))


        range = max(vals) - min(vals)
        scaled = [(x, (((species_yields[x] + min_val)/range)* int(maxWidth)) + 1) for x in li]
        print("[6/7] got linearly scaled weights")
        return list(scaled), minVal, maxVal
def CalculateEdgesAndNodes(reactions, species, scaledLineWeights, blockedSpecies):
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
    return {'edges': list(edges), 'species_nodes': list(species), 'reaction_nodes': list(reactions)}
def createLegend():
    x = -300
    y = -250
    legend_nodes = [
       'Element', 'Reaction'
    ]
    return legend_nodes
# parent function for generating flow diagram
def generate_flow_diagram(request_dict):
    global userSelectedMinMax
    global minAndMaxOfSelectedTimeFrame

    if ('maxMolval' in request_dict and 'minMolval' in request_dict) and (request_dict['maxMolval'] != '' and request_dict['minMolval'] != '') and (request_dict['maxMolval'] != 'NULL' and request_dict['minMolval'] != 'NULL'):
        userSelectedMinMax = [float(request_dict["minMolval"]), float(request_dict["maxMolval"])]
        # print("new user selected min and max: ", userSelectedMinMax)
    if 'startStep' not in request_dict:
        request_dict.update({'startStep': 1})

    if 'maxArrowWidth' not in request_dict:
        request_dict.update({'maxArrowWidth': 10})

    # load csv file
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pd.read_csv(csv_results_path)
    
    start_step = int(request_dict['startStep'])
    end_step = int(request_dict['endStep'])

    # scale with correct scaling function
    scale_type = request_dict['arrowScalingType']
    max_width = request_dict['maxArrowWidth']

    previousMin = float(request_dict["currentMinValOfGraph"])
    previousMax = float(request_dict["currentMaxValOfGraph"])

    # load species json and reactions json

    with open(path_to_reactions, 'r') as f:
        reactions_data = json.load(f)

    with open(path_to_species, 'r') as f:
        species_data = json.load(f)

    # NEW METHOD OF CREATING NODES
    reactions, species = getAllNodes(request_dict, reactions_data)
    reactionRates = getIntegratedReactionRates(csv, start_step, end_step, reactions)
    raw_yields, edgeColors = CalculateRawYields(csv, reactions_data, reactions, reactionRates, request_dict['blockedSpecies'].split(','))
    scaledLineWeights, minVal, maxVal = calculateLineWeights(max_width, raw_yields, scale_type)
    network_content = CalculateEdgesAndNodes(reactions, species, scaledLineWeights, request_dict['blockedSpecies'].split(','))

    #add edges and nodes
    net = Network(height='100%', width='100%',directed=True) #force network to be 100% width and height before it's sent to page so we don't have cross-site scripting issues
    net.inherit_edge_colors(False) #make it so we can manually change arrow colors

    net.add_nodes(network_content['reaction_nodes'], color=["#FF7F7F" for x in network_content['reaction_nodes']])
    net.add_nodes(network_content['species_nodes'], color=['#94b8f8' for x in network_content['species_nodes']])
    
    # add edges individually so we can modify contents
    i=0
    values=list(edgeColors.values())
    for edge in network_content['edges']:
        if values[i] == "#e0e0e0":
            # don't allow blocked edge to show value on hover (by removing title)
            net.add_edge(edge[0], edge[1], color=values[i], width=edge[2])
        else:
            # hover over arrow to show value for arrows within range
            net.add_edge(edge[0], edge[1], color=values[i], width=float(edge[2]), title=edge[2])
        i=i+1
    # net.add_edges(network_content['edges'], edge_color=["#94b8f8" for x in network_content['edges']])
    
    print("[DEBUG] pushing new table to page using url:",path_to_template)
    #save as html
    net.force_atlas_2based(gravity=-200, overlap=1)
    net.show(path_to_template)
    if minAndMaxOfSelectedTimeFrame[0] == minAndMaxOfSelectedTimeFrame[1]:
        minAndMaxOfSelectedTimeFrame = [0, maxVal]
    with open(path_to_template, 'r+') as f:
        ###################################################################################################################
        # here we are going to replace the contents of the file with new html to avoid problems with cross-site scripting #
        ###################################################################################################################
        a = ''
        # print("((DEBUG)) [min,max] of selected time frame:",minAndMaxOfSelectedTimeFrame)
        # print("((DEBUG)) [min,max] given by user:",userSelectedMinMax)
        if int(minAndMaxOfSelectedTimeFrame[1]) == -1 or int(minAndMaxOfSelectedTimeFrame[0]) == 999999999999:
            a = '<script>parent.document.getElementById("flow-start-range2").value = "NULL"; parent.document.getElementById("flow-end-range2").value = "NULL"; console.log("inputting NULL");'
        
        else:
            a = '<script>parent.document.getElementById("flow-start-range2").value = "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))+'"; parent.document.getElementById("flow-end-range2").value = "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))+'"; console.log("Overrided element values via cross scripting?");'
        formattedPrevMin = str('{:0.3e}'.format(previousMin))
        formattedPrevMax = str('{:0.3e}'.format(previousMax))
        formattedMinOfSelected = str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))
        formattedMaxOfSelected = str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))

        if str(formattedPrevMin) != str(formattedMinOfSelected) or str(formattedPrevMax) != str(formattedMaxOfSelected) or previousMin == 0 or previousMax == 1:
            print("previousMin:",formattedPrevMin,"does not equal",formattedMinOfSelected)
            print("previousMax:",formattedPrevMax,"does not equal",formattedMaxOfSelected)
            a = a + 'parent.document.getElementById("filterRange").value = "'+str(formattedMinOfSelected)+'" + " to " + "'+str(formattedMaxOfSelected)+'";' #update our filter range with new values
            a = a + 'parent.document.getElementById("flow-start-range2").value = "'+str(formattedMinOfSelected)+'"; parent.document.getElementById("flow-end-range2").value = "'+str(formattedMaxOfSelected)+'";'
            a = a + 'parent.reloadSlider("'+str(formattedMinOfSelected)+'", "'+str(formattedMaxOfSelected)+'", "'+str(formattedMinOfSelected)+'", "'+str(formattedMaxOfSelected)+'");</script>' #destroy slider and update slider entirely
        else:

            if int(userSelectedMinMax[1]) != -1 or int(userSelectedMinMax[0]) != 999999999999:
                # print("user has selected min and max that are valid")
                a = a + 'parent.document.getElementById("filterRange").value = "'+str('{:0.3e}'.format(userSelectedMinMax[0]))+'" + " to " + "'+str('{:0.3e}'.format(userSelectedMinMax[1]))+'";' #update our filter range with new values
                a = a + 'parent.document.getElementById("flow-start-range2").value = "'+str('{:0.3e}'.format(userSelectedMinMax[0]))+'"; parent.document.getElementById("flow-end-range2").value = "'+str('{:0.3e}'.format(userSelectedMinMax[1]))+'";'
                a = a + 'parent.reloadSlider("'+str('{:0.3e}'.format(userSelectedMinMax[0]))+'", "'+str('{:0.3e}'.format(userSelectedMinMax[1]))+'", "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))+'", "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))+'");</script>' #destroy slider and update slider entirely
            else:
                # print("user selected values not valid, just pushing timeframe: ",minAndMaxOfSelectedTimeFrame)
                a = a + 'parent.document.getElementById("filterRange").value = "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))+'" + " to " + "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))+'";' #update our filter range with new values
                a = a + 'parent.reloadSlider("'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))+'", "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))+'", "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[0]))+'", "'+str('{:0.3e}'.format(minAndMaxOfSelectedTimeFrame[1]))+'");</script>' #destroy slider and update slider entirely
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('</script>'):   # find a pattern so that we can add next to that line
                lines[i] = lines[i]+a
        f.truncate()
        f.seek(0)  # rewrite into the file
        for line in lines:
            f.write(line)
    