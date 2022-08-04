# listener to be hosted on main API server
# listens for messages from rabbitmq that indicate finished models

import logging
import pika
import sys
import os
from session_model_runner import SessionModelRunner

RABBIT_HOST = 'host.docker.internal' # access parent host from outside of docker container
RABBIT_PORT = 5672

logging.basicConfig(filename='logs.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s', level=logging.DEBUG)
logging.basicConfig(filename='errors.log', filemode='w', format='%(asctime)s - [ERROR!!] %(message)s', level=logging.ERROR)
# disable propagation
# logging.getLogger("pika").propagate = False

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT))
    channel = connection.channel()

    channel.queue_declare(queue='model_finished_queue')

    def run_model_finished_callback(ch, method, properties, body):
        logging.info('received model_finished_queue message:' + str(body.decode()))
        # TODO: once we have seperated the rabbit_mq_model_runner server from the api server, we would move files
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
