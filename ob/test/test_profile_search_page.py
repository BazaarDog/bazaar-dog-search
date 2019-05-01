from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ProfileSearchTests(APITestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        # Test definitions as before.
        pass

    def test_profile_page(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('api-public:profile-page')
        data = {'q': '*'}
        response = self.client.get(url,
                                   data,
                                   format='json',
                                   HTTP_USER_AGENT='OpenBazaar')
        print(str(response))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
