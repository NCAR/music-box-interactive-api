# import re
from django.shortcuts import render
from .forms.optionsforms import *
from .forms.report_bug_form import BugForm
from .forms.evolvingforms import *
from .forms.initial_condforms import *
from .flow_diagram import generate_flow_diagram
from .flow_diagram import get_simulation_length, get_species
from .upload_handler import *
from .build_unit_converter import *
from .save import *
# from .models import Document
from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404
from django.http import JsonResponse, HttpResponseBadRequest, HttpRequest
import os
from django.conf import settings
import mimetypes
from django.core.files import File
from interactive.tools import *
import pandas
import platform
import codecs
import time
from io import TextIOWrapper
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from mechanism.reactions import *
from mechanism.species import *
from mechanism.network_plot import *
from plots.plot_setup import *
from dashboard.forms.formsetup import *
from plots.plot_setup import *
from os.path import exists
from dashboard.flow_diagram import *
import logging
from .models import *
from .database_tools import *
import pika
from io import StringIO

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


def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '__' in reaction:
        reaction = reaction.replace('__', ' (')
        reaction = reaction+")"
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction


class HealthView(views.APIView):
    def get(self, request):
        logging.info("health")
        response = JsonResponse({'data': 1})
        return response


class ExampleView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        # set example conditions and species/reactions
        example_name = 'example_' + str(request.GET.dict()['example'])
        examples_path = os.path.join(
            settings.BASE_DIR, 'dashboard/static/examples')
        example_folder_path = os.path.join(examples_path, example_name)

        logging.debug("|_ loading example #" + str(request.GET.dict()['example']))
        logging.info("|_ example folder path: " + example_folder_path)

        user = get_user(request.session.session_key) # get user via sessionkey
        # get files in example_folder_path
        files = get_files(example_folder_path)
        # loop through files and remove example_folder_path from file path
        for i in range(len(files)):
            files[i] = files[i].replace(example_folder_path, '')
        print("|_ files: ", str(files))
        # check if files exist
        if not files:
            raise Http404("No files in example folder")
        # loop through files and load them into database
        for file in files:
            # check if json
            if file.endswith('.json'):
                # get json from file
                with open(example_folder_path + file) as f:
                    data = json.load(f)
                    # put json into user.config_files
                    user.config_files.update({file: data})
                    f.close()
            # check if other file type
            elif file.endswith('.csv'):
                # get string representation of  file
                with open(example_folder_path + file) as f:
                    data = f.read()
                    # put string representation into user.config_files
                    user.binary_files.update({file: data})
                    f.close()
        #save user
        user.save()
        export_to_database(request.session.session_key)
        menu_names = get_species_menu_list(request.session.session_key)

        print("* menu names: " + str(menu_names))
        response = Response(menu_names, status=status.HTTP_200_OK)
        return response


class SpeciesView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SPECIES_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.info("fetching species for session: " + request.session.session_key)

        menu_names = get_species_menu_list(request.session.session_key)
        response = Response(menu_names, status=status.HTTP_200_OK)
        return response

class SpeciesDetailView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SPECIES_DETAIL ******")
        if not request.session.session_key:
            request.session.create()
        if 'name' not in request.GET:
            return JsonResponse({"error": "missing species name"})
        species_name = request.GET['name']
        logging.info("fetching species: " + species_name)
        species = get_species_detail(request.session.session_key, species_name)
        response = JsonResponse(species)
        return response


class RemoveSpeciesView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received REMOVE_SPECIES ******")
        if not request.session.session_key:
            request.session.create()
        if 'name' not in request.GET:
            return HttpResponseBadRequest("missing species name")
        species_name = request.GET['name']
        logging.info("removing species: " + species_name)
        remove_species(request.session.session_key, species_name)
        return HttpResponse(status=status.HTTP_200_OK)


class AddSpeciesView(views.APIView):
    def post(self, request):
        logging.info("****** POST request received ADD_SPECIES ******")
        species_data = json.loads(request.body)
        if 'name' not in species_data:
            return JsonResponse({"error": "missing species name"})
        species_data['type'] = "CHEM_SPEC"
        # add species to database
        add_species(request.session.session_key, species_data)
        return HttpResponse(status=status.HTTP_200_OK)


