from django.db import models

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class User(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=50)

    # dictionary of user's config files [DictField]
    config_files = models.DictField() # {filename: json}

    # dictionary field that holds binary data of csv files
    csv_files = models.DictField() # {filename: binary data}

class ModelRun(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=50)

    # checksum of config files [CharField]
    config_checksum = models.CharField(max_length=50)

    # is running? [BooleanField]
    is_running = models.BooleanField(default=False)
    
    # results name and binary data [DictField]
    results = models.DictField() # {name: binary data}
