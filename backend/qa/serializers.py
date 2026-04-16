from rest_framework import serializers


class QARequestSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=1)


class SourceSerializer(serializers.Serializer):
    source_type = serializers.CharField()
    source_id = serializers.CharField()
    title = serializers.CharField()
    summary = serializers.CharField()
    url = serializers.CharField()


class QAResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = SourceSerializer(many=True)
    keywords_used = serializers.DictField()
    latency_ms = serializers.IntegerField()
