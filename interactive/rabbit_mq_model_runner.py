# these import must come first
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')
django.setup()

from concurrent.futures import ThreadPoolExecutor as Pool
from multiprocessing import cpu_count
from shared.utils import check_for_rabbit_mq

import functools
import json
import logging
import numpy as np
import os
import pandas as pd
import pika
import shutil
import subprocess
import sys
from shared.configuration_handler import load_configuration

# main model runner interface class for rabbitmq and actual model runner
# 1) listen to run_queue
# 2) run model when receive message
# 3) send message to model_finished_queue when model is finished

# cpu_count() returns number of cores on machine
# this will run as many threads as there are cores (and will be faster but very cpu intensive)
# set this number to 1 if you want to run everything in one thread -- if you are running on a server
# without much cpu power/want to reduce energy usage you should probably set this to 1
pool = Pool(max_workers=cpu_count()) # sets max number of workers to add to pool

RABBIT_HOST = os.environ["RABBIT_MQ_HOST"]
RABBIT_PORT = int(os.environ["RABBIT_MQ_PORT"])
RABBIT_USER = os.environ["RABBIT_MQ_USER"]
RABBIT_PASSWORD = os.environ["RABBIT_MQ_PASSWORD"]

def publish_message(message):
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
    with pika.BlockingConnection(connParam) as connection:
        channel = connection.channel()
        channel.queue_declare(queue='model_finished_queue')
        channel.basic_publish(exchange='',
                                routing_key='model_finished_queue',
                                body=json.dumps(message))

# disable propagation
logging.getLogger("pika").propagate = False

def music_box_exited_callback(session_id, output_directory, future):
    if future.exception() is not None:
        logging.info("["+session_id+"] Got exception: %s" % future.exception())
    else:
        logging.info("["+session_id+"] Model finished.")
        # 1) check for output files (in /build)
        # 2) send output files to model_finished_queue
        # 3) delete config files and binary files from file system

        # check number of output files in /build
        logging.info(f"output directory: {output_directory}")
        output_files = getListOfFiles(output_directory)
        if len(output_files) == 0:
            logging.info("["+session_id+"] No output files found, exiting")
            return
        # body to send to model_finished_queue
        body = {'session_id': session_id}
        complete_path = os.path.join(output_directory, 'MODEL_RUN_COMPLETE')
        csv_path = os.path.join(output_directory, 'output.csv')
        error_path = os.path.join(output_directory, 'error.json')
        if os.path.exists(complete_path):
            # read complete file
            with open(complete_path, 'r') as f:
                body["MODEL_RUN_COMPLETE"] = f.read()
        if os.path.exists(error_path):
            # read error file
            with open(error_path, 'r') as f:
                body["error.json"] = f.read()
        if os.path.exists(csv_path):
            # read csv file
            with open(csv_path, 'r') as f:
                body["output.csv"] = f.read()
        # remove all files to save space
        # shutil.rmtree(output_directory)
        # send body to model_finished_queue
        publish_message(body)
        logging.info("["+session_id+"] Sent output files to model_finished_queue")


def run_queue_callback(ch, method, properties, body):
    logging.info("Received run message")
    session_id = None
    try:
        data = json.loads(body)
        session_id = data["session_id"]
        config = data["config"]

        load_configuration(session_id, config)

        logging.info("Adding runner for session {} to pool".format(session_id))

        # run model in separate thread, remove stdout=subprocess.DEVNULL if you want to see output
        f = pool.submit(
            subprocess.call, 
            # run music box with this configuration
            f"/music-box/build/music_box {config_file_path}", 
            shell=True, 
            cwd=working_directory, 
            stdout=subprocess.DEVNULL
        )
        f.add_done_callback(functools.partial(music_box_exited_callback, session_id, working_directory))
    except Exception as e:
        error = {"error.json": str(e), "session_id": session_id}
        publish_message(error)
        logging.exception('Setting up run failed')


def main():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
    with pika.BlockingConnection(connParam) as connection:
        channel = connection.channel()

        channel.queue_declare(queue='run_queue')
        channel.basic_consume(queue='run_queue',
                            on_message_callback=run_queue_callback,
                            auto_ack=True)

        logging.info("Waiting for model_finished_queue messages")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

if __name__ == '__main__':
    # config to easily see threads and process IDs
    logging.basicConfig(
        level=logging.DEBUG,
        format=("%(relativeCreated)04d %(process)05d %(threadName)-10s "
                "%(levelname)-5s %(msg)s"))
    try:
        if check_for_rabbit_mq():
            main()
        else:
            logging.error('[ERR!] RabbitMQ server is not running.')
            sys.exit(1)
    except KeyboardInterrupt:
        logging.debug('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
