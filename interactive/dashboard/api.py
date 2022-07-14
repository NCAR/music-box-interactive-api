# from types import NoneType
import re
from django.shortcuts import render
from .forms.optionsforms import *
from .forms.report_bug_form import BugForm
from .forms.evolvingforms import *
from .forms.initial_condforms import *
from .flow_diagram import generate_flow_diagram, get_simulation_length, get_species
from .upload_handler import *
from .build_unit_converter import *
from .save import *
from .models import Document
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
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

# api.py contains all DJANGO based backend requests made to the server
# each browser session creates a "session_key" saved to cookie on client
#       - request.session.session_key is a string representation of this value
#       - request.session.session_key is used to access documents from DJANGO


def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '__' in reaction:
        reaction = reaction.replace('__', ' (')
        reaction = reaction+")"
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction

class TestAPIView(views.APIView):
    def get(self, request):
        return Response({"message": "This is a test API view"})
class ExampleView(views.APIView):
    def get(self, request):
        session_key = ""
        try:
            request.COOKIES['sessionid']
        except KeyError:
            print("no cookie found client side")
        if not request.session.session_key or session_key == "":
            request.session.create()
        #set example conditions and species/reactions
        example_name = 'example_' + str(request.GET.dict()['example'])
        examples_path = os.path.join(settings.BASE_DIR, 'dashboard/static/examples')
        example_folder_path = os.path.join(examples_path, example_name)

        print("* loading example for user "+request.session.session_key+" *")
        print("|_ loading example #"+str(request.GET.dict()['example']))
        print("|_ example folder path:",example_folder_path)

        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            os.makedirs(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key))
        # path to save data for user
        config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        print("|_ putting data into path:",config_path)

        shutil.rmtree(config_path)
        shutil.copytree(example_folder_path, config_path)
        export_to_user_config_files(config_path)

        menu_names = api_species_menu_names(config_path+"/camp_data/species.json")
        print("|_ pushing menu names to user:",menu_names)
        response = Response(menu_names, status=status.HTTP_200_OK)
        return response
