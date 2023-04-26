from django.conf import settings
from django.http import Http404

import json
import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)


def load_example(example):
    conditions = {}
    mechanism = {}

    example_path = os.path.join(
        settings.BASE_DIR, 'dashboard/static/examples', example)

    files = [os.path.join(dp, f)
             for dp, _, fn in os.walk(example_path) for f in fn]
    logger.info(files)
    if not files:
        raise Http404("No files in example folder")

    for file in files:
        if 'species.json' in file:
            with open(file) as contents:
                mechanism['species'] = json.load(contents)
        if 'reactions.json' in file:
            with open(file) as contents:
                mechanism['reactions'] = json.load(contents)
        if 'my_config.json' in file:
            with open(file) as contents:
                conditions = json.load(contents)
            if "initial conditions" in conditions:
                rates_file = list(conditions["initial conditions"].keys())[0]
                logger.debug(f"Found rates file: {rates_file}")
                path = [f for f in files if rates_file in f]
                if len(path) > 0:
                    rates_file = path[0]
                    df = pd.read_csv(rates_file)
                    conditions["initial conditions"] = df.to_dict()
                    del df
                else:
                    logger.warning("Could not find initial rates condition file")

    return conditions, mechanism
