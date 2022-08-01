import re
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
from .models import Document
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
from model_driver.session_model_runner import *
from dashboard.flow_diagram import *
import logging

# api.py contains all DJANGO based backend requests made to the server
# each browser session creates a "session_key" saved to cookie on client
#       - request.session.session_key is a string representation of this value
#       - request.session.session_key is used to access documents from DJANGO

logging.basicConfig(filename='logs.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s', level=logging.DEBUG)
logging.basicConfig(filename='errors.log', filemode='w', format='%(asctime)s - [ERROR!!] %(message)s', level=logging.ERROR)

def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '__' in reaction:
        reaction = reaction.replace('__', ' (')
        reaction = reaction+")"
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction


class ExampleView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        # set example conditions and species/reactions
        example_name = 'example_' + str(request.GET.dict()['example'])
        examples_path = os.path.join(
            settings.BASE_DIR, 'dashboard/static/examples')
        example_folder_path = os.path.join(examples_path, example_name)

        logging.debug("loading example for user " + request.session.session_key+" *")
        logging.debug("|_ loading example #" + str(request.GET.dict()['example']))
        logging.info("|_ example folder path: " + example_folder_path)

        if not os.path.isdir(os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)):
            os.makedirs(os.path.join(settings.BASE_DIR,
                        'configs/' + request.session.session_key))
        # path to save data for user
        config_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        logging.debug("|_ putting data into path: " + config_path)

        shutil.rmtree(config_path)
        shutil.copytree(example_folder_path, config_path)
        export_to_user_config_files(config_path)

        menu_names = api_species_menu_names(
            config_path + "/camp_data/species.json")
        logging.info("|_ pushing menu names to user: " + str(menu_names))
        response = Response(menu_names, status=status.HTTP_200_OK)
        return response


