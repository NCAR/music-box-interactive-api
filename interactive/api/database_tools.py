from api import models
from api.run_status import RunStatus

import hashlib
import json
import logging

logger = logging.getLogger(__name__)

# get model run based on uid
def get_model_run(uid):
    try:
        model = models.ModelRun.objects.get(uid=uid)
        return model
    except models.ModelRun.DoesNotExist:
        # if not, create new model run
        model_run = create_model_run(uid)
        return model_run


# get results of model run
def get_results(uid):
    return get_model_run(uid).results


# create new model run
def create_model_run(uid):
    model_run = models.ModelRun(uid=uid)
    model_run.save()
    return model_run


# get status of a run
def get_run_status(uid):
    error = {}
    try:
        model = get_model_run(uid)
        logger.debug(f"model: {model} | {model.status}")
        status = RunStatus(model.status)
        if status == RunStatus.ERROR:
            error = json.loads(model.results['error'])
    except models.ModelRun.DoesNotExist:
        status = RunStatus.NOT_FOUND
        logger.info(f"[{uid}] model run not found for user")
    return {'status': status, 'error': error}