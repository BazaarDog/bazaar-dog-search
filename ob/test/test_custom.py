from django.test import TestCase
from custom import get_profile_rank, get_listing_rank
from ob.models.profile import Profile
from ob.models.listing import Listing


class CutomTest(TestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        pass

    def test_listing_rank(self):
        peer = "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7"
        slug = "openbazaar-decentralize-together-t-shirt"
        p, p_c = Profile.objects.get_or_create(peerID=peer)
        l, l_c = Listing.objects.get_or_create(profile=p, slug=slug)
        v = l.get_rank()
        self.assertTrue(int(v) > 0)

    def test_profile_rank(self):
        peer = "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7"
        p = Profile.objects.get(peerID=peer)
        v = p.get_rank()
        self.assertTrue(int(v) > 0)
