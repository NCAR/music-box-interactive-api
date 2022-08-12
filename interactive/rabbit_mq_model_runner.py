# main model runner interface class for rabbitmq and actual model runner
# 1) listen to run_queue
# 2) run model when receive message
# 3) send message to model_finished_queue when model is finished


import logging
import pika
import sys
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
from model_driver.session_model_runner import SessionModelRunner
from update_environment_variables import update_environment_variables
update_environment_variables()
RABBIT_HOST = os.environ["rabbit-mq-host"]
RABBIT_PORT = int(os.environ["rabbit-mq-port"])

logging.basicConfig(filename='logs.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s', level=logging.DEBUG)
logging.basicConfig(filename='errors.log', filemode='w', format='%(asctime)s - [ERROR!!] %(message)s', level=logging.ERROR)
# disable propagation
# logging.getLogger("pika").propagate = False

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT))
    channel = connection.channel()

    channel.queue_declare(queue='run_queue')

    def run_queue_callback(ch, method, properties, body):
        logging.info('received run_queue message:' + str(body.decode()))
        runner = SessionModelRunner(body.decode())
        runner.run()
    channel.basic_consume(queue='run_queue', on_message_callback=run_queue_callback, auto_ack=True)

    print(' [*] Waiting for run_queue messages. To exit press CTRL+C')
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
            print('[ERR!] RabbitMQ server is not running.')
            sys.exit(1)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
