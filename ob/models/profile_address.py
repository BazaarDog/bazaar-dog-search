from django.db import models


class ProfileAddress(models.Model):
    IPV4 = 0
    IPV6 = 1
    TOR = 2

    ADDRESS_TYPE_CHOICES = (
        (IPV4, 'ipv4'),
        (IPV6, 'ipv6'),
        (TOR, 'onion'),
    )
    ADDRESS_TYPE_DICT = dict(ADDRESS_TYPE_CHOICES)

    profile = models.ForeignKey('Profile',
                                related_name='addresses',
                                on_delete=models.CASCADE)
    address = models.TextField(blank=True, default='')
    address_type = models.IntegerField(choices=ADDRESS_TYPE_CHOICES,
                                       null=True,
                                       blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ob'
