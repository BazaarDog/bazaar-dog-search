from django.urls import reverse
from rest_framework import status
from rest_framework.test import RequestsClient


class ListingTests(RequestsClient):
    fixtures = ['20190417.json']

    def setUp(self):
        pass

    def test_listing_page(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'q': 'This'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only_true(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'nsfw_options': 'true'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'nsfw_options': 'Affirmative'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_nsfw_options_only_false(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'nsfw_options': 'false'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_network_options_(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'network_options': 'mainnet'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_network_options_testnet(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'network_options': 'testnet'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_listing_page_moderator_verified(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'moderator_verified': 'true'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_rating(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'rating': 5}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listing_page_condition(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'condition_type': 'USED'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
