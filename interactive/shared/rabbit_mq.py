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

def publish_message(message, on_queue = None):
    """
    Publishes a message on a queue
    """
    if not on_queue:
        raise ValueError(f"No queue to listen on was specified.")
    
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(
        RABBIT_HOST, RABBIT_PORT, credentials=credentials)
    with pika.BlockingConnection(connParam) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=on_queue)
        channel.basic_publish(exchange='',
                            routing_key=on_queue,
                            body=json.dumps(message))


def consume(log_message=None, on_queue=None, callback=None):
    """
    Setup a consumer for a queue. The queue and callback must be supplied
    """
    if not on_queue:
        raise ValueError(f"No queue to listen on was specified.")
    if not callback:
        raise ValueError(
            f"A callback must be supplied when consuming from a message queue.")

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(
        RABBIT_HOST, RABBIT_PORT, credentials=credentials)

    with pika.BlockingConnection(connParam) as connection:
        channel = connection.channel()

        channel.queue_declare(queue=on_queue)
        channel.basic_consume(queue=on_queue,
                                on_message_callback=callback,
                                auto_ack=True)

        if log_message:
            logger.info(log_message)
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
