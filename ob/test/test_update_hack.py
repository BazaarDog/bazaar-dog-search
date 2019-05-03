import json

from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from ob.models.listing import Listing
from .util import json2obj


class UpdateHackTests(APITestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        pass

    def base_test_listing_page(self, data):
        url = reverse('api-public:listing-page')
        return self.client.get(url,
                               data,
                               format='json',
                               HTTP_USER_AGENT='OpenBazaar')

    def test_update_hack(self):
        """
        Base search
        """
        data = {'q': 'QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
