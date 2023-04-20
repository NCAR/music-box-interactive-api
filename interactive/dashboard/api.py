from .save import *
from .upload_handler import *
from dashboard.flow_diagram import *
from dashboard.forms.formsetup import *
from dashboard import models 
from django.conf import settings
from django.http import HttpResponse, Http404
from django.http import JsonResponse
from io import StringIO
from rest_framework import status, views
from rest_framework.response import Response
from shared.utils import check_for_rabbit_mq, create_unit_converter

import datetime
import logging
import os
import pika
import dashboard.database_tools as db_tools

# api.py contains all DJANGO based backend requests made to the server
# each browser session creates a "session_key" saved to cookie on client
#       - request.session.session_key is a string representation of this value
#       - request.session.session_key is used to access documents from DJANGO

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s',
                    level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s - [ERROR!!] %(message)s',
                    level=logging.ERROR)


class HealthView(views.APIView):
    def get(self, request):
        logging.info("health")
        response = JsonResponse({'data': 1})
        return response


class ExampleView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        example_name = request.GET.dict()['example']
        example_folder_path = os.path.join(settings.BASE_DIR, 'dashboard/static/examples', example_name)

        logging.debug(f"Examples| loading : {example_name}")

        user = db_tools.get_user(request.session.session_key)
        # recursively pull config file paths
        files = [os.path.join(dp, f) for dp, _, fn in os.walk(example_folder_path) for f in fn]
        if not files:
            raise Http404("No files in example folder")
        # loop through files and load them into database
        for path in files:
            filename = path.replace(example_folder_path, '')
            # each file is expected to be prefixed with / in the config section, like /my_config.json
            logging.info(f"Examples| processing {filename}")
            # check if json
            if path.endswith('.json'):
                # get json from file
                with open(path) as f:
                    data = json.load(f)
                    # put json into user.config_files
                    user.config_files.update({filename: data})
            # check if other file type
            elif path.endswith('.csv'):
                # get string representation of  file
                with open(path) as f:
                    data = f.read()
                    # put string representation into user.config_files
                    user.binary_files.update({filename: data})
        user.save()
        db_tools.export_to_database(request.session.session_key)
        menu_names = db_tools.get_mechanism(request.session.session_key)

        return JsonResponse(menu_names)


        

