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

    @classmethod
    def create_from_json(cls, parent, data):

        option = getattr(ShippingOptions, data['type'])
        c, ccreated = cls.objects.get_or_create(listing=parent,
                                                name=data['name'])
        c.option_type = option
        if len(data['services']) == 1:
            if 'name' in data['services'][0].keys():
                c.service_name = data['services'][0]['name']
            if 'price' in data['services'][0].keys():
                c.service_price = data['services'][0]['price']
            if 'estimatedDelivery' in data['services'][0].keys():
                c.service_estimated_delivery = data['services'][0][
                    'estimatedDelivery']

        c.regions = data['regions']
        return c
