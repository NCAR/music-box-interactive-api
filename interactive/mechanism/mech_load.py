import json
from django.conf import settings
import logging
import os

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def molecule_info():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            mechanism = json.loads(g.read())['mechanism']

    molecules = mechanism['molecules']
    molec_dict = {}
    for i in molecules:
        molec_dict.update({i['moleculename']: i})
    logging.info('getting molecule info')
    return molec_dict


def molecule_list():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            mechanism = json.loads(g.read())['mechanism']

    molecules = mechanism['molecules']
    molec_list = []
    for i in molecules:
        molec_list.append(i['moleculename'])
    return molec_list


def henry_equations(value):
    equation1 = "\\" + "begin{equation} H_{e f f}=K_{H}\left(1+" + "\\" + "frac{K_{1}}{K_{2}}[H+]" + "\\" + "right) " + "\\" + "end{equation}"
    equation2 = "\\" + "begin{equation}H_{e f f}=K_{H}" + "\\" + "left(1+" + "\\" + "frac{K_{1}}{[H+]}" + "\\" + "left(1+" + "\\" + "frac{K_{2}}{[H+]}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    equation3 = "\\" + "begin{equation}K_{H}=\mathrm{kh}_{298} " + "\\" + "exp " + "\\" + "left(" + "\\" + "mathrm{dh}_{r}" + "\\" + "left(" + "\\" + "frac{1}{T}-" + "\\" + "frac{1}{298}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    equation4 = "\\" + "begin{equation}K_{1}=\mathrm{k} 1_{298} " + "\\" + "exp " + "\\" + "left(" + "\\" + "operatorname{dh} 1_{r}" + "\\" + "left(" + "\\" + "frac{1}{T}-" + "\\" + "frac{1}{298}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    equation5 = "\\" + "begin{equation}K_{2}=\mathrm{k} 2_{298} " + "\\" + "exp " + "\\" + "left(" + "\\" + "mathrm{dh} 2_{r}" + "\\" + "left(" + "\\" + "frac{1}{T}-" + "\\" + "frac{1}{298}" + "\\" + "right)" + "\\" + "right)" + "\\" + "end{equation}"
    if value == 0:
        return([equation1, equation3, equation4, equation5])
    if value == 1:
        return([equation2, equation3, equation4, equation5])


def stage_form_info(item):
    initial = molecule_info()[item]
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "form_stage.json"), 'w') as f:
        json.dump(initial, f, indent=4)


def initialize_form():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "form_stage.json")) as g:
            info = json.loads(g.read())
    logging.info('filling' + info['moleculename'] + 'form')
    return info


def id_molecule():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "form_stage.json")) as g:
        info = json.loads(g.read())
    
    return info['moleculename']


def pretty_names():
    names = {
        "formula": "Formula:",
        'solve': "Solve Type:",
        'hl.henrys_law_type': "Henry's Law Type:",
        'hl.kh_298': "\\" + "begin{equation} \mathrm{kh}_{298}\end{equation}",
        'hl.dh_r': "\\" + "begin{equation}\mathrm{dh}_{r}\end{equation}",
        'hl.k1_298': "\\" + "begin{equation}\mathrm{k1}_{298}\end{equation}",
        'hl.dh1_r': "\\" + "begin{equation}\mathrm{dh1}_{r}\end{equation}",
        'hl.k2_298': "\\" + "begin{equation}\mathrm{k2}_{298}\end{equation}",
        'hl.dh2_r': "\\" + "begin{equation}\mathrm{dh2}_{r}\end{equation}",
        'molecular_weight': "Molecular Weight:",
        'standard_name': "Standard Name:",
        'kh_298': "\\" + "begin{equation} \mathrm{kh}_{298}\end{equation}",
        'dh_r': "\\" + "begin{equation}\mathrm{dh}_{r}\end{equation}",
        'k1_298': "\\" + "begin{equation}\mathrm{k1}_{298}\end{equation}",
        'dh1_r': "\\" + "begin{equation}\mathrm{dh1}_{r}\end{equation}",
        'k2_298': "\\" + "begin{equation}\mathrm{k2}_{298}\end{equation}",
        'dh2_r': "\\" + "begin{equation}\mathrm{dh2}_{r}\end{equation}",
        'henrys_law_type': "Henry's Law Type:",
        'transport': "Transport:",
        'moleculename': "Molecule Name:"
    }
    return names


def save_mol(name, myDict):
    logging.info('saving molecule...')
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            datafile = json.loads(g.read())
    mechanism = datafile['mechanism']
    molecules = mechanism['molecules']
    for i in molecules:
        if i['moleculename'] == name:
            n = molecules.index(i)
    old = molecules[n]
    for key in myDict:
        if key.split('.')[0] == 'hl':
            old['henrys_law'].update({key.split('.')[1]: myDict[key]})
        else:
            old.update({key: myDict[key]})
    molecules[n] = old
    mechanism.update({'molecules':molecules})
    datafile.update({'mechanism': mechanism})
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json"), 'w') as f:
        json.dump(datafile, f, indent=4)
    logging.info('...saved')


def new_m(myDict):
    logging.info('adding new molecule...')
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            datafile = json.loads(g.read())
    mechanism = datafile['mechanism']
    molecules = mechanism['molecules']
    new = {
                "moleculename": myDict['moleculename'],
                "formula": myDict['formula'],
                "transport": myDict['transport'],
                "solve": myDict['solve'],
                "henrys_law": {
                    "henrys_law_type": myDict['hl.henrys_law_type'],
                    "kh_298": myDict['hl.kh_298'],
                    "dh_r": myDict['hl.dh_r'],
                    "k1_298": myDict['hl.k1_298'],
                    "dh1_r": myDict['hl.dh1_r'],
                    "k2_298": myDict['hl.k2_298'],
                    "dh2_r": myDict['hl.dh2_r']
                },
                "molecular_weight": myDict['molecular_weight'],
                "standard_name": myDict['standard_name']
            }
    
    molecules.append(new)
    mechanism.update({'molecules': molecules})
    datafile.update({'mechanism': mechanism})
    with open(os.path.join(mech_path, "datamolec_info.json"), 'w') as f:
        json.dump(datafile, f, indent=4)
    logging.info('...added')


