from collections import namedtuple
import json

from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from rest_framework import status
from rest_framework.test import RequestsClient

from ob.models.listing import Listing


def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)


class ListingTests(RequestsClient):
    fixtures = ['datadump.json']

    def setUp(self):
        pass

    def base_test_listing_page(self, data):
        url = reverse('api-public:listing-page')
        return self.client.get(url, data, format='json')

    def get_json_object(self, content):
        return json2obj(content.decode('utf-8'))

    def test_listing_page(self):
        """
        Base search
        """
        data = {'q': 'The'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_second_page(self):
        """
        Base search
        """
        data = {'ps': '20', 'p': '2'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sorting_param(self):
        data = {'sortBy': '-asdfasdfasdfasfd'}
        response = self.base_test_listing_page_object(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json2obj(response.content)
        self.assertTrue(c.results.total > 0)

    def test_sort_price_desc(self):
        pass

    def test_sort_price_asc(self):
        pass

    def test_sort_relevance(self):
        pass

    def test_sort_new(self):
        data = {'sortBy': '-created'}
        response = self.base_test_listing_page_object(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json2obj(response.content)
        tmp_time = now()
        for r in c.results.results:
            l = Listing.objects.get(hash=r.data.hash)
            self.assertTrue(l.created < tmp_time)


    def test_sort_old(self):
        data = {'sortBy': 'created'}
        response = self.base_test_listing_page_object(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json2obj(response.content)
        tmp_time = now() - timedelta(weeks=52*5)
        for r in c.results.results:
            l = Listing.objects.get(hash=r.data.hash)
            self.assertTrue(l.created > tmp_time)

    def test_sort_rating(self):
        data = {'sortBy': 'rating'}

    def test_sort_random_string(self):
        data = {'sortBy': 'random'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only_true(self):
        data = {'nsfw_options': 'true'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only(self):
        data = {'nsfw_options': 'Affirmative'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only_false(self):
        url = reverse('api-public:listing-page')
        data = {'nsfw_options': 'false'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_network_options_(self):
        data = {'network_options': 'mainnet'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_network_options_testnet(self):
        data = {'network_options': 'testnet'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
            data = {'contract_type': c}
            response = self.base_test_listing_page(data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_condition(self):
        for c in Listing.CONDITION_TYPE_DICT.values():
            data = {'condition_type': c}
            response = self.base_test_listing_page(data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_connection_type(self):
        data = {'connection_type': 1}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_dust(self):
        data = {'dust': 'true'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_dust(self):
        data = {'dust': 'true'}
        response = self.base_test_listing_page(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)