import json

from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from ob.models.listing import Listing
from ob.models.profile import Profile


class ListingReportTests(APITestCase):
    fixtures = ['datadump.json']

    def setUp(self):
        # Test definitions as before.
        pass

    def test_listing_report_post_illegal(self):
        """ 
        Ensure the vendor is marked illegal
        """
        url = reverse('api-public:report-listing')
        data = {
            "peerID": "QmPyweNFHayJgBRqYaoBatmnfeonxtuVZvQjtWymzmwkav",
            "slug": "vintage-dress-physical-w-options",
            "reason": settings.ILLEGAL
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = json.loads(response.content.decode('utf-8'))
        p = Profile.objects.get(pk=obj['peerID'])
        self.assertTrue(p.illegal_in_us)

    def test_listing_report_post_nsfw(self):
        """
        Ensure the listing is marked nsfw
        """
        url = reverse('api-public:report-listing')
        data = {
            "peerID": "QmPyweNFHayJgBRqYaoBatmnfeonxtuVZvQjtWymzmwkav",
            "slug": "vintage-dress-physical-w-options",
            "reason": settings.NSFW
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = json.loads(response.content.decode('utf-8'))
        l = Listing.objects.get(pk=obj['listing'])
        self.assertTrue(l.nsfw)

    def test_listing_report_post_scam(self):
        """
        Ensure the profile is marked as scam
        """
        url = reverse('api-public:report-listing')
        data = {
            "peerID": "QmPyweNFHayJgBRqYaoBatmnfeonxtuVZvQjtWymzmwkav",
            "slug": "vintage-dress-physical-w-options",
            "reason": settings.SCAM
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = json.loads(response.content.decode('utf-8'))
        p = Profile.objects.get(pk=obj['peerID'])
        self.assertTrue(p.scam)
