from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
import json
import os.path
import subprocess


def run(request):
    mb_dir           = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    nc_outfile_path  = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.nc")
    csv_outfile_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    running_path     = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "MODEL_RUNNING")
    done_path        = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "MODEL_RUN_COMPLETE")
    if os.path.isfile(nc_outfile_path):
        os.remove(nc_outfile_path)
    if os.path.isfile(csv_outfile_path):
        os.remove(csv_outfile_path)
    if os.path.isfile(running_path):
        os.remove(running_path)
    if os.path.isfile(done_path):
        os.remove(done_path)

    process = subprocess.Popen(
        [r'./music_box', r'/music-box-interactive/interactive/dashboard/static/config/my_config.json'], cwd=mb_dir)

    return JsonResponse({ "status" : "started"})


def check_status(request):
    running_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "MODEL_RUNNING")
    failure_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "MODEL_FAILURE")
    done_path    = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "MODEL_RUN_COMPLETE")
    if os.path.isfile(done_path):
        return JsonResponse({ "status" : "done" })
    if os.path.isfile(failure_path):
        return JsonResponse({ "status" : "failure" })
    if os.path.isfile(running_path):
        return JsonResponse({ "status" : "running" })
    return JsonResponse({ "status" : "not started" })


def mechanism_data(request):
    mechanism_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "molec_info.json")
    mech_json = json.load(open(mechanism_path, 'r'))
    return JsonResponse(mech_json)


def download(request):
    nc_outfile_path  = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.nc")
    csv_outfile_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    if os.path.isfile(nc_outfile_path):
        with open(nc_outfile_path, 'rb') as outfile:
            response = HttpResponse(outfile.read(), content_type="application/x-netcdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(nc_outfile_path)
            return response
    if os.path.isfile(csv_output_path):
        with open(csv_outfile_path, 'r') as outfile:
            response = HttpResponse(outfile.read(), content_type="text/plain")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(csv_outfile_path)
            return response
    return HttpResponseBadRequest('Missing output file', status=405)
