# from types import NoneType
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
from dashboard.forms.formsetup import *
from os.path import exists

# api.py contains all DJANGO based backend requests made to the server from client --
# each browser session creates a "session_key" saved to cookie on client side
#       - request.session.session_key is a string representation of this value
#       - request.session.session_key is used to access documents from DJANGO sql database
# CONDITIONSVIEW
#       - Catches all get and post requests made from conditions page
#       - POST REQUEST => Save new data to request.session.session_key conditions document in SQL server
#       - GET REQUEST => Return JSON format of user set conditions
# MECHANISMVIEW
#       - Catches all get and post requests made from mechanism page
#       - POST REQUEST => Save new data to request.session.session_key mechanisms document in SQL server
#       - GET REQUEST => Return JSON format of user set mechanisms
# SESSIONVIEW
#       - Called when user wants their session_key or wants to change it (i.e. import another users' simulation)
#       - POST REQUEST => Save new session_key for user and set cookie in browser
#       - GET REQUEST => Return JSON with key 'session_id' equal to the users' session_key




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



class GetModelOptionsView(views.APIView):
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
        if not request.session.session_key:
            request.session.create()
        print("* saving model options for user: "+request.session.session_key)
        
class ConditionsView(views.APIView):
    def get(self, request):
        print("****** GET request received CONDITIONS_VIEW ******")
        if not request.session.session_key:
            request.session.create()
        
        print("fetching conditions for session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
    def post(self, request):
        print("post request")


class SessionView(views.APIView):
    def get(self, request):
        print("****** GET request received SESSION_VIEW ******")
        session_key = ""
        try:
            session_key = request.COOKIES['sessionid']
            request.session.session_key = session_key
        except KeyError:
            request.session.create()
        
        print("returning session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
    def post(self, request):
        new_session_id = request.POST.dict()["session_id"]
        request.session.session_key = new_session_id
        print("****** setting new session key for user:",new_session_id,"******")
        return Response({"session_id": request.session.session_key}, status=status.HTTP_201_CREATED)
class RunView(views.APIView):
    def post(self, request):
        session_key = ""
        try:
            session_key = request.COOKIES['sessionid']
            request.session.session_key = session_key
        except KeyError:
            request.session.create()
        print("****** Running simulation for user session:",request.session.session_key,"******")
        return Response({"session_id": request.session.session_key}, status=status.HTTP_201_CREATED)