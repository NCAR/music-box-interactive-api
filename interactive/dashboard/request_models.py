from rest_framework import serializers

class LoadExampleSerializer(serializers.Serializer):
    example = serializers.CharField(required=True)