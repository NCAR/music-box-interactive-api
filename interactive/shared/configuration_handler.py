import json
import logging
import numpy as np
import os
import pandas as pd
import shutil
from zipfile import ZipFile


def get_session_path(session_id):
    '''Returns the absolute path to the configuration folder for a given session id'''
    os.makedirs(os.environ['MUSIC_BOX_CONFIG_DIR'], exist_ok=True)
    os.makedirs(os.path.join(os.environ['MUSIC_BOX_CONFIG_DIR'], session_id), exist_ok=True)
    path = os.path.join(os.environ['MUSIC_BOX_CONFIG_DIR'], session_id, "configuration")
    os.makedirs(path, exist_ok=True)
    return path


def remove_session_folder(session_id):
    '''Removes the folder containing the configuration for a given session'''
    shutil.rmtree(os.path.join(os.environ['MUSIC_BOX_CONFIG_DIR'], session_id))


def get_config_file_path(session_id):
    '''Returns the absolute path to the MusicBox configuration file'''
    return os.path.join(get_session_path(session_id), "my_config.json")


def get_working_directory(session_id):
    '''Returns the working directory for model runs for a given session id'''
    os.makedirs(os.environ['MUSIC_BOX_BUILD_DIR'], exist_ok=True)
    path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], session_id)
    os.makedirs(path, exist_ok=True)
    return path


def get_zip_folder_path(session_id):
    '''Returns the folder for compressed configurations for a given session'''
    os.makedirs(os.environ['MUSIC_BOX_ZIP_DIR'], exist_ok=True)
    path = os.path.join(os.environ['MUSIC_BOX_ZIP_DIR'], session_id)
    os.makedirs(path, exist_ok=True)
    return path


def get_unzip_folder_path(session_id):
    '''Returns the folder to unzip configurations into'''
    os.makedirs(os.environ['MUSIC_BOX_CONFIG_DIR'], exist_ok=True)
    path = os.path.join(os.environ['MUSIC_BOX_CONFIG_DIR'], session_id)
    os.makedirs(path, exist_ok=True)
    return path


def get_zip_file_path(session_id):
    '''Returns the path for a zip file for a given session id'''
    return os.path.join(get_zip_folder_path(session_id), "config.zip")


def remove_zip_folder(session_id):
    '''Removes the folder holding a compressed configuration for a session'''
    shutil.rmtree(get_zip_folder_path(session_id))


def load_configuration(session_id, config, keep_relative_paths=False):
    '''Loads a JSON configuration from the client and saves it in MusicBox format'''
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
            if keep_relative_paths:
                model_config["configuration file"] = camp_config
            else:
                model_config["configuration file"] = full_camp_config_path
    if camp_config is None:
        raise Exception("Could not find camp config")

    camp_dir = os.path.dirname(full_camp_config_path)
    species_config   = os.path.join(camp_dir, 'species.json')
    reactions_config = os.path.join(camp_dir, 'reactions.json')
    # make a workding directory in the music box build folder
    # this prevents jobs from differing sessions from overwriting each other
    working_directory = get_working_directory(session_id)

    os.makedirs(camp_dir, exist_ok=True)
    if not os.path.exists(working_directory):
        raise Exception("Did not create working directory")

    if "evolving conditions" in config["conditions"] and isinstance(config["conditions"]["evolving conditions"], list):
        evolving = config["conditions"]["evolving conditions"]
        if len(evolving) > 1:
            headers, vals = evolving[0], np.array(evolving[1:])
            data = {}
            for idx, column in enumerate(headers):
                data[column] = vals[:, idx]
            csv_path = os.path.join(session_path, "evolving_conditions.csv")
            pd.DataFrame(data).to_csv(csv_path, index=False)
            if keep_relative_paths:
                config["conditions"]["evolving conditions"] = {
                    "evolving_conditions.csv": {}
                }
            else:
                config["conditions"]["evolving conditions"] = {
                    csv_path: {}
                }

    # write the box model configuration
    with open(config_file_path, 'w') as f:
        json.dump(config["conditions"], f)

    # write the mechanism to the camp configuration
    with open(full_camp_config_path, 'w') as f:
        if keep_relative_paths:
            json.dump({"camp-files": ["species.json", "reactions.json"]}, f)
        else:
            json.dump({"camp-files": [species_config, reactions_config]}, f)

    # write the mechanism to the camp configuration
    with open(species_config, 'w') as f:
        json.dump(config["mechanism"]["species"], f)
    with open(reactions_config, 'w') as f:
        json.dump(config["mechanism"]["reactions"], f)


def filter_diagnostics(mechanism):
    '''Removes diagnostic species from the mechanism'''
    def species_filter(species):
        if "name" in species and species["name"][0:5]=="irr__":
            return False
        else:
            return True

    mechanism["species"]["camp-data"] = list(filter(species_filter, mechanism["species"]["camp-data"]))

    def product_filter(pair):
        key, value = pair
        if key[0:5]=="irr__":
            return False
        else:
            return True

    reactions = mechanism["reactions"]["camp-data"][0]["reactions"]
    for idx, rxn in enumerate(reactions):
        if "products" in rxn:
            reactions[idx]["products"] = dict(list(filter(product_filter, rxn["products"].items())))
    mechanism["reactions"]["camp-data"][0]["reactions"] = reactions

    return mechanism


def compress_configuration(session_id):
    '''Creates a compressed file holding the previously loaded configuration for a given session id'''
    config_folder = get_session_path(session_id)
    zip_file_path = get_zip_file_path(session_id)
    logging.info(f'Compressing configuration: {config_folder} to: {zip_file_path}')
    make_archive(config_folder, zip_file_path)
    remove_session_folder(session_id)


def make_archive(source, destination):
    '''Creates a compressed version of the source folder. From: http://www.seanbehan.com/how-to-use-python-shutil-make_archive-to-zip-up-a-directory-recursively-including-the-root-folder/'''
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to   = os.path.basename(source.strip(os.sep))
    logging.info(f"make archive {name} {format} {archive_from} {archive_to}")
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move(f'{name}.{format}', os.path.dirname(destination))


def extract_configuration(session_id, zipfile):
    '''Extracts a compressed configuration and returns it as JSON'''
    content = zipfile.read()
    with open(get_zip_file_path(session_id), 'wb') as f:
        f.write(content)
    with ZipFile(get_zip_file_path(session_id), 'r') as zip:
        zip.extractall(get_unzip_folder_path(session_id))
    remove_zip_folder(session_id)
    return True
