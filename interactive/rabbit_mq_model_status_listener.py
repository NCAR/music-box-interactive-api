# these imports must come first # noqa: E402
import os  # noqa: E402
import django  # noqa: E402
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage.settings')  # noqa: E402
django.setup()  # noqa: E402

import sys
import logging
import json
from api.run_status import RunStatus
from shared.rabbit_mq import rabbit_is_available, consume, ConsumerConfig
from api.controller import get_model_run

# disable propagation
logging.getLogger("pika").propagate = False


def done_status_callback(ch, method, properties, body):
    json_body = json.loads(body)
    session_id = json_body["session_id"]
    # grab ModelRun for session_id
    model_run = get_model_run(session_id)
    logging.info("Model finished for session {}".format(session_id))

    status = RunStatus.DONE.value
    if "MODEL_RUN_COMPLETE" in json_body:
        status = RunStatus.DONE.value
    error_json = {}
    if "error.json" in json_body:
        error_json = json_body["error.json"]
        status = RunStatus.ERROR.value
        logging.info(f"Model error for session {session_id}: {error_json}")
    else:
        logging.info(f"No errors for session {session_id}")
    if "output.csv" in json_body:
        output_csv = json_body["output.csv"]
        model_run.results['/output.csv'] = output_csv
        logging.info(f"Output found for session {session_id}")
    elif 'partmc_output_path' in json_body:
        model_run.results['partmc_output_path'] = json_body['partmc_output_path']
    else:
        status = RunStatus.ERROR.value
        error_json = json.dumps({'message': 'No output found'})
        logging.info(f"No output found for session {session_id}")

    # update model_run with MODEL_RUN_COMPLETE and error_json
    model_run.results['error'] = error_json
    model_run.status = status
    model_run.save()
    logging.info("Model run saved to database")


def other_status_callback(ch, method, properties, body):
    logging.info(f"status update: {method.routing_key} {body}")
    json_body = json.loads(body)
    session_id = json_body["session_id"]
    model_run = get_model_run(session_id)
    model_run.status = method.routing_key
    if RunStatus(method.routing_key) == RunStatus.ERROR:
        model_run.results = {'error': json_body['error.json']}
    model_run.save()


def main():
    done = ConsumerConfig(
        route_keys=[RunStatus.DONE.value], callback=done_status_callback
    )

    other = ConsumerConfig(
        route_keys=[
            status.value for status in RunStatus if status != RunStatus.DONE],
        callback=other_status_callback)

    consume(consumer_configs=[done, other])


if __name__ == '__main__':
    # config to easily see threads and process IDs
    logging.basicConfig(
        level=logging.INFO,
        format=("%(relativeCreated)04d %(process)05d %(threadName)-10s "
                "%(levelname)-5s %(msg)s"))
    try:
        if rabbit_is_available():
            main()
        else:
            logging.error('[ERR!] RabbitMQ server is not running. Exiting...')
            sys.exit(1)
    except KeyboardInterrupt:
        logging.debug('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
