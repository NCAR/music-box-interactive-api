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
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
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
class ConditionsView(views.APIView):
    def get(self, request):
        print("****** GET request received CONDITIONS_VIEW ******")
        if not request.session.exists(request.session.session_key):
            request.session.create() 
            print("new session created")
        
        print("fetching conditions for session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
    def post(self, request):
        print("post request")
class MechanismView(views.APIView):
    def get(self, request):
        print("****** GET request received MECHANISM_VIEW ******")
        if not request.session.exists(request.session.session_key):
            request.session.create() 
            print("new session created")
        
        print("fetching mechanisms for session id: " + request.session.session_key)
        species = request.session.get("species", []) #set default value to [] so that we don't get any errors
        reactions = request.session.get("reactions", [])
        return Response({"session_id": request.session.session_key, "species":species, "reactions":reactions})
    
    def delete(self, request):
        # delete mechanism
        print("****** DELETE request received MECHANISM_VIEW ******")
        #delete all species and reactions
        del request.session['species']
        del request.session['reactions']

        return Response(status=status.HTTP_200_OK)
class AddMechanismView(views.APIView):
    def post(self, request):
        if not request.session.exists(request.session.session_key):
            request.session.create() 
        print("********* adding mechanism for user "+request.session.session_key+" *********")
        print(request.POST.dict())
        type_to_add = request.POST.dict()["type"] # 'species' or 'reaction'
        if type_to_add == "species":

            name = request.POST.dict()["name"]
            convergence_tolerance = request.POST.dict()["absolute_convergence_tolerance"]
            description = request.POST.dict()["description"]
            molecular_weight = request.POST.dict()["molecular_weight"]
            tracer_type = request.POST.dict()["tracer_type"]

            if 'species' not in request.session:
                print("no species added, creating new array")
                request.session['species'] = [{"name":name, "convergence_tolerance": convergence_tolerance, "description":description,"molecular_weight":molecular_weight,"tracer_type":tracer_type}]
            else:
                print("species array exists, appending")
                species = request.session['species']
                species.append({"name":name, "convergence_tolerance": convergence_tolerance, "description":description,"molecular_weight":molecular_weight,"tracer_type":tracer_type})
                request.session['species'] = species
            
            print("returning species:",request.session['species'])
            return Response(request.session['species'])
        elif type_to_add == "reaction":
            reaction_type = request.POST.dict()["reaction_type"]
            reactants = request.POST.dict()["reactants"]
            products = request.POST.dict()["products"]
            scaling_factor = request.POST.dict()["scaling_factor"]
            musica_name = request.POST.dict()["musica_name"]
            if 'reactions' not in request.session:
                print("no reactions added, creating new array")
                request.session['reactions'] = [{"reaction_type":reaction_type, "reactants": reactants, "products":products,"scaling_factor":scaling_factor,"musica_name":musica_name}]
            else:
                print("reactions array exists, appending")
                reactions = request.session['species']
                reactions.append({"reaction_type":reaction_type, "reactants": reactants, "products":products,"scaling_factor":scaling_factor,"musica_name":musica_name})
                request.session['reactions'] = reactions
            
            print("returning reactions:",request.session['reactions'])
            return Response(request.session['reactions'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
class ExampleView(views.APIView):
    def get(self, request):
        if not request.session.exists(request.session.session_key):
            request.session.create() 
        #set example conditions and species/reactions
        example_name = 'example_' + str(request.GET.dict()['example'])
        examples_path = os.path.join(settings.BASE_DIR, 'dashboard/static/examples')
        example_folder_path = os.path.join(examples_path, example_name)
class SessionView(views.APIView):
    def get(self, request):
        print("****** GET request received SESSION_VIEW ******")
        if not request.session.exists(request.session.session_key):
            request.session.create() 
            print("new session created")
        
        print("returning session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
    def post(self, request):
        new_session_id = request.POST.dict()["session_id"]
        request.session.session_key = new_session_id
        print("****** setting new session key for user:",new_session_id,"******")
        return Response({"session_id": request.session.session_key}, status=status.HTTP_201_CREATED)
class RunView(views.APIView):
    def post(self, request):
        if not request.session.exists(request.session.session_key):
            request.session.create() 
        print("****** Running simulation for user session:",request.session.session_key,"******")
        return Response({"session_id": request.session.session_key}, status=status.HTTP_201_CREATED)