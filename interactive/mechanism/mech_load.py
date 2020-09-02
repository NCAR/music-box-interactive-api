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
