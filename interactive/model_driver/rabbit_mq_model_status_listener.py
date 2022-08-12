# listener to be hosted on main API server
# listens for messages from rabbitmq that indicate finished models

import logging
import pika
import sys
import os
import json
from session_model_runner import SessionModelRunner
from django.db import connection

RABBIT_HOST = os.environ["rabbit-mq-host"]
RABBIT_PORT = int(os.environ["rabbit-mq-port"])

logging.basicConfig(filename='logs.log', filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s',
                    level=logging.DEBUG)
logging.basicConfig(filename='errors.log', filemode='w',
                    format='%(asctime)s - [ERROR!!] %(message)s',
                    level=logging.ERROR)
def main():
    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT)
    connection = pika.BlockingConnection(connParam)
    channel = connection.channel()

    channel.queue_declare(queue='model_finished_queue')

    def run_model_finished_callback(ch, method, properties, body):
        logging.info('received model_finished message -- extracting results')
        # TODO: once we have seperated the rabbit_mq_model_runner
        # server from the api server, we would move files
        decoded_body = json.loads(body.decode())
        if type(decoded_body) is dict:
            logging.info('decoded_body is properly formatted as a dict')
            # get session_id from message
            session_id = decoded_body['session_id']
            # checksum of config files
            model_checksum = decoded_body['model_checksum']
            # name for results file
            results_name = decoded_body['results_name']
            # binary data of csv results
            results_binary_data = decoded_body['results_binary_data']

            # step 1: save results to file
            logging.info('saving results to file')
            results_file_path = os.path.join('/build/'+session_id, results_name)
            with open(results_file_path, 'wb') as f:
                f.write(results_binary_data)
            logging.info('results saved to file')

            # step 2: save checksum to database
            logging.info('saving checksum to database')
            
            cursor = connection.cursor()
            cursor.execute("UPDATE config_checksums SET model_checksum = %s WHERE id = %s", [model_checksum, session_id])
            connection.commit()
            logging.info('checksum saved to database ('+str(model_checksum)+')')
        else:
            logging.info('decoded_body is not properly formatted as a dict')
            # return error?
    channel.basic_consume(queue='model_finished_queue', on_message_callback=run_model_finished_callback, auto_ack=True)

    print(' [*] Waiting for model_finished_queue messages. To exit press CTRL+C')
    channel.start_consuming()


# checks server by trying to connect
def check_for_rabbit_mq(host, port):
    """
    Checks if RabbitMQ server is running.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        if connection.is_open:
            connection.close()
            return True
        else:
            connection.close()
            return False
    except:
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