def search_list():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            datafile = json.loads(g.read())
    mechanism = datafile['mechanism']
    molecules = mechanism['molecules']
    name_list = []
    for i in molecules:
        name_list.append(i['moleculename'])
    return name_list


def reaction_name_list():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
        datafile = json.loads(g.read())
    mechanism = datafile['mechanism']
    reactions = mechanism['reactions']
    r_list = []
    for i in reactions:
        reactants = []
        for j in i['reactants']:
            reactants.append(j)
        products = []
        for k in i['products']:
            coef = str(k['coefficient'])
            if coef == '1':
                coef = ''
            prod = k['molecule']
            products.append(coef + prod)
        r_list.append(" + ".join(str(l) for l in reactants) + " -> " + " + ".join(str(x) for x in products))
    
    return r_list


def reaction_dict():
    logging.info('getting reaction info')
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
        datafile = json.loads(g.read())
    mechanism = datafile['mechanism']
    reactions = mechanism['reactions']
    r_dict = {}
    for i in reactions:
        reactants = []
        for j in i['reactants']:
            reactants.append(j)
        products = []
        for k in i['products']:
            coef = str(k['coefficient'])
            if coef == '1':
                coef = ''
            prod = k['molecule']
            products.append(coef + prod)
        name = " + ".join(str(l) for l in reactants) + " -> " + " + ".join(str(x) for x in products)
        r_dict.update({name: i})
    
    return r_dict
    

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


def stage_reaction_form(name):
    initial = reaction_dict()[name]
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "reaction_stage.json"), 'w') as f:
        json.dump(initial, f, indent=4)
    

def initialize_reactions():
    logging.info('filling form')
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "reaction_stage.json")) as g:
            info = json.loads(g.read())
    
    return info


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
        'p.0.molecule': 'Product 0:',
        'p.1.molecule': 'Product 1:',
        'p.2.molecule': 'Product 2:',
        'p.3.molecule': 'Product 3:',
        'p.4.molecule': 'Product 4:',
        'p.5.molecule': 'Product 5:'
    }
    return names


def id_reaction():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "reaction_stage.json")) as g:
            info = json.loads(g.read())
    
    r_dict = reaction_dict()

    for key in r_dict:
        if info == r_dict[key]:
            name = key
    
    return name


def save_reacts(name, myDict):
    logging.info('saving reaction...')
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            datafile = json.loads(g.read())
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
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json"), 'w') as f:
        json.dump(datafile, f, indent=4)
    
    reactants = []
    for j in reaction['reactants']:
        reactants.append(j)
    products = []
    for k in reaction['products']:
        coef = str(k['coefficient'])
        if coef == '1':
            coef = ''
        prod = k['molecule']
        products.append(coef + prod)
    new_name = " + ".join(str(l) for l in reactants) + " -> " + " + ".join(str(x) for x in products)
    logging.info('...saved')

    return new_name


def reaction_menu_names():
    r_list = reaction_name_list()
    newlist = []
    for name in r_list:
        if len(name) > 40:
            shortname = name[0:38] + '...'
            newlist.append(shortname)
        else:
            newlist.append(name)
    zipped = zip(r_list, newlist)
    return zipped


def molecule_menu_names():
    m_list = molecule_list()
    newlist = []
    for name in m_list:
        if len(name) > 8:
            shortname = name[0:8] + '..'
            newlist.append(shortname)
        else:
            newlist.append(name)
    zipped = zip(m_list, newlist)
    return zipped


def reaction_rate_equations(rc_dict):
    rc_type = rc_dict['reaction_class']
    params = rc_dict["parameters"]
    for key in params:
        params.update({key: str(params[key])})
    if rc_type == "Arrhenius":            
        eq = "\\" + "begin{equation}" + params['A'] + "e^{(" + "\\" + "frac{-" + params['C'] + "}{T})}" +  "\\" + "left(" + "\\" + "frac{T}{" + params['D'] + "}" + "\\" + "right)^" + params['B'] + "(1.0+" + params['E'] + "*P)" + "\\" + "end{equation}"
    elif rc_type == "CH3COCH3_OH":
        eq = "\\" + "begin{equation}" + "k = " + params['A'] + '+' + params['B'] + "e^{(" + "\\" + "frac{-" + params["C"] + "}{T})}" + "\\" + "end{equation}"
    elif rc_type == "Combined_CO_OH":
        eq1 = "\\" + "begin{equation}" + params['A'] + "(1 + " + params['B'] + "k_b M T )" + "\\" + "end{equation}"
        eq2 = "\\" + "begin{equation}" + "k_b = " + "\\" + "mbox{Boltzmann}" + "\\" + "end{equation}"
        eq3 = "\\" + "begin{equation}" + "M = " + "\\" + "mbox{number density}" + "\\" + "end{equation}"
        eq = "<li>" + eq1 + "</li><li>" + eq2 + "</li><li>" + eq3 + "</li>"
    else:
        eq = 'Unknown reaction class'
    return eq


def unfilled_r_equations(rc_dict):
    for key in rc_dict['parameters']:
        rc_dict['parameters'].update({key: key})
    eqa = reaction_rate_equations(rc_dict)
    return eqa

