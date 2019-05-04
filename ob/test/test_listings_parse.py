import json
import os

from django.test.testcases import TestCase

from ob.models.profile import Profile
from ob.tasks.sync_listings import parse_listing_fast


class ListingsTests(TestCase):
    fixtures = ['exchange_rates.json']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_listings_parse(self):
        pwd = os.path.dirname(__file__)
        with open(pwd + '/data_responses/listings.json') as json_file:
            listings_data = json.load(json_file)
            peer = "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7"
            slug = "openbazaar-decentralize-together-t-shirt"
            p, p_c = Profile.objects.get_or_create(peerID=peer)
            for data in listings_data:
                listing = parse_listing_fast(data, p)
                listing.save()

