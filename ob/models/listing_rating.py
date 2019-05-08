from django.db import models


class ListingRating(models.Model):
    ratingID = models.CharField(primary_key=True, max_length=46)
    average = models.FloatField(default=0, null=True)
    overall = models.IntegerField(default=0, null=True)
    quality = models.IntegerField(default=0, null=True)
    description = models.IntegerField(default=0, null=True)
    delivery_speed = models.IntegerField(default=0, null=True)
    customer_service = models.IntegerField(default=0, null=True)
    review = models.TextField(default='', blank=True)
    timestamp = models.DateTimeField(null=True)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', related_name='ratings',
                                on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ob'

    def get_average(self):
        return float(
            self.overall + self.quality + self.description +
            self.delivery_speed + self.customer_service) / 5.0

    def save(self, *args, **kwargs):
        self.average = self.get_average()
        super(ListingRating, self).save(*args, **kwargs)
        self.listing.save()
