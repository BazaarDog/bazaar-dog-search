from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ob.models.listing import Listing


class ShippingOptions(models.Model):
    LOCAL_PICKUP = 0
    FIXED_PRICE = 1

    OPTION_TYPE_CHOICES = (
        (LOCAL_PICKUP, _('Local Pickup')),
        (FIXED_PRICE, _('Fixed Price')),
    )

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    name = models.TextField(null=True)
    option_type = models.IntegerField(choices=OPTION_TYPE_CHOICES, null=True,
                                      blank=True)
    regions = ArrayField(models.CharField(max_length=80),
                         null=True,
                         blank=True)
    service_name = models.TextField(null=True)
    service_price = models.TextField(null=True)
    service_estimated_delivery = models.TextField(null=True)

    class Meta:
        app_label = 'ob'
        unique_together = ('listing', 'name')

    @classmethod
    def create_from_json(cls, parent, data):

        c, ccreated = cls.objects.get_or_create(listing=parent,
                                                name=data.get('name'))
        option = getattr(ShippingOptions, data.get('type'))
        c.option_type = option
        services = data.get('services')
        if services:
            c.service_name = services[0].get('name')
            c.service_price = services[0].get('price')
            c.service_estimated_delivery = services[0].get('estimatedDelivery')
        c.regions = data.get('regions')
        return c

