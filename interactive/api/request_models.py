from rest_framework import serializers

class LoadExampleSerializer(serializers.Serializer):
    example = serializers.CharField(required=True)

class RunSerializer(serializers.Serializer):
    mechanism = serializers.JSONField()
    conditions = serializers.JSONField()