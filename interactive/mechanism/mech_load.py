import json
from django.conf import settings
import logging
import os

def molecule_info():
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism")
    with open(os.path.join(mech_path, "datamolec_info.json")) as g:
            mechanism = json.loads(g.read())['mechanism']

    molecules = mechanism['molecules']
    molec_dict = {}
    for i in molecules:
        molec_dict.update({i['moleculename']: i})
    
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
    
    return info


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
        'henrys_law_type': "Henry's Law Type:"
    }
    return names