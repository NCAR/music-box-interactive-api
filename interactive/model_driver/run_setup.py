import os
import time
import subprocess
from django.conf import settings
from interactive.tools import *
from shutil import rmtree


if "MUSIC_BOX_BUILD_DIR" in os.environ:
    mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    interface_solo = False
else:
    print(os.environ)
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
    

def create_file_list():
    config = open_json('my_config.json')
    filelist = []
    configFolderContents = os.listdir(config_folder_path)

    for configSection in config:
        section = config[configSection]
        for configItem in section:
            if '.' in configItem:
                filelist.append(configItem)
    
    for name in filelist:
        if name not in configFolderContents:
            filelist.remove(name)
    return filelist

def setup_run():
    if interface_solo:
        return {'model_connected': False}
    
    if os.path.isfile(out_path):
        os.remove(out_path)
    if os.path.isfile(error_path):
        os.remove(error_path)


    config = open_json('my_config.json')
    

    newpath = os.path.join(mb_dir, 'mb_configuration')
    if os.path.exists(newpath):
        rmtree(newpath)
        os.mkdir(newpath)
    else:
        os.mkdir(newpath)
    filelist = create_file_list()
    filelist.append('my_config.json')
    print(filelist)
    for f in filelist:
        copyConfigFile(os.path.join(config_folder_path, f), os.path.join(newpath, f))

    time.sleep(0.1)
   
    filelist.remove('my_config.json')
    for f in filelist:
        copyConfigFile(os.path.join('/build/mb_configuration', f), os.path.join('/build', f))
    process = subprocess.Popen([r'./music_box', r'./mb_configuration/my_config.json'], cwd=mb_dir)

    return {'model_connected': True}
