from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.conf import settings
import json
import os
import subprocess
import mimetypes
import pandas as pd
import time


mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
out_path = os.path.join(mb_dir, 'output.csv')
error_path = os.path.join(mb_dir, 'error.json')

def run(request):
    if os.path.isfile(out_path):
        os.remove(out_path)
    if os.path.isfile(error_path):
        os.remove(error_path)
    process = subprocess.Popen(
        [r'./music_box', r'/music-box-interactive/interactive/dashboard/static/config/my_config.json'], cwd=mb_dir)

    return render(request, 'run_model.html')


def check(request):
    response_message = {}
    out_path = os.path.join(mb_dir, 'output.csv')
    error_path = os.path.join(mb_dir, 'error.json')
    status = 'checking'

    # check if output file exists
    while status == 'checking':
        print(status)
        time.sleep(.1)
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

    print(response_message)
    return JsonResponse(response_message)


def download(request):
    fl_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    filename = 'output.csv'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response