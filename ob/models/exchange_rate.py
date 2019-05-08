from django.db import models


class ExchangeRate(models.Model):
    symbol = models.TextField(null=True)
    rate = models.FloatField(default=0)
    base_unit = models.IntegerField(default=100)

    class Meta:
        app_label = 'ob'