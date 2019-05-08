from django.db import models


class ListingImage(models.Model):
    listing = models.ForeignKey('Listing',
                                related_name='images',
                                on_delete=models.CASCADE)
    index = models.PositiveIntegerField(verbose_name='Index')
    filename = models.TextField(null=True)
    original = models.TextField(null=True)
    large = models.TextField(null=True)
    medium = models.TextField(null=True)
    small = models.TextField(null=True)
    tiny = models.TextField(null=True)

    class Meta:
        app_label = 'ob'
        unique_together = (
            'listing', 'index', 'filename',
            'original', 'large', 'medium',
            'small', 'tiny'
        )

