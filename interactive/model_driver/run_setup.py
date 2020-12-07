import os
import time
import subprocess
from django.conf import settings
from interactive.tools import *



if "MUSIC_BOX_BUILD_DIR" in os.environ:
    mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    interface_solo = False
else:
    mb_dir = ''
    interface_solo = True

out_path = os.path.join(mb_dir, 'output.csv')
error_path = os.path.join(mb_dir, 'error.json')
copy_path = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/past.csv')
config_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/my_config.json")
config_dest = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/config.json')

config_folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")


def copyConfigFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()
    


def setup_run():
    if interface_solo:
        return JsonResponse({'model_connected': False})
    
    copyConfigFile(config_path, config_dest)
    if os.path.isfile(out_path):
        copyConfigFile(out_path, copy_path)
        os.remove(out_path)
    if os.path.isfile(error_path):
        os.remove(error_path)


    config = open_json('my_config.json')
    filelist = os.listdir(config_folder_path)
    internals = [
        'initials.json',
        'options.json',
        'photo.json',
        'post.json',
        'species.json',
        'linear_combinations.json'
    ]
    for f in internals:
        filelist.remove(f)
    
    for f in filelist:
        if os.path.getsize(os.path.join(config_folder_path, f)) > 1:
            filelist.remove(f)
    

    newpath = os.path.join(mb_dir, 'mb_configuration')
    os.mkdir(newpath)
    for f in filelist:
        copyConfigFile(os.path.join(config_folder_path, f), os.path.join(newpath, f))


   

    process = subprocess.Popen(
        [r'./music_box', r'/mb_configuration/my_config.json'], cwd=mb_dir)
