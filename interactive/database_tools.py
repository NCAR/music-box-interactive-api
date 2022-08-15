# import django models
from django.db import models
# import models from interactive/dashboard
from dashboard import models

# get user based on uid
def get_user(uid):
    return models.User.objects.get(uid=uid)

# get model run based on uid
def get_model_run(uid):
    return models.ModelRun.objects.get(uid=uid)

# get config files of user
def get_config_files(uid):
    return get_user(uid).config_files

# get csv files of user
def get_csv_files(uid):
    return get_user(uid).csv_files

# get results of model run
def get_results(uid):
    return get_model_run(uid).results

# get is running of model run
def get_is_running(uid):
    return get_model_run(uid).is_running

# set config files of user
def set_config_files(uid, config_files):
    user = get_user(uid)
    user.config_files = config_files
    user.save()

# set csv files of user
def set_csv_files(uid, csv_files):
    user = get_user(uid)
    user.csv_files = csv_files
    user.save()

# set results of model run
def set_results(uid, results):
    model_run = get_model_run(uid)
    model_run.results = results
    model_run.save()

# set is running of model run
def set_is_running(uid, is_running):
    model_run = get_model_run(uid)
    model_run.is_running = is_running
    model_run.save()

# create new user
def create_user(uid):
    user = models.User(uid=uid)
    user.save()
    return user

# create new model run
def create_model_run(uid):
    model_run = models.ModelRun(uid=uid)
    model_run.save()
    return model_run

# delete user
def delete_user(uid):
    user = get_user(uid)
    user.delete()

# delete model run
def delete_model_run(uid):
    model_run = get_model_run(uid)
    model_run.delete()

# delete all users
def delete_all_users():
    models.User.objects.all().delete()

# delete all model runs
def delete_all_model_runs():
    models.ModelRun.objects.all().delete()

# delete all config files
def delete_all_config_files(uid):
    user = get_user(uid)
    user.config_files = {}
    user.save()

# delete all csv files
def delete_all_csv_files(uid):
    user = get_user(uid)
    user.csv_files = {}
    user.save()

# delete results
def delete_results(uid):
    model_run = get_model_run(uid)
    model_run.results = {}
    model_run.save()

# set specific config file of user
def set_config_file(uid, filename, config_file):
    user = get_user(uid)
    user.config_files[filename] = config_file
    user.save()

# set specific csv file of user
def set_csv_file(uid, filename, csv_file):
    user = get_user(uid)
    user.csv_files[filename] = csv_file
    user.save()

# delete specific config file of user
def delete_config_file(uid, filename):
    user = get_user(uid)
    del user.config_files[filename]
    user.save()

# delete specific csv file of user
def delete_csv_file(uid, filename):
    user = get_user(uid)
    del user.csv_files[filename]
    user.save()
