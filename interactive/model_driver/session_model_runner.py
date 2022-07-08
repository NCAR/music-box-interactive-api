# SESSION BASED MODEL RUNNING


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
# from .run_logging import *
from datetime import datetime
from mechanism.reactions import reactions_are_valid
from interactive.tools import *

class SessionModelRunner():
    def __init__(self, session_id):
        self.setPathsForSessionID(session_id)
    interface_solo = False
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
    old_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/old_config.json")
    complete_path = os.path.join(mb_dir, 'MODEL_RUN_COMPLETE')


    config_dest = os.path.join(settings.BASE_DIR, 'dashboard/static/past_run/config.json')

    config_folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/config")
    log_path = os.path.join(settings.BASE_DIR, 'dashboard/static/log/log')
    camp_folder_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data")

    reactions_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/reactions.json")
    species_path = os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")

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

        self.mb_dir = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], session_id)
        print("* set mb_dir to: " + self.mb_dir)
        self.out_path = os.path.join(self.mb_dir, session_id+'/output.csv')
        # print("* set out_path to: " + out_path)
        self.error_path = os.path.join(self.mb_dir, session_id+'/error.json')
        # print("* set error_path to: " + error_path)
        self.copy_path = os.path.join(settings.BASE_DIR, 'past_run/'+session_id+'/past.csv')
        # print("* set copy_path to: " + copy_path)
        self.config_path = os.path.join(settings.BASE_DIR, "configs/"+session_id+"/my_config.json")
        # print("* set config_path to: " + config_path)
        self.old_path = os.path.join(settings.BASE_DIR, "configs/"+session_id+"/old_config.json")
        # print("* set old_path to: " + old_path)
        self.complete_path = os.path.join(self.mb_dir, 'MODEL_RUN_COMPLETE')
        # print("* set complete_path to: " + complete_path)


        self.config_dest = os.path.join(settings.BASE_DIR, 'past_run/'+session_id+'/config.json')
        # print("* set config_dest to: " + config_dest)

        self.config_folder_path = os.path.join(settings.BASE_DIR, "configs/"+session_id)
        # self.log_path = os.path.join(settings.BASE_DIR, 'logs/'+session_id)
        # print("* set log_path to: " + self.log_path)
        self.camp_folder_path = os.path.join(settings.BASE_DIR, "configs/"+session_id+"/camp_data")

        self.reactions_path = os.path.join(settings.BASE_DIR, "configs/"+session_id+"/camp_data/reactions.json")
        # print("* set reactions_path to: " + reactions_path)
        self.species_path = os.path.join(settings.BASE_DIR, "configs/"+session_id+"/camp_data/species.json")
        # print("* set species_path to: " + species_path)
        self.sessionid = session_id

    def copyConfigFile(self, source, destination):
        configFile = open(source, 'rb')
        content = configFile.read()
        g = open(destination, 'wb')
        g.write(content)
        g.close()
        configFile.close()
        print("* Copied config file: " + source + " ==> " + destination)
    def add_integrated_rates(self):
        with open(self.reactions_path) as f:
                r_data = json.loads(f.read())

        with open(self.species_path) as h:
                s_data = json.loads(h.read())

        names_list = []
        reactions = r_data['camp-data'][0]['reactions']
        for r in reactions:
            if 'reactants' in r:
                reactants = [j for j in r['reactants']]
            else:
                reactants = ['null']
            if 'products' in r:
                products = [m for m in r['products']]
            else:
                products = ['null']    
            name = "myrate__" + '_'.join(reactants) + "->" + '_'.join(products)
            if 'type' in r:
                name = name + "__" + r['type']
            if 'products' not in r:
                r.update({'products': {name: {}}})
            else:
                r['products'].update({name: {}})
            names_list.append(name)
        
        for name in names_list:
            s_data['camp-data'].append({"name": name, "type": "CHEM_SPEC"})

        r_data['camp-data'][0].update({'reactions': reactions})
        with open(self.reactions_path, 'w') as g:
            json.dump(r_data, g)
        
        with open(self.species_path, 'w') as i:
            json.dump(s_data, i)


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
        print("* setup run called")
        if self.interface_solo:
            return {'model_running': False, 'error_message': 'Model not connected to interface.'}
        if not reactions_are_valid(self.reactions_path):
            return {'model_running': False, 'error_message': 'At least one reaction must be present for the model to run.'}

        if os.path.isfile(self.complete_path):
            os.remove(self.complete_path)
        if os.path.isfile(self.out_path):
            os.remove(self.out_path)
        if os.path.isfile(self.error_path):
            os.remove(self.error_path)
        print("* setup run to path: " + self.complete_path)
        with open(self.reactions_path) as h:
            reactions_data = json.load(h)

        with open(self.species_path) as j:
            species_data = json.load(j)

        self.add_integrated_rates()
        print("* [debug] config path: " + self.config_path)
        config = direct_open_json(self.config_path)

        newpath = os.path.join(self.mb_dir, 'mb_configuration')
        if os.path.exists(newpath):
            rmtree(newpath)
            os.makedirs(newpath)
        else:
            os.makedirs(newpath)
        filelist = self.create_file_list()
        filelist.append('my_config.json')
        print(filelist)
        for f in filelist:
            self.copyConfigFile(os.path.join(self.config_folder_path, f), os.path.join(newpath, f))

        camp_path = os.path.join(self.mb_dir, 'camp_data')
        print("* [debug] camp_path: " + camp_path)
        if os.path.exists(camp_path):
            rmtree(camp_path)
        os.makedirs(camp_path)
        for f in os.listdir(self.camp_folder_path):
            self.copyConfigFile(os.path.join(self.camp_folder_path, f), os.path.join(camp_path, f))

        time.sleep(0.1)

        filelist.remove('my_config.json')
        #check file list remove for being right?
        for f in filelist:
            self.copyConfigFile(os.path.join(self.mb_dir+'/mb_configuration', f), os.path.join(self.mb_dir, f))
        print("* running model from base directory: " + self.mb_dir)
        print("* my_config location:", self.mb_dir+'/mb_configuration/my_config.json')
        # process = subprocess.Popen([r'./music_box', r'.'+self.mb_dir+'/mb_configuration/my_config.json'], cwd=self.mb_dir) 
        process = subprocess.Popen([r'./music_box', r''+self.mb_dir+'/mb_configuration/my_config.json'], cwd=os.environ['MUSIC_BOX_BUILD_DIR'])
        with open(self.reactions_path, 'w') as k:
            json.dump(reactions_data, k)

        with open(self.species_path, 'w') as l:
            json.dump(species_data, l)

        return {'model_running': True}

    # copy inital config file on first model run
    def setup_config_check(self):
        self.copyConfigFile(self.config_path, self.old_path)

    def check(self, request):
        print("* checking...")
        time.sleep(1)
        response_message = {}
        status = 'checking'

        # check if output file exists
        t = 0
        while status == 'checking':
            print(status)
            time.sleep(.2)
            if os.path.isfile(self.error_path): # check if error file exists
                if os.path.getsize(self.error_path) != 0:  # check if error has been output
                    status = 'error'
            elif os.path.isfile(self.complete_path):
                time.sleep(0.2)
                if os.path.getsize(self.out_path) != 0:  # check if model has finished
                    status = 'done'

        # update_with_result(status)
        response_message.update({'status': status})

        if status == 'error':
            with open(self.error_path) as g:
                errorfile = json.loads(g.read())
            if "Property 'chemical_species%" in errorfile['message']:   #search for the species which returned the error
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
        print("* checking via check_load...")
        response_message = {}

        status = 'checking'
        if os.path.isfile(self.error_path): # check if error file exists
            if os.path.getsize(self.error_path) != 0:  # check if error has been output
                status = 'error'
        elif os.path.isfile(self.complete_path):
            if os.path.getsize(self.out_path) != 0:  # check if model has finished
                status = 'done'

        response_message.update({'status': status})

        return JsonResponse(response_message)

    def run(self, request):
        print("* running...")
        run = self.setup_run()
        print(run)
        self.save_run()
        return JsonResponse(run)

    def copyAFile(self, source, destination):
        configFile = open(source, 'rb')
        content = configFile.read()
        g = open(destination, 'wb')
        g.write(content)
        g.close()
        configFile.close()
        print("* Copied file: " + source + " ==> " + destination)

    def save_run(self):
        config = direct_open_json(self.config_path)
        print("* [debug] SAVE RUN config path: " + self.config_path)
        filelist = []
        configFolderContents = os.listdir(self.config_folder_path)

        logEntryName = 'run_at_' + str(datetime.now())
        foldername = os.path.join(self.log_path, logEntryName)
        print("* [debug] SAVE RUN foldername: " + foldername)
        print("* [debug] SAVE RUN log_config: " + os.path.join(self.log_path, 'log_config.json'))
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
            self.copyAFile(os.path.join(self.config_folder_path, f), os.path.join(foldername, f))

        
        # li = [int(x.split('_')[1]) for x in history.keys()]
        # largest = li.sort()[-1]
        # if largest > lc['log_length']:
        #     smallest = li.sort()[0]
        #     path_for_deletion = os.path.join(log_path, 'run_' + str(smallest))
        #     rmtree(path_for_deletion)


    def update_with_result(self, status):
        lc = direct_open_json(os.path.join(self.log_path, 'log_config.json'))
        if not lc['logging_enabled']:
            return
        current = lc['current']
        history = lc['history']
        if status == 'error':
            history.update({current: 'error'})
            self.copyAFile(error_path, os.path.join(os.path.join(self.log_path, current), 'error.json'))
        elif status == 'done':
            history.update({current: 'done'})
            self.copyAFile(out_path, os.path.join(os.path.join(self.log_path, current), 'output.csv'))
        elif status == 'timeout':
            history.update({current: 'timeout'})
        elif status == 'empty_output':
            history.update({current: 'empty_output'})


        lc.update({'history': history})
        direct_dump_json(os.path.join(self.log_path, 'log_config.json'), lc)    
        return


    def clear_log(self):
        rmtree(self.log_path)
        os.mkdir(self.log_path)

        lc = direct_open_json(os.path.join(self.log_path, 'log_config.json'))
        lc.update({'history': {}})
        direct_dump_json(os.path.join(self.log_path, 'log_config.json'), lc)
        print('log cleared')
