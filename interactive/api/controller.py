from django.conf import settings
from django.http import Http404

import json
import logging
import os
import pandas as pd
import pika
from shared.configuration_utils import compress_configuration, \
                                       extract_configuration, \
                                       load_configuration, \
                                       filter_diagnostics, \
                                       get_session_path, \
                                       get_zip_file_path

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
    load_configuration(session_id, config, keep_relative_paths=True)
    compress_configuration(session_id)
    return open(get_zip_file_path(session_id), 'rb')


def handle_extract_configuration(session_id, zipfile):
    '''Returns a JSON version of a compressed MusicBox configuration'''
    extract_configuration(session_id, zipfile)
    return get_configuration_as_json(get_session_path(session_id))


def publish_run_request(session_id, config):
    RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
    RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
    RABBIT_USER = os.environ["RABBIT_MQ_USER"]
    RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]

    try:
        credentials = pika.PlainCredentials( RABBIT_USER, RABBIT_PASSWORD)
        connParam = pika.ConnectionParameters( RABBIT_HOST, RABBIT_PORT, credentials=credentials)
        with pika.BlockingConnection(connParam) as connection:
            channel = connection.channel()
            channel.queue_declare(queue='run_queue')
            body = {"session_id": session_id, "config": config}
            channel.basic_publish(exchange='',
                                routing_key='run_queue',
                                body=json.dumps(body))
    except Exception as e:
        logger.exception(f"Unable to publish run message")
        return False

    logger.info("published message to run_queue")

    return True
