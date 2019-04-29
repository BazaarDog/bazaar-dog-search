from django.test.testcases import TestCase

from ob.models.exchange_rate import ExchangeRate
from ob.models.listing import Listing
from ob.util import update_price_values


class UpdateExchangeRateTests(TestCase):
    fixtures = ['exchange_rates.json']

    def setUp(self):
        # Test definitions as before.
        pass

    def got_usd(self):
        usd = ExchangeRate.objects.get(symbol='USD')
        self.assertIsNotNone(usd.rate)

    def one_bch_is_one_bch(self):
        bch = ExchangeRate.objects.get(symbol='BCH')
        self.assertTrue(bch.rate == 1)

    def update_price_values(self):
        peer = "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7"
        slug = "openbazaar-decentralize-together-t-shirt"
        l, l_c = Listing.objects.get_or_create(profile_id=peer,
                                               slug=slug,
                                               price=1500,
                                               pricing_currency='USD'
                                               )
        l.price_value = None
        l.save()
        update_price_values()
        l = Listing.objects.get(peerID=peer,
                                slug=slug)
        self.assertTrue(l.price_value > 0.001)
