from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.conf import settings
import json
import os
import subprocess
import mimetypes
import pandas as pd
import time
from shutil import copy
from .run_setup import setup_run
from .run_logging import *
from datetime import datetime


if "MUSIC_BOX_BUILD_DIR" in os.environ:
    mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    interface_solo = False
else:
    mb_dir = ''
    interface_solo = True

print("interface_solo:", interface_solo)
clear_log()

out_path = os.path.join(mb_dir, 'output.csv')
error_path = os.path.join(mb_dir, 'error.json')
copy_path = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/past.csv')
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/my_config.json")
config_dest = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/config.json')


def run(request):
    run = setup_run()
    print(run)
    save_run()
    return JsonResponse(run)


def check_load(request):
    response_message = {}
    out_path = os.path.join(mb_dir, 'output.csv')
    error_path = os.path.join(mb_dir, 'error.json')
    
    status = 'checking'

    # check if output file exists
    if os.path.isfile(out_path):
        if os.path.getsize(out_path) == 0:  # check if output file has content
            if os.path.getsize(error_path) > 0: #check if error file has content
                status = 'error'
            else:
                status = 'empty_output'
        else:
            status = 'done'
            


    response_message.update({'status': status})

    if status == 'error':
        with open(error_path) as g:
            errorfile = json.loads(g.read())
        if "Property 'chemical_species%" in errorfile['message']:   #search for the species which returned the error
            part = errorfile['message'].split('%')[1]
            specie = part.split("'")[0]
            with open(os.path.join(settings.BASE_DIR, 'dashboard/static/config/species.json')) as g:
                spec_json = json.loads(g.read())
            for key in spec_json['formula']:
                if spec_json['formula'][key] == specie:
                    response_message.update({'e_type': 'species'})
                    response_message.update({'spec_ID': key + '.Formula'})
        response_message.update({'e_code': errorfile['code']})
        response_message.update({'e_message': errorfile['message']})

    return JsonResponse(response_message)


def download(request):
    fl_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    now = datetime.now()
    filename = str(now) + '_model_output.csv'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response



def check(request):
    response_message = {}
    out_path = os.path.join(mb_dir, 'output.csv')
    error_path = os.path.join(mb_dir, 'error.json')
    status = 'checking'

    # check if output file exists
    t = 0
    while status == 'checking':
        print(status)
        time.sleep(.1)
        t += 0.1
        if os.path.isfile(out_path):
            if os.path.getsize(out_path) == 0:  # check if output file has content
                if os.path.isfile(error_path): #check if error file exists
                    if os.path.getsize(error_path) > 0: #check if error file has content
                        status = 'error'
            else:
                status = 'done'
        if t > 10:
            status = 'timeout'
            break
        
    update_with_result(status)
    response_message.update({'status': status})

    if status == 'error':
        with open(error_path) as g:
            errorfile = json.loads(g.read())
        if "Property 'chemical_species%" in errorfile['message']:   #search for the species which returned the error
            part = errorfile['message'].split('%')[1]
            specie = part.split("'")[0]
            with open(os.path.join(settings.BASE_DIR, 'dashboard/static/config/species.json')) as g:
                spec_json = json.loads(g.read())
            for key in spec_json['formula']:
                if spec_json['formula'][key] == specie:
                    response_message.update({'e_type': 'species'})
                    response_message.update({'spec_ID': key + '.Formula'})
        response_message.update({'e_code': errorfile['code']})
        response_message.update({'e_message': errorfile['message']})

    return JsonResponse(response_message)


