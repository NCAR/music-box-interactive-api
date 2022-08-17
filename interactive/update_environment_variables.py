import os
import logging
import json


# open settings.json and set environment variables
def update_environment_variables():
    ff = os.path.dirname(__file__)
    __location__ = os.path.realpath(os.path.join(os.getcwd(), ff))

    settings_location = os.path.join(__location__, 'settings.json')
    with open(settings_location) as f:
        settings = json.load(f)
        # load environment variables into settings via json dump
        os.environ.update(settings)
        # set log level
        if os.environ["log_level"] == "DEBUG":
            logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s',
                                level=logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
        elif os.environ["log_level"] == "INFO":
            logging.basicConfig(format='%(asctime)s - [INFO] %(message)s',
                                level=logging.INFO)
            logging.getLogger().setLevel(logging.INFO)
        f.close()