class SaveReactionView(views.APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.save()

        reaction_data = json.loads(request.body)
        if 'index' not in reaction_data:
            return JsonResponse({"error": "missing reaction index"})
        if 'name' not in reaction_data:
            return JsonResponse({"error": "missing reaction name"})
        if 'reactants' not in reaction_data:
            return JsonResponse({"error": "missing reaction reactants"})
        if 'products' not in reaction_data:
            return JsonResponse({"error": "missing reaction products"})

        db_tools.save_reaction(request.session.session_key, reaction_data)
        return Response(status=status.HTTP_200_OK)


class ReactionTypeSchemaView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SCHEMATYPEVIEW ******")
        if not request.session.session_key:
            request.session.save()
        if 'type' not in request.GET:
            return JsonResponse({"error": "missing reaction type"})
        reaction_type = request.GET['type']
        reaction_schema = db_tools.get_reaction_type_schema(request.session.session_key, reaction_type)
        return JsonResponse(reaction_schema)


class ModelOptionsView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("fetching model options for: " + request.session.session_key)
        model_options = db_tools.db_tools.get_model_options(request.session.session_key)
        return JsonResponse(model_options)
       
    def post(self, request):
        logging.info("****** POST request received MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("saving model options for user: "
                      + request.session.session_key)
        newOptions = json.loads(request.body)
        options = {}
        for key in newOptions:
            options.update({key: newOptions[key]})
        user = db_tools.get_user(request.session.session_key)
        # dump options into options.json
        user.config_files['/options.json'] = options
        user.save()
        
        logging.info('box model options updated')
        options = db_tools.get_model_options(request.session.session_key)
        db_tools.export_to_database_path(request.session.session_key)
        return JsonResponse(options)


class InitialConditionsFiles(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received INITIAL CONDITIONS FILE ******")
        if not request.session.session_key:
            request.session.save()

        logging.debug("fetching conditions files for session id: " +
              request.session.session_key)
        conditions_files = db_tools.get_initial_conditions_files(request.session.session_key)
        return JsonResponse(conditions_files)


class ConditionsSpeciesList(views.APIView):
    def get(self, request):
        logging.info("****** GET request received INITIAL SPECIES LIST ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("fetching species list for session id: " +
              request.session.session_key)
        
        species = {"species": db_tools.get_condition_species(request.session.session_key)}
        logging.info("returning species [csl]:" + str(species))
        return JsonResponse(species)


class InitialConditionsSetup(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.save()

        logging.debug("fetching initial conditions setup for session id: " +
              request.session.session_key)
        data = db_tools.get_user(request.session.session_key).config_files['/initials.json']
        return JsonResponse(data)
       

    def post(self, request):
        logging.info(
            "****** POST request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("saving initial conditions setup for session id: " +
                      request.session.session_key)
        logging.debug("received initial conditions setup: " +
                      str(request.body))
        newData = json.loads(request.body)
        user = db_tools.get_user(request.session.session_key)
        user.config_files['/initials.json'] = newData
        user.save()
        return JsonResponse({})


class InitialSpeciesConcentrations(views.APIView):
    def get(self, request):

        logging.info("****** GET request received INIT_SPECIES_CONC ******")
        if not request.session.session_key:
            request.session.save()
        values = db_tools.get_initial_species_concentrations(request.session.session_key)
        return JsonResponse(values)

    def post(self, request):
        logging.info(
            "****** POST request received INITIAL SPECIES CONC. ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("received options:" + str(request.body))
        initial_values = json.loads(request.body)

        logging.info("* pushing new options:" + str(initial_values))
        formulas = {}
        units = {}
        values = {}
        i = 0
        for key, value in initial_values.items():
            name = "Species " + str(i)
            formulas[name] = key
            units[name] = value["units"]
            values[name] = value["value"]
            i += 1
        file_data = {}
        file_data["formula"] = formulas
        file_data["unit"] = units
        file_data["value"] = values
        # dump file_data into species.json
        user = db_tools.get_user(request.session.session_key)
        user.config_files['/species.json'] = file_data
        user.save()
        # run export
        db_tools.export_to_database_path(request.session.session_key)
        return JsonResponse({})


class InitialReactionRates(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.save()

        logging.debug("fetching initial species conc. for session id: " +
                      request.session.session_key)
        initial_rates = {}
        initial_rates = db_tools.convert_initial_conditions_file(request.session.session_key, ',')
        return JsonResponse(initial_rates)

    def post(self, request):
        logging.info(
            "****** POST request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("received options:" + str(request.body))
        initial_values = json.loads(request.body)

        initial_reaction_rates_file_path = '/initial_reaction_rates.csv'
        db_tools.convert_initial_conditions_dict(request.session.session_key, initial_values, initial_reaction_rates_file_path, ',')
        db_tools.export_to_database_path(request.session.session_key)
        return JsonResponse({})


class ConvertValues(views.APIView):
    def get(self, request):
        unit_type = request.GET['type']
        new_unit = request.GET['new unit']
        initial_value = float(request.GET['value'])
        if any(c in unit_type for c in ('temperature', 'pressure')):
            response = convert_initial_conditions(
                unit_type, new_unit, initial_value)
        else:
            response = {}
        return JsonResponse(response)


class UnitConversionArguments(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received UNIT CONVERSION ARGUMENTS ******")
        if not request.session.session_key:
            request.session.save()
        initial = request.GET['initialUnit']
        final = request.GET['finalUnit']
        arguments = db_tools.get_required_arguments(initial, final)
        f = db_tools.make_additional_argument_form(arguments)
        return f


class UnitOptions(views.APIView):
    def get(self, request):
        unit_type = request.GET['unitType']
        response = db_tools.make_unit_convert_form(unit_type)
        return response


class ConversionCalculator(views.APIView):
    def get(self, request):
        conversion_request = request.GET.dict()
        args = [x for x in conversion_request if 'args' in x]
        arg_dict = {}
        for key in conversion_request:
            if 'title' in key:
                arg_dict.update({conversion_request[key]: float(
                    conversion_request[key.replace('title', 'value')])})
                arg_dict.update(
                    {conversion_request[key] + ' units': (
                        conversion_request[key.replace('title', 'unit')])})
        converter = create_unit_converter(
            conversion_request['initialUnit'],
            conversion_request['finalUnit'])
        if arg_dict:
            new_value = converter(
                float(conversion_request['initialValue']), arg_dict)
        else:
            new_value = converter(float(conversion_request['initialValue']))

        return HttpResponse(new_value)


class MusicaReactionsList(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received MUSICA REACTIONS LIST ******")
        if not request.session.session_key:
            request.session.save()

        logging.debug("* fetching species list for session id: " +
                      request.session.session_key)
        reactions = {}
        reactions = {"reactions": db_tools.get_reaction_musica_names(request.session.session_key)}
        return JsonResponse(reactions)
            

class EvolvingConditions(views.APIView):
    def get(self, request):
        logging.info("****** GET request received EVOLVING CONDITIONS ******")
        if not request.session.session_key:
            request.session.save()
        config = db_tools.get_user(request.session.session_key).config_files['/my_config.json']

        e = config['evolving conditions']
        evolving_conditions_list = e.keys()

        # contains a dictionary w/ key as filename and value as header of file
        file_header_dict = {}
        for i in evolving_conditions_list:
            if '.csv' in i or '.txt' in i:
                logging.info("adding file: " + i)
                read_obj = db_tools.get_user(request.session.session_key).binary_files['/'+i]
                csv_reader = reader(read_obj)
                list_of_rows = list(csv_reader)

                try:
                    file_header_dict.update({i: list_of_rows[0]})
                except IndexError:
                    file_header_dict.update({i: ['EMPTY FILE']})
            elif '.nc' in i:
                file_header_dict.update({i: ['NETCDF FILE']})
        return JsonResponse(file_header_dict)


class LinearCombinations(views.APIView):
    def get(self, request):
        logging.info("****** GET request received LINEAR COMBINATIONS ******")
        if not request.session.session_key:
            request.session.save()
        config_path = os.path.join(settings.BASE_DIR,
                                   'configs/' + request.session.session_key +
                                   "/my_config.json")
        logging.debug("config path: " + config_path)
        config = direct_open_json(config_path)

        if 'evolving conditions' not in config:
            return []
        else:
            filelist = config['evolving conditions'].keys()

        linear_combo_dict = {}

        for f in filelist:
            if config['evolving conditions'][f]['linear combinations']:
                cond = config['evolving conditions'][f]
                combos = cond['linear combinations']
                for key in combos:
                    combo = combos[key]['properties']
                    c = [key for key in combo]
                    linear_combo_dict.update({f.replace('.', '-'): c})

        return JsonResponse(linear_combo_dict)


class CheckLoadView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received RUN_STATUS_VIEW ******")
        logging.info(request)
        if not request.session.session_key:
            request.session.save()
        logging.debug(f"session key: {request.session.session_key}")
        response_message = db_tools.get_run_status(request.session.session_key)
        logging.info(f"status: {response_message}")
        return JsonResponse(response_message)


class CheckView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received RUN_STATUS_VIEW ******")
        logging.info(request)
        if not request.session.session_key:
            request.session.save()
        logging.debug(f"session key: {request.session.session_key}")
        response_message = db_tools.get_run_status(request.session.session_key)
        print("status: ", response_message)
        return JsonResponse(response_message)


class RunView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        # check if model is already running
        if db_tools.get_run_status(request.session.session_key) == 'running':
            return JsonResponse({'status': 'running'})
        else:
            # start model run by adding job to queue via pika
            # get ModelRun object and set status to true
            db_tools.set_is_running(request.session.session_key, True)

            # disable pika logging because it's annoying
            logging.getLogger("pika").propagate = False
            isRabbitUp = check_for_rabbit_mq()
            if isRabbitUp:
                user = db_tools.get_user(request.session.session_key)
                # check if we should save checksum
                if user.should_cache:
                    logging.info("saving checksum")
                    # get checksum and save to session
                    checksum = db_tools.calculate_checksum(request.session.session_key)
                    logging.info("got checksum for current user config files: " + str(checksum))
                    # try to find user with same checksum and should_cache = True
                    user = db_tools.get_user_by_checksum(checksum)
                    db_tools.set_current_checksum(request.session.session_key, checksum)
                    
                    if user:
                        # if found, copy results from that user to current user
                        logging.info("found user with same checksum, copying results")
                        db_tools.copy_results(user.uid, request.session.session_key)
                        # set is_running to false
                        db_tools.set_is_running(request.session.session_key, False)
                        # return status of done
                        return JsonResponse({'status': 'done',
                                             'session_id': request.session.session_key,
                                             'running': False})
                # check to make sure we have a model to run by
                # checking if config and binary files exist
                if user.config_files is not {} and user.binary_files is not {}:
                    # if we get here, we need to run the model
                    logging.info("rabbit is up, adding simulation to queue")
                    RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
                    RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
                    RABBIT_USER = os.environ["RABBIT_MQ_USER"]
                    RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]
                    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
                    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
                    connection = pika.BlockingConnection(connParam)
                    channel = connection.channel()
                    channel.queue_declare(queue='run_queue')
                    body = {}
                    body.update({"session_id": request.session.session_key})
                    # put all config files in body
                    body.update({"config_files": user.config_files})
                    # put all binary files in body
                    body.update({"binary_files": user.binary_files})
                    channel.basic_publish(exchange='',
                                    routing_key='run_queue',
                                    body=json.dumps(body))

                    # close connection
                    connection.close()
                    logging.info("published message to run_queue")
                    return JsonResponse({'status': 'queued', 'model_running': True})
                else:
                    logging.info("no config or binary files found for user " + request.session.session_key + ", not running model")
                    return JsonResponse({'status': 'error', 'model_running': False})
            else:
                from model_driver.session_model_runner import SessionModelRunner
                runner = SessionModelRunner(request.session.session_key)
                logging.info("rabbit is down, sim. will be run on API server")
                return runner.run()



class DownloadConfig(views.APIView):
    def get(self, request):
        logging.info("****** GET request received DOWNLOAD_CONFIG ******")
        if not request.session.session_key:
            request.session.save()
        sessid = request.session.session_key
        logging.info("sessid: "+sessid)
        destination_path = os.path.join(
            settings.BASE_DIR,
            "dashboard/static/zip/"
            + sessid
            + "/config_copy")
        zip_path = os.path.join(
            settings.BASE_DIR, "dashboard/static/zip/output/"
            + sessid
            + "/config.zip")
        conf_path = os.path.join(
            settings.BASE_DIR, 'configs/' + sessid)
        logging.debug("destination path: " + destination_path)
        logging.debug("zip path: " + zip_path)
        logging.debug("conf path: " + conf_path)
        # get config files for this session
        config_files = db_tools.get_config_files(sessid)
        # temporarily copy config files to static folder
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        for file in config_files:
            config_file_string = config_files[file]
            with open(conf_path + file, "w") as f:
                f.write(json.dumps(config_file_string))
        # now do the same for binary files
        binary_files = models.SessionUser.objects.get(
            uid=sessid).binary_files
        for file in binary_files:
            binary_file_string = binary_files[file]
            with open(conf_path + file, "wb") as f:
                f.write(binary_file_string.encode('utf-8'))
        
        # zip up config files
        create_config_zip(destination_path, zip_path, conf_path)
        fl_path = zip_path
        zip_file = open(fl_path, 'rb')
        response = HttpResponse(zip_file, content_type='application/zip')
        attach_string = 'attachment; filename="%s"' % 'config.zip'
        response['Content-Disposition'] = attach_string

        # delete temporary files
        shutil.rmtree(destination_path)
        os.remove(zip_path)

        return response


class DownloadResults(views.APIView):
    def get(self, request):
        logging.info("****** GET request received DOWNLOAD_RESULTS ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("session key: " + request.session.session_key)
        # fl_path = os.path.join(
        #     os.environ['MUSIC_BOX_BUILD_DIR'],
        #     request.session.session_key + "/output.csv")
        now = datetime.now()
        filename = str(now) + '_model_output.csv'
        # fl = open(fl_path, 'r')
        # mime_type, _ = mimetypes.guess_type(fl_path)
        # get output csv from database
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        # check if output csv exists
        if model.results['/output.csv'] is None:
            return HttpResponse("No output file available", status=404)
        output_csv = StringIO(model.results['/output.csv'])
        # put csv in response
        response = HttpResponse(output_csv, content_type='text/csv')
        attach_string = 'inline; filename=' + filename
        response['Content-Disposition'] = attach_string
        return response


class ConfigJsonUpload(views.APIView):
    def post(self, request):
        logging.info("****** GET request received CONFIG_UPLOAD ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("session key: " + request.session.session_key)
        uploaded = request.FILES['file']
        configs_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        handle_uploaded_zip_config(
            uploaded, "dashboard/static/zip/" + request.session.session_key,
            configs_path)
        export_to_path(configs_path+"/")
        # now copy files from export_to_path into database and delete from file system 
        user = models.SessionUser.objects.get(uid=request.session.session_key)
        # start with species.json
        with open(configs_path+"/species.json", "r") as f:
            species_json = f.read()
            # set user.config_files['species.json'] to species_json
            user.config_files['/species.json'] = species_json
        # now do the same for the other files
        with open(configs_path+"/reactions.json", "r") as f:
            reactions_json = f.read()
            user.config_files['/reactions.json'] = reactions_json
        with open(configs_path+"/options.json", "r") as f:
            options_json = f.read()
            user.config_files['/options.json'] = options_json
        with open(configs_path+"/initials.json", "r") as f:
            initials_json = f.read()
            user.config_files['/initials.json'] = initials_json
        with open(configs_path+"/my_config.json", "r") as f:
            my_config_json = f.read()
            user.config_files['/my_config.json'] = my_config_json
        # save user, delete files from file system
        user.save()

        shutil.rmtree(configs_path)
        
        return JsonResponse({})


class RemoveInitialConditionsFile(views.APIView):
    def post(self, request):
        logging.info(
            "****** GET request received REMOVE_INIT_COND_FILE ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("session key: " + request.session.session_key)
        configs_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        remove_request = json.loads(request.body)
        logging.debug("removing file:" + str(remove_request))

        # remove 'file name' from user.binary_files
        user = models.SessionUser.objects.get(uid=request.session.session_key)
        user.binary_files.remove(remove_request['file name'])
        # update my_config
        my_config = json.loads(user.config_files['/my_config.json'])
        del my_config['initial conditions'][remove_request['file name']]
        user.config_files['/my_config.json'] = my_config
        user.save()

        
        return JsonResponse({})


# upload on conditions/intial page
class InitCSV(views.APIView):
    def post(self, request):
        logging.info("****** POST request received INIT_CSV ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("session key: " + request.session.session_key)
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        conf_path = os.path.join(
            settings.BASE_DIR,
            'configs/' + request.session.session_key)
        logging.debug("uploaded file: " + filename)
        logging.debug("saving to conf_path: " + conf_path)
        # manage_initial_conditions_files(uploaded, filename, conf_path)
        # save file to database
        user = models.SessionUser.objects.get(uid=request.session.session_key)
        # save file to user.binary_files
        user.binary_files[filename] = uploaded.read()
        # update my_config
        my_config = user.config_files['/my_config.json']
        if 'initial conditions' in my_config:
            initials = my_config['initial conditions']
        else:
            initials = {}
        initials.update({filename: {}})
        my_config.update({'initial conditions': initials})
        user.config_files['/my_config.json'] = my_config
        user.save()
        return JsonResponse({})


class ClearEvolutionFiles(views.APIView):
    def get(self, request):
        logging.info("****** POST request received INIT_CSV ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("session key: " + request.session.session_key)
        conf_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        logging.debug("clearing evolution files:" + conf_path)
        # clear_e_files(conf_path)
        # clear files from database
        user = models.SessionUser.objects.get(uid=request.session.session_key)
        binary_files = user.binary_files
        config = user.config_files['/my_config.json']
        # clear user.binary_files
        e = config['evolving conditions']
        # delete files from user.binary_files
        for file in e:
            del binary_files['/'+file]
        config.update({'evolving conditions': {}})
        user.config_files['/my_config.json'] = config
        user.save()
        logging.info('finished clearing evolution files')
        return JsonResponse({})


class EvolvFileUpload(views.APIView):
    def post(self, request):
        logging.info("****** POST request received EVOLV_FILE_UPLOAD ******")
        if not request.session.session_key:
            request.session.save()
        logging.debug("session key: " + request.session.session_key)
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        conf_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        logging.debug("uploading file: " + filename)
        # manage_uploaded_evolving_conditions_files(
            # uploaded, filename, conf_path)
        # save file to database
        user = models.SessionUser.objects.get(uid=request.session.session_key)
        # save file to user.binary_files
        user.binary_files[filename] = uploaded.read()
        # update my_config
        my_config = user.config_files['/my_config.json']
        if 'evolving conditions' in my_config:
            evolving = my_config['evolving conditions']
        else:
            evolving = {}
        evolving.update({filename: {}})
        my_config.update({'evolving conditions': evolving})
        user.config_files['/my_config.json'] = my_config
        user.save()

        logging.info("uploaded evolving file: " + filename)
        return JsonResponse({})


class LoadFromConfigJsonView(views.APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.save()
        logging.info("saving model options for user: " +
                     request.session.session_key)
        uploaded = request.FILES['file']

