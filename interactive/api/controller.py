from django.conf import settings
from django.http import Http404
from django.db import transaction, DatabaseError

import json
import logging
import os
import time
import pandas as pd
from api import models
from api.run_status import RunStatus
from io import StringIO
from shared.configuration_utils import compress_configuration, \
    extract_configuration, \
    load_configuration, \
    filter_diagnostics, \
    get_session_path, \
    get_zip_file_path
from partmc_model.partmc_utils import compress_partmc, get_partmc_zip_file_path
from shared.rabbit_mq import publish_message
from acom_music_box import Examples
from api.request_models import Example

logger = logging.getLogger(__name__)

# retry limits for db operations
RETRY_LIMIT = 10
RETRY_DELAY = 1  # seconds


def load_example(example):
    '''Returns a JSON version of one of the example configurations'''

    # Short names on the right are the names in music box
    to_short_name = {
        Example.FULL_GAS_PHASE.name: 'CB5',
        Example.FLOW_TUBE.name: 'FlowTube',
        Example.TS1.name: 'TS1',
        Example.CHAPMAN.name: 'Chapman',
    }

    configuration = None

    for ex in Examples:
        if ex.short_name == to_short_name[example]:
            configuration = ex
            break

    if not configuration:
        logging.error(f"Example {example} not found")
        raise Http404(f"Example {example} not found")
    return get_configuration_as_json(os.path.dirname(configuration.path))


def get_configuration_as_json(file_path):
    '''Returns a JSON version of a full MusicBox configuration'''

    conditions = {}
    mechanism = {}

    files = [os.path.join(dp, f)
             for dp, _, fn in os.walk(file_path) for f in fn if '__MACOSX' not in dp]
    if not files:
        logging.error("No files in example foler")
        raise Http404("No files in example folder")

    for file in files:
        if 'species.json' in file:
            with open(file, 'r') as contents:
                mechanism['species'] = json.load(contents)
        if 'reactions.json' in file:
            with open(file, 'r') as contents:
                mechanism['reactions'] = json.load(contents)
        if 'my_config.json' in file:
            with open(file, 'r') as contents:
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
            if "evolving conditions" in conditions:
                evolving_conditions = conditions["evolving conditions"]
                if evolving_conditions:
                    evolving_conditions = list(evolving_conditions.keys())[0]
                    path = [f for f in files if evolving_conditions in f]
                    if path:
                        evolving_conditions = path[0]
                        df = pd.read_csv(evolving_conditions)
                        conditions["evolving conditions"] = df.to_dict()
                        del df
                    else:
                        logger.warning("Could not find evolving conditions file")

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

# safely save data to the database


def safely_save_data(data):
    for i in range(RETRY_LIMIT):
        try:
            with transaction.atomic():
                data.save()
                break
        except DatabaseError:
            logger.error(f"Database error: retrying in {RETRY_DELAY} seconds")
            time.sleep(RETRY_DELAY)
    else:
        logger.error(f"Failed to save model after {RETRY_LIMIT} retries")


def publish_run_request(session_id, config):
    model_run = create_model_run(session_id)
    model_run.status = RunStatus.WAITING.value
    safely_save_data(model_run)
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
    safely_save_data(model_run)
    return model_run


# get status of a run
def get_run_status(uid):
    error = {}
    status = RunStatus.NOT_FOUND
    current_time = 0.0
    try:
        model = get_model_run(uid)
        logger.debug(f"model: {model} | {model.status}")
        status = RunStatus(model.status)
        if status == RunStatus.ERROR:
            error = json.loads(model.results['error'])
        current_time = model.current_time
    except Exception:
        status = RunStatus.NOT_FOUND
        logger.info(f"[{uid}] model run not found for user")
    return {'status': status, 'error': error, 'current_time': current_time}
