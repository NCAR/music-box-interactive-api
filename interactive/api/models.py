from api.run_status import RunStatus
from django.db import models


class ModelRun(models.Model):
    # uid of user [CharField]
    uid = models.CharField(max_length=60, primary_key=True)

    # status of the model run [CharField]
    status = models.CharField(
        max_length=50, choices=[
            (status.value, status.value) for status in RunStatus])

    # results name and binary data [JSONField]
    results = models.JSONField(default=dict)  # {name: binary data}