class PlotSpeciesView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        if 'name' not in request.GET:
            return HttpResponseBadRequest("missing species name")
        species = request.GET['name']
        network_plot_dir = os.path.join(
                settings.BASE_DIR, "dashboard/templates/network_plot/" +
                request.session.session_key)
        template_plot = os.path.join(
            settings.BASE_DIR,
            "dashboard/templates/network_plot/plot.html")
        if not os.path.isdir(network_plot_dir):
            os.makedirs(network_plot_dir)
        # use copyfile()
        if exists(os.path.join(network_plot_dir, "plot.html")) is False:
            # create plot.html file if doesn't exist
            f = open(os.path.join(network_plot_dir, "plot.html"), "w")
            logging.info("putting plot into file " + str(os.path.join(network_plot_dir, "plot.html")))
        shutil.copyfile(template_plot, network_plot_dir + "/plot.html")
        logging.info("generating plot and exporting to " + str(network_plot_dir + "/plot.html"))
        # generate network plot and place it in unique directory for user
        html = generate_database_network_plot(request.session.session_key,
                                       species,
                                       network_plot_dir + "/plot.html")
        #plot = ('network_plot/'
        #        + request.session.session_key
        #        + '/plot.html')
        plot = str(network_plot_dir + "/plot.html")[1:]
        #logging.info("[debug] rendering from " + plot)
        #return render(request, plot)
        #logging.info("returning html: " + str(html))
        return HttpResponse(html)
        
class ReactionsView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received REACTIONS_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        reactions = get_reactions_menu_list(request.session.session_key)
        response = Response(reactions, status=status.HTTP_200_OK)
        return response

class ReactionsDetailView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        if 'index' not in request.GET:
            return JsonResponse({"error": "missing reaction index"})
        reaction_detail = get_reactions_info(request.session.session_key)[int(request.GET['index'])]
        reaction_detail['index'] = int(request.GET['index'])
        return JsonResponse(reaction_detail)


class RemoveReactionView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received REMOVE_REACTION ******")
        if not request.session.session_key:
            request.session.create()
        if 'index' not in request.GET:
            return HttpResponseBadRequest("missing reaction index")
        reaction_index = int(request.GET['index'])
        remove_reaction(request.session.session_key, reaction_index)
        return Response(status=status.HTTP_200_OK)


