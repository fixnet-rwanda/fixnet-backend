from rest_framework import serializers


class AIChatRequestSerializer(serializers.Serializer):
    technician_id = serializers.UUIDField()
    prompt = serializers.CharField()
