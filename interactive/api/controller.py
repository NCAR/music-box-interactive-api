from django.conf import settings
from django.http import Http404

import json
import logging
import os
import pandas as pd
import api.database_tools as db_tools
from api import models
from api.run_status import RunStatus
from io import StringIO
from shared.configuration_utils import compress_configuration, \
                                       extract_configuration, \
                                       load_configuration, \
                                       filter_diagnostics, \
                                       get_session_path, \
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
                    logger.warning("Could not find initial rates condition file")
            if "evolving conditions" in conditions and \
               len(list(conditions["evolving conditions"].keys())) > 0:
                evolving_conditions = list(conditions["evolving conditions"].keys())
                if len(evolving_conditions) > 0:
                    evolving_conditions = evolving_conditions[0]
                    path = [f for f in files if evolving_conditions in f]
                    if len(path) > 0:
                        evolving_conditions = path[0]
                        df = pd.read_csv(evolving_conditions)
                        conditions["evolving conditions"] = df.to_dict()
                        del df
                    else:
                        logger.warning("Could not find initial rates condition file")

    return conditions, filter_diagnostics(mechanism)


def handle_compress_configuration(session_id, config):
    '''Returns a compress file containing the provided configuration'''
    load_configuration(session_id, config, keep_relative_paths=True, in_scientific_notation=False)
    compress_configuration(session_id)
    return open(get_zip_file_path(session_id), 'rb')


def handle_extract_configuration(session_id, zipfile):
    '''Returns a JSON version of a compressed MusicBox configuration'''
    extract_configuration(session_id, zipfile)
    return get_configuration_as_json(get_session_path(session_id))


def publish_run_request(session_id, config):
    model_run = db_tools.create_model_run(session_id)
    model_run.status = RunStatus.WAITING.value
    model_run.save()
    logger.debug(config)
    body = {"session_id": session_id, "config": config}
    publish_message(route_key = 'run_request', message=body)
    logger.info("published message to run_queue")


def get_results_file(session_id):
    '''Returns a csv file with the model results'''
    model = models.ModelRun.objects.get(uid=session_id)
    output_csv = StringIO(model.results['/output.csv'])
    return pd.read_csv(output_csv, encoding='latin1')
