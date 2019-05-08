from django.db import models


class Image(models.Model):
    filename = models.TextField(null=True)
    original = models.TextField(null=True)
    large = models.TextField(null=True)
    medium = models.TextField(null=True)
    small = models.TextField(null=True)
    tiny = models.TextField(null=True)

    class Meta:
        app_label = 'ob'
