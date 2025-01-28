from django.db import models


class URLInfo(models.Model):
    url = models.URLField(unique=True)
    domain_name = models.CharField(max_length=255)
    protocol = models.CharField(max_length=10)
    title = models.CharField(max_length=255, null=True, blank=True)
    images = models.JSONField(default=list)
    stylesheets_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
