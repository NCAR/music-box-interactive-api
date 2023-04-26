# SESSION BASED MODEL RUNNING
from datetime import datetime
from django.conf import settings
from django.conf import settings
from django.http import JsonResponse
from mechanism.reactions import reactions_are_valid
from shared.utils import direct_dump_json, direct_open_json

import json
import json
import logging
import os
import pika
import shutil
import subprocess
import time

RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
RABBIT_USER = os.environ["RABBIT_MQ_USER"]
RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]

# BASE_DIR = '/music-box-interactive/interactive'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
BASE_DIR = settings.BASE_DIR

# disable propagation
logging.getLogger("pika").propagate = False


# add session_id to queue model_finished
def add_status_to_queue(session_id, host, port, status):
    """
    Adds session_id to queue model_finished.
    """
    message = {'session_id': session_id, "model_status": status}
    conn_params = pika.ConnectionParameters(host, port)
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    channel.queue_declare(queue='model_finished_queue')
    channel.basic_publish(exchange='',
                          routing_key='model_finished_queue',
                          body=json.dumps(message))
    connection.close()


class SessionModelRunner():
    def __init__(self, session_id):
        self.setPathsForSessionID(session_id)
    if "MUSIC_BOX_BUILD_DIR" in os.environ:
        mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'])

    out_path = os.path.join(mb_dir, 'output.csv')
    error_path = os.path.join(mb_dir, 'error.json')
    log_path = os.path.join(BASE_DIR, 'dashboard/static/log/log')

    sessionid = ""
    def setPathsForSessionID(self, session_id):
        global mb_dir
        global out_path
        global error_path
        global copy_path
        global config_path
        global old_path
        global complete_path
        global config_dest
        global config_folder_path
        global camp_folder_path
        global reactions_path
        global species_path
        global sessionid
        global log_path

        self.mb_dir = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'], session_id)
        logging.info("set mb_dir to: " + self.mb_dir)
        self.out_path = os.path.join(self.mb_dir, 'output.csv')
        self.error_path = os.path.join(self.mb_dir, 'error.json')
        self.copy_path = os.path.join(
            BASE_DIR, 'past_run/'+session_id+'/past.csv')
        self.config_path = os.path.join(
            BASE_DIR, "configs/"+session_id+"/my_config.json")
        self.old_path = os.path.join(
            BASE_DIR, "configs/"+session_id+"/old_config.json")
        self.complete_path = os.path.join(self.mb_dir, 'MODEL_RUN_COMPLETE')
        self.config_dest = os.path.join(
            BASE_DIR, 'past_run/'+session_id+'/config.json')
        self.config_folder_path = os.path.join(
            BASE_DIR, "configs/"+session_id)
        self.log_path = os.path.join(BASE_DIR, 'logs/'+session_id)
        self.camp_folder_path = os.path.join(
            BASE_DIR, "configs/"+session_id+"/camp_data")
        reac = "/camp_data/reactions.json"
        self.reactions_path = os.path.join(
            BASE_DIR, "configs/"+session_id+reac)
        self.species_path = os.path.join(
            BASE_DIR, "configs/"+session_id+"/camp_data/species.json")
        self.sessionid = session_id


    def create_file_list(self):
        config = direct_open_json(self.config_path)
        filelist = []
        configFolderContents = os.listdir(self.config_folder_path)

        for configSection in config:
            section = config[configSection]
            for configItem in section:
                if '.' in configItem:
                    filelist.append(configItem)

        for name in filelist:
            if name not in configFolderContents:
                filelist.remove(name)
        return filelist

    def setup_run(self):
        logging.info("setup run called")

        config = direct_open_json(self.config_path)

        newpath = os.path.join(self.mb_dir, 'mb_configuration')
        if os.path.exists(newpath):
            shutil.rmtree(newpath)
            os.makedirs(newpath)
        else:
            os.makedirs(newpath)
        filelist = self.create_file_list()
        filelist.append('my_config.json')
        for f in filelist:
            self.copyAFile(os.path.join(
                self.config_folder_path, f), os.path.join(newpath, f))

        camp_path = os.path.join(self.mb_dir, 'camp_data')
        if os.path.exists(camp_path):
            shutil.rmtree(camp_path)
        os.makedirs(camp_path)
        for f in os.listdir(self.camp_folder_path):
            self.copyAFile(os.path.join(
                self.camp_folder_path, f), os.path.join(camp_path, f))
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        originalPath = os.path.join(
            BASE_DIR, 'dashboard/static/log/log_config.json')
        self.copyAFile(originalPath, os.path.join(
            self.log_path, "log_config.json"))
        time.sleep(0.1)

        filelist.remove('my_config.json')
        # check file list remove for being right?
        for f in filelist:
            self.copyAFile(os.path.join(
                           self.mb_dir+'/mb_configuration', f),
                           os.path.join(self.mb_dir, f))
        # checksum = self.calculate_checksum()
        logging.info("running model from base directory: " + self.mb_dir)


    # copy inital config file on first model run
    def setup_config_check(self):
        self.copyAFile(self.config_path, self.old_path)

    def check(self, request):
        time.sleep(2)
        response_message = {}
        status = 'checking'
        # check if output file exists
        t = 0
        while status == 'checking':
            logging.info(status)
            time.sleep(1)
            if os.path.isfile(self.error_path):  # check if error file exists
                # check if error has been output
                if os.path.getsize(self.error_path) != 0:
                    status = 'error'
            elif os.path.isfile(self.complete_path):
                time.sleep(0.2)
                logging.info("complete file found")
                if os.path.getsize(self.out_path) != 0:  # model has finished?
                    logging.info("output file found")
                    status = 'done'
        # update_with_result(status)
        response_message.update({'status': status})
        if status == 'error':
            with open(self.error_path) as g:
                errorfile = json.loads(g.read())
            # search for the species which returned the error
            if "Property 'chemical_species%" in errorfile['message']:
                part = errorfile['message'].split('%')[1]
                specie = part.split("'")[0]
                path = os.path.join(self.config_folder_path, 'species.json')
                with open(path) as g:
                    spec_json = json.loads(g.read())
                for key in spec_json['formula']:
                    if spec_json['formula'][key] == specie:
                        response_message.update({'e_type': 'species'})
                        response_message.update({'spec_ID': key + '.Formula'})
            response_message.update({'e_code': errorfile['code']})
            response_message.update({'e_message': errorfile['message']})
        return JsonResponse(response_message)

    def check_load(self, request):
        logging.info("checking via check_load...")
        response_message = {}
        status = 'checking'
        # check if error file exists
        if os.path.isfile(self.error_path):
            # check if error has been output
            if os.path.getsize(self.error_path) != 0:
                status = 'error'
        elif os.path.isfile(self.complete_path):
            # check if model has finished
            if os.path.getsize(self.out_path) != 0:
                status = 'done'

        response_message.update({'status': status,
                                 'session_id': request.session.session_key})
        return JsonResponse(response_message)

    def run(self):
        logging.info("running...")
        self.setup_run()
        self.save_run()

    def copyAFile(self, source, destination):
        configFile = open(source, 'rb')
        content = configFile.read()
        g = open(destination, 'wb')
        g.write(content)
        g.close()
        configFile.close()

    def save_run(self):
        config = direct_open_json(self.config_path)
        filelist = []
        configFolderContents = os.listdir(self.config_folder_path)

        logEntryName = 'run_at_' + str(datetime.now())
        foldername = os.path.join(self.log_path, logEntryName)
        lc = direct_open_json(os.path.join(self.log_path, 'log_config.json'))
        if not lc['logging_enabled']:
            return
        lc.update({'current': foldername})
        history = lc['history']
        history.update({foldername: 'running'})
        lc.update({'history': history})
        direct_dump_json(os.path.join(self.log_path, 'log_config.json'), lc)

        for configSection in config:
            section = config[configSection]
            for configItem in section:
                if '.' in configItem:
                    filelist.append(configItem)

        for name in filelist:
            if name not in configFolderContents:
                filelist.remove(name)

        filelist.append('my_config.json')

        os.makedirs(foldername)

        for f in filelist:
            self.copyAFile(os.path.join(self.config_folder_path,
                           f), os.path.join(foldername, f))

    def update_with_result(self, status):
        lc = direct_open_json(os.path.join(self.log_path,
                              'log_config.json'))
        if not lc['logging_enabled']:
            return
        current = lc['current']
        history = lc['history']
        if status == 'error':
            history.update({current: 'error'})
            self.copyAFile(error_path, os.path.join(
                os.path.join(self.log_path, current),
                'error.json'))
        elif status == 'done':
            history.update({current: 'done'})
            self.copyAFile(out_path, os.path.join(
                os.path.join(self.log_path, current),
                'output.csv'))
        elif status == 'timeout':
            history.update({current: 'timeout'})
        elif status == 'empty_output':
            history.update({current: 'empty_output'})

        lc.update({'history': history})
        direct_dump_json(os.path.join(self.log_path,
                         'log_config.json'), lc)
        return

    def clear_log(self):
        shutil.rmtree(self.log_path)
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        lc = direct_open_json(os.path.join(self.log_path,
                                           'log_config.json'))
        lc.update({'history': {}})
        direct_dump_json(os.path.join(self.log_path,
                                      'log_config.json'), lc)
        logging.info('log cleared')
