import json

from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from ob.models.profile import Profile


class ProfileSearchTests(APITestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        # Test definitions as before.
        Profile.objects.filter().update(was_online=now())
        super().setUp()

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sorting_param(self):
        url = reverse('api-public:profile-page')
        data = {'sortBy': '-asdfasdfasdfasfd'}
        response = self.client.get(url,
                                   data,
                                   format='json',
                                   HTTP_USER_AGENT='OpenBazaar')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        self.assertTrue(c['results']['total'] > 0)

    def test_sorting_param_moderated(self):
        url = reverse('api-public:profile-page')
        data = {'sortBy': '-moderated_items_count'}
        response = self.client.get(url,
                                   data,
                                   format='json',
                                   HTTP_USER_AGENT='OpenBazaar')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_count = 10e6
        for r in c["results"]["results"]:
            p = Profile.objects.get(peerID=r['data']['peerID'])
            if p.moderated_items_count:
                self.assertTrue(p.moderated_items_count <= tmp_count)
            tmp_count = p.moderated_items_count

    def test_sorting_param_listing_count(self):
        url = reverse('api-public:profile-page')
        data = {'sortBy': '-listing_count'}
        response = self.client.get(url,
                                   data,
                                   format='json',
                                   HTTP_USER_AGENT='OpenBazaar')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_count = 10e6
        for r in c["results"]["results"]:
            p = Profile.objects.get(peerID=r['data']['peerID'])
            self.assertTrue(p.listing_count <= tmp_count)
            tmp_count = p.listing_count

    def test_sorting_param_rating_dot(self):
        url = reverse('api-public:profile-page')
        data = {'sortBy': '-rating_dot'}
        response = self.client.get(url,
                                   data,
                                   format='json',
                                   HTTP_USER_AGENT='OpenBazaar')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c = json.loads(response.content.decode('utf-8'))
        tmp_count = 10e6
        for r in c["results"]["results"]:
            p = Profile.objects.get(peerID=r['data']['peerID'])
            self.assertTrue(p.rating_dot <= tmp_count)
            tmp_count = p.rating_dot
