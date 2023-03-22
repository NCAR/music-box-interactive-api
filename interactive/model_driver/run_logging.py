from datetime import datetime
from interactive.tools import *
from django.conf import settings
import os
import logging
from shutil import rmtree

if "MUSIC_BOX_BUILD_DIR" in os.environ:
    mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])
    interface_solo = False
else:
    mb_dir = ''
    interface_solo = True

out_path = os.path.join(mb_dir, 'output.csv')
error_path = os.path.join(mb_dir, 'error.json')


log_path = os.path.join(settings.BASE_DIR, 'dashboard/static/log/log')
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

    lc = open_json('log_config.json')
    if not lc['logging_enabled']:
        return
    lc.update({'current': foldername})
    history = lc['history']
    history.update({foldername: 'running'})
    lc.update({'history': history})
    dump_json('log_config.json', lc)

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

    
    # li = [int(x.split('_')[1]) for x in history.keys()]
    # largest = li.sort()[-1]
    # if largest > lc['log_length']:
    #     smallest = li.sort()[0]
    #     path_for_deletion = os.path.join(log_path, 'run_' + str(smallest))
    #     rmtree(path_for_deletion)


def update_with_result(status):
    lc = open_json('log_config.json')
    if not lc['logging_enabled']:
        return
    current = lc['current']
    history = lc['history']
    if status == 'error':
        history.update({current: 'error'})
        copyAFile(error_path, os.path.join(os.path.join(log_path, current), 'error.json'))
    elif status == 'done':
        history.update({current: 'done'})
        copyAFile(out_path, os.path.join(os.path.join(log_path, current), 'output.csv'))
    elif status == 'timeout':
        history.update({current: 'timeout'})
    elif status == 'empty_output':
        history.update({current: 'empty_output'})


    lc.update({'history': history})
    dump_json('log_config.json', lc)    
    return


def clear_log():
    rmtree(log_path)
    os.mkdir(log_path)

    lc = open_json('log_config.json')
    lc.update({'history': {}})
    dump_json('log_config.json', lc)
    logging.info('log cleared')
