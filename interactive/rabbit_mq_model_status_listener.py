import logging
import pika
import sys
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
from update_environment_variables import update_environment_variables

import json
# from session_model_runner import SessionModelRunner
import django
django.setup()
from django.db import connection
update_environment_variables()
from dashboard.database_tools import *
# listener to be hosted on main API server
# listens for messages from rabbitmq that indicate finished models


RABBIT_HOST = os.environ["rabbit-mq-host"]
RABBIT_PORT = int(os.environ["rabbit-mq-port"])

def main():
    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT)
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
        if "output.csv" in json_body:
            output_csv = json_body["output.csv"]
            model_run.results['/output.csv'] = output_csv
        
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


# checks server by trying to connect
def check_for_rabbit_mq(host, port):
    """
    Checks if RabbitMQ server is running.
    """
    try:
        conn_params = pika.ConnectionParameters(host, port)
       
        connection = pika.BlockingConnection(conn_params)
        if connection.is_open:
            connection.close()
            return True
        else:
            connection.close()
            return False
    except pika.exceptions.AMQPConnectionError:
        return False


if __name__ == '__main__':
    try:
        if check_for_rabbit_mq(RABBIT_HOST, RABBIT_PORT):
            main()
        else:
            print('[ERR!] RabbitMQ server is not running. Exiting...')
            sys.exit(1)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
