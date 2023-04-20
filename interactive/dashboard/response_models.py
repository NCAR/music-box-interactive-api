from enum import Enum
from rest_framework import serializers

class RunStatus(Enum):
    RUNNING = 'RUNNING'
    WAITING = 'WAITING'
    NOT_FOUND = 'NOT_FOUND'
    DONE = 'DONE'
    ERROR = 'ERROR'
    UNKNOWN = 'UNKNOWN'

class PollingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(choice.name, choice.value) for choice in RunStatus])
    error_code = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)