class SpeciesView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SPECIES_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("fetching species for session: " + request.session.session_key)
        if not os.path.isdir(os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            # path to save data for user
            conf = ('configs/'+request.session.session_key
                    + "/camp_data/species.json")
            configz_path = os.path.join(
                settings.BASE_DIR, conf)
            menu_names = api_species_menu_names(configz_path)
            logging.info("|_ pushing menu names to user:" + str(menu_names))
            response = Response(menu_names, status=status.HTTP_200_OK)
            return response


class SpeciesDetailView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SPECIES_DETAIL ******")
        if not request.session.session_key:
            request.session.create()
        if 'name' not in request.GET:
            return JsonResponse({"error": "missing species name"})
        if not os.path.isdir(os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/species.json")
            # path to save data for user
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            for entry in species_info(config_path):
                if (entry['type'] == 'CHEM_SPEC' and
                        entry['name'] == request.GET['name']):
                    species_convert_to_SI(entry)
                    return JsonResponse(entry)
        return JsonResponse({})


class RemoveSpeciesView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received REMOVE_SPECIES ******")
        if not request.session.session_key:
            request.session.create()
        if 'name' not in request.GET:
            return HttpResponseBadRequest("missing species name")

        # check for config dir
        if not os.path.isdir(os.path.join(settings.BASE_DIR,
                             'configs/'+request.session.session_key)):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/species.json")
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            species_remove(request.GET['name'], config_path)
            reac = ('configs/' + request.session.session_key
                    + "/camp_data/reactions.json")
            reac_path = os.path.join(settings.BASE_DIR, reac)
            my_conf = ('configs/' + request.session.session_key
                    + "/my_config.json")
            my_path = os.path.join(settings.BASE_DIR, my_conf)
            remove_reactions_with_species(request.GET['name'], reac_path,
                                          my_path)
            return HttpResponse('')


class AddSpeciesView(views.APIView):
    def post(self, request):
        logging.info("****** POST request received ADD_SPECIES ******")
        species_data = json.loads(request.body)
        if 'name' not in species_data:
            return JsonResponse({"error": "missing species name"})
        species_data['type'] = "CHEM_SPEC"
        direc = os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/species.json")
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            species_remove(species_data['name'], config_path)
            species_save(species_data, config_path)
            return JsonResponse({})


class PlotSpeciesView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        if 'name' not in request.GET:
            return HttpResponseBadRequest("missing species name")
        species = request.GET['name']
        # check for config dir
        direc = os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            logging.debug("loading plot info for species: " + str(species))
            config_path = os.path.join(
                settings.BASE_DIR,
                'configs/' + request.session.session_key +
                "/camp_data/reactions.json")
            network_plot_dir = os.path.join(
                settings.BASE_DIR, "dashboard/templates/network_plot/" +
                request.session.session_key)
            template_plot = os.path.join(
                settings.BASE_DIR,
                "dashboard/templates/network_plot/plot.html")
            if not os.path.isdir(network_plot_dir):
                logging.debug("making dir:" + str(network_plot_dir))
                os.makedirs(network_plot_dir)
            # use copyfile()
            if exists(os.path.join(network_plot_dir, "plot.html")) is False:
                # create plot.html file if doesn't exist
                f = open(os.path.join(network_plot_dir, "plot.html"), "w")
            shutil.copyfile(template_plot, network_plot_dir + "/plot.html")
            # generate network plot and place it in unique directory for user
            generate_network_plot(
                species, network_plot_dir + "/plot.html", config_path)
            plot = ('network_plot/'
                    + request.session.session_key
                    + '/plot.html')
            return render(request, plot)


class ReactionsView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received REACTIONS_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("fetching reactions for session id: " +
              request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            # path to save data for user
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/reactions.json")
            config_path = os.path.join(settings.BASE_DIR, conf)
            menu_names = reaction_menu_names(config_path)
            logging.debug("|_ pushing menu names to user:" + str(menu_names))
            response = Response(menu_names, status=status.HTTP_200_OK)
            return response


class ReactionsDetailView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        logging.info("fetching reactions for session id: " +
            request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/'+request.session.session_key)
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            # path to save data for user
            if 'index' not in request.GET:
                return JsonResponse({"error": "missing reaction index"})
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/reactions.json")
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            reaction_detail = reactions_info(
                config_path)[int(request.GET['index'])]
            reaction_detail['index'] = int(request.GET['index'])
            return JsonResponse(reaction_detail)


class RemoveReactionView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received REMOVE_REACTION ******")
        if not request.session.session_key:
            request.session.create()
        if 'index' not in request.GET:
            return HttpResponseBadRequest("missing reaction index")
        direc = os.path.join(settings.BASE_DIR,
                             'configs/'+request.session.session_key)
        # check for config dir
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/reactions.json")
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            reaction_remove(int(request.GET['index']), config_path)
            return HttpResponse('')


class SaveReactionView(views.APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.create()

        reaction_data = json.loads(request.body)
        conf = ('configs/' + request.session.session_key
                + "/camp_data/reactions.json")
        config_path = os.path.join(
            settings.BASE_DIR, conf)
        reaction_save(reaction_data, config_path)
        return JsonResponse({})


class ReactionTypeSchemaView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received SCHEMATYPEVIEW ******")
        if not request.session.session_key:
            request.session.create()
        if 'type' not in request.GET:
            return JsonResponse({"error": "missing reaction type"})
        direc = os.path.join(settings.BASE_DIR,
                             'configs/'+request.session.session_key)
        # check for config dir
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/reactions.json")
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            schema = reaction_type_schema(request.GET['type'], config_path)
            return JsonResponse(schema)


class ModelOptionsView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("fetching model options for: " + request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)
        # check for config dir
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            config_path = os.path.join(
                settings.BASE_DIR, 'configs/' + request.session.session_key)
            options = option_setup(config_path)
            logging.info("returning options:" + str(options))
            return JsonResponse(options)

    def post(self, request):
        logging.info("****** POST request received MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("saving model options for user: " + request.session.session_key)
        print("received options: ",request.body)
        newOptions = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/' +
                            request.session.session_key)+"/options.json"
        logging.debug("saving to path: "+str(path))
        options = {}
        for key in newOptions:
            options.update({key: newOptions[key]})
        with open(path, 'w') as f:
            json.dump(options, f, indent=4)
        logging.info('box model options updated')
        config_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        options = option_setup(config_path)
        logging.info("returning options:" + str(options))
        export_to_path(os.path.join(settings.BASE_DIR,
                       'configs/' + request.session.session_key) + "/")
        return JsonResponse(options)


class InitialConditionsFiles(views.APIView):
    def get(self, request):
        logging.info("****** GET request received INITIAL CONDITIONS FILE ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching conditions files for session id: " +
              request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)
        if not os.path.isfile(direc):
            logging.error("detected no data from this user")
            return JsonResponse({})
        else:
            conf = ('configs/' + request.session.session_key
                    + "/my_config.json")
            config_path = os.path.join(
                settings.BASE_DIR, conf)
            values = initial_conditions_files(config_path)
            logging.info("returning values [icf]:" + str(values))
            return JsonResponse(values)


class ConditionsSpeciesList(views.APIView):
    def get(self, request):
        logging.info("****** GET request received INITIAL SPECIES LIST ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("fetching species list for session id: " +
              request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/' + request.session.session_key)
        if not os.path.isdir(direc):
            logging.error("detected no data from this user")
            return JsonResponse({})
        else:
            conf = ('configs/' + request.session.session_key
                    + "/camp_data/species.json")
            conf = os.path.join(
                settings.BASE_DIR, conf)
            logging.debug("fetching species list:" + str(conf))
            species = {"species": conditions_species_list(conf)}
            logging.info("returning species [csl]:" + str(species))
            return JsonResponse(species)


class InitialConditionsSetup(views.APIView):
    def get(self, request):
        logging.info("****** GET request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching initial conditions setup for session id: " +
              request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/'
                             + request.session.session_key
                             + "/initials.json")
        if not os.path.isfile(direc):
            logging.error("detected no data from this user")
            return JsonResponse({})
        else:
            data = ""
            with open(direc) as f:
                data = json.loads(f.read())
            logging.info("returning initial conditions setup:" + str(data))
            return JsonResponse(data)

    def post(self, request):
        logging.info("****** POST request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("saving initial conditions setup for session id: " +
              request.session.session_key)
        logging.debug("received initial conditions setup: " + str(request.body))
        newData = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR,
                            'configs/'
                            + request.session.session_key
                            + "/initials.json")
        logging.debug("saving to path: " + path)
        with open(path, 'w') as f:
            json.dump(newData, f, indent=4)
        logging.info('initial conditions setup updated')
        return JsonResponse({})


class InitialSpeciesConcentrations(views.APIView):
    def get(self, request):

        logging.info("****** GET request received INIT_SPECIES_CONC ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching initial species conc. for session id: " +
              request.session.session_key)
        direc = os.path.join(settings.BASE_DIR,
                             'configs/'
                             + request.session.session_key
                             + "/species.json")
        if not os.path.isfile(direc):
            logging.error("detected no data from this user")
            return JsonResponse({})
        else:

            path = os.path.join(settings.BASE_DIR, 'configs/' +
                                request.session.session_key + "/species.json")
            logging.debug("getting initial species concentrations:" + path)
            values = initial_species_concentrations(path)
            logging.info("returning species [isc]:" + str(values))
            return JsonResponse(values)

    def post(self, request):
        logging.info("****** POST request received INITIAL SPECIES CONC. ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("received options:" + str(request.body))
        initial_values = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/' +
                            request.session.session_key + "/species.json")
        logging.debug("saving to path: "+path)
        if not os.path.isfile(path):
            logging.error("* detected no species this user")
            return Response(status=status.HTTP_200_OK)
        else:
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
            with open(path, 'w') as f:
                json.dump(file_data, f, indent=4)
            # run export next?
            export_to_path(os.path.join(settings.BASE_DIR,
                           'configs/' + request.session.session_key) + "/")
            return JsonResponse({})


class InitialReactionRates(views.APIView):
    def get(self, request):
        logging.info("****** GET request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("fetching initial species conc. for session id: " +
              request.session.session_key)
        initial_rates = {}
        path = os.path.join(settings.BASE_DIR, 'configs/' +
                            request.session.session_key
                            + "/initial_reaction_rates.csv")
        if not os.path.isfile(path):
            logging.error("detected no data from this user")
            return JsonResponse({})
        else:
            initial_reaction_rates_file_path = path
            with open(initial_reaction_rates_file_path, 'r') as f:
                initial_rates = initial_conditions_file_to_dictionary(f, ',')
            logging.info("returning rates [irr]:" + initial_rates)
            return JsonResponse(initial_rates)

    def post(self, request):
        logging.info("****** POST request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("received options:" + str(request.body))
        initial_values = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/' +
                            request.session.session_key
                            + "/initial_reaction_rates.csv")
        logging.debug("saving to path: " + path)

        logging.debug("pushing new options:" + str(initial_values))
        config_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key
            + "/camp_data/reactions.json")
        initial_reaction_rates_file_path = path
        with open(initial_reaction_rates_file_path, 'w+') as f:
            dictionary_to_initial_conditions_file(
                initial_values, f, ',', config_path)
        logging.info("done pushing new options")
        export_to_path(os.path.join(settings.BASE_DIR,
                       'configs/' + request.session.session_key) + "/")
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
        logging.info("****** GET request received UNIT CONVERSION ARGUMENTS ******")
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
        logging.info("****** GET request received MUSICA REACTIONS LIST ******")
        if not request.session.session_key:
            request.session.create()

        logging.debug("* fetching species list for session id: " +
              request.session.session_key)
        reactions = {}
        path = os.path.join(settings.BASE_DIR, 'configs/'
                            + request.session.session_key)
        if not os.path.isdir(path):
            logging.error("detected no data from this user")
            return JsonResponse({})
        else:
            reactions = {"reactions": reaction_musica_names(os.path.join(
                settings.BASE_DIR, 'configs/' + request.session.session_key)
                + "/camp_data/reactions.json")}
            logging.info("returning reactions [mrl]:" + str(reactions))
            return JsonResponse(reactions)


class EvolvingConditions(views.APIView):
    def get(self, request):
        logging.info("****** GET request received EVOLVING CONDITIONS ******")
        if not request.session.session_key:
            request.session.create()
        config_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key
            + "/my_config.json")
        logging.debug("config path: " + config_path)
        with open(config_path) as f:
            config = json.loads(f.read())

        e = config['evolving conditions']
        evolving_conditions_list = e.keys()

        # contains a dictionary w/ key as filename and value as header of file
        file_header_dict = {}
        for i in evolving_conditions_list:
            if '.csv' in i or '.txt' in i:
                logging.info("adding file: " + i)
                path = os.path.join(os.path.join(
                    settings.BASE_DIR, 'configs/'
                    + request.session.session_key), i)
                with open(path, 'r') as read_obj:
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
        if not request.session.session_key:
            request.session.create()
        runner = SessionModelRunner(request.session.session_key)
        return runner.check_load(request)


class CheckView(views.APIView):
    def get(self, request):
        logging.info("****** GET request received RUN_STATUS_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        runner = SessionModelRunner(request.session.session_key)
        return runner.check(request)


class RunView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        logging.info("****** Running simulation for user session: " + request.session.session_key + "******")
        runner = SessionModelRunner(request.session.session_key)

        return runner.run(request)


class GetPlotContents(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_PLOT_CONTENTS ******")
        if not request.session.session_key:
            request.session.create()
        get = request.GET
        prop = get['type']
        csv_results_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            request.session.session_key+"/output.csv")
        logging.debug("searching for file: "+csv_results_path)
        response = HttpResponse()
        response.write(plots_unit_select(prop))
        subs = sub_props(prop, csv_results_path)
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
        sessid = request.GET.get('sess_id')
        logging.info("sessid: "+sessid)
        csv_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            sessid+"/output.csv")
        logging.debug("csv path: "+csv_path)
        if request.method == 'GET':
            props = request.GET['type']
            logging.debug("grabbing props: "+str(props))
            buffer = io.BytesIO()
            species_p = (os.path.join(
                    settings.BASE_DIR,
                    'configs/' + sessid)
                    + "/camp_data/species.json")
            if request.GET['unit'] == 'n/a':
                buffer = output_plot(str(props), False, csv_path, species_p)
            else:
                buffer = output_plot(str(props), request.GET['unit'],
                                     csv_path, species_p)
            return HttpResponse(buffer.getvalue(), content_type="image/png")
        return HttpResponseBadRequest('Bad format for plot request',
                                      status=405)


class GetBasicDetails(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_BASIC_DETAILS ******")
        if not request.session.session_key:
            request.session.create()
        csv_results_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            request.session.session_key + "/output.csv")
        logging.debug("fetching details from: " + csv_results_path)
        csv = pandas.read_csv(csv_results_path)
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
        csv_results_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            request.session.session_key + "/output.csv")
        context = {
            "species": get_species(csv_results_path),
            "stepVal": get_step_length(csv_results_path),
            "simulation_length": get_simulation_length(csv_results_path)
        }
        logging.debug("returning basic info:" + str(context))
        return JsonResponse(context)


class GetFlow(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_FLOW ******")
        if not request.session.session_key:
            request.session.create()
        csv_results_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            request.session.session_key + "/output.csv")
        logging.debug("fetching flow from: " + csv_results_path)
        logging.debug("using data:" + str(request.GET.dict()))
        csv_results_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            request.session.session_key + "/output.csv")
        react_path = (os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
            + "/camp_data/reactions.json")
        path_to_template = os.path.join(
            settings.BASE_DIR,
            "dashboard/templates/network_plot/flow_plot.html")
        flow = create_and_return_flow_diagram(request.GET.dict(),
                                              react_path, path_to_template,
                                              csv_results_path)
        return HttpResponse(flow)


class DownloadConfig(views.APIView):
    def get(self, request):
        logging.info("****** GET request received DOWNLOAD_CONFIG ******")
        sessid = request.GET.get('sess_id')
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
        create_config_zip(destination_path, zip_path, conf_path)
        fl_path = zip_path
        zip_file = open(fl_path, 'rb')
        response = HttpResponse(zip_file, content_type='application/zip')
        attach_string = 'attachment; filename="%s"' % 'config.zip'
        response['Content-Disposition'] = attach_string
        return response


class DownloadResults(views.APIView):
    def get(self, request):
        logging.info("****** GET request received DOWNLOAD_RESULTS ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("session key: " + request.session.session_key)
        fl_path = os.path.join(
            os.environ['MUSIC_BOX_BUILD_DIR'],
            request.session.session_key + "/output.csv")
        now = datetime.now()
        filename = str(now) + '_model_output.csv'
        fl = open(fl_path, 'r')
        mime_type, _ = mimetypes.guess_type(fl_path)
        if os.path.exists(fl_path):
            with open(fl_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=mime_type)
                attach_string = 'inline; filename=' + filename
                response['Content-Disposition'] = attach_string
                return response
        raise Http404


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
        return JsonResponse({})


class RemoveInitialConditionsFile(views.APIView):
    def post(self, request):
        logging.info("****** GET request received REMOVE_INIT_COND_FILE ******")
        if not request.session.session_key:
            request.session.create()
        logging.debug("session key: " + request.session.session_key)
        configs_path = os.path.join(
            settings.BASE_DIR, 'configs/' + request.session.session_key)
        remove_request = json.loads(request.body)
        logging.debug("removing file:" + str(remove_request))
        initial_conditions_file_remove(remove_request, configs_path)
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
        manage_initial_conditions_files(uploaded, filename, conf_path)
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
        clear_e_files(conf_path)
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
        manage_uploaded_evolving_conditions_files(
            uploaded, filename, conf_path)
        logging.info("uploaded evolving file: " + filename)
        return JsonResponse({})


class LoadFromConfigJsonView(views.APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        logging.info("saving model options for user: "+request.session.session_key)
        uploaded = request.FILES['file']
# checks server by trying to connect to default port
def checkForRabbitMQServer():
    """
    Checks if RabbitMQ server is running.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 5672))
        s.close()
        return True
    except socket.error:
        return False