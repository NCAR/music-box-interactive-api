from concurrent.futures import ThreadPoolExecutor as Pool
from multiprocessing import cpu_count
from api.run_status import RunStatus
from shared.configuration_utils import load_configuration, \
    get_config_file_path, \
    get_working_directory
from shared.rabbit_mq import consume, rabbit_is_available, publish_message, ConsumerConfig
import django  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage.settings')  
django.setup() 
import functools
import json
import logging
import os
import shutil
import subprocess
import sys
from api.controller import get_model_run
 

# main model runner interface class for rabbitmq and actual model runner
# 1) listen to run_queue
# 2) run model when receive message
# 3) send message to model_finished_queue when model is finished

# cpu_count() returns number of cores on machine
# this will run as many threads as there are cores (and will be faster but very cpu intensive)
# set this number to 1 if you want to run everything in one thread -- if you are running on a server
# without much cpu power/want to reduce energy usage you should probably
# set this to 1
# sets max number of workers to add to pool
pool = Pool(max_workers=cpu_count())

# disable propagation
logging.getLogger("pika").propagate = False


def music_box_exited_callback(session_id, output_directory, future):
    if future.exception() is not None:
        logging.info(
            "[" + session_id + "] Got exception: %s" %
            future.exception())
    else:
        logging.info("[" + session_id + "] MusicBox Model finished.")
        # 1) check for output files (in /build)
        # 2) send output files to model_finished_queue
        # 3) delete config files and binary files from file system

        # check number of output files in /build
        logging.info(f"output directory: {output_directory}")
        output_files = getListOfFiles(output_directory)
        if len(output_files) == 0:
            logging.info("[" + session_id + "] No output files found, exiting")
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
        shutil.rmtree(output_directory)
        # send body to model_finished_queue
        publish_message(route_key=RunStatus.DONE.value, message=body)
        logging.info(
            "[" + session_id + "] Sent output files to model_finished_queue")
        
def partmc_exited_callback(session_id, output_directory, future):
    if future.exception() is not None:
        logging.info(
            "[" + session_id + "] Got exception: %s" %
            future.exception())
    else:
        logging.info("[" + session_id + "] PartMC Model finished.")
        # 1) check for output files (in /out)
        # 2) send output files to DB directly
        # 3) delete config files and binary files from file system
        
    
        # Copy the data into a new directory called "shared" in the volume. Just for testing
        src_dir = output_directory
        dst_dir = "/partmc/partmc-volume/shared"
        shutil.copytree(src_dir, dst_dir)
        # remove all files to save space
        shutil.rmtree(output_directory)
        volume_directory = dst_dir

        # check number of output files in output directory
        logging.info(f"output directory: {volume_directory}")
        output_files = getListOfFiles(volume_directory)
        if len(output_files) == 0:
            logging.info("[" + session_id + "] No output files found, exiting")
            # delete only for the sake of testing
            shutil.rmtree("/partmc/partmc-volume/shared/out")
            return
        # body to send to DB
        body = {'session_id': session_id, "address": volume_directory}
        # send body to model_finished_queue
        model_run = get_model_run(session_id)
        # delete only for the sake of testing
        shutil.rmtree("/partmc/partmc-volume/shared/out")
        
        model_run.results['partmc_output'] = body
        model_run.save()
        logging.info(
            "[" + session_id + "] Sent output files to Database")

def run_request_callback(ch, method, properties, body):
    logging.info("Received run message")
    session_id = None
    try:
        data = json.loads(body)
        session_id = data["session_id"]
        config = data["config"]

        load_configuration(session_id, config)
        logging.info(f"Adding runner for session {session_id} to pool")
        
        # Searching through the payload json to see if aerosol is present. If it is, run musicbox
        # and PartMC. If it isn't, run musicbox only.
        payload = config.get('config',{})
        mechanism_in_payload = payload.get('mechanism',{})
        contains_aerosol = 'aerosol' in mechanism_in_payload
        
        if not contains_aerosol:
            run_music_box(session_id)
           
        # Just for testing
        else:
            run_partmc(session_id)
            
    except Exception as e:
        body = {"error.json": json.dumps(
            {'message': str(e)}), "session_id": session_id}
        publish_message(route_key=RunStatus.ERROR.value, message=body)
        logging.exception('Setting up run failed')

def run_music_box(session_id):
    config_file_path = get_config_file_path(session_id)
    working_directory = get_working_directory(session_id)
    # run model in separate thread, remove stdout=subprocess.DEVNULL if you
    # want to see output
    f = pool.submit(
        subprocess.call,
        # run music box with this configuration
        f"/music-box/build/music_box {config_file_path}",
        shell=True,
        cwd=working_directory,            
        stdout=subprocess.DEVNULL
        )
    f.add_done_callback(
        functools.partial(
        music_box_exited_callback,
        session_id,
        working_directory))
    body = {"session_id": session_id}
    publish_message(route_key=RunStatus.RUNNING.value, message=body)
    
def run_partmc(session_id):
    # This is now still a test. config file path will not be used
    config_file_path = get_config_file_path(session_id)
    # working_directory = get_working_directory(session_id)
    working_directory = "/partmc/scenarios/4_chamber"
    # For testing's sake
    if os.path.exists("/partmc/scenarios/4_chamber/out"):
        shutil.rmtree("/partmc/scenarios/4_chamber/out")
    os.mkdir("/partmc/scenarios/4_chamber/out")
    f = pool.submit(
        subprocess.call,
        # run partmc with this configuration
        f"/build/partmc /partmc/scenarios/4_chamber/chamber.spec", # config_file_path is chamber.spec for the testing purpose
        shell=True,
        # Here it moves to the same directory of the "out" directory
        cwd = working_directory,
        stdout=subprocess.DEVNULL
        )
    f.add_done_callback(
        functools.partial(
            partmc_exited_callback,
            session_id,
            # This is the output directory
            "/partmc/scenarios/4_chamber/out"))
    body = {"session_id": session_id}
    publish_message(route_key=RunStatus.RUNNING.value, message=body)

def main():
    consume(consumer_configs=[
        ConsumerConfig(
            route_keys=['run_request'], callback=run_request_callback
        )
    ])


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
        if rabbit_is_available():
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

