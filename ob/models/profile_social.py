from django.db import models


class ProfileSocial(models.Model):
    profile = models.ForeignKey('Profile',
                                related_name='social',
                                on_delete=models.CASCADE)
    social_type = models.TextField(blank=True, default='')
    username = models.TextField(blank=True, default='')
    proof = models.TextField(blank=True, default='')
