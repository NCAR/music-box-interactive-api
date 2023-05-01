import json
import logging
import numpy as np
import os
import pandas as pd
import shutil


def get_session_path(session_id):
    '''Returns the absolute path to the configuration folder for a given session id'''
    os.makedirs(os.environ['MUSIC_BOX_CONFIG_DIR'], exist_ok=True)
    path = os.path.join('/music-box-interactive/interactive/configs', session_id)
    os.makedirs(path)
    return path


def get_config_file_path(session_id):
    '''Returns the absolute path to the MusicBox configuration file'''
    return os.path.join(get_session_path(session_id), "my_config.json")


def get_working_directory(session_id):
    '''Returns the working directory for model runs for a given session id'''
    os.makedirs(os.environ['MUSIC_BOX_BUILD_DIR'], exist_ok=True)
    path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], session_id)
    os.makedirs(path, exist_ok=True)
    return path


def get_zip_file_path(session_id):
    '''Returns the path for a zip file for a given session id'''
    os.makedirs(os.environ['MUSIC_BOX_ZIP_DIR'], exist_ok=True)
    path = os.path.join(os.environ['MUSIC_BOX_ZIP_DIR'], session_id)
    os.makedirs(path, exist_ok=True)
    return path


def load_configuration(session_id, config):
    '''Loads a JSON configuration from the client and saves it in MusicBox format'''
    try:
        session_path = get_session_path(session_id)
        config_file_path = get_config_file_path(session_id)

        camp_config = None
        full_camp_config_path = None
        for model_config in config["conditions"]["model components"]:
            if ("type" in model_config) and (model_config["type"] == "CAMP"):
                camp_config = model_config["configuration file"]
                full_camp_config_path = os.path.join(session_path, camp_config)
                # update the camp configuration path to point to the full path on the file system
                # so that the model can find it
                model_config["configuration file"] = full_camp_config_path
        if camp_config is None:
            raise Exception("Could not find camp config")

        camp_dir = os.path.dirname(full_camp_config_path)
        mechanism_config = os.path.join(camp_dir, 'mechanism.json')
        # make a workding directory in the music box build folder
        # this prevents jobs from differing sessions from overwriting each other
        working_directory = get_working_directory(session_id)
        logging.info(f"Working directory: {working_directory}")

        os.makedirs(camp_dir, exist_ok=True)
        if not os.path.exists(working_directory):
            raise Exception("Did not create working directory")

        if "evolving conditions" in config["conditions"] and isinstance(config["conditions"]["evolving conditions"], list):
            evolving = config["conditions"]["evolving conditions"]
            logging.info(evolving)
            if len(evolving) > 1:
                headers, vals = evolving[0], np.array(evolving[1:])
                data = {}
                for idx, column in enumerate(headers):
                    data[column] = vals[:, idx]
                logging.info(data)
                csv_path = os.path.join(session_path, "evolving_conditions.csv")
                pd.DataFrame(data).to_csv(csv_path, index=False)
                config["conditions"]["evolving conditions"] = {
                    csv_path: {}
                }

        # write the box model configuration
        with open(config_file_path, 'w') as f:
            json.dump(config["conditions"], f)

        # write the mechanism to the camp configuration 
        with open(full_camp_config_path, 'w') as f:
            json.dump({"camp-files": [mechanism_config]}, f)

        # write the mechanism to the camp configuration 
        with open(mechanism_config, 'w') as f:
            json.dump(config["mechanism"], f)

    except Exception as e:
        error = {"error.json": str(e), "session_id": session_id}
        publish_message(error)
        logging.exception('Loading configuration failed')


def compress_configuration(session_id):
    '''Creates a compressed file holding the previously loaded configuration for a given session id'''

    config_folder = get_session_path(session_id)
    zip_file_path = get_zip_file_path(session_id)
    logging.info(f'Compressing configuration: {config_folder} to: {zip_file_path}')
    make_archive(config_folder, zip_file_path)


def make_archive(source, destination):
    '''Creates a compressed version of the source folder. From: http://www.seanbehan.com/how-to-use-python-shutil-make_archive-to-zip-up-a-directory-recursively-including-the-root-folder/'''
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to   = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move(f'{name}.{format}', destination)


def extract_configuration(session_id, zipfile):
    '''Extracts a compressed configuration and returns it as JSON'''
    content = zipfile.read()
    with open(get_zip_file_path(session_id), 'wb') as f:
        f.write(content)
    with ZipFile(get_zip_file_path(session_id, 'r') as zip:
        zip.extractall(get_session_path(session_id)
    return True
