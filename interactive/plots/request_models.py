from rest_framework import serializers

class GetFlowSerializer(serializers.Serializer):
    includedSpecies = serializers.CharField()
    blockedSpecies = serializers.CharField()
    startStep = serializers.IntegerField()
    endStep = serializers.IntegerField()
    maxArrowWidth = serializers.FloatField()
    arrowScalingType = serializers.CharField()
    minMolval = serializers.FloatField()
    maxMolval = serializers.FloatField()
    currentMinValOfGraph = serializers.FloatField()
    currentMaxValOfGraph = serializers.FloatField()
    isPhysicsEnabled = serializers.BooleanField()