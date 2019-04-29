from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ProfileTests(APITestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        # Test definitions as before.
        pass

    def test_profile_page(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:profile-page')
        data = {'q': 'OpenBazaar'}
        response = self.client.get(url, data, format='json')
        print(str(response))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
