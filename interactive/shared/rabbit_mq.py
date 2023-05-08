import logging
import json
import os
import pika

logger = logging.getLogger(__name__)

# fallback to defaults
RABBIT_HOST = os.getenv("RABBIT_MQ_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBIT_MQ_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_MQ_USER", "guest")
RABBIT_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD", "guest")


class RabbitConfig:
    def __init__(self, exchange, queue, route_keys=None, 
                 host=RABBIT_HOST, 
                 port=RABBIT_PORT, 
                 user=RABBIT_USER, 
                 password=RABBIT_PASSWORD):
        self.exchange = exchange
        self.queue = queue
        self.route_keys = route_keys
        self.host = host
        self.port = port
        self.user = user
        self.password = password


def publish_message(message, queue=None, route_key=None, exchange='musicbox.model_runs'):
    """
    Publishes a message on a queue
    """
    if not queue:
        raise ValueError(f"No queue to listen on was specified.")
    if not route_key:
        raise ValueError(f"A route key must be supplied")

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(
        RABBIT_HOST, RABBIT_PORT, credentials=credentials)
    with pika.BlockingConnection(connParam) as connection:
        channel = connection.channel()

        # Ensure the queue is initialized
        channel.queue_declare(queue=queue)

        # Bind the queue to the routing key
        channel.queue_bind(exchange=exchange, queue=queue,
                           routing_key=route_key)

        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=json.dumps(message))


def consume(queue=None, route_key=None, callback=None, exchange='musicbox.model_runs'):
    """
    Setup a consumer for a queue. The queue and callback must be supplied
    """
    if not queue:
        raise ValueError(f"No queue to listen on was specified.")
    if not route_key:
        raise ValueError(f"A route key must be supplied")
    if not callback:
        raise ValueError(
            f"A callback must be supplied when consuming from a message queue.")

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(
        RABBIT_HOST, RABBIT_PORT, credentials=credentials)

    with pika.BlockingConnection(connParam) as connection:
        channel = connection.channel()

        channel.queue_declare(queue=queue)
        channel.basic_consume(queue=queue,
                              on_message_callback=callback,
                              auto_ack=True)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()


def check_for_rabbit_mq():
    """
    Determine if rabbit mq is accepting connections
    """
    try:
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
        connParam = pika.ConnectionParameters(
            RABBIT_HOST, RABBIT_PORT, credentials=credentials)
        with pika.BlockingConnection(connParam) as connection:
            return connection.is_open
    except pika.exceptions.AMQPConnectionError as e:
        logger.exception(f"Failed to connect to RabbitMQ", e)
        return False
