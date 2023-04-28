# these import must come first
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')
django.setup()

from api.database_tools import get_model_run
from shared.utils import check_for_rabbit_mq

import json
import logging
import pika
import sys

RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
RABBIT_USER = os.environ["RABBIT_MQ_USER"]
RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]

# disable propagation
logging.getLogger("pika").propagate = False
def main():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
    conn = pika.BlockingConnection(connParam)
    channel = conn.channel()
    channel.queue_declare(queue='model_finished_queue')

    def run_model_finished_callback(ch, method, properties, body):
        json_body = json.loads(body)
        session_id = json_body["session_id"]
        # grab ModelRun for session_id
        model_run = get_model_run(session_id)
        logging.info("Model finished for session {}".format(session_id))
        # grab MODEL_RUN_COMPLETE and error.json from data
        # save results to database
        
        MODEL_RUN_COMPLETE = json_body["MODEL_RUN_COMPLETE"]
        error_json = {}
        if "error.json" in json_body:
            error_json = json_body["error.json"]
            logging.info(f"Model error for session {session_id}: {error_json}")
        else:
            logging.info(f"No errors for session {session_id}")
        if "output.csv" in json_body:
            output_csv = json_body["output.csv"]
            model_run.results['/output.csv'] = output_csv
            logging.info(f"Output found for session {session_id}")
        else:
            logging.info(f"No output found for session {session_id}")
        
        # update model_run with MODEL_RUN_COMPLETE and error_json
        model_run.results['/MODEL_RUN_COMPLETE'] = MODEL_RUN_COMPLETE
        model_run.results['/error.json'] = error_json
        model_run.is_running = False
        model_run.save()
        logging.info("Model run saved to database")

        
    channel.basic_consume(queue='model_finished_queue',
                          on_message_callback=run_model_finished_callback,
                          auto_ack=True)

    logging.info("Waiting for model_finished_queue messages")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
   # connection.close()



if __name__ == '__main__':
    # config to easily see threads and process IDs
    logging.basicConfig(
        level=logging.INFO,
        format=("%(relativeCreated)04d %(process)05d %(threadName)-10s "
                "%(levelname)-5s %(msg)s"))
    try:
        if check_for_rabbit_mq():
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
