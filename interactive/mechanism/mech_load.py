import json
from django.conf import settings
import logging
import os
from interactive.tools import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def id_dict(namelist):
    outlist = {}
    i = 0
    for x in namelist:
        first = x.split(' ')[0]
        name = first + str(i)
        i = i+1
        outlist.update({x: name})
    print(outlist)
    return outlist


# returns dict with display names for reaction edit form fields
def pretty_reaction_names():
    names = {
        'rate': 'Rate:',
        'rate_call': 'Rate Call:',
        'rc.reaction_class': 'Reaction Class:',
        'troe': "troe",
        'reactant.0': 'Reactant 0',
        'reactant.1': 'Reactant 1',
        'reactant.2': 'Reactant 2',
        'reactant.3': 'Reactant 3',
        'reactant.4': 'Reactant 4',
        'rc.p.A': "A:",
        'rc.p.B': "B:",
        'rc.p.C': "C:",
        'rc.p.D': "D:",
        'rc.p.E': "E:",
        'rc.p.A_k0': "A_k0:",
        'rc.p.B_k0': "B_k0:",
        'rc.p.C_k0': "C_k0:",
        'p.0.coefficient': 'Product 0 Coefficient:',
        'p.1.coefficient': 'Product 1 Coefficient:',
        'p.2.coefficient': 'Product 2 Coefficient:',
        'p.3.coefficient': 'Product 3 Coefficient:',
        'p.4.coefficient': 'Product 4 Coefficient:',
        'p.5.coefficient': 'Product 5 Coefficient:',
        'p.0.species': 'Product 0:',
        'p.1.species': 'Product 1:',
        'p.2.species': 'Product 2:',
        'p.3.species': 'Product 3:',
        'p.4.species': 'Product 4:',
        'p.5.species': 'Product 5:'
    }
    return names


# returns the name of the most recently staged reaction
# used to save reaction edit form in correct place
def id_reaction():
    info = open_json('reaction_stage.json')
    r_dict = reaction_dict()
    for key in r_dict:
        if info == r_dict[key]:
            name = key
    
    return name


#save updated reaction info to mechanism, returns new reaction name
def save_reacts(name, myDict):
    logging.info('saving reaction...')
    datafile = open_json('datamolec_info.json')
    mechanism = datafile['mechanism']
    reactions = mechanism['reactions']
    info = reaction_dict()[name]
    for i in reactions:
        if i == info:
            r_index = reactions.index(i)

    reaction = reactions[r_index]
    for key in myDict:
        if key.split('.')[0] == 'rc':
            if key.split('.')[1] == 'p':
                reaction['rate_constant']['parameters'].update({key.split('.')[2]: float(myDict[key])})
            else:
                reaction['rate_constant'].update({key.split('.')[1]: myDict[key]})
        elif key.split('.')[0] == 'reactant':
            reaction['reactants'][int(key.split('.')[1])] = myDict[key]
        elif key.split('.')[0] == 'p':
            if key.split('.')[2] == 'coefficient':
                reaction['products'][int(key.split('.')[1])].update({key.split('.')[2]: float(myDict[key])})
            else:
                reaction['products'][int(key.split('.')[1])].update({key.split('.')[2]: myDict[key]})
        elif key == 'troe':
            reaction.update({key: bool(myDict[key])})
        elif key == 'rate':
            if myDict[key] == 'None':
                reaction.update({'rate': None})
            else:
                reaction.update({'rate': myDict[key]})
    
    reactions[r_index] = reaction
    mechanism.update({'reactions': reactions})
    datafile.update({'mechanism': mechanism})
    dump_json('datamolec_info.json', datafile)
    
    reactants = []
    for j in reaction['reactants']:
        reactants.append(j)
    products = []
    for k in reaction['products']:
        coef = str(k['coefficient'])
        if coef == '1':
            coef = ''
        prod = k['species']
        products.append(coef + prod)
    new_name = " + ".join(str(l) for l in reactants) + " -> " + " + ".join(str(x) for x in products)
    logging.info('...saved')

    return new_name


