from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ob.models.listing import Listing


class ListingTests(APITestCase):
    def test_listing_page(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:listing-page')
        data = {'q': 'This'}
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
