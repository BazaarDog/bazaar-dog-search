from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ob.models.listing import Listing


class ListingTests(APITestCase):
    def test_listing_parse(self):

        pass
        url = 'https://gateway.ob1.io/ob/listings/QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7'