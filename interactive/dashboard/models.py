from django.db import models
class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class User(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=50)

    # JSONField of user's config files [JSONField]
    config_files = models.JSONField(default={}) 

    # dictionary field that holds binary data of csv/other files [JSONField]
    binary_files = models.JSONField(default={})

    # should cache? [BooleanField]
    should_cache = models.BooleanField(default=False)

    # checksum of config files [CharField]
    config_checksum = models.CharField(max_length=50, default='')


class ModelRun(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=50)

    # checksum of config files [CharField]
    config_checksum = models.CharField(max_length=50)

    # is running? [BooleanField]
    is_running = models.BooleanField(default=False)
    
    # results name and binary data [JSONField]
    results = models.JSONField(default={}) # {name: binary data}

    # should cache?
    should_cache = models.BooleanField(default=True)
