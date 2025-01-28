import validators
from rest_framework import serializers

from .models import URLInfo


class URLInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLInfo
        fields = (
            "pk",
            "url",
            "domain_name",
            "protocol",
            "title",
            "images",
            "stylesheets_count",
            "created_at",
        )


class URLPostSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        if not validators.url(value):
            raise serializers.ValidationError("Invalid URL provided.")
        return value
