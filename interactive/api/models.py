from django.db import models
from enum import Enum

class RunStatus(Enum):
    RUNNING = 'RUNNING'
    WAITING = 'WAITING'
    NOT_FOUND = 'NOT_FOUND'
    DONE = 'DONE'
    ERROR = 'ERROR'
    UNKNOWN = 'UNKNOWN'


class SessionUser(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=50, primary_key=True)

    # JSONField of user's config files [JSONField]
    config_files = models.JSONField(default=dict) 

    # dictionary field that holds binary data of csv/other files [JSONField]
    binary_files = models.JSONField(default=dict)

    # should cache? [BooleanField]
    should_cache = models.BooleanField(default=False)

    # checksum of config files [CharField]
    config_checksum = models.CharField(max_length=50, default='')


class ModelRun(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=50, primary_key=True)

    # checksum of config files [CharField]
    config_checksum = models.CharField(max_length=50)

    # status of the model run [CharField]
    status = models.CharField(max_length=50, choices=[(status.value, status.value) for status in RunStatus])

    # results name and binary data [JSONField]
    results = models.JSONField(default=dict) # {name: binary data}

    # should cache?
    should_cache = models.BooleanField(default=True)
