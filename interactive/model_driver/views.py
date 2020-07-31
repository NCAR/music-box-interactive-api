from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
import json
import os.path
import subprocess

def run(request):
    mb_dir       = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    outfile_path = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "MusicBox_output.nc")
    running_path = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "MODEL_RUNNING")
    done_path    = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "MODEL_RUN_COMPLETE")
    if os.path.isfile(outfile_path):
        os.remove(outfile_path)
    if os.path.isfile(running_path):
        os.remove(running_path)
    if os.path.isfile(done_path):
        os.remove(done_path)
    process = subprocess.Popen(r'./MusicBox', cwd=mb_dir)
    return JsonResponse({ "status" : "started"})

def check_status(request):
    running_path = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "MODEL_RUNNING")
    done_path    = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "MODEL_RUN_COMPLETE")
    if os.path.isfile(done_path):
        return JsonResponse({ "status" : "done" })
    if os.path.isfile(running_path):
        return JsonResponse({ "status" : "running" })
    return JsonResponse({ "status" : "not started" })

def mechanism_data(request):
    mechanism_path = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "molec_info.json")
    mech_json = json.load(open(mechanism_path, 'r'))
    return JsonResponse(mech_json)

def download(request):
    outfile_path = os.path.join(os.environ['MUSIC_BOX_OUTPUT_DIR'], "MusicBox_output.nc")
    if os.path.isfile(outfile_path):
        with open(outfile_path, 'rb') as outfile:
            response = HttpResponse(outfile.read(), content_type="application/x-netcdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(outfile_path)
            return response
    return HttpResponseBadRequest('Missing output file', status=405)
