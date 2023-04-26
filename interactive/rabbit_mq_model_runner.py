from concurrent.futures import ThreadPoolExecutor as Pool
from model_driver.session_model_runner import SessionModelRunner
from multiprocessing import cpu_count
from shared.utils import check_for_rabbit_mq

import functools
import json
import logging
import os
import pika
import shutil
import subprocess
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')

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


# disable propagation
logging.getLogger("pika").propagate = False
def callback(session_id, config_files_dict, future):
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connParam = pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, credentials=credentials)
    connection = pika.BlockingConnection(connParam)

    if future.exception() is not None:
        logging.info("["+session_id+"] Got exception: %s" % future.exception())
    else:
        logging.info("["+session_id+"] Model finished.")
        # 1) check for output files (in /build)
        # 2) send output files to model_finished_queue
        # 3) delete config files and binary files from file system

        # check number of output files in /build
        build_dir = os.path.join('/music-box/build', session_id)
        output_files = getListOfFiles(build_dir)
        if len(output_files) == 0:
            logging.info("["+session_id+"] No output files found, exiting")
            return
        # body to send to model_finished_queue
        body = {'session_id': session_id}
        complete_path = os.path.join(build_dir, 'MODEL_RUN_COMPLETE')
        csv_path = os.path.join(build_dir, 'output.csv')
        error_path = os.path.join(build_dir, 'error.json')
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
        shutil.rmtree(build_dir)
        # send body to model_finished_queue
        channel = connection.channel()
        channel.queue_declare(queue='model_finished_queue')
        channel.basic_publish(exchange='',
                                routing_key='model_finished_queue',
                                body=json.dumps(body))
        logging.info("["+session_id+"] Sent output files to model_finished_queue")


def run_queue_callback(ch, method, properties, body):
    data = json.loads(body)
    # grab config files and binary files from data
    config_files = data["config_files"]
    binary_files = data["binary_files"]
    session_id = data["session_id"]
    # base directory for config files
    config_file_path = os.path.join('/music-box-interactive/interactive/configs', session_id)
    files_array = [] # will be used to parse results on callback
    # create directory if it doesn't exist
    if not os.path.exists(config_file_path):
        os.makedirs(config_file_path)
    # put config files and binary files into file system
    for config_file in config_files:
        files_array.append(config_file)
        full_path = os.path.join(config_file_path, config_file[1:])
        # if config file does not exist, create it
        dirname = os.path.dirname(full_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # write config file to file system
        with open(full_path, 'w') as f:
            # dump json
            json.dump(config_files[config_file], f)
    for binary_file in binary_files:
        files_array.append(binary_file)
        full_path = os.path.join(config_file_path, binary_file[1:])
        # if config file does not exist, create it
        dirname = os.path.dirname(full_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # write binary file to file system
        with open(full_path, 'w') as f:
            f.write(binary_files[binary_file])
    logging.info("Adding runner for session {} to pool".format(session_id))
    # run model
    
    runner = SessionModelRunner(session_id)
    runner.set_run_as_rabbit(True) # set to true if running as rabbitmq
    runner.run() # sets up everything

    new_callback_function = functools.partial(callback, session_id, files_array) # pass session_id and files_array to callback function
    f = pool.submit(subprocess.call, "../music_box ./mb_configuration/my_config.json", shell=True, cwd=runner.mb_dir, stdout=subprocess.DEVNULL) # run model in separate thread, remove stdout=subprocess.DEVNULL if you want to see output
    f.add_done_callback(new_callback_function) # calls callback when model is finished

    
    # pool.shutdown(wait=False) # no .submit() calls after that point

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
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
        print("Stopping consuming")
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
        filename='logs.log',
        filemode='w+',
        level=logging.INFO,
        format=("%(relativeCreated)04d %(process)05d %(threadName)-10s "
                "%(levelname)-5s %(msg)s"))
    try:
        if check_for_rabbit_mq():
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
