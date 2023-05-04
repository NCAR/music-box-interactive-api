from enum import Enum
from rest_framework import serializers

import json
import base64

class RunStatus(Enum):
    RUNNING = 'RUNNING'
    WAITING = 'WAITING'
    NOT_FOUND = 'NOT_FOUND'
    DONE = 'DONE'
    ERROR = 'ERROR'
    UNKNOWN = 'UNKNOWN'

class RunStatusEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RunStatus):
            return obj.value
        return super().default(obj)

class PollingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(choice.name, choice.value) for choice in RunStatus])
    error_code = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)

class ConfigSerializer(serializers.Serializer):
    mechanism = serializers.JSONField()
    conditions = serializers.JSONField()

    class Meta:
        ref_name = "ConfigResponse"

class FileSerializer(serializers.Serializer):
    filename = serializers.CharField()
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        with open(obj, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')