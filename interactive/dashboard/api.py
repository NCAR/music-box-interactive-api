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




class TestAPIView(APIView):
    def get(self, request):
        return Response({"message": "This is a test API view"})
class ConditionsView(APIView):
    def get(self, request):
        print("****** GET request received CONDITIONS_VIEW ******")
        if not request.session.exists(request.session.session_key):
            request.session.create() 
            print("new session created")
        
        print("fetching conditions for session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
class MechanismView(APIView):
    def get(self, request):
        print("****** GET request received MECHANISM_VIEW ******")
        if not request.session.exists(request.session.session_key):
            request.session.create() 
            print("new session created")
        
        print("fetching mechanisms for session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
class SessionView(APIView):
    def get(self, request):
        print("****** GET request received SESSION_VIEW ******")
        if not request.session.exists(request.session.session_key):
            request.session.create() 
            print("new session created")
        
        print("fetching mechanisms for session id: " + request.session.session_key)
        return Response({"session_id": request.session.session_key})
    def post(self, request):
        new_session_id = request.POST.dict()["set_session_id"]
        request.session.session_key = new_session_id
        print("****** setting new session key for user:",new_session_id,"******")
        return Response({"session_id": request.session.session_key}, status=status.HTTP_201_CREATED)