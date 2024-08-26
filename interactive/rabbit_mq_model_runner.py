import sys
import shutil
import logging
import json
import functools
import os
from shared.rabbit_mq import consume, rabbit_is_available, publish_message, ConsumerConfig
from shared.configuration_utils import load_configuration, \
    get_working_directory, \
    get_session_path
from api.run_status import RunStatus
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor as Pool

from acom_music_box import MusicBox


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


def partmc_exited_callback(session_id, future):
    body = {'session_id': session_id}
    route_key = RunStatus.DONE.value
    if future.exception() is not None:
        body['error.json'] = json.dumps(
            {'message': str(future.exception())})
        route_key = RunStatus.ERROR.value
        logging.info("[" + session_id + "] Got exception: %s" % future.exception())
    else:
        logging.info("[" + session_id + "] PartMC Model finished.")

        output_directory = f"/partmc/partmc-volume/{session_id}"
        body['partmc_output_path'] = f"/music-box-interactive/interactive/partmc-volume/{session_id}"

        # check number of output files in output directory
        logging.info(f"output directory: {output_directory}")
        output_files = getListOfFiles(output_directory)
        if len(output_files) == 0:
            logging.info("[" + session_id + "] No output files found, exiting")
            shutil.rmtree(output_directory)
            route_key = RunStatus.ERROR.value
            body['error.json'] = json.dumps(
                {'message': 'No output files found for PartMC'})

    logging.info(f"Sending message to {route_key}")
    logging.info(f"Message: {body}")
    publish_message(route_key=route_key, message=body)


def run_request_callback(ch, method, properties, body):
    logging.info("Received run message")
    session_id = None
    try:
        data = json.loads(body)
        session_id = data["session_id"]
        config = data["config"]

        load_configuration(session_id, config, keep_relative_paths=True)
        logging.info(f"Adding runner for session {session_id} to pool")

        # Searching through the payload json to see if aerosol is present. If it is, run musicbox
        # and PartMC. If it isn't, run musicbox only.
        aerosols_payload = config.get('aerosols', {})
        contains_aerosol = len(
            aerosols_payload.get(
                'aerosolSpecies',
                [])) != 0 or len(
            aerosols_payload.get(
                'aerosolPhase',
                [])) != 0

        if contains_aerosol:
            run_partmc(session_id)
        else:
            run_music_box(session_id)

    except Exception as e:
        body = {"error.json": json.dumps(
            {'message': str(e)}), "session_id": session_id}
        publish_message(route_key=RunStatus.ERROR.value, message=body)
        logging.exception('Setting up run failed')


def run_music_box(session_id):
    path = get_session_path(session_id)
    config_file_path = os.path.join(path, 'my_config.json')
    logging.info(f"config file path: {config_file_path}")

    music_box = MusicBox()
    music_box.readConditionsFromJson(config_file_path)

    campConfig = os.path.join(
        os.path.dirname(config_file_path),
        music_box.config_file)

    working_directory = get_working_directory(session_id)

    music_box.create_solver(campConfig)

    future = pool.submit(music_box.solve, os.path.join(working_directory, "output.csv"))

    future.add_done_callback(
        functools.partial(
            music_box_exited_callback,
            session_id,
            working_directory
        )
    )

    body = {"session_id": session_id}
    publish_message(route_key=RunStatus.RUNNING.value, message=body)


def run_partmc(session_id):
    from partmc_model.default_partmc import run_pypartmc_model
    os.makedirs(f"/partmc/partmc-volume/{session_id}", exist_ok=True)
    body = {"session_id": session_id}
    publish_message(route_key=RunStatus.RUNNING.value, message=body)
    future = pool.submit(
        run_pypartmc_model,
        session_id
    )
    future.add_done_callback(
        functools.partial(
            partmc_exited_callback,
            session_id,
        ))


def main():
    consume(consumer_configs=[
        ConsumerConfig(
            route_keys=['run_request'], callback=run_request_callback
        )
    ])


def getListOfFiles(dirName):
    return [os.path.join(root, file) for root, _, files in os.walk(dirName) for file in files]


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
