import json

from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from ob.models.listing import Listing
from ob.models.profile import Profile


class ListingSearchTests(APITestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        Profile.objects.filter().update(was_online=now())

    def base_test_listing_page(self, data):
        url = reverse('api-public:listing-page')
        return self.client.get(url,
                               data,
                               format='json',
                               HTTP_USER_AGENT='OpenBazaar')

    def test_listing_page(self):
        """
        Base search
        """
        data = {'q': '*', 'p': '0', 'ps': '6'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_second_page(self):
        """
        Base search
        """
        data = {'q': '*', 'ps': '20', 'p': '2'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sorting_param(self):
        data = {'sortBy': '-asdfasdfasdfasfd'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        self.assertTrue(c['results']['total'] > 0)

    def test_sort_price_desc(self):
        data = {'sortBy': '-price_value'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sort_price_asc(self):
        data = {'sortBy': 'price_value'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sort_relevance(self):
        data = {'sortBy': ''}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_rank = 100000000000
        for r in c["results"]["results"]:
            l = Listing.objects.get(hash=r['data']['hash'])
            self.assertTrue(l.rank <= tmp_rank)
            tmp_rank = l.rank

    def test_sort_least_relevant(self):
        data = {'sortBy': 'rank'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_rank = -100000000000
        for r in c["results"]["results"]:
            l = Listing.objects.get(hash=r['data']['hash'])
            self.assertTrue(l.rank >= tmp_rank)
            tmp_rank = l.rank

    def test_sort_new(self):
        data = {'sortBy': '-created'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_time = now()
        for r in c["results"]["results"]:
            l = Listing.objects.get(hash=r['data']['hash'])
            self.assertTrue(l.created <= tmp_time)
            tmp_time = l.created

    def test_sort_old(self):
        data = {'sortBy': 'created'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_time = now() - timedelta(weeks=52 * 5)
        for r in c["results"]["results"]:
            if r['data']['hash']:
                l = Listing.objects.get(hash=r['data']['hash'])
                self.assertTrue(l.created >= tmp_time)
                tmp_time = l.created

    def test_sort_rating(self):
        data = {'sortBy': '-rating_dot'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sort_random_string(self):
        data = {'sortBy': 'signature'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only_true(self):
        data = {'nsfw': 'true'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only(self):
        data = {'nsfw': 'Affirmative'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        for r in c["results"]["results"]:
            l = Listing.objects.get(hash=r['data']['hash'])
            self.assertTrue(l.nsfw)

    def test_listing_page_nsfw_options_only_false(self):
        url = reverse('api-public:listing-page')
        data = {'nsfw_options': 'false'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        for r in c["results"]["results"]:
            l = Listing.objects.get(hash=r['data']['hash'])
            self.assertTrue(l.nsfw is not True)

    def test_listing_page_network_options_(self):
        data = {'network_options': 'mainnet'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_network_options_testnet(self):
        data = {'network_options': 'testnet'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_moderator_verified(self):
        data = {'moderator_verified': 'true'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_rating(self):
        for r in [5.0, 4.95, 4.8, 4.5, 4.0, 0.0]:
            data = {'rating': r}
            response = self.base_test_listing_page(data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_contract_type(self):
        for c in Listing.CONTRACT_TYPE_DICT.values():
            data = {'contract_type': 0}
            response = self.base_test_listing_page(data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_condition(self):
        for c in Listing.CONDITION_TYPE_DICT.values():
            data = {'condition_type': 0}
            response = self.base_test_listing_page(data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_connection_type(self):
        data = {'connection_type': 1}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
