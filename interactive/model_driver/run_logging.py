from datetime import datetime
from interactive.tools import *
from django.conf import settings
import os

log_path = os.path.join(settings.BASE_DIR, 'dashboard/static/log')
config_folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")


def copyAFile(source, destination):
    configFile = open(source, 'rb')
    content = configFile.read()
    g = open(destination, 'wb')
    g.write(content)
    g.close()
    configFile.close()


def save_run():
    config = open_json('my_config.json')
    filelist = []
    configFolderContents = os.listdir(config_folder_path)

    logEntryName = 'run_at_' + str(datetime.now())
    foldername = os.path.join(log_path, logEntryName)

    for configSection in config:
        section = config[configSection]
        for configItem in section:
            if '.' in configItem:
                filelist.append(configItem)
    
    for name in filelist:
        if name not in configFolderContents:
            filelist.remove(name)

    
    filelist.append('my_config.json')

    os.mkdir(foldername)

    for f in filelist:
        copyAFile(os.path.join(config_folder_path, f), os.path.join(foldername, f))
    



def update_with_result():
    return True