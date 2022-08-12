import os
import logging
import json

# open settings.json and set environment variables
def update_environment_variables():
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    settings_location = os.path.join(__location__, 'settings.json')
    with open(settings_location) as f:
        settings = json.load(f)
        os.environ["rabbit-mq-host"] = settings["rabbit-mq-host"]
        os.environ["rabbit-mq-port"] = settings["rabbit-mq-port"]
        os.environ["queue_for_requested_model_runs"] = settings["queue_for_requested_model_runs"]
        os.environ["queue_for_model_run_results"] = settings["queue_for_model_run_results"]
        os.environ["log_level"] = settings["log_level"]
        os.environ["mongo-db-host"] = settings["mongo-db-host"]
        os.environ["mongo-db-port"] = settings["mongo-db-port"]
        # set log level
        if os.environ["log_level"] == "DEBUG":
            logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s', level=logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
        elif os.environ["log_level"] == "INFO":
            logging.basicConfig(format='%(asctime)s - [INFO] %(message)s', level=logging.INFO)
            logging.getLogger().setLevel(logging.INFO)
        f.close()