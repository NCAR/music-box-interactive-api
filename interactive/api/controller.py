from django.conf import settings
from django.http import Http404

import json
import logging
import os
import pandas as pd
from api import models
from api.run_status import RunStatus
from io import StringIO
from shared.configuration_utils import compress_configuration, \
    extract_configuration, \
    load_configuration, \
    compress_partmc, \
    filter_diagnostics, \
    get_session_path, \
    get_partmc_zip_file_path, \
    get_zip_file_path
from shared.rabbit_mq import publish_message

logger = logging.getLogger(__name__)


def load_example(example):
    '''Returns a JSON version of one of the example configurations'''
    example_path = os.path.join(
        settings.BASE_DIR, 'api/static/examples', example)
    return get_configuration_as_json(example_path)


def get_configuration_as_json(file_path):
    '''Returns a JSON version of a full MusicBox configuration'''

    conditions = {}
    mechanism = {}

    files = [os.path.join(dp, f)
             for dp, _, fn in os.walk(file_path) for f in fn]
    if not files:
        logging.error("No files in example foler")
        raise Http404("No files in example folder")

    for file in files:
        if 'species.json' in file:
            with open(file) as contents:
                mechanism['species'] = json.load(contents)
        if 'reactions.json' in file:
            with open(file) as contents:
                mechanism['reactions'] = json.load(contents)
        if 'my_config.json' in file:
            with open(file) as contents:
                conditions = json.load(contents)
            if "initial conditions" in conditions and \
               len(list(conditions["initial conditions"].keys())) > 0:
                rates_file = list(conditions["initial conditions"].keys())[0]
                logger.debug(f"Found rates file: {rates_file}")
                path = [f for f in files if rates_file in f]
                if len(path) > 0:
                    rates_file = path[0]
                    df = pd.read_csv(rates_file)
                    conditions["initial conditions"] = df.to_dict()
                    del df
                else:
                    logger.warning(
                        "Could not find initial rates condition file")
            if "evolving conditions" in conditions and \
               len(list(conditions["evolving conditions"].keys())) > 0:
                evolving_conditions = list(
                    conditions["evolving conditions"].keys())
                if len(evolving_conditions) > 0:
                    evolving_conditions = evolving_conditions[0]
                    path = [f for f in files if evolving_conditions in f]
                    if len(path) > 0:
                        evolving_conditions = path[0]
                        df = pd.read_csv(evolving_conditions)
                        conditions["evolving conditions"] = df.to_dict()
                        del df
                    else:
                        logger.warning(
                            "Could not find initial rates condition file")

    return conditions, filter_diagnostics(mechanism)


def handle_compress_configuration(session_id, config):
    '''Returns a compress file containing the provided configuration'''
    load_configuration(
        session_id,
        config,
        keep_relative_paths=True,
        in_scientific_notation=False)
    compress_configuration(session_id)
    return open(get_zip_file_path(session_id), 'rb')


def handle_compress_partmc(session_id):
    '''Returns a compress file containing the partmc output'''
    compress_partmc(session_id)
    return open(get_partmc_zip_file_path(session_id), 'rb')


def handle_extract_configuration(session_id, zipfile):
    '''Returns a JSON version of a compressed MusicBox configuration'''
    extract_configuration(session_id, zipfile)
    return get_configuration_as_json(get_session_path(session_id))


def publish_run_request(session_id, config):
    model_run = create_model_run(session_id)
    model_run.status = RunStatus.WAITING.value
    model_run.save()
    body = {"session_id": session_id, "config": config}
    publish_message(route_key='run_request', message=body)
    logger.info("published message to run_queue")


def get_results_file(session_id):
    '''Returns a csv file with the model results'''
    model = models.ModelRun.objects.get(uid=session_id)
    if '/output.csv' in model.results:
        output_csv = StringIO(model.results['/output.csv'])
        df = pd.read_csv(output_csv, encoding='latin1')
        df.columns = df.columns.str.strip()
        return df
    else:
        return pd.DataFrame()


# get model run based on uid
def get_model_run(uid):
    try:
        model = models.ModelRun.objects.get(uid=uid)
        return model
    except Exception:
        # if not, create new model run
        model_run = create_model_run(uid)
        return model_run


# get results of model run
def get_results(uid):
    return get_model_run(uid).results


# create new model run
def create_model_run(uid):
    model_run = models.ModelRun(uid=uid)
    model_run.save()
    return model_run


# get status of a run
def get_run_status(uid):
    error = {}
    try:
        model = get_model_run(uid)
        logger.debug(f"model: {model} | {model.status}")
        status = RunStatus(model.status)
        if status == RunStatus.ERROR:
            error = json.loads(model.results['error'])
    except Exception:
        status = RunStatus.NOT_FOUND
        logger.info(f"[{uid}] model run not found for user")
    return {'status': status, 'error': error}
