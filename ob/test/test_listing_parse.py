import json
import os

from django.test.testcases import TestCase

from ob.models.listing import Listing
from ob.models.profile import Profile
from ob.tasks.sync_listing import parse_listing


class ListingTests(TestCase):
    fixtures = ['datadump.json']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_listing_parse(self):
        pwd = os.path.dirname(__file__)
        with open(pwd + '/data_responses/listing.json') as json_file:
            data = json.load(json_file)
            peer = "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7"
            slug = "openbazaar-decentralize-together-t-shirt"
            p, p_c = Profile.objects.get_or_create(peerID=peer)
            l, l_c = Listing.objects.get_or_create(profile=p, slug=slug)
            l.save()
            parse_listing(l, data)
