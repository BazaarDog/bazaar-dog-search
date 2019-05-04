import base64
from django.urls import reverse
from django.test import TestCase, override_settings
from ob.views import listing_icons, profile_icons


class IconTests(TestCase):

    @override_settings(DEBUG=True)
    def test_dev_listing_icon(self):
        url = reverse('logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, listing_icons['debug'])

    @override_settings(DEBUG=True)
    def test_dev_profile_icon(self):
        url = reverse('profile-logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, profile_icons['debug'])

    @override_settings(DEBUG=False, DEV=True)
    def test_stage_listing_icon(self):
        url = reverse('logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, listing_icons['stage'])

    @override_settings(DEBUG=False, DEV=True)
    def test_stage_profile_icon(self):
        url = reverse('profile-logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, profile_icons['stage'])

    @override_settings(DEBUG=False, DEV=False, ONION=True)
    def test_onion_listing_icon(self):
        url = reverse('logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, listing_icons['onion'])

    @override_settings(DEBUG=False, DEV=False, ONION=True)
    def test_onion_profile_icon(self):
        url = reverse('profile-logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, profile_icons['onion'])

    @override_settings(DEBUG=False, DEV=False, ONION=False)
    def test_plain_listing_icon(self):
        url = reverse('logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, listing_icons['plain'])

    @override_settings(DEBUG=False, DEV=False, ONION=False)
    def test_plain_profile_icon(self):
        url = reverse('profile-logo')
        response = self.client.get(url)
        image = base64.b64encode(response.content)
        self.assertEqual(image, profile_icons['plain'])