class SpeciesView(views.APIView):
    def get(self, request):
        print("****** GET request received SPECIES_VIEW ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        print("fetching species for session id: " + request.session.session_key)
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
             # path to save data for user
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/species.json")
            menu_names = api_species_menu_names(config_path)
            print("|_ pushing menu names to user:",menu_names)
            response = Response(menu_names, status=status.HTTP_200_OK)
            return response
class SpeciesDetailView(views.APIView):
    def get(self, request):
        print("****** GET request received SPECIES_DETAIL ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        if not 'name' in request.GET:
            return JsonResponse({"error":"missing species name"})
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
             # path to save data for user
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/species.json")
            for entry in species_info(config_path):
                if entry['type'] == 'CHEM_SPEC' and entry['name'] == request.GET['name']:
                    species_convert_to_SI(entry)
                    return JsonResponse(entry)
        return JsonResponse({})
class RemoveSpeciesView(views.APIView):
    def get(self, request):
        print("****** GET request received REMOVE_SPECIES ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        if not 'name' in request.GET:
            return HttpResponseBadRequest("missing species name")
        
        #check for config dir
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/species.json")
            species_remove(request.GET['name'], config_path)
            return HttpResponse('')
class AddSpeciesView(views.APIView):
    def post(self, request):
        print("****** POST request received ADD_SPECIES ******")
        species_data = json.loads(request.body)
        if not 'name' in species_data:
            return JsonResponse({"error":"missing species name"})
        species_data['type'] = "CHEM_SPEC"
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/species.json")
            species_remove(species_data['name'], config_path)
            species_save(species_data, config_path)
            return JsonResponse({})
class PlotSpeciesView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        if not 'name' in request.GET:
            return HttpResponseBadRequest("missing species name")
        species = request.GET['name']
         #check for config dir
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            print("* loading plot info for species: "+species)
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
            network_plot_dir = os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/"+request.session.session_key)
            template_plot = os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/plot.html")
            if not os.path.isdir(network_plot_dir):
                print("* directory doesnt exist, making:"+network_plot_dir)
                os.makedirs(network_plot_dir)
            # use copyfile()
            if exists(os.path.join(network_plot_dir, "plot.html")) == False:
                #create plot.html file if doesn't exist
                print("* "+str(os.path.join(network_plot_dir, "plot.html"))+" does not exist, creating file")
                f = open(os.path.join(network_plot_dir, "plot.html"), "w")
            shutil.copyfile(template_plot,network_plot_dir+"/plot.html")
            # generate network plot and place it in unique directory for user
            generate_network_plot(species, network_plot_dir+"/plot.html", config_path)
            return render(request, 'network_plot/'+request.session.session_key+'/plot.html')
class ReactionsView(views.APIView):
     def get(self, request):
        print("****** GET request received REACTIONS_VIEW ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        print("fetching reactions for session id: " + request.session.session_key)
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
             # path to save data for user
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
            menu_names = reaction_menu_names(config_path)
            print("|_ pushing menu names to user:",menu_names)
            response = Response(menu_names, status=status.HTTP_200_OK)
            return response
class ReactionsDetailView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        print("fetching reactions for session id: " + request.session.session_key)
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
             # path to save data for user
            if not 'index' in request.GET:
                return JsonResponse({"error":"missing reaction index"})
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
            reaction_detail = reactions_info(config_path)[int(request.GET['index'])]
            reaction_detail['index'] = int(request.GET['index'])
            return JsonResponse(reaction_detail)
class RemoveReactionView(views.APIView):
    def get(self, request):
        print("****** GET request received REMOVE_REACTION ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        if not 'index' in request.GET:
            return HttpResponseBadRequest("missing reaction index")
        
        #check for config dir
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
            reaction_remove(int(request.GET['index']), config_path)
            return HttpResponse('')
class SaveReactionView(views.APIView):
    def get(self, request):
        print("****** GET request received ADD_REACTION ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        return JsonResponse({"error":"saving a reaction should be a POST request"})
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        
        reaction_data = json.loads(request.body)
        config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
        reaction_save(reaction_data,config_path)
        return JsonResponse({})

class ReactionTypeSchemaView(views.APIView):
    def get(self, request):
        print("****** GET request received SCHEMATYPEVIEW ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        if not 'type' in request.GET:
            return JsonResponse({"error":"missing reaction type"})
        
        #check for config dir
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
            schema = reaction_type_schema(request.GET['type'], config_path)
            return JsonResponse(schema)



class ModelOptionsView(views.APIView):
    def get(self, request):
        print("****** GET request received GET_MODEL_VIEW ******")
        # print("current cookie:" + request.COOKIES['sessionid'])
        if not request.session.session_key:
            request.session.create()
        print("* fetching model options for user: "+request.session.session_key)
         #check for config dir
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return Response(status=status.HTTP_200_OK)
        else:
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
            options = option_setup(config_path)
            print("* returning options:", options)
            return  JsonResponse(options)
    def post(self, request):
        print("****** POST request received MODEL_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        print("* saving model options for user: "+request.session.session_key)
        print("* received options:", request.body)
        newOptions = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/options.json"
        print("* saving to path: "+path)
        options = {}
        for key in newOptions:
            options.update({key: newOptions[key]})
        with open(path, 'w') as f:
            json.dump(options, f, indent=4)
        print('box model options updated')
        config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        options = option_setup(config_path)
        print("* returning options:", options)
        return  JsonResponse(options)

class InitialConditionsFiles(views.APIView):
    def get(self, request):
        print("****** GET request received INITIAL CONDITIONS FILE ******")
        if not request.session.session_key:
            request.session.create()
        
        print("* fetching conditions files for session id: " + request.session.session_key)
        if not os.path.isfile(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/my_config.json")):
            print("* detected no data from this user")
            return JsonResponse({})
        else:
            config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/my_config.json")
            values = initial_conditions_files(config_path)
            print("* returning values [icf]:", values)
            return JsonResponse(values)
class ConditionsSpeciesList(views.APIView):
    def get(self, request):
        print("****** GET request received INITIAL SPECIES LIST ******")
        if not request.session.session_key:
            request.session.create()
        print("* fetching species list for session id: " + request.session.session_key)
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return JsonResponse({})
        else:
            print("* fetching species list:",os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/camp_data/species.json")
            species = { "species" : conditions_species_list(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/camp_data/species.json") }
            print("* returning species [csl]:", species)
            return JsonResponse(species)
class InitialConditionsSetup(views.APIView):
    def get(self, request):
        print("****** GET request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.create()
        
        print("* fetching initial conditions setup for session id: " + request.session.session_key)
        if not os.path.isfile(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/initials.json")):
            print("* detected no data from this user")
            return JsonResponse({})
        else:
            data = ""
            with open(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/initials.json")) as f:
                data = json.loads(f.read())
            print("* returning initial conditions setup:", data)
            return JsonResponse(data)
    def post(self, request):
        print("****** POST request received INITIAL CONDITIONS SETUP ******")
        if not request.session.session_key:
            request.session.create()
        print("* saving initial conditions setup for session id: " + request.session.session_key)
        print("* received initial conditions setup:", request.body)
        newData = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/initials.json"
        print("* saving to path: "+path)
        with open(path, 'w') as f:
            json.dump(newData, f, indent=4)
        print('initial conditions setup updated')
        return JsonResponse({})
class InitialSpeciesConcentrations(views.APIView):
    def get(self, request):
        
        print("****** GET request received INITIAL SPECIES CONCENTRATIONS ******")
        if not request.session.session_key:
            request.session.create()
        
        print("* fetching initial species conc. for session id: " + request.session.session_key)
        if not os.path.isfile(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/species.json")):
            print("* detected no data from this user")
            return JsonResponse({})
        else:
           
            path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/species.json")
            print("* getting initial species concentrations:",path)
            values = initial_species_concentrations(path)
            print("* returning species [isc]:", values)
            return JsonResponse(values)
    def post(self, request):
        print("****** POST request received INITIAL SPECIES CONCENTRATIONS ******")
        if not request.session.session_key:
            request.session.create()
        print("* received options:", request.body)
        initial_values = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/species.json")
        print("* saving to path: "+path)
        if not os.path.isfile(path):
            print("* detected no species this user")
            return Response(status=status.HTTP_200_OK)
        else:
            print("* pushing new options:", initial_values)
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
            export_to_path(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/")
            return JsonResponse({})
class InitialReactionRates(views.APIView):
    def get(self, request):
        print("****** GET request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.create()
        
        print("* fetching initial species conc. for session id: " + request.session.session_key)
        initial_rates = {}
        path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/initial_reaction_rates.csv")
        if not os.path.isfile(path):
            print("* detected no data from this user")
            return JsonResponse({})
        else:
            initial_reaction_rates_file_path = path
            with open(initial_reaction_rates_file_path, 'r') as f:
                initial_rates = initial_conditions_file_to_dictionary(f, ',')
            print("* returning rates [irr]:", initial_rates)
            return JsonResponse(initial_rates)
    def post(self, request):
        print("****** POST request received INITIAL REACTION RATES ******")
        if not request.session.session_key:
            request.session.create()
        print("* received options:", request.body)
        initial_values = json.loads(request.body)
        path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/initial_reaction_rates.csv")
        print("* saving to path: "+path)
        
        print("* pushing new options:", initial_values)
        config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/camp_data/reactions.json")
        initial_reaction_rates_file_path = path
        with open(initial_reaction_rates_file_path, 'w+') as f:
            dictionary_to_initial_conditions_file(initial_values, f, ',', config_path)
        print("* done pushing new options")
        export_to_path(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/")
        return JsonResponse({})
class ConvertValues(views.APIView):
    def get(self, request):
        unit_type = request.GET['type']
        new_unit = request.GET['new unit']
        initial_value = float(request.GET['value'])
        if any(c in unit_type for c in ('temperature', 'pressure')):
            response = convert_initial_conditions(unit_type, new_unit, initial_value)
        else:
            response = {}
        return JsonResponse(response)
class UnitConversionArguments(views.APIView):
    def get(self, request):
        print("****** GET request received UNIT CONVERSION ARGUMENTS ******")
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
                arg_dict.update({conversion_request[key]: float(conversion_request[key.replace('title', 'value')])})
                arg_dict.update({conversion_request[key] + ' units': conversion_request[key.replace('title', 'unit')]})
        converter = create_unit_converter(conversion_request['initialUnit'], conversion_request['finalUnit'])
        if arg_dict:
            new_value = converter(float(conversion_request['initialValue']), arg_dict)
        else:
            new_value = converter(float(conversion_request['initialValue']))

        return HttpResponse(new_value)
class MusicaReactionsList(views.APIView):
    def get(self, request):
        print("****** GET request received MUSICA REACTIONS LIST ******")
        if not request.session.session_key:
            request.session.create()
        
        print("* fetching species list for session id: " + request.session.session_key)
        reactions = {}
        if not os.path.isdir(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)):
            print("* detected no data from this user")
            return JsonResponse({})
        else:
            reactions = { "reactions" : reaction_musica_names(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/camp_data/reactions.json") }
            print("* returning reactions [mrl]:", reactions)
            return JsonResponse(reactions)
class EvolvingConditions(views.APIView):
    def get(self, request):
        print("****** GET request received EVOLVING CONDITIONS ******")
        if not request.session.session_key:
            request.session.create()
        config_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key+"/my_config.json")
        print("* config path: "+config_path)
        with open(config_path) as f:
            config = json.loads(f.read())

        e = config['evolving conditions']
        evolving_conditions_list = e.keys()

        file_header_dict = {} #contains a dictionary w/ key as filename and value as header of file
        for i in evolving_conditions_list:
            if '.csv' in i or '.txt' in i:
                print("* adding file: "+i)
                path = os.path.join(os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key), i)
                with open(path, 'r') as read_obj:
                    csv_reader = reader(read_obj)
                    list_of_rows = list(csv_reader)

                try:
                    file_header_dict.update({i:list_of_rows[0]})
                except IndexError:
                    file_header_dict.update({i:['EMPTY FILE']})
            elif '.nc' in i:
                file_header_dict.update({i:['NETCDF FILE']})
        return JsonResponse(file_header_dict)
class LinearCombinations(views.APIView):
    def get(self, request):
        print("****** GET request received LINEAR COMBINATIONS ******")
        if not request.session.session_key:
            request.session.create()
        config_path = os.path.join(settings.BASE_DIR,
                                   'configs/'+request.session.session_key+
                                   "/my_config.json")
        print("* config path: "+config_path)
        config = direct_open_json(config_path)
       
        if 'evolving conditions' not in config:
            return []
        else:
            filelist = config['evolving conditions'].keys()

        linear_combo_dict = {}

        for f in filelist:
            if config['evolving conditions'][f]['linear combinations']:
                for key in config['evolving conditions'][f]['linear combinations']:
                    combo = config['evolving conditions'][f]['linear combinations'][key]['properties']
                    c = [key for key in combo]
                    linear_combo_dict.update({f.replace('.','-'): c})
        
        return JsonResponse(linear_combo_dict)
class CheckLoadView(views.APIView):
    def get(self, request):
        print("****** GET request received RUN_STATUS_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        # print("****** Running simulation for user session:",request.session.session_key,"******")
        runner = SessionModelRunner(request.session.session_key)
        return runner.check_load(request)
class CheckView(views.APIView):
    def get(self, request):
        print("****** GET request received RUN_STATUS_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        # print("****** Running simulation for user session:",request.session.session_key,"******")
        runner = SessionModelRunner(request.session.session_key)
        return runner.check(request)
class RunView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
        print("****** Running simulation for user session:",request.session.session_key,"******")
        runner = SessionModelRunner(request.session.session_key)

        return runner.run(request)
class GetPlotContents(views.APIView):
    def get(self, request):
        print("****** GET request received GET_PLOT_CONTENTS ******")
        if not request.session.session_key:
            request.session.create()
        get = request.GET
        prop = get['type']
        csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        print("* searching for file: "+csv_results_path)
        print("* getting contents of: "+prop+", isfile?",os.path.isfile(csv_results_path))
        response = HttpResponse()
        response.write(plots_unit_select(prop))
        subs = sub_props(prop, csv_results_path)
        subs.sort()
        if prop != 'compare':
            for i in subs:
                response.write('<a href="#" class="sub_p list-group-item list-group-item-action" subType="normal" id="' + i + '">☐ ' + beautifyReaction(sub_props_names(i)) + "</a>")
        elif prop == 'compare':
            for i in subs:
                response.write('<a href="#" class="sub_p list-group-item list-group-item-action" subType="compare" id="' + i + '">☐ ' + beautifyReaction(sub_props_names(i)) + "</a>")
        return response
class GetPlot(views.APIView):
    def get(self, request):
        print("****** GET request received GET_PLOT ******")
        if not request.session.session_key:
            request.session.create()
        csv_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        print("* csv path: "+csv_path)
        print("* does csv exist:",os.path.isfile(csv_path))
        if request.method == 'GET':
            props = request.GET['type']
            print("* grabbing props: "+props)
            if request.GET['unit'] == 'n/a':
                buffer = output_plot(str(props), False, csv_path, os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/camp_data/species.json")
            else:
                buffer = output_plot(str(props), request.GET['unit'], csv_path, os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/camp_data/species.json")

            # return HttpResponse(buffer.getvalue(), content_type="image/png")
            return HttpResponse(buffer, content_type="image/png")
        return HttpResponseBadRequest('Bad format for plot request', status=405)
class GetBasicDetails(views.APIView):
    def get(self, request):
        print("****** GET request received GET_BASIC_DETAILS ******")
        if not request.session.session_key:
            request.session.create()
        csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        print("* fetching details from: "+csv_results_path)
        csv = pandas.read_csv(csv_results_path)
        plot_property_list = [x.split('.')[0] for x in csv.columns.tolist()]
        plot_property_list = [x.strip() for x in plot_property_list]
        for x in csv.columns.tolist():
            if "myrate" in x:
                plot_property_list.append('RATE')
        context = {
            'plots_list': plot_property_list
        }
        print("* plots list: ", context)
        return JsonResponse(context)
class GetFlowDetails(views.APIView):
    def get(self, request):
        print("****** GET request received GET_FLOW_DETAILS ******")
        if not request.session.session_key:
            request.session.create()
        csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        context = {
            "species": get_species(csv_results_path),
            "simulation_length": get_simulation_length(csv_results_path)
        }
        print("* returning basic info:", context)
        return JsonResponse(context)
class GetFlow(views.APIView):
    def get(self, request):
        print("****** GET request received GET_FLOW ******")
        if not request.session.session_key:
            request.session.create()
        csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        print("* fetching flow from: "+csv_results_path)
        print("* using data:",request.GET.dict())
        csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        react_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)+"/camp_data/reactions.json"
        path_to_template = os.path.join(
    settings.BASE_DIR, "dashboard/templates/network_plot/flow_plot.html")
        return HttpResponse(create_and_return_flow_diagram(request.GET.dict(), react_path, path_to_template, csv_results_path))
class DownloadConfig(views.APIView):
    def get(self, request):
        print("****** GET request received DOWNLOAD_CONFIG ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        destination_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/"+request.session.session_key+"/config_copy")
        zip_path = os.path.join(settings.BASE_DIR, "dashboard/static/zip/output/"+request.session.session_key+"/config.zip")
        conf_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        print("* destination path: "+destination_path)
        print("* zip path: "+zip_path)
        print("* conf path: "+conf_path)
        create_config_zip(destination_path, zip_path, conf_path)

        fl_path = zip_path
        zip_file = open(fl_path, 'rb')
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'config.zip'
        return response
class DownloadResults(views.APIView):
    def get(self, request):
        print("****** GET request received DOWNLOAD_RESULTS ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        fl_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], request.session.session_key+"/output.csv")
        now = datetime.now()
        filename = str(now) + '_model_output.csv'

        fl = open(fl_path, 'r')
        mime_type, _ = mimetypes.guess_type(fl_path)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        print("* returning results:", response)
        print("* returning file:", filename)
        return response
class ConfigJsonUpload(views.APIView):
    def post(self, request):
        print("****** GET request received CONFIG_UPLOAD ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        uploaded = request.FILES['file']
        print("* uploaded file: "+uploaded.name)
        print("* uploaded file size: "+str(uploaded.size))
        configs_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        handle_uploaded_zip_config(uploaded, "dashboard/static/zip/"+request.session.session_key, configs_path)
        export_to_path(configs_path+"/")
        return HttpResponseRedirect('/mechanism.html')
class RemoveInitialConditionsFile(views.APIView):
    def get(self, request):
        return JsonResponse({"error":"removing initial conditions files should be a POST request"})
    def post(self, request):
        print("****** GET request received REMOVE_INITIAL_CONDITIONS_FILE ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        configs_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        remove_request = json.loads(request.body)
        # remove_initial_conditions_file(configs_path)
        print("* removing file:", remove_request)
        initial_conditions_file_remove(remove_request, configs_path)
        return JsonResponse({})
# upload on conditions/intial page
class InitCSV(views.APIView):
    def post(self, request):
        print("****** POST request received INIT_CSV ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        conf_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        print("* uploaded file: "+filename)
        print("* saving to conf_path: "+conf_path)
        manage_initial_conditions_files(uploaded, filename, conf_path)
        # return HttpResponseRedirect('/conditions/initial.html')
        return JsonResponse({})
class ClearEvolutionFiles(views.APIView):
    def get(self, request):
        print("****** POST request received INIT_CSV ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        conf_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        print("* clearing evolution files:", conf_path)
        clear_e_files(conf_path)
        return JsonResponse({})
class EvolvFileUpload(views.APIView):
    def post(self, request):
        print("****** POST request received EVOLV_FILE_UPLOAD ******")
        if not request.session.session_key:
            request.session.create()
        print("* session key: "+request.session.session_key)
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        conf_path = os.path.join(settings.BASE_DIR, 'configs/'+request.session.session_key)
        print("* uploading file: "+filename)
        manage_uploaded_evolving_conditions_files(uploaded, filename, conf_path)
        print("* uploaded evolving file: "+filename)
        return JsonResponse({})
class SessionView(views.APIView):
    def get(self, request):
        print("****** GET request received SESSION_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        print("returning session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
    def post(self, request):
        new_session_id = request.POST.dict()["session_id"]
        request.session.session_key = new_session_id
        print("****** setting new session key for user:",new_session_id,"******")
        return Response({"session_id": request.session.session_key}, status=status.HTTP_201_CREATED)

class LoadFromConfigJsonView(views.APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        print("* saving model options for user: "+request.session.session_key)
        uploaded = request.FILES['file']