# returns mathjax formatted strings of rate equations
def reaction_rate_equations(rc_dict):
    rc_type = rc_dict['reaction_class']
    params = rc_dict["parameters"]
    for key in params:
        params.update({key: sci_note(str(params[key]))})
    if rc_type == "Arrhenius":            
        eq = "\\" + "begin{equation}{" + params['A'] + "}e^{(" + "\\" + "frac{-{" + params['C'] + "}}{T})}" +  "\\" + "left(" + "\\" + "frac{T}{" + params['D'] + "}" + "\\" + "right)^{" + params['B'] + "}(1.0+{" + params['E'] + "}*P)" + "\\" + "end{equation}"
    elif rc_type == "CH3COCH3_OH":
        eq = "\\" + "begin{equation}" + "k = {" + params['A'] + '}+{' + params['B'] + "}e^{(" + "\\" + "frac{-{" + params["C"] + "}}{T})}" + "\\" + "end{equation}"
    elif rc_type == "Combined_CO_OH":
        eq1 = "\\" + "begin{equation}{" + params['A'] + "}(1 + {" + params['B'] + "}k_b M T )" + "\\" + "end{equation}"
        eq2 = "\\" + "begin{equation}" + "k_b = " + "\\" + "mbox{Boltzmann}" + "\\" + "end{equation}"
        eq3 = "\\" + "begin{equation}" + "M = " + "\\" + "mbox{number density}" + "\\" + "end{equation}"
        eq = "<li>" + eq1 + "</li><li>" + eq2 + "</li><li>" + eq3 + "</li>"
    elif rc_type == "Troe_low_pressure":
        eq = "\\" + "begin{equation}" + "k_0 = {" + params['A_k0'] + "}e^{(" + '\\' + "frac{-{" + params['C_k0'] + "}}{T})} " + '\\' + "left( " + '\\' + "frac{T}{300} " + '\\' + "right)^{" + params['B_k0'] + "}" + "\\" + "end{equation}"
    else:
        eq = 'Unknown reaction class'
    return eq


# same as above, but with variables instead of filled values
def unfilled_r_equations(rc_dict):
    for key in rc_dict['parameters']:
        rc_dict['parameters'].update({key: key})
    eqa = reaction_rate_equations(rc_dict)
    return eqa


# searches for reactions containing query, returns list 
def reaction_search(query):
    logging.info('searching...')
    react_dict = reaction_dict()
    resultlist = []
    #for 'or' query with comma
    if ',' in query:
        div_query = query.split(',')
        cleaned = []
        for q in div_query:
            newq = q.replace(' ','')
            cleaned.append(newq)
        
        for q in cleaned:
            for reaction_name in react_dict:
                for reactant in react_dict[reaction_name]['reactants']:
                    if q == reactant:
                        resultlist.append(reaction_name)
            for product in react_dict[reaction_name]['products']:
                if product['species'] == q:
                    resultlist.append(reaction_name)
        #for 'and' query with plus sign
    elif '+' in query:
        div_query = query.split('+')
        cleaned = []
        for q in div_query:
            newq = q.replace(' ','')
            cleaned.append(newq)
        
        for reaction_name in react_dict: 
            contains = []
            for reactant in react_dict[reaction_name]['reactants']:
                contains.append(reactant) 
            for product in react_dict[reaction_name]['products']:
                contains.append(product['species'])
            if all(elem in contains  for elem in cleaned):
                resultlist.append(reaction_name)
                
        #if single query
    else:
        for reaction_name in react_dict:
            for reactant in react_dict[reaction_name]['reactants']:
                if query == reactant:
                    resultlist.append(reaction_name)
            for product in react_dict[reaction_name]['products']:
                if product['species'] == query:
                    resultlist.append(reaction_name)
    
    #remove duplicate results
    list(dict.fromkeys(resultlist))
    logging.info('...search complete')
    return resultlist
    

# add photolysis to reactions section
def process_photolysis():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info copy.json")) as g:
            datafile = json.loads(g.read())
    
    mechanism = datafile['mechanism']
    reactions = mechanism['reactions']
    photo_reactions = mechanism['photolysis']

    for p_reaction in photo_reactions:
        reactions.append(p_reaction)
    
    mechanism.update({'reactions': reactions})
    datafile.update({'mechanism': mechanism})

    with open(os.path.join(mech_path, "datamolec_info.json"), 'w') as f:
        json.dump(datafile, f, indent=4)
