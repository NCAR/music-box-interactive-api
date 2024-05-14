# these imports must come first # noqa: E402
import os  # noqa: E402
import django  # noqa: E402
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage.settings')  # noqa: E402
django.setup()  # noqa: E402

from api.run_status import RunStatus
from api.controller import get_model_run
from shared.configuration_utils import load_configuration, \
    get_config_file_path, \
    get_working_directory
from shared.rabbit_mq import consume, rabbit_is_available, publish_message, ConsumerConfig

import functools
import json
import logging
import os
import shutil
import subprocess
import sys

# main model runner interface class for rabbitmq and actual model runner
# 1) listen to run_queue
# 2) run model when receive message
# 3) send message to model_finished_queue when model is finished

# disable propagation
logging.getLogger("pika").propagate = False

# updates the status of the model run in the database
def set_model_run_status(session_id, status, error=None, output=None):
    model_run = get_model_run(session_id)
    model_run.status = status
    model_run.results['error'] = error
    model_run.results['/output.csv'] = output
    model_run.save()
    logging.info(f"Model run saved to database for session {session_id}")


def music_box_exited_callback(session_id, output_directory):
    logging.info("[" + session_id + "] Model finished.")
    # 1) check for output files (in /build)
    # 2) save results to the database
    # 3) delete config files and binary files from file system

    # check number of output files in /build
    logging.info(f"output directory: {output_directory}")
    output_files = getListOfFiles(output_directory)
    if len(output_files) == 0:
        logging.info("[" + session_id + "] No output files found, exiting")
        set_model_run_status(
            session_id,
            RunStatus.ERROR.value,
            json.dumps({"message": "No output files found"}),
        )
        return
    # check for output.csv, error.json, warning.json, MODEL_RUN_COMPLETE
    complete_path = os.path.join(output_directory, "MODEL_RUN_COMPLETE")
    csv_path = os.path.join(output_directory, "output.csv")
    error_path = os.path.join(output_directory, "error.json")
    warning_path = os.path.join(output_directory, "warning.json")
    output_data = None
    if os.path.exists(csv_path):
        # read csv file
        with open(csv_path, "r") as f:
            output_data = f.read()
    if os.path.exists(complete_path):
        set_model_run_status(
            session_id, RunStatus.DONE.value, error=None, output=output_data
        )
    elif os.path.exists(error_path):
        # read error file
        with open(error_path, "r") as f:
            set_model_run_status(
                session_id, RunStatus.ERROR.value, error=f.read(), output=output_data
            )
    elif os.path.exists(warning_path):
        # read warning file
        with open(warning_path, "r") as f:
            set_model_run_status(
                session_id, RunStatus.ERROR.value, error=f.read(), output=output_data
            )
    else:
        set_model_run_status(
            session_id,
            RunStatus.ERROR.value,
            error=json.dumps({"message": "Model run status unknown"}),
            output=output_data,
        )
    # remove all files to save space
    shutil.rmtree(output_directory)


def run_request_callback(ch, method, properties, body):
    logging.info("Received run message")
    session_id = None
    try:
        data = json.loads(body)
        session_id = data["session_id"]
        config = data["config"]

        load_configuration(session_id, config)
        config_file_path = get_config_file_path(session_id)
        working_directory = get_working_directory(session_id)

        logging.info(f"Adding runner for session {session_id} to pool")

        # Searching through the payload json to see if aerosol is present. If it is, run musicbox
        # and PartMC. If it isn't, run musicbox only.
        payload = config.get('config', {})
        mechanism_in_payload = payload.get('mechanism', {})
        contains_aerosol = 'aerosol' in mechanism_in_payload
        if not contains_aerosol:
            # run model in separate thread, remove stdout=subprocess.DEVNULL if you
            # want to see output
            process = subprocess.Popen(
                # run music box with this configuration
                # config_file_path is chamber.spec in the case of partmc
                f"/music-box/build/music_box {config_file_path}",
                shell=True,
                cwd=working_directory,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            set_model_run_status(session_id, RunStatus.RUNNING.value)
            for line in process.stderr:
                logging.info(line.decode())
                if "Solver failed" in line.decode():
                    process.kill()  # Kill the process if the string is found
                    set_model_run_status(
                        session_id,
                        RunStatus.ERROR.value,
                        error=json.dumps(
                            {'message': 'Solver failed'}))
                    return
            music_box_exited_callback(session_id, working_directory)
    except Exception as e:
        set_model_run_status(
            session_id,
            RunStatus.ERROR.value,
            error=json.dumps(
                {'message': str(e)}))
        logging.exception('Setting up run failed')


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
