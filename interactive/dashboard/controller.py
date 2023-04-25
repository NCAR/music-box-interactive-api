from django.conf import settings
from django.http import Http404

import json
import logging
import os

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

    return conditions, mechanism
