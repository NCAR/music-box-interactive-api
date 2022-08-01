# helper file that contains functions for unit testing
# helper function getting all files for user session
from tabnanny import check
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.conf import settings
import json
import os
import subprocess
import mimetypes
import pandas as pd
import time
import shutil
# from .run_logging import *
from datetime import datetime
from pathlib import Path
import logging
import hashlib

'''
For the given path, get the List of all files in the directory tree 
'''
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles


# calculate checksum for config/model so we can check if it's run before
def calculate_checksum(dir_to_check):
    filenames = getListOfFiles(dir_to_check)
    hash = hashlib.md5()
    for fn in filenames:
        if os.path.isfile(fn):
            hash.update(open(fn, "rb").read())
    return hash.hexdigest()