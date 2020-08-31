from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
import json
import os.path
import subprocess
import mimetypes


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

    return render(request, 'run_model.html', { "status" : "Started"})


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
    fl_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    filename = 'output.csv'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
