from api.run_status import RunStatus
from django.db import models


class ModelRun(models.Model):
    uid = models.CharField(max_length=50, primary_key=True)

    # status of the model run [CharField]
    status = models.CharField(
        max_length=50, choices=[
            (status.value, status.value) for status in RunStatus])

    # results name and binary data [JSONField]
    results = models.JSONField(default=dict)  # {name: binary data}

    current_time = models.FloatField(default=0.0)