class SaveReactionView(views.APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.create()

        reaction_data = json.loads(request.body)
        if 'index' not in reaction_data:
            return JsonResponse({"error": "missing reaction index"})
        if 'name' not in reaction_data:
            return JsonResponse({"error": "missing reaction name"})
        if 'reactants' not in reaction_data:
            return JsonResponse({"error": "missing reaction reactants"})
        if 'products' not in reaction_data:
            return JsonResponse({"error": "missing reaction products"})

        save_reaction(request.session.session_key, reaction_data)
        return Response(status=status.HTTP_200_OK)


class ReactionTypeSchemaView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SCHEMATYPEVIEW ******")
        if not request.session.session_key:
            request.session.create()
        if 'type' not in request.GET:
            return JsonResponse({"error": "missing reaction type"})
        reaction_type = request.GET['type']
        reaction_schema = get_reaction_type_schema(request.session.session_key, reaction_type)
        return JsonResponse(reaction_schema)


class ModelOptionsView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("fetching model options for: " + request.session.session_key)
        model_options = get_model_options(request.session.session_key)
        return JsonResponse(model_options)
       
    def post(self, request):
        logging.info("****** POST request received MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("saving model options for user: "
                      + request.session.session_key)
        newOptions = json.loads(request.body)
        options = {}
        for key in newOptions:
            options.update({key: newOptions[key]})
        user = get_user(request.session.session_key)
        # dump options into options.json
        user.config_files['/options.json'] = options
        user.save()
        
        logging.info('box model options updated')
        options = get_model_options(request.session.session_key)
        export_to_database_path(request.session.session_key) # equivalent of export_to_path()
        return JsonResponse(options)


class InitialConditionsFiles(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received INITIAL CONDITIONS FILE ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching conditions files for session id: " +
              request.session.session_key)
        conditions_files = get_initial_conditions_files(request.session.session_key)
        return JsonResponse(conditions_files)


class ConditionsSpeciesList(views.APIView):
    def get(self, request):
        logging.info("****** GET request received INITIAL SPECIES LIST ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("fetching species list for session id: " +
              request.session.session_key)
        
        species = {"species": get_condition_species(request.session.session_key)}
        logging.info("returning species [csl]:" + str(species))
        return JsonResponse(species)


class InitialConditionsSetup(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching initial conditions setup for session id: " +
              request.session.session_key)
        data = get_user(request.session.session_key).config_files['/initials.json']
        return JsonResponse(data)
       

    def post(self, request):
        logging.info(
            "****** POST request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("saving initial conditions setup for session id: " +
                      request.session.session_key)
        logging.debug("received initial conditions setup: " +
                      str(request.body))
        newData = json.loads(request.body)
        user = get_user(request.session.session_key)
        user.config_files['/initials.json'] = newData
        user.save()
        return JsonResponse({})


class InitialSpeciesConcentrations(views.APIView):
    def get(self, request):

        logging.info("****** GET request received INIT_SPECIES_CONC ******")
        if not request.session.session_key:
            request.session.create()
        values = get_initial_species_concentrations(request.session.session_key)
        return JsonResponse(values)

    def post(self, request):
        logging.info(
            "****** POST request received INITIAL SPECIES CONC. ******")
        if not request.session.session_key:
            request.session.create()
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
        user = get_user(request.session.session_key)
        user.config_files['/species.json'] = file_data
        user.save()
        # run export
        export_to_database_path(request.session.session_key)
        return JsonResponse({})


class InitialReactionRates(views.APIView):
    def get(self, request):
        logging.info(
            "****** GET request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching initial species conc. for session id: " +
                      request.session.session_key)
        initial_rates = {}
        initial_rates = convert_initial_conditions_file(request.session.session_key, ',')
        return JsonResponse(initial_rates)

    def post(self, request):
        logging.info(
            "****** POST request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("received options:" + str(request.body))
        initial_values = json.loads(request.body)

        initial_reaction_rates_file_path = '/initial_reaction_rates.csv'
        convert_initial_conditions_dict(request.session.session_key, initial_values, initial_reaction_rates_file_path, ',')
        export_to_database_path(request.session.session_key)
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
            request.session.create()
        initial = request.GET['initialUnit']
        final = request.GET['finalUnit']
        arguments = get_required_arguments(initial, final)
        f = make_additional_argument_form(arguments)
        return f


class UnitOptions(views.APIView):
    def get(self, request):
        unit_type = request.GET['unitType']
        response = make_unit_convert_form(unit_type)
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
            request.session.create()

        logging.debug("* fetching species list for session id: " +
                      request.session.session_key)
        reactions = {}
        reactions = {"reactions": get_reaction_musica_names(request.session.session_key)}
        return JsonResponse(reactions)
            


class EvolvingConditions(views.APIView):
    def get(self, request):
        logging.info("****** GET request received EVOLVING CONDITIONS ******")
        if not request.session.session_key:
            request.session.create()
        config = get_user(request.session.session_key).config_files['/my_config.json']

        e = config['evolving conditions']
        evolving_conditions_list = e.keys()

        # contains a dictionary w/ key as filename and value as header of file
        file_header_dict = {}
        for i in evolving_conditions_list:
            if '.csv' in i or '.txt' in i:
                logging.info("adding file: " + i)
                read_obj = get_user(request.session.session_key).binary_files['/'+i]
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
            request.session.create()
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
            request.session.create()
        logging.debug(f"session key: {request.session.session_key}")
        response_message = get_run_status(request.session.session_key)
        logging.info(f"status: {response_message}")
        return JsonResponse(response_message)

class CheckView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received RUN_STATUS_VIEW ******")
        logging.info(request)
        if not request.session.session_key:
            request.session.create()
        logging.debug(f"session key: {request.session.session_key}")
        response_message = get_run_status(request.session.session_key)
        print("status: ", response_message)
        return JsonResponse(response_message)


class RunView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        # check if model is already running
        if get_run_status(request.session.session_key) == 'running':
            return JsonResponse({'status': 'running'})
        else:
            # start model run by adding job to queue via pika
            # get ModelRun object and set status to true
            set_is_running(request.session.session_key, True)

            # disable pika logging because it's annoying
            logging.getLogger("pika").propagate = False
            isRabbitUp = check_for_rabbit_mq()
            if isRabbitUp:
                # check if we should save checksum
                if get_user(request.session.session_key).should_cache:
                    logging.info("saving checksum")
                    # get checksum and save to session
                    checksum = calculate_checksum(request.session.session_key)
                    logging.info("got checksum for current user config files: " + str(checksum))
                    # try to find user with same checksum and should_cache = True
                    user = get_user_by_checksum(checksum)
                    set_current_checksum(request.session.session_key, checksum)
                    
                    if user:
                        # if found, copy results from that user to current user
                        logging.info("found user with same checksum, copying results")
                        copy_results(user.uid, request.session.session_key)
                        # set is_running to false
                        set_is_running(request.session.session_key, False)
                        # return status of done
                        return JsonResponse({'status': 'done',
                                             'session_id': request.session.session_key,
                                             'running': False})
                # check to make sure we have a model to run by
                # checking if config and binary files exist
                if get_user(request.session.session_key).config_files is not {} and get_user(request.session.session_key).binary_files is not {}:
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
                    body.update({"config_files": get_user(request.session.session_key).config_files})
                    # put all binary files in body
                    body.update({"binary_files": get_user(request.session.session_key).binary_files})
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


class GetPlotContents(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_PLOT_CONTENTS ******")
        if not request.session.session_key:
            request.session.create()
        get = request.GET
        prop = get['type']
        # csv_results_path = os.path.join(
            # os.environ['MUSIC_BOX_BUILD_DIR'],
            # request.session.session_key+"/output.csv")
        # logging.debug("searching for file: "+csv_results_path)
        response = HttpResponse()
        response.write(plots_unit_select(prop))
        # get model run from session
        model_run = get_model_run(request.session.session_key)

        if '/output.csv' not in model_run.results:
            return response
        # get /output.csv file from model run
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        output_csv = StringIO(model.results['/output.csv'])
        csv = pd.read_csv(output_csv, encoding='latin1')
        subs = direct_sub_props(prop, csv)
        subs.sort()
        if prop != 'compare':
            for i in subs:
                prop = beautifyReaction(sub_props_names(i))
                response.write('<a href="#" class="sub_p list-group-item \
                                list-group-item-action" subType="normal" id="'
                               + i + '">☐ ' + prop + "</a>")
        elif prop == 'compare':
            for i in subs:
                prop = beautifyReaction(sub_props_names(i))
                response.write('<a href="#" class="sub_p list-group-item \
                                list-group-item-action" subType="compare" id="'
                               + i + '">☐ ' + prop + "</a>")
        return response


class GetPlot(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_PLOT ******")
        model_run = get_model_run(request.session.session_key)
        if '/output.csv' not in model_run.results:
            return HttpResponseBadRequest('Bad format for plot request',
                                      status=405)
        if request.method == 'GET':
            props = request.GET['type']
            # logging.debug("grabbing props: "+str(props))
            buffer = io.BytesIO()
            # run get_plot function
            if request.GET['unit'] == 'n/a':
                buffer = get_plot(request.session.session_key, props, False)
            else:
                buffer = get_plot(request.session.session_key, props, request.GET['unit'])
            return HttpResponse(buffer.getvalue(), content_type="image/png")
        return HttpResponseBadRequest('Bad format for plot request',
                                      status=405)


class GetBasicDetails(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_BASIC_DETAILS ******")
        if not request.session.session_key:
            request.session.create()
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        output_csv = StringIO(model.results['/output.csv'])
        csv = pd.read_csv(output_csv, encoding='latin1')
        plot_property_list = [x.split('.')[0] for x in csv.columns.tolist()]
        plot_property_list = [x.strip() for x in plot_property_list]
        for x in csv.columns.tolist():
            if "myrate" in x:
                plot_property_list.append('RATE')
        context = {
            'plots_list': plot_property_list
        }
        logging.info("plots list: " + str(context))
        return JsonResponse(context)


class GetFlowDetails(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_FLOW_DETAILS ******")
        if not request.session.session_key:
            request.session.create()
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        output_csv = StringIO(model.results['/output.csv'])
        csv = pd.read_csv(output_csv, encoding='latin1')
        concs = [x for x in csv.columns if 'CONC' in x]
        species = [x.split('.')[1] for x in concs if 'myrate' not in x]

        step_length = 0
        if csv.shape[0] - 1 > 2:
            step_length = int(csv['time'].iloc[1])
        context = {
            "species": species,
            "stepVal": step_length,
            "simulation_length": int(csv['time'].iloc[-1])
        }
        logging.debug("returning basic info:" + str(context))
        return JsonResponse(context)


class GetFlow(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_FLOW ******")
        if not request.session.session_key:
            request.session.create()
        logging.info(f"session id: {request.session.session_key}")
        logging.info("using data:" + str(request.GET.dict()))
        path_to_template = os.path.join(
            settings.BASE_DIR,
            "dashboard/templates/network_plot/flow_plot.html")
        flow = generate_flow_diagram(request.GET.dict(), request.session.session_key, path_to_template)
        return HttpResponse(flow)


class DownloadConfig(views.APIView):
    def get(self, request):
        logging.info("****** GET request received DOWNLOAD_CONFIG ******")
        if not request.session.session_key:
            request.session.create()
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
        config_files = get_config_files(sessid)
        # temporarily copy config files to static folder
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)
        for file in config_files:
            config_file_string = config_files[file]
            with open(conf_path + file, "w") as f:
                f.write(json.dumps(config_file_string))
        # now do the same for binary files
        binary_files = models.User.objects.get(
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
            request.session.create()
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
            request.session.create()
        logging.debug("session key: " + request.session.session_key)
        uploaded = request.FILES['file']
        configs_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        handle_uploaded_zip_config(
            uploaded, "dashboard/static/zip/" + request.session.session_key,
            configs_path)
        export_to_path(configs_path+"/")
        # now copy files from export_to_path into database and delete from file system 
        user = models.User.objects.get(uid=request.session.session_key)
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
            request.session.create()
        logging.debug("session key: " + request.session.session_key)
        configs_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        remove_request = json.loads(request.body)
        logging.debug("removing file:" + str(remove_request))

        # remove 'file name' from user.binary_files
        user = models.User.objects.get(uid=request.session.session_key)
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
            request.session.create()
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
        user = models.User.objects.get(uid=request.session.session_key)
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
            request.session.create()
        logging.debug("session key: " + request.session.session_key)
        conf_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        logging.debug("clearing evolution files:" + conf_path)
        # clear_e_files(conf_path)
        # clear files from database
        user = models.User.objects.get(uid=request.session.session_key)
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
            request.session.create()
        logging.debug("session key: " + request.session.session_key)
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        conf_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        logging.debug("uploading file: " + filename)
        # manage_uploaded_evolving_conditions_files(
            # uploaded, filename, conf_path)
        # save file to database
        user = models.User.objects.get(uid=request.session.session_key)
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
            request.session.create()
        logging.info("saving model options for user: " +
                     request.session.session_key)
        uploaded = request.FILES['file']


# checks server by trying to connect
def check_for_rabbit_mq():
    """
    Checks if RabbitMQ server is running.
    """
    try:
        RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
        RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
        RABBIT_USER = os.environ["RABBIT_MQ_USER"]
        RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
        connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
        connection = pika.BlockingConnection(connParam)
        if connection.is_open:
            connection.close()
            return True
        else:
            connection.close()
            return False
    except pika.exceptions.AMQPConnectionError:
        return